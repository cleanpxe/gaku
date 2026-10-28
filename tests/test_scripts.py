"""Tests for scripts/. Run: python3 -m unittest discover -s tests"""
import io, json, os, shutil, sys, tempfile, unittest
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


def tiny_pdf():
    """A valid one-page PDF, built by hand so the tests need no PDF library."""
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 72 72] >>"]
    out, offs = bytearray(b"%PDF-1.4\n"), []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for o in offs:
        out += b"%010d 00000 n \n" % o
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


BLOCK = ("%% claude-heal:start | generated 2026-01-01T00:00:00Z | DO NOT EDIT INSIDE %%\n\n"
         "**Linked from (live backlinks):**\n```dataview\nLIST WHERE contains(file.outlinks, this.file.link)\n```\n\n"
         "**Semantic threads:**\n{threads}\n%% claude-heal:end %%\n")


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

    def test_unclosed_fence_runs_to_the_end(self):
        text = "[[Before]]\n```python\n[[Inside]]\n\n[[After]]\n"
        self.assertEqual([t for _, _, t in g.links(text)], ["Before"])

    def test_things_that_are_not_fences(self):
        for text, want in [("```c``` is the syntax\n\n[[After]]\n", ["After"]),
                           ("```\ncode [[In]]\n````\n[[AfterLong]]\n", ["AfterLong"]),
                           ("```` ``` ````\n[[AfterQuoted]]\n", ["AfterQuoted"]),
                           ("~~~\n[[In]]\n```\n~~~\n[[AfterTilde]]\n", ["AfterTilde"])]:
            self.assertEqual([t for _, _, t in g.links(text)], want, text)

    def test_bom_crlf_and_quoted_commas(self):
        fm = g.frontmatter('\ufeff---\r\naliases: ["X, Y", Z]\r\ntype: concept\r\n---\r\nbody')
        self.assertEqual(fm, {"aliases": ["X, Y", "Z"], "type": "concept"})

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

    def test_unreadable_note_is_an_error_not_a_crash(self):
        self.v.write("Synthesis/Latin1.md", b"caf\xe9 [[Chain Rule]]\n")
        self.assertEqual(cats(self.v.lint()), ["encoding"])

    def test_md_suffix_and_any_file_type_resolve(self):
        self.v.write("Synthesis/Data.json.md", "---\ntype: note\n---\n")
        self.v.write("Synthesis/script.py", "print(1)\n")
        self.v.write("Synthesis/L.md", "[[Chain Rule.md]] [[chain rule.MD]] [[script.py]] [[Data.json]]\n")
        self.assertEqual(cats(self.v.lint()), [])

    def test_lint_scope(self):
        self.v.write("Synthesis/Old.md", "[[Nope]]\n")
        self.v.write("gaku.toml", '[lint]\nscope = ["Courses/"]\n')
        self.assertEqual(cats(self.v.lint()), [])

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

    def test_adding_to_an_existing_block_keeps_its_queries(self):
        note = f"{COURSE}/Derivative Rules.md"
        self.v.write(note, "---\ntype: concept\n---\nOther words.\n\n" + BLOCK.format(threads="- *(none yet — flagged for the next run)*\n"))
        data = {"blocks": {note: [["Chain Rule", "the composition rule in depth"]]}}
        code, out = quiet(heal.main, ["heal.py", "apply", self.props(data), "--write", "--vault", str(self.v.root)])
        self.assertEqual(code, 0, out)
        text = self.v.read(note)
        self.assertIn("```dataview\nLIST WHERE contains(file.outlinks, this.file.link)\n```", text)
        self.assertIn("**Semantic threads:**\n- [[Chain Rule]] — the composition rule in depth\n", text)
        self.assertNotIn("none yet", text)

    def test_crlf_note_keeps_its_bytes(self):
        note = f"{COURSE}/Derivative Rules.md"
        raw = b"---\r\ntype: concept\r\n---\r\nOther words.\r\n"
        (self.v.root / note).write_bytes(raw)
        data = {"blocks": {note: [["Chain Rule", "the composition rule in depth"]]}}
        code, out = quiet(heal.main, ["heal.py", "apply", self.props(data), "--write", "--vault", str(self.v.root)])
        self.assertEqual(code, 0, out)
        after = (self.v.root / note).read_bytes()
        self.assertTrue(after.startswith(raw.rstrip(b"\r\n")))
        self.assertNotIn(b"\n", after.replace(b"\r\n", b""))
        more = {"blocks": {note: [["MATH101 — Calculus I/_Overview", "the course map for context"]]}}
        quiet(heal.main, ["heal.py", "apply", self.props(more), "--write", "--vault", str(self.v.root)])
        again = (self.v.root / note).read_bytes()
        self.assertNotIn(b"\n", again.replace(b"\r\n", b""))
        self.assertIn(b"```dataview\r\nLIST WHERE contains", again)

    def test_refuses_to_append_after_an_unclosed_fence(self):
        note = f"{COURSE}/Derivative Rules.md"
        self.v.write(note, "---\ntype: concept\n---\n```\ncode never closed\n")
        data = {"blocks": {note: [["Chain Rule", "the composition rule in depth"]]}}
        changes, errors, _ = heal.plan(self.v.root, self.v.cfg, data)
        self.assertEqual(changes, {})
        self.assertTrue(errors)

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
                                                       ["Derivative Rules", "too short"],
                                                       ["Derivative Rules", "first line\nsecond line here"],
                                                       ["Derivative Rules", "has ]] inside the gloss text"]],
                           "Boards/Deadlines.md": [["Chain Rule", "boards are outside the scope"]]}}
        changes, errors, _ = heal.plan(self.v.root, self.v.cfg, data)
        self.assertEqual(changes, {})
        self.assertEqual(len(errors), 7)

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


    def test_identical_downloads_in_one_batch_file_once(self):
        Path(self.dl.name, "Lecture 05 Series.pdf").write_bytes(b"deck-five")
        Path(self.dl.name, "Lecture 05 Series (1).pdf").write_bytes(b"deck-five")
        _, rows = intake.plan(self.v.root, self.v.cfg, ["intake.py", "--from", self.dl.name])
        acts = sorted(r["action"] for r in rows if "Series" in r["file"])
        self.assertEqual(acts, ["duplicate", "move"])

    def test_course_one_folder_down(self):
        nested = Path(self.src.name, "PHYS101")
        self.v.write("Courses/SP27/PHYS101 — Mechanics/_Overview.md", (
            "---\ntype: course\nstatus: planned\n"
            f'source-dir: "{nested}"\n'
            "deck-pattern: 'PHYS101 Lec(?P<n>\\d+)\\.pdf'\n---\n"))
        Path(self.dl.name, "PHYS101 Lec2.pdf").write_bytes(b"phys-two")
        _, rows = intake.plan(self.v.root, self.v.cfg, ["intake.py", "--from", self.dl.name])
        row = next(r for r in rows if r["file"].endswith("PHYS101 Lec2.pdf"))
        self.assertEqual((row["action"], row["course"], row["target"]),
                         ("move", "PHYS101", str(nested / "PHYS101 Lec2.pdf")))


@unittest.skipUnless(shutil.which("pdftoppm"), "needs poppler's pdftoppm")
class TestIntakeRender(unittest.TestCase):
    def setUp(self):
        self.dl = tempfile.TemporaryDirectory()
        self.src = tempfile.TemporaryDirectory()
        self.v = Vault({f"{COURSE}/_Overview.md": (
            "---\ntype: course\n"
            f'source-dir: "{self.src.name}"\n'
            "deck-pattern: 'Lecture (?P<n>\\d+) (?P<title>.+)\\.pdf'\ndeck-offset: 1\n---\n")})

    def tearDown(self):
        self.v.close(); self.dl.cleanup(); self.src.cleanup()

    def run_intake(self):
        return quiet(intake.main, ["intake.py", "--from", self.dl.name, "--apply", "--render", "--vault", str(self.v.root)])

    def test_renders_never_overwrite_and_bad_pdfs_dont_stop_the_batch(self):
        Path(self.dl.name, "Lecture 01 Limits.pdf").write_bytes(tiny_pdf())
        self.run_intake()
        slides = sorted((self.v.root / "raw_images").glob("MATH101-L2-slide-*.png"))
        self.assertEqual(len(slides), 1)
        stamp = slides[0].stat().st_mtime_ns
        Path(self.dl.name, "Lecture 01 Limits v2.pdf").write_bytes(tiny_pdf() + b"% v2\n")
        Path(self.dl.name, "Lecture 03 Broken.pdf").write_bytes(b"not a pdf")
        Path(self.dl.name, "Lecture 04 Next.pdf").write_bytes(tiny_pdf() + b"% four\n")
        code, out = self.run_intake()
        self.assertEqual(code, 0, out)
        self.assertIn("already exist", out)
        self.assertIn("render failed", out)
        self.assertEqual(slides[0].stat().st_mtime_ns, stamp)
        self.assertTrue(Path(self.src.name, "Lecture 04 Next.pdf").exists())
        self.assertTrue(list((self.v.root / "raw_images").glob("MATH101-L5-slide-*.png")))


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
        _, edits, skipped, *_ = rename_note.plan(self.v.root, self.v.cfg, old, "Cheat Sheet - MATH101 Exam 1")
        self.assertEqual(edits, {})
        self.assertTrue(skipped)

    def test_same_course_resolves_ambiguous_bare_links_at_home_only(self):
        self.v.write("Courses/PHYS101 — Mechanics/Cheat Sheets/Cheat Sheet - Exam 1.md", "---\ntype: cheat-sheet\n---\n")
        self.v.write("Courses/PHYS101 — Mechanics/Forces.md", "[[Cheat Sheet - Exam 1]]\n")
        self.v.write("Synthesis/Both.md", "[[Cheat Sheet - Exam 1]]\n")
        old = f"{COURSE}/Cheat Sheets/Cheat Sheet - Exam 1.md"
        _, edits, skipped, *_ = rename_note.plan(self.v.root, self.v.cfg, old, "Cheat Sheet - MATH101 Exam 1", same_course=True)
        self.assertEqual(sorted(edits), [f"{COURSE}/Chain Rule.md", old])
        self.assertEqual(len(skipped), 2)  # PHYS101's own note and the Synthesis note stay as they are

    def test_partial_paths_keep_their_depth_and_skip_dirs_are_updated(self):
        self.v.write("Synthesis/P.md", "[[Cheat Sheets/Cheat Sheet - Exam 1|x]]\n")
        self.v.write("Inbox/MATH101/Raw.md", "[[Cheat Sheet - Exam 1]]\n")
        old = f"{COURSE}/Cheat Sheets/Cheat Sheet - Exam 1.md"
        quiet(rename_note.main, ["rename_note.py", old, "Cheat Sheet - MATH101 Exam 1", "--apply", "--vault", str(self.v.root)])
        self.assertEqual(self.v.read("Synthesis/P.md"), "[[Cheat Sheets/Cheat Sheet - MATH101 Exam 1|x]]\n")
        self.assertEqual(self.v.read("Inbox/MATH101/Raw.md"), "[[Cheat Sheet - MATH101 Exam 1]]\n")

    def test_slashed_new_without_md(self):
        old = f"{COURSE}/Cheat Sheets/Cheat Sheet - Exam 1.md"
        code, out = quiet(rename_note.main, ["rename_note.py", old, f"{COURSE}/Cheat Sheets/Sheet One", "--apply", "--vault", str(self.v.root)])
        self.assertEqual(code, 0, out)
        self.assertTrue((self.v.root / COURSE / "Cheat Sheets" / "Sheet One.md").exists())
        self.assertIn("[[Sheet One|sheet]]", self.v.read(f"{COURSE}/Chain Rule.md"))

    def test_alias_links_and_line_endings_kept(self):
        old = f"{COURSE}/Cheat Sheets/Cheat Sheet - Exam 1.md"
        self.v.write(old, "---\naliases:\n  - Sheet\ntype: cheat-sheet\n---\n")
        (self.v.root / "Synthesis").mkdir(exist_ok=True)
        (self.v.root / "Synthesis/W.md").write_bytes(b"[[Sheet]] and [[Cheat Sheet - Exam 1]]\r\nend\r\n")
        quiet(rename_note.main, ["rename_note.py", old, "Cheat Sheet - MATH101 Exam 1", "--apply", "--vault", str(self.v.root)])
        self.assertEqual((self.v.root / "Synthesis/W.md").read_bytes(),
                         b"[[Sheet]] and [[Cheat Sheet - MATH101 Exam 1]]\r\nend\r\n")


if __name__ == "__main__":
    unittest.main()
