#!/usr/bin/env python3
"""File downloaded course material: match each download to a course, skip re-downloads,
move it into the course's source folder, and optionally render deck slides.

A course opts in through its `_Overview.md` frontmatter:
  source-dir: "~/School/MATH101"                        where its files live (outside the vault is fine)
  deck-pattern: 'Lecture (?P<n>\\d+) (?P<title>.+)\\.pdf'  regex for its slide decks (case-insensitive)
  deck-offset: 0                                        vault lecture number = deck number + offset
  extra-patterns: ['HW\\d+.*\\.pdf', '.*\\.m']            other files to move as they are (no rendering)

Usage:
  python3 scripts/intake.py                    plan only (default)
  python3 scripts/intake.py --apply            move the matched files
  python3 scripts/intake.py --apply --render   also render decks to raw_images/<CODE>-L<N>-slide-NN.png
  options: --from DIR · --course CODE · --json · --vault DIR
Never deletes anything. A download byte-identical to a filed file is reported and left in place.
"""
import hashlib, json, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gakulib as g


def arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def courses(root, only=None):
    out = []
    for ov in sorted(Path(root, "Courses").glob("*/_Overview.md")):
        fm = g.frontmatter(g.read(ov))
        folder = ov.parent.name
        code = fm.get("code") or folder.split(" — ")[0].split()[0]
        if not fm.get("source-dir") or fm.get("status") == "archived":
            continue
        if only and code.casefold() != only.casefold():
            continue
        extra = fm.get("extra-patterns") or []
        out.append({
            "code": code, "folder": folder,
            "source_dir": Path(fm["source-dir"]).expanduser(),
            "deck": re.compile(fm["deck-pattern"], re.I) if fm.get("deck-pattern") else None,
            "extra": [re.compile(p, re.I) for p in (extra if isinstance(extra, list) else [extra])],
            "offset": int(fm.get("deck-offset") or 0),
        })
    return out


def filed_hashes(course_list, sizes):
    """Hashes of filed files, reading only those whose size matches a download."""
    seen = {}
    for c in course_list:
        if c["source_dir"].is_dir():
            for p in sorted(c["source_dir"].rglob("*")):
                if p.is_file() and p.stat().st_size in sizes:
                    seen.setdefault(sha256(p), p)
    return seen


def plan(root, cfg, argv):
    src = Path(arg(argv, "--from", cfg["intake"]["from"])).expanduser()
    exts = {"." + e.lstrip(".").lower() for e in cfg["intake"]["extensions"]}
    clist = courses(root, arg(argv, "--course"))
    downloads = sorted(p for p in src.iterdir() if p.is_file() and p.suffix.lower() in exts) if src.is_dir() else []
    filed = filed_hashes(clist, {p.stat().st_size for p in downloads})
    rows = []
    for f in downloads:
        row = {"file": str(f), "action": "unmatched"}
        h = sha256(f)
        if h in filed:
            row.update(action="duplicate", target=str(filed[h]))
            rows.append(row)
            continue
        hits = []
        for c in clist:
            m = c["deck"].fullmatch(f.name) if c["deck"] else None
            if m:
                hits.append((c, m, True))
            elif any(p.fullmatch(f.name) for p in c["extra"]):
                hits.append((c, None, False))
        if len(hits) > 1:
            row.update(action="ambiguous", courses=[c["code"] for c, _, _ in hits])
        elif hits:
            c, m, deck = hits[0]
            dest = c["source_dir"] / f.name
            row.update(action="conflict" if dest.exists() else "move", course=c["code"], target=str(dest), deck=deck)
            if m and "n" in m.groupdict() and m.group("n"):
                n = int(m.group("n")) + c["offset"]
                title = re.sub(r"[_\s]+", " ", m.groupdict().get("title") or "").strip()
                row.update(lecture=n, note=f"Lecture - {n} {title}".strip())
        rows.append(row)
    return src, rows


def render(root, cfg, row):
    if not shutil.which("pdftoppm"):
        return "pdftoppm not found (install poppler) — skipped"
    images = Path(root) / cfg["vault"]["images"]
    images.mkdir(exist_ok=True)
    tag = f"L{row['lecture']}" if "lecture" in row else re.sub(r"\W+", "-", Path(row["file"]).stem).strip("-")
    prefix = images / f"{row['course']}-{tag}-slide"
    subprocess.run(["pdftoppm", "-r", str(cfg["intake"]["dpi"]), "-png", row["target"], str(prefix)], check=True)
    return f"rendered {len(list(images.glob(prefix.name + '-*.png')))} slide(s) → {prefix.name}-NN.png"


LABEL = {"move": "MOVE", "duplicate": "DUP ", "unmatched": "??  ", "ambiguous": "AMBG", "conflict": "CONF"}


def main(argv):
    root = g.vault_root(argv)
    cfg = g.load_config(root)
    src, rows = plan(root, cfg, argv)
    apply, do_render = "--apply" in argv, "--render" in argv
    for row in rows:
        if apply and row["action"] == "move":
            Path(row["target"]).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(row["file"], row["target"])
            row["done"] = True
            if do_render and row.get("deck"):
                row["render"] = render(root, cfg, row)
    if "--json" in argv:
        print(json.dumps({"from": str(src), "rows": rows}, indent=1, ensure_ascii=False))
        return 0
    for r in rows:
        name = Path(r["file"]).name
        extra = {
            "move": f"→ {r.get('target')}  [{r.get('course')}{' · ' + r['note'] if r.get('note') else ''}]",
            "duplicate": f"= already filed at {r.get('target')} (left in place)",
            "unmatched": "no course pattern matches — route by hand",
            "ambiguous": f"matches {', '.join(r.get('courses', []))} — tighten a pattern",
            "conflict": f"→ {r.get('target')} exists with different content — not moved",
        }[r["action"]]
        print(f"{LABEL[r['action']]} {name} {extra}" + (f"\n     {r['render']}" if r.get("render") else ""))
    moves = sum(r["action"] == "move" for r in rows)
    print(f"{len(rows)} file(s) in {src}: {moves} to move, "
          f"{sum(r['action'] == 'duplicate' for r in rows)} re-download(s), "
          f"{sum(r['action'] in ('unmatched', 'ambiguous', 'conflict') for r in rows)} need you")
    if moves and not apply:
        print("plan only — add --apply to move (and --render for slide images)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
