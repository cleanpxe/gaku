"""Tests for scripts/. Run: python3 -m unittest discover -s tests"""
import io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import gakulib as g
import check_vault, heal, intake, rename_note

COURSE = "Courses/MATH101 — Calculus I"


class Vault:
    """A throwaway vault on disk."""

    def __init__(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel, text in files.items():
            self.write(rel, text)

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8") if isinstance(text, str) else p.write_bytes(text)

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    @property
    def cfg(self):
        return g.load_config(self.root)

    def lint(self):
        _, findings = check_vault.lint(self.root, self.cfg)
        return findings

    def close(self):
        self.tmp.cleanup()


def cats(findings):
    return sorted(f["category"] for f in findings if f["severity"] == "error")


def quiet(fn, *a):
    with redirect_stdout(io.StringIO()) as out:
        code = fn(*a)
    return code, out.getvalue()


class TestLinks(unittest.TestCase):
    def test_link_forms(self):
        text = ("[[A]] [[B|alias]] [[C#Heading]] ![[pic.png]] [[#local]]\n"
                "| t | [[D\\|alias]] |\n`[[NotALink]]` and ``[[Nor]]``\n"
                "```\n[[InFence]]\n```\n[[Reading - 4.3 Torsion]]\n")
        got = [(e, t) for _, e, t in g.links(text)]
        self.assertEqual(got, [(False, "A"), (False, "B"), (False, "C"), (True, "pic.png"),
                               (False, "D"), (False, "Reading - 4.3 Torsion")])

    def test_stray_backtick_does_not_swallow_paragraphs(self):
        text = "an unclosed ` tick\n\n[[Visible]] and a later `code`\n"
        self.assertEqual([t for _, _, t in g.links(text)], ["Visible"])

    def test_frontmatter(self):
        fm = g.frontmatter('---\naliases:\n  - "X — Y"\ntype: course\ntags: [a, b]\npattern: \'L(?P<n>\\d+)\\.pdf\'\n---\nbody')
        self.assertEqual(fm["aliases"], ["X — Y"])
        self.assertEqual(fm["tags"], ["a", "b"])
        self.assertEqual(fm["pattern"], r"L(?P<n>\d+)\.pdf")

    def test_attachment_vs_dotted_name(self):
        self.assertTrue(g.is_attachment("fig.svg"))
        self.assertFalse(g.is_attachment("Jeff S. Shamma"))


class TestLint(unittest.TestCase):
    def setUp(self):
        self.v = Vault({
            f"{COURSE}/_Overview.md": "---\naliases:\n  - MATH101 — Calculus I\ntype: course\n---\n[[Chain Rule]]\n",
            f"{COURSE}/Chain Rule.md": "---\ntype: concept\n---\n[[MATH101 — Calculus I]] ![[fig.png]]\n",
            "Courses/PHYS101 — Mechanics/_Overview.md": "---\ntype: course\n---\n[[PHYS101 — Mechanics/_Overview]]\n",
            "raw_images/fig.png": b"\x89PNG",
            "Inbox/MATH101/Lecture - 1 Limits.md": "raw\n",
            "Home.md": "[[Inbox/MATH101/Lecture - 1 Limits]]\n",
        })

    def tearDown(self):
        self.v.close()

    def test_clean_vault(self):
        self.assertEqual(cats(self.v.lint()), [])

    def test_dead_ambiguous_missing(self):
        self.v.write("Synthesis/Notes.md", "[[Nope]] [[_Overview]] ![[gone.png]]\n")
        self.assertEqual(cats(self.v.lint()), ["ambiguous-link", "dead-link", "missing-embed"])

    def test_inbox_only_wins_when_nothing_else_matches(self):
        self.v.write(f"{COURSE}/Lectures/Lecture - 1 Limits.md", "---\ntype: lecture\n---\n[[Chain Rule]]\n")
        self.v.write("Synthesis/S.md", "[[Lecture - 1 Limits]]\n")
        self.assertEqual(cats(self.v.lint()), [])

    def test_heal_block_damage(self):
        block = "%% claude-heal:start | generated 2026-01-01T00:00:00Z | DO NOT EDIT INSIDE %%\n- x\n%% claude-heal:end %%\n"
        self.v.write("Synthesis/A.md", "text\n\n" + block + "\nhuman text after\n")
        self.v.write("Synthesis/B.md", "quoted inline %% claude-heal:start marker\n")
        self.v.write("Synthesis/C.md", "use `%% claude-heal:start` markers\n")
        errs = [f for f in self.v.lint() if f["category"] == "heal-block"]
        self.assertEqual(sorted(f["file"] for f in errs), ["Synthesis/A.md", "Synthesis/B.md"])

    def test_block_quoted_in_a_fence_is_not_the_block(self):
        block = "%% claude-heal:start | generated 2026-01-01T00:00:00Z | DO NOT EDIT INSIDE %%\n- x\n%% claude-heal:end %%\n"
        self.v.write("Synthesis/D.md", "Example:\n\n````\n" + block + "````\n\nMore text.\n\n" + block)
        self.assertEqual(cats(self.v.lint()), [])
        body, found, tail = g.split_heal(self.v.read("Synthesis/D.md"))
        self.assertIn("More text.", body)
        self.assertEqual(tail, "")

    def test_allowlist(self):
        self.v.write("Synthesis/N.md", "[[Nope]]\n")
        self.v.write("gaku.toml", '[lint]\nallow = ["[[Nope]]"]\n')
        self.assertEqual(cats(self.v.lint()), [])


class TestHeal(unittest.TestCase):
    def setUp(self):
        self.v = Vault({
            f"{COURSE}/_Overview.md": "---\naliases:\n  - MATH101 — Calculus I\ntype: course\n---\n",
            f"{COURSE}/Chain Rule.md": '---\ntype: concept\ncourse: "[[MATH101 — Calculus I]]"\n---\nMy words.\n',
            f"{COURSE}/Derivative Rules.md": "---\ntype: concept\n---\nOther words.\n",
            "Boards/Deadlines.md": "board\n",
        })

    def tearDown(self):
        self.v.close()

    def props(self, data):
        p = self.v.root / "props.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        return str(p)

    def test_write_then_converge(self):
        data = {"blocks": {f"{COURSE}/Chain Rule.md": [["Derivative Rules", "the rule table this extends"]]},
                "reverse": [[f"{COURSE}/Derivative Rules.md", "Chain Rule", "the composition rule in depth"]]}
        code, out = quiet(heal.main, ["heal.py", "apply", self.props(data), "--write", "--vault", str(self.v.root)])
        self.assertEqual(code, 0, out)
        self.assertIn("converged", out)
        text = self.v.read(f"{COURSE}/Chain Rule.md")
        self.assertTrue(text.startswith('---\ntype: concept\ncourse: "[[MATH101 — Calculus I]]"\n---\nMy words.\n'))
        self.assertIn("**Siblings (live):**", text)
        self.assertIn("- [[Derivative Rules]] — the rule table this extends", text)
        self.assertNotIn("Siblings", self.v.read(f"{COURSE}/Derivative Rules.md"))
        changes, errors, _ = heal.plan(self.v.root, self.v.cfg, data)
        self.assertEqual((changes, errors), ({}, []))
        self.assertEqual(cats(self.v.lint()), [])

    def test_adds_to_existing_block_only(self):
        data = {"blocks": {f"{COURSE}/Chain Rule.md": [["Derivative Rules", "the rule table this extends"]]}}
        quiet(heal.main, ["heal.py", "apply", self.props(data), "--write", "--vault", str(self.v.root)])
        before = self.v.read(f"{COURSE}/Chain Rule.md")
        more = {"blocks": {f"{COURSE}/Chain Rule.md": [["MATH101 — Calculus I/_Overview", "the course map for context"]]}}
        changes, errors, st = heal.plan(self.v.root, self.v.cfg, more)
        self.assertEqual(errors, [])
        after = changes[f"{COURSE}/Chain Rule.md"]
        self.assertEqual(g.split_heal(after)[0], g.split_heal(before)[0])
        self.assertEqual(st["added"], 1)
        self.assertIn("- [[Derivative Rules]]", after)

    def test_existing_aliased_thread_is_not_duplicated(self):
        block = ("\n%% claude-heal:start | generated 2026-01-01T00:00:00Z | DO NOT EDIT INSIDE %%\n\n"
                 "**Semantic threads:**\n- [[Courses/MATH101 — Calculus I/Derivative Rules|Derivative Rules]] — the rule table this extends\n\n"
                 "%% claude-heal:end %%\n")
        self.v.write(f"{COURSE}/Chain Rule.md", self.v.read(f"{COURSE}/Chain Rule.md") + block)
        data = {"blocks": {f"{COURSE}/Chain Rule.md": [["Derivative Rules", "the same note named another way"]]}}
        changes, errors, st = heal.plan(self.v.root, self.v.cfg, data)
        self.assertEqual((changes, errors, st["added"]), ({}, [], 0))
        code, out = quiet(heal.main, ["heal.py", "check", "--vault", str(self.v.root)])
        self.assertEqual(code, 0, out)

    def test_rejects_bad_proposals(self):
        self.v.write("Courses/PHYS101 — Mechanics/_Overview.md", "---\ntype: course\n---\n")
        data = {"blocks": {f"{COURSE}/Chain Rule.md": [["_Overview", "which course map is this"],
                                                       ["Nope", "a target that does not exist"],
                                                       ["Chain Rule", "links straight back to itself"],
                                                       ["Derivative Rules", "too short"]],
                           "Boards/Deadlines.md": [["Chain Rule", "boards are outside the scope"]]}}
        changes, errors, _ = heal.plan(self.v.root, self.v.cfg, data)
        self.assertEqual(changes, {})
        self.assertEqual(len(errors), 5)

    def test_inventory(self):
        code, out = quiet(heal.main, ["heal.py", "inventory", "--json", "--vault", str(self.v.root)])
        report = json.loads(out)
        self.assertEqual(report["in_scope"], 3)
        self.assertEqual(len(report["missing"]), 3)


class TestIntake(unittest.TestCase):
    def setUp(self):
        self.dl = tempfile.TemporaryDirectory()
        self.src = tempfile.TemporaryDirectory()
        self.v = Vault({
            f"{COURSE}/_Overview.md": (
                "---\ntype: course\nstatus: active\n"
                f'source-dir: "{self.src.name}"\n'
                "deck-pattern: 'Lecture (?P<n>\\d+) (?P<title>.+)\\.pdf'\ndeck-offset: 1\n"
                "extra-patterns: ['HW\\d+\\.pdf']\n---\n"),
        })
        Path(self.src.name, "Lecture 01 Limits.pdf").write_bytes(b"deck-one")
        Path(self.dl.name, "Lecture 01 Limits (1).pdf").write_bytes(b"deck-one")
        Path(self.dl.name, "Lecture 02 Chain_Rule.pdf").write_bytes(b"deck-two")
        Path(self.dl.name, "HW3.pdf").write_bytes(b"hw")
        Path(self.dl.name, "receipt.pdf").write_bytes(b"other")

    def tearDown(self):
        self.v.close(); self.dl.cleanup(); self.src.cleanup()

    def test_plan_and_apply(self):
        argv = ["intake.py", "--from", self.dl.name, "--vault", str(self.v.root)]
        _, rows = intake.plan(self.v.root, self.v.cfg, argv)
        by = {Path(r["file"]).name: r for r in rows}
        self.assertEqual(by["Lecture 01 Limits (1).pdf"]["action"], "duplicate")
        self.assertEqual(by["Lecture 02 Chain_Rule.pdf"]["action"], "move")
        self.assertEqual(by["Lecture 02 Chain_Rule.pdf"]["note"], "Lecture - 3 Chain Rule")
        self.assertEqual(by["HW3.pdf"]["action"], "move")
        self.assertEqual(by["receipt.pdf"]["action"], "unmatched")
        quiet(intake.main, argv + ["--apply"])
        self.assertTrue(Path(self.src.name, "Lecture 02 Chain_Rule.pdf").exists())
        self.assertTrue(Path(self.dl.name, "Lecture 01 Limits (1).pdf").exists())  # never deleted
        self.assertTrue(Path(self.dl.name, "receipt.pdf").exists())


class TestRename(unittest.TestCase):
    def setUp(self):
        self.v = Vault({
            f"{COURSE}/Cheat Sheets/Cheat Sheet - Exam 1.md": "---\ntype: cheat-sheet\n---\nself [[Cheat Sheet - Exam 1#Top]]\n",
            f"{COURSE}/Chain Rule.md": ("[[Cheat Sheet - Exam 1]] [[Cheat Sheet - Exam 1|sheet]]\n"
                                        "| a | [[Cheat Sheet - Exam 1\\|sheet]] |\n![[Cheat Sheet - Exam 1#Chain]]\n"
                                        "`[[Cheat Sheet - Exam 1]]` stays\n"),
            "Snapshots/2026-01-01-fall.md": "[[Cheat Sheet - Exam 1]]\n",
        })

    def tearDown(self):
        self.v.close()

    def test_rename_rewrites_links(self):
        old = f"{COURSE}/Cheat Sheets/Cheat Sheet - Exam 1.md"
        code, out = quiet(rename_note.main, ["rename_note.py", old, "Cheat Sheet - MATH101 Exam 1", "--apply", "--vault", str(self.v.root)])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.v.read(f"{COURSE}/Chain Rule.md"),
                         "[[Cheat Sheet - MATH101 Exam 1]] [[Cheat Sheet - MATH101 Exam 1|sheet]]\n"
                         "| a | [[Cheat Sheet - MATH101 Exam 1\\|sheet]] |\n![[Cheat Sheet - MATH101 Exam 1#Chain]]\n"
                         "`[[Cheat Sheet - Exam 1]]` stays\n")
        self.assertIn("[[Cheat Sheet - MATH101 Exam 1#Top]]", self.v.read(f"{COURSE}/Cheat Sheets/Cheat Sheet - MATH101 Exam 1.md"))
        self.assertEqual(self.v.read("Snapshots/2026-01-01-fall.md"), "[[Cheat Sheet - Exam 1]]\n")

    def test_ambiguous_bare_links_left_alone(self):
        self.v.write("Courses/PHYS101 — Mechanics/Cheat Sheets/Cheat Sheet - Exam 1.md", "---\ntype: cheat-sheet\n---\n")
        old = f"{COURSE}/Cheat Sheets/Cheat Sheet - Exam 1.md"
        _, edits, skipped, _ = rename_note.plan(self.v.root, self.v.cfg, old, "Cheat Sheet - MATH101 Exam 1")
        self.assertEqual(edits, {})
        self.assertTrue(skipped)


if __name__ == "__main__":
    unittest.main()
