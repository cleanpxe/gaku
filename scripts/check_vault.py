#!/usr/bin/env python3
"""Vault lint: broken wikilinks, stray personal data, placeholder syntax.

Usage: python3 scripts/check_vault.py [--strict]
  --strict   also fail on unfilled ⬜ placeholders outside System/ and Templates/
Exit 1 on any finding.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", ".obsidian", "node_modules", "Inbox", "_trash"}
# Prose *about* links (directives, docs, commands) — checked for personal data only
PROSE_DIRS = ("docs/", "Methodology/", ".claude/")
ALIASES = re.compile(r"^aliases:\s*\n((?:\s+-\s+.*\n)+)", re.M)
WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
EMBED = re.compile(r"!\[\[([^\]|#]+)")
PERSONAL = [
    (re.compile(r"[\w.+-]+@(?!example\.edu|anthropic\.com)[\w-]+\.(edu|com|org|net)\b"), "email address"),
    (re.compile(r"canvas\.[\w.-]+/courses/\d+"), "LMS course URL"),
    (re.compile(r"/home/[a-z0-9_]+/"), "absolute home path"),
]
ALLOW_PERSONAL = {"LICENSE", "THIRD-PARTY-NOTICES.md"}

def md_files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if fn.endswith(".md"):
                yield os.path.join(dp, fn)

def main():
    strict = "--strict" in sys.argv
    files = list(md_files())
    names = {}
    for f in files:
        rel = os.path.relpath(f, ROOT)
        if rel.startswith(PROSE_DIRS):
            continue
        base = os.path.splitext(os.path.basename(f))[0]
        names.setdefault(base, []).append(rel)
        head = open(f, encoding="utf-8").read(2000)
        am = ALIASES.search(head)
        if am:
            for line in am.group(1).splitlines():
                alias = line.strip().lstrip("-").strip().strip('"')
                if alias:
                    names.setdefault(alias, []).append(rel)
        # also allow path-style links: "Boards/Deadlines", "MATH101 — Calculus I/_Overview"
        names.setdefault(os.path.splitext(rel)[0], []).append(rel)
    all_files = set()
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            all_files.add(fn)
    findings = []
    for f in files:
        rel = os.path.relpath(f, ROOT)
        text = open(f, encoding="utf-8").read()
        in_template = rel.startswith("Templates/")
        prose = rel.startswith(PROSE_DIRS)
        for m in WIKILINK.finditer(text) if not prose else ():
            target = m.group(1).strip()
            if in_template and ("<%" in target or "{{" in target):
                continue
            if target.endswith("/"):  # folder link
                continue
            if target not in names and os.path.basename(target) not in names:
                findings.append(f"{rel}: broken wikilink [[{target}]]")
        for m in EMBED.finditer(text) if not prose else ():
            target = m.group(1).strip()
            if os.path.basename(target) not in all_files and not (in_template):
                findings.append(f"{rel}: missing embed ![[{target}]]")
        if os.path.basename(rel) not in ALLOW_PERSONAL:
            for rx, label in PERSONAL:
                for m in rx.finditer(text):
                    findings.append(f"{rel}: {label} '{m.group(0)}'")
        if "{{" in text and in_template:
            findings.append(f"{rel}: mustache placeholder — use Templater <% %> syntax")
        if strict and "⬜" in text and not (rel.startswith("System/") or in_template):
            findings.append(f"{rel}: unfilled ⬜ placeholder")
    dupes = {k: v for k, v in names.items() if len(set(v)) > 1 and "/" not in k}
    for k, v in dupes.items():
        findings.append(f"duplicate note name '{k}': {sorted(set(v))}")
    for line in findings:
        print(line)
    print(f"{len(files)} notes checked, {len(findings)} finding(s)")
    return 1 if findings else 0

if __name__ == "__main__":
    sys.exit(main())
