#!/usr/bin/env python3
"""Vault lint: links, embeds, heal blocks, frontmatter, stray personal data.

Usage: python3 scripts/check_vault.py [--strict] [--json] [--vault DIR]
  --strict   warnings fail too, and unfilled ⬜ placeholders outside System/ and
             Templates/ count as warnings
  --json     machine-readable findings
Exit 1 on any error (or any warning under --strict). Read-only.

Errors:   dead-link · missing-embed · ambiguous-link · heal-block · template-syntax · personal-data · encoding
Warnings: duplicate-name · missing-frontmatter · orphan · placeholder

`[lint] scope` in gaku.toml limits which files are reported on (links still resolve
across the whole vault). Suppress a known false positive by adding a substring of its
output line to `[lint] allow`.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gakulib as g

PERSONAL = [
    (re.compile(r"[\w.+-]+@(?!example\.edu|anthropic\.com)[\w-]+\.(edu|com|org|net)\b"), "email address"),
    (re.compile(r"canvas\.[\w.-]+/courses/\d+"), "LMS course URL"),
    (re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+/"), "absolute home path"),
]
ALLOW_PERSONAL = {"LICENSE", "THIRD-PARTY-NOTICES.md"}
ERRORS = {"dead-link", "missing-embed", "ambiguous-link", "heal-block", "template-syntax", "personal-data", "encoding"}


def lint(root, cfg, strict=False):
    idx = g.Index(root, cfg)
    prose = tuple(cfg["vault"]["prose_dirs"])
    fm_dirs = tuple(cfg["lint"]["frontmatter_dirs"])
    scope = tuple(d.rstrip("/") + "/" for d in cfg["heal"]["scope"])
    findings, inbound, outbound = [], {}, {}

    def add(rel, line, cat, msg):
        findings.append({"file": rel, "line": line, "category": cat,
                         "severity": "error" if cat in ERRORS else "warning", "message": msg})

    for rel, fm in idx.notes.items():
        if rel in idx.unreadable:
            add(rel, 1, "encoding", "not valid UTF-8 — Obsidian and the scripts can't read it reliably")
            continue
        text = g.read(idx.root / rel)
        in_template = rel.startswith("Templates/")
        is_prose = rel.startswith(prose)

        if not is_prose:
            for line, embed, target in g.links(text):
                if g.is_placeholder(target) or target.endswith("/"):
                    continue
                hits = idx.resolve(target)
                if not hits:
                    if embed and g.is_attachment(target):
                        add(rel, line, "missing-embed", f"![[{target}]] — no such file")
                    elif not in_template:
                        add(rel, line, "dead-link", f"[[{target}]] — no such note")
                elif len(hits) > 1 and not in_template:
                    add(rel, line, "ambiguous-link",
                        f"[[{target}]] matches {len(hits)} notes — path-qualify it: "
                        + ", ".join(sorted(h[:-3] if h.endswith(".md") else h for h in hits)))
                else:
                    dest = next(iter(hits))
                    if dest != rel:
                        outbound.setdefault(rel, set()).add(dest)
                        inbound.setdefault(dest, set()).add(rel)

        starts, ends, loose = g.heal_markers(text)
        for line in loose:
            add(rel, line, "heal-block", "heal marker not at line start (quote it in backticks, or it was pasted into prose)")
        if len(starts) > 1:
            add(rel, starts[1], "heal-block", f"{len(starts)} heal blocks — exactly one allowed")
        if len(starts) != len(ends):
            add(rel, (starts or ends)[0], "heal-block", f"unbalanced heal markers ({len(starts)} start, {len(ends)} end)")
        elif len(starts) == 1:
            _, _, tail = g.split_heal(text)
            if tail.strip():
                add(rel, ends[0], "heal-block", "content after the heal block — the block must close the note")

        if in_template and "{{" in text:
            add(rel, 1, "template-syntax", "mustache placeholder — use Templater <% %> syntax")
        if rel.startswith(fm_dirs) and not fm.get("type"):
            add(rel, 1, "missing-frontmatter", "no `type:` in frontmatter")
        if strict and "⬜" in text and not (rel.startswith("System/") or in_template or is_prose):
            add(rel, 1, "placeholder", "unfilled ⬜ placeholder")
        if cfg["lint"]["personal_scan"] and Path(rel).name not in ALLOW_PERSONAL:
            for i, ln in enumerate(text.splitlines(), 1):
                for rx, label in PERSONAL:
                    for m in rx.finditer(ln):
                        add(rel, i, "personal-data", f"{label} '{m.group(0)}'")

    for rel in idx.notes:
        if rel.startswith(scope) and not inbound.get(rel) and not outbound.get(rel):
            add(rel, 1, "orphan", "no links in or out")
    only = tuple(cfg["lint"]["scope"])
    in_scope = lambda rel: not only or rel.startswith(only)
    for name, rels in idx.duplicates().items():
        shown = next((r for r in rels if in_scope(r)), rels[0])
        add(shown, 1, "duplicate-name", f"'{name}' is shared by {len(rels)} notes: {', '.join(rels)}"
            " — bare links to it are ambiguous")

    allow = cfg["lint"]["allow"]
    kept = [f for f in findings if in_scope(f["file"]) and not any(a in fmt(f) for a in allow)]
    return len(idx.notes), sorted(kept, key=lambda f: (f["severity"] != "error", f["file"], f["line"]))


def fmt(f):
    return f"{f['file']}:{f['line']}: [{f['category']}] {f['message']}"


def main(argv):
    root = g.vault_root(argv)
    cfg = g.load_config(root)
    strict = "--strict" in argv
    n, findings = lint(root, cfg, strict)
    errors = sum(f["severity"] == "error" for f in findings)
    warnings = len(findings) - errors
    if "--json" in argv:
        print(json.dumps({"notes": n, "errors": errors, "warnings": warnings, "findings": findings}, indent=1))
    else:
        for f in findings:
            print(("E " if f["severity"] == "error" else "W ") + fmt(f))
        print(f"{n} notes checked: {errors} error(s), {warnings} warning(s)")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
