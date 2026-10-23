#!/usr/bin/env python3
"""The deterministic half of /heal: check thread proposals, write managed blocks, prove convergence.

The AI decides which notes should point where and why (judgment). This script
validates every target, writes the `%% claude-heal %%` blocks, refuses to touch a
byte outside them, and re-plans before and after writing to show the vault
converged (mechanics).

Usage:
  python3 scripts/heal.py inventory [--json]        notes in scope, with and without blocks
  python3 scripts/heal.py apply PROPOSALS.json      dry run: what would change
  python3 scripts/heal.py apply PROPOSALS.json --write [--refresh]
  python3 scripts/heal.py check                     dead or ambiguous threads inside blocks
All commands take --vault DIR.

PROPOSALS.json:
  {"blocks":  {"Courses/X — Y/Note.md": [["Target", "three to ten word why"], ...]},
   "reverse": [["Courses/X — Y/Host.md", "Target", "why"], ...]}
Both add threads to a host note's block; "reverse" lets a drafting pass list bridges
back into existing notes. A thread whose target is already in the block is kept as
is, unless --refresh, which replaces its gloss. On an existing block only the
Semantic threads list changes (a `*(none yet …)*` placeholder there is dropped).
"""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gakulib as g

THREAD = re.compile(r"^- \[\[([^\]]+)\]\] — (.+)$")
PLACEHOLDER = re.compile(r"^- \*\(none yet.*\)\*\s*$")
THREADS_HEAD = "**Semantic threads:**"
STAMP = re.compile(r"^(%% claude-heal:start \| generated )\S+( \| DO NOT EDIT INSIDE %%)", re.M)
UNSAFE = re.compile(r"[\r\n]|\[\[|\]\]|%%")  # would break a thread line or the block markers


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def in_scope(rel, cfg):
    return rel.startswith(tuple(d.rstrip("/") + "/" for d in cfg["heal"]["scope"]))


def siblings_query(fm):
    if fm.get("course"):
        return 'LIST WHERE course = this.course AND file.name != this.file.name SORT file.name ASC'
    if fm.get("type") == "project":
        return 'LIST WHERE type = "project" AND file.name != this.file.name SORT file.name ASC'
    return None


def new_block(fm, threads):
    parts = [
        f"%% claude-heal:start | generated {now()} | DO NOT EDIT INSIDE %%", "",
        "### 🔗 Connections — auto-woven (heal)", "",
        "**Linked from (live backlinks):**",
        "```dataview", "LIST WHERE contains(file.outlinks, this.file.link)", "```", "",
    ]
    q = siblings_query(fm)
    if q:
        parts += ["**Siblings (live):**", "```dataview", q, "```", ""]
    parts += [THREADS_HEAD] + [f"- [[{t}]] — {gl}" for t, gl in threads] + ["", g.HEAL_END]
    return "\n".join(parts) + "\n"


def _thread_run(lines):
    """(start, end) of the thread lines (and placeholders) under the Semantic threads heading."""
    heads = [i for i, l in enumerate(lines) if l.strip() == THREADS_HEAD]
    if not heads:
        return None
    i = j = heads[0] + 1
    while j < len(lines) and (THREAD.match(lines[j]) or PLACEHOLDER.match(lines[j])):
        j += 1
    return i, j


def block_threads(block):
    """The threads listed directly under the Semantic threads heading."""
    lines = block.splitlines()
    run = _thread_run(lines)
    return [(m.group(1), m.group(2)) for l in (lines[run[0]:run[1]] if run else []) if (m := THREAD.match(l))]


def set_threads(block, threads):
    """Rewrite only the Semantic threads list of an existing block."""
    if not threads:
        return block
    lines = block.rstrip("\n").split("\n")
    rendered = [f"- [[{t}]] — {gl}" for t, gl in threads]
    run = _thread_run(lines)
    if run:
        lines[run[0]:run[1]] = rendered
    else:
        end = max(k for k, l in enumerate(lines) if l.startswith(g.HEAL_END))
        lines[end:end] = [THREADS_HEAD] + rendered + [""]
    return "\n".join(lines) + "\n"


def restamp(old, new):
    """Keep the old timestamp unless something besides it changed, so re-runs are byte-identical."""
    if STAMP.sub(r"\1-\2", old) == STAMP.sub(r"\1-\2", new):
        return old
    return STAMP.sub(lambda m: m.group(1) + now() + m.group(2), new)


def plan(root, cfg, proposals, refresh=False, overlay=None):
    """Validate proposals and compute new file contents. Returns (changes, errors, stats).
    `overlay` maps paths to contents to plan against instead of the files on disk."""
    idx = g.Index(root, cfg)
    lo, hi = cfg["heal"]["gloss_words"]
    wanted, errors = {}, []
    try:
        items = [(h, t, gl, "block") for h, ts in proposals.get("blocks", {}).items() for t, gl in ts]
        items += [(h, t, gl, "reverse") for h, t, gl in proposals.get("reverse", [])]
    except (AttributeError, TypeError, ValueError):
        return {}, ["proposals must be {\"blocks\": {host: [[target, gloss], …]}, \"reverse\": [[host, target, gloss], …]}"], {}
    for host, target, gloss, kind in items:
        where = f"{kind} {host} → [[{target}]]"
        if host not in idx.notes or host in idx.unreadable:
            errors.append(f"{where}: host note not found, unreadable, or inside a skip dir")
            continue
        if not in_scope(host, cfg):
            errors.append(f"{where}: host is outside [heal] scope")
            continue
        if UNSAFE.search(target) or UNSAFE.search(gloss) or "|" in target:
            errors.append(f"{where}: target and gloss must be one line without [[, ]], |, or %%")
            continue
        hits = idx.resolve(target)
        if not hits:
            errors.append(f"{where}: dead target")
        elif len(hits) > 1:
            errors.append(f"{where}: ambiguous target, path-qualify it ({', '.join(sorted(hits))})")
        elif next(iter(hits)) == host:
            errors.append(f"{where}: links to itself")
        elif not lo <= len(gloss.split()) <= hi:
            errors.append(f"{where}: gloss must be {lo}–{hi} words, got {len(gloss.split())}")
        else:
            wanted.setdefault(host, []).append((target.strip(), gloss.strip(), next(iter(hits)), kind))
    changes, stats = {}, {"created": 0, "added": 0, "reverse": 0, "refreshed": 0, "before": 0, "after": 0}
    for host, threads in sorted(wanted.items()):
        raw = overlay[host] if overlay and host in overlay else g.read_raw(idx.root / host)
        crlf = "\r\n" in raw
        if (crlf and raw.count("\n") != raw.count("\r\n")) or "\r" in raw.replace("\r\n", ""):
            errors.append(f"{host}: mixed line endings — not touched")
            continue
        text = raw.replace("\r\n", "\n") if crlf else raw
        body, block, tail = g.split_heal(text)
        if block and tail.strip():
            errors.append(f"{host}: content after its heal block — fix the note first (check_vault reports it)")
            continue
        current = block_threads(block) if block else []
        stats["before"] += len(current)
        dest_of = {next(iter(idx.resolve(g.target_of(t)) or {t})): i for i, (t, _) in enumerate(current)}
        merged = list(current)
        for target, gloss, dest, kind in threads:
            if dest in dest_of:
                i = dest_of[dest]
                if refresh and merged[i][1] != gloss:
                    merged[i] = (merged[i][0], gloss)
                    stats["refreshed"] += 1
                continue
            dest_of[dest] = len(merged)
            merged.append((target, gloss))
            stats["added"] += 1
            stats["reverse"] += kind == "reverse"
        stats["after"] += len(merged)
        if block:
            nb = restamp(block, set_threads(block, merged))
            if nb == block:
                continue
            new = body + nb + tail
        else:
            stats["created"] += 1
            new = text.rstrip("\n") + "\n\n" + new_block(idx.notes[host], merged)
        out = new.replace("\n", "\r\n") if crlf else new
        if g.split_heal(out)[0].rstrip() != g.split_heal(raw)[0].rstrip():
            errors.append(f"{host}: refusing — the write would change text outside the heal block")
            continue
        changes[host] = out
    return changes, errors, stats


def cmd_apply(root, cfg, argv):
    path = next((a for a in argv[2:] if a.endswith(".json")), None)
    if not path:
        print("usage: heal.py apply PROPOSALS.json [--write] [--refresh]")
        return 2
    try:
        proposals = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"E cannot read {path}: {e}")
        return 2
    refresh = "--refresh" in argv
    changes, errors, st = plan(root, cfg, proposals, refresh)
    if not errors and changes:
        again, more, _ = plan(root, cfg, proposals, refresh, overlay=changes)
        if again or more:
            errors.append(f"would not converge: a second pass would still change {len(again)} note(s) "
                          f"({', '.join(sorted(again)) or '; '.join(more)})")
    for e in errors:
        print("E " + e)
    if errors:
        print(f"{len(errors)} error(s) — nothing written. Fix the proposals and re-run.")
        return 1
    for host in changes:
        print(("~ " if g.HEAL_START in g.read(Path(root) / host) else "+ ") + host)
    print(f"{len(changes)} note(s) to change · {st['created']} new block(s) · {st['added']} thread(s) added "
          f"({st['reverse']} reverse) · {st['refreshed']} gloss(es) refreshed · threads in touched blocks "
          f"{st['before']} → {st['after']}")
    if "--write" not in argv:
        print("dry run — add --write to apply")
        return 0
    for host, new in changes.items():
        g.write_raw(Path(root) / host, new)
    again, errors, _ = plan(root, cfg, proposals, refresh)
    if again or errors:
        print(f"E not converged on disk: a re-run would still change {len(again)} note(s)")
        return 1
    print("written · re-run plans 0 changes (converged)")
    return 0


def cmd_inventory(root, cfg, argv):
    idx = g.Index(root, cfg)
    rows = []
    for rel in sorted(idx.notes):
        if in_scope(rel, cfg) and rel not in idx.unreadable:
            _, block, _ = g.split_heal(g.read(idx.root / rel))
            rows.append((rel, bool(block), len(block_threads(block)) if block else 0))
    missing = [r for r, has, _ in rows if not has]
    report = {"in_scope": len(rows), "with_block": len(rows) - len(missing),
              "threads": sum(n for _, _, n in rows), "missing": missing,
              "skeleton": {"blocks": {r: [] for r in missing}, "reverse": []}}
    if "--json" in argv:
        print(json.dumps(report, indent=1, ensure_ascii=False))
    else:
        for r in missing:
            print("  no block: " + r)
        print(f"{report['in_scope']} notes in scope · {report['with_block']} with blocks · "
              f"{len(missing)} without · {report['threads']} semantic threads")
    return 0


def cmd_check(root, cfg, argv):
    idx = g.Index(root, cfg)
    bad = 0
    for rel in sorted(idx.notes):
        if rel in idx.unreadable:
            continue
        _, block, _ = g.split_heal(g.read(idx.root / rel))
        for target, _ in block_threads(block) if block else []:
            hits = idx.resolve(g.target_of(target))
            if len(hits) != 1:
                bad += 1
                print(f"E {rel}: [[{target}]] is {'dead' if not hits else 'ambiguous'}")
    print(f"{bad} bad thread(s)")
    return 1 if bad else 0


def main(argv):
    root = g.vault_root(argv)
    cfg = g.load_config(root)
    cmd = argv[1] if len(argv) > 1 else ""
    run = {"apply": cmd_apply, "inventory": cmd_inventory, "check": cmd_check}.get(cmd)
    if not run:
        print(__doc__)
        return 2
    return run(root, cfg, argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
