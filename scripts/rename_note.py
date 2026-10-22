#!/usr/bin/env python3
"""Rename or move a note and rewrite every wikilink that points to it.

Usage: python3 scripts/rename_note.py OLD NEW [--apply] [--vault DIR]
  OLD  vault-relative path of the note, e.g. "Courses/MATH101 — Calculus I/Lectures/Lecture - 4 Chain Rule.md"
  NEW  a bare name (same folder) or a vault-relative path ending in .md
Uses `git mv` inside a git repo. Leaves Snapshots/ alone (they are frozen) and
never rewrites a bare link that also matches another note — those are listed so
you can path-qualify them. Dry run unless --apply.
"""
import re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gakulib as g

FROZEN = ("Snapshots/",)


def plan(root, cfg, old, new):
    idx = g.Index(root, cfg)
    if old not in idx.notes:
        raise SystemExit(f"not a note (or inside a skip dir): {old}")
    if "/" not in new:
        new = str(Path(old).parent / (new if new.endswith(".md") else new + ".md"))
    if (Path(root) / new).exists():
        raise SystemExit(f"already exists: {new}")
    new_stem = Path(new).stem
    clash = idx.resolve(new_stem) - {old}
    edits, skipped = {}, []
    for rel in idx.notes:
        if rel.startswith(FROZEN):
            continue
        text = g.read(Path(root) / rel)
        clean = g.strip_code(text)
        out, last, n = [], 0, 0
        for m in g.LINK.finditer(clean):
            raw = text[m.start(2):m.end(2)]
            target = re.split(r"\\?\||#|\^", raw, maxsplit=1)[0].rstrip("\\").strip()
            hits = idx.resolve(target) if target else set()
            if old not in hits:
                continue
            if hits != {old}:
                skipped.append(f"{rel}: [[{target}]] also matches another note — not rewritten")
                continue
            path_style = "/" in target
            repl = new[:-3] if path_style else new_stem
            if clash and not path_style:
                repl = new[:-3]  # the new name is taken elsewhere: qualify so the link stays exact
            start = m.start(2) + raw.index(target)
            out.append(text[last:start] + repl)
            last = start + len(target)
            n += 1
        if n:
            edits[rel] = ("".join(out) + text[last:], n)
    return new, edits, skipped, clash


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if "--vault" in argv:
        args.remove(argv[argv.index("--vault") + 1])
    if len(args) != 2:
        print(__doc__)
        return 2
    root = g.vault_root(argv)
    cfg = g.load_config(root)
    old, new = args
    new, edits, skipped, clash = plan(root, cfg, old, new)
    for rel, (_, n) in sorted(edits.items()):
        print(f"~ {rel} ({n} link{'s' * (n != 1)})")
    for s in skipped:
        print("! " + s)
    if clash:
        print(f"! the name '{Path(new).stem}' is also used by {', '.join(sorted(clash))} — rewritten links are path-qualified")
    print(f"{old} → {new}: {sum(n for _, n in edits.values())} link(s) in {len(edits)} note(s)")
    if "--apply" not in argv:
        print("dry run — add --apply to rename")
        return 0
    rootp = Path(root)
    (rootp / new).parent.mkdir(parents=True, exist_ok=True)
    if (rootp / ".git").exists():
        subprocess.run(["git", "-C", str(rootp), "mv", old, new], check=True)
    else:
        (rootp / old).rename(rootp / new)
    for rel, (text, _) in edits.items():
        rel = new if rel == old else rel
        (rootp / rel).write_text(text, encoding="utf-8")
    print("renamed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
