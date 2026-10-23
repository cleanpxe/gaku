#!/usr/bin/env python3
"""Rename or move a note and rewrite every wikilink that points to it.

Usage: python3 scripts/rename_note.py OLD NEW [--apply] [--same-course] [--vault DIR]
  OLD  vault-relative path of the note, e.g. "Courses/MATH101 — Calculus I/Lectures/Lecture - 4 Chain Rule.md"
  NEW  a bare name (same folder) or a vault-relative path; `.md` is added if missing
Uses `git mv` inside a git repo. Like Obsidian, it rewrites links everywhere —
skip dirs (raw notes, demo inputs) included — except Snapshots/, which are frozen.
It keeps links that reach the note through one of its `aliases:` (the alias moves
with it), keeps a path-qualified link's folder part when the note stays in its
folder, and preserves each file's line endings.

A bare link that also matches another note is ambiguous and is left alone and
listed, unless --same-course: then a bare link from a note in the same
`Courses/<course>/` folder as OLD (and no other match there) is taken to mean OLD.
Dry run unless --apply.
"""
import re, subprocess, sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gakulib as g

FROZEN = ("Snapshots/",)


def course_of(rel):
    parts = rel.split("/")
    return "/".join(parts[:2]) if parts[0] == "Courses" and len(parts) > 2 else None


def plan(root, cfg, old, new, same_course=False):
    idx = g.Index(root, cfg)
    if old not in idx.notes:
        raise SystemExit(f"not a note (or inside a skip dir): {old}")
    if "/" not in new:
        new = (PurePosixPath(old).parent / new).as_posix()
    if not new.lower().endswith(".md"):
        new += ".md"
    if (Path(root) / new).exists():
        raise SystemExit(f"already exists: {new}")
    old_stem, new_stem = Path(old).stem, Path(new).stem
    clash = idx.resolve(new_stem) - {old}
    home = course_of(old)
    edits, skipped, aliased, unreadable = {}, [], 0, []
    same_folder = PurePosixPath(new).parent == PurePosixPath(old).parent
    for rel in sorted(set(idx.notes) | {r for r in idx.secondary if r.endswith(".md")}):
        if rel.startswith(FROZEN):
            continue
        try:
            text = g.read_raw(Path(root) / rel)
        except UnicodeDecodeError:
            unreadable.append(rel)
            continue
        clean = g.strip_code(text)
        out, last, n = [], 0, 0
        for m in g.LINK.finditer(clean):
            raw = text[m.start(2):m.end(2)]
            target = g.target_of(raw)
            hits = idx.resolve(target) if target else set()
            if old not in hits:
                continue
            bare = target[:-3] if target.lower().endswith(".md") else target
            path_style = "/" in bare
            if not path_style and bare.casefold() != old_stem.casefold():
                aliased += 1  # reached through an alias, which still works after the rename
                continue
            if hits != {old}:
                mine = same_course and not path_style and home and course_of(rel) == home \
                    and not any(course_of(h) == home for h in hits - {old})
                if not mine:
                    skipped.append(f"{rel}: [[{target}]] also matches another note — not rewritten")
                    continue
            if path_style:  # keep the link's own folder part when the note doesn't move
                repl = f"{bare.rsplit('/', 1)[0]}/{new_stem}" if same_folder else new[:-3]
            else:
                repl = new[:-3] if clash else new_stem  # qualify if the new name is taken
            start = m.start(2) + raw.index(target)
            out.append(text[last:start] + repl)
            last = start + len(target)
            n += 1
        if n:
            edits[rel] = ("".join(out) + text[last:], n)
    return new, edits, skipped, clash, aliased, unreadable


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    vault = g.arg_value(argv, "--vault")
    if vault:
        args.remove(vault)
    if len(args) != 2:
        print(__doc__)
        return 2
    root = g.vault_root(argv)
    cfg = g.load_config(root)
    old, new = args
    new, edits, skipped, clash, aliased, unreadable = plan(root, cfg, old, new, "--same-course" in argv)
    for rel, (_, n) in sorted(edits.items()):
        print(f"~ {rel} ({n} link{'s' * (n != 1)})")
    for s in skipped:
        print("! " + s)
    for rel in unreadable:
        print(f"! {rel}: not valid UTF-8 — not checked for links")
    if clash:
        print(f"! the name '{Path(new).stem}' is also used by {', '.join(sorted(clash))} — rewritten links are path-qualified")
    if aliased:
        print(f"  {aliased} link(s) through an alias left as they are")
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
        g.write_raw(rootp / (new if rel == old else rel), text)
    print("renamed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
