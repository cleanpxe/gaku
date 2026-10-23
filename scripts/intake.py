#!/usr/bin/env python3
"""File downloaded course material: match each download to a course, skip re-downloads,
move it into the course's source folder, and optionally render deck slides.

A course opts in through its `_Overview.md` frontmatter:
  source-dir: "~/School/MATH101"                        where its files live (outside the vault is fine)
  deck-pattern: 'Lecture (?P<n>\\d+) (?P<title>.+)\\.pdf'  regex for its slide decks (case-insensitive)
  deck-offset: 0                                        vault lecture number = deck number + offset
  extra-patterns: ['HW\\d+.*\\.pdf', '.*\\.m']            other files to move as they are (no rendering)
Only files whose extension is in `[intake] extensions` (gaku.toml, default pdf) are looked at,
so add e.g. "m" there for MATLAB files.

Usage:
  python3 scripts/intake.py                    plan only (default)
  python3 scripts/intake.py --apply            move the matched files
  python3 scripts/intake.py --apply --render   also render decks to raw_images/<CODE>-L<N>-slide-<page>.png
  options: --from DIR · --course CODE · --json · --vault DIR
Never deletes or overwrites anything: a download byte-identical to a filed file (or to another
download in the same batch) is reported and left in place, an existing destination is a
conflict, and slides already rendered for a lecture are not rendered again.
"""
import glob, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gakulib as g


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
        try:
            out.append({
                "code": code, "folder": folder,
                "source_dir": Path(fm["source-dir"]).expanduser(),
                "deck": re.compile(fm["deck-pattern"], re.I) if fm.get("deck-pattern") else None,
                "extra": [re.compile(p, re.I) for p in (extra if isinstance(extra, list) else [extra])],
                "offset": int(fm.get("deck-offset") or 0),
            })
        except (re.error, ValueError) as e:
            raise SystemExit(f"{ov.relative_to(root)}: bad deck-pattern / extra-patterns / deck-offset — {e}")
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
    src = Path(g.arg_value(argv, "--from", cfg["intake"]["from"])).expanduser()
    exts = {"." + e.lstrip(".").lower() for e in cfg["intake"]["extensions"]}
    clist = courses(root, g.arg_value(argv, "--course"))
    downloads = sorted(p for p in src.iterdir() if p.is_file() and p.suffix.lower() in exts) if src.is_dir() else []
    filed = filed_hashes(clist, {p.stat().st_size for p in downloads})
    rows, batch = [], {}
    for f in downloads:
        row = {"file": str(f), "action": "unmatched"}
        h = sha256(f)
        if h in filed or h in batch:
            row.update(action="duplicate", target=str(filed.get(h) or batch[h]))
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
            if not dest.exists():
                batch[h] = dest
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
    pattern = glob.escape(prefix.name) + "-*.png"
    if any(images.glob(pattern)):
        return f"{prefix.name}-*.png already exist — not re-rendered (move them aside to re-render)"
    try:
        subprocess.run(["pdftoppm", "-r", str(cfg["intake"]["dpi"]), "-png", row["target"], str(prefix)],
                       check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        why = (e.stderr or "").strip().splitlines()
        return f"render failed ({why[-1] if why else f'exit {e.returncode}'}) — the file was filed; check it opens"
    return f"rendered {len(list(images.glob(pattern)))} slide(s) → {prefix.name}-<page>.png"


LABEL = {"move": "MOVE", "duplicate": "DUP ", "unmatched": "??  ", "ambiguous": "AMBG", "conflict": "CONF", "error": "ERR "}


def main(argv):
    root = g.vault_root(argv)
    cfg = g.load_config(root)
    src, rows = plan(root, cfg, argv)
    apply, do_render = "--apply" in argv, "--render" in argv
    for row in rows:
        if apply and row["action"] == "move":
            if Path(row["target"]).exists():
                row["action"] = "conflict"
                continue
            try:
                Path(row["target"]).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(row["file"], row["target"])
            except OSError as e:
                row.update(action="error", error=str(e))
                continue
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
            "error": f"→ {r.get('target')} failed: {r.get('error')}",
        }[r["action"]]
        print(f"{LABEL[r['action']]} {name} {extra}" + (f"\n     {r['render']}" if r.get("render") else ""))
    moves = sum(r["action"] == "move" for r in rows)
    print(f"{len(rows)} file(s) in {src}: {moves} to move, "
          f"{sum(r['action'] == 'duplicate' for r in rows)} re-download(s), "
          f"{sum(r['action'] in ('unmatched', 'ambiguous', 'conflict', 'error') for r in rows)} need you")
    if moves and not apply:
        print("plan only — add --apply to move (and --render for slide images)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
