# Changelog

## 2.0.0 — unreleased

The template catches up with how a gaku vault is actually used: decks arrive before
class, students type plain phrases instead of commands, and the mechanical steps belong
in tested scripts rather than one-off code. Plan for the rest of 2.0:
[`docs/ROADMAP-2.0.md`](docs/ROADMAP-2.0.md).

**Breaking**

- Exam-keyed notes carry the course code: `Cheat Sheet - MATH101 Exam 1`,
  `Assessments/MATH101 Exam 1.md`, `Review - MATH101 Midterm`. Migrate with
  `python3 scripts/rename_note.py OLD NEW --apply`, which rewrites every link.
- `scripts/check_vault.py` now fails on ambiguous links (a bare `[[Cheat Sheet - Exam 1]]`
  that two notes share) and on damaged heal blocks.
- Learning Mode commits only the note it edited, never `git add -A`.

**Added**

- `scripts/heal.py` — the AI drafts heal threads as JSON; the script validates every
  target, writes the blocks, refuses to touch a byte outside them, and re-runs to prove
  convergence. The heal directive's execution order now runs through it.
- `scripts/intake.py` — files downloaded course material into each course's `source-dir`
  by a per-course `deck-pattern`, reports byte-identical re-downloads instead of filing
  them twice, renders slides with `pdftoppm`. Plan-only unless `--apply`; never deletes.
- `scripts/rename_note.py` — rename or move a note and rewrite every link (aliases,
  headings, embeds, escaped table pipes), skipping frozen snapshots.
- `scripts/gakulib.py` — shared link resolution (names, aliases, path suffixes,
  case-insensitive), frontmatter parsing, heal-block parsing; `--vault DIR` /
  `GAKU_VAULT` on every script.
- `tests/` (unittest, stdlib only); CI runs them before the lint.
- `gaku.toml` — settings: push policy (`auto` / `ask` / `never`), skip dirs, personal-data
  scan, lint allowlist, heal scope, intake.
- `/skeleton` and ingestion §4E: deck-first lectures — intake, then a fill-in skeleton
  announced before the long ingest. `Templates/Lecture Skeleton.md`.
- Ingestion §4C.2 exam reviews (checklist, coverage table, cheat-sheet audit), §4F
  recordings (transcript + reconciliation), §4G inline `claude draw …` directives with a
  diagram house style, §5 scaffolds. Routing rows `Review - <exam>`, `Video`, `Handout`.
- A Phrasebook in `CLAUDE.md`, and a trigger-phrase `description` on every command.
- `CLAUDE.md` § Git (commit per unit of work, push per `gaku.toml`) and § Scripts.
- Course Overview template: `source-dir`, `deck-pattern`, `deck-offset`.
- Obsidian: `raw_images/` is the attachment folder; `mermaid-center` CSS snippet.
- `.gitattributes`: union merge for the append-only logs, so two machines don't conflict.
- `.claude/settings.json` allows the poppler tools and the test runner.

**Fixed**

- Review fixes before first use: `rename_note.py` accepts a NEW path without `.md`,
  keeps alias links and line endings, and gains `--same-course`; `heal.py` keeps CRLF
  notes' bytes, keeps the Dataview queries of a block it adds to, rejects multi-line or
  bracketed glosses, re-plans in memory before writing, and drops `*(none yet)*`
  placeholders; `intake.py` never re-renders over existing slides, survives a broken PDF
  mid-batch, and files byte-identical downloads in one batch once; non-UTF-8 notes are a
  lint error instead of a crash; unclosed fences, BOMs, CRLF frontmatter, quoted commas in
  inline lists, `[[Note.md]]` and links to any existing file type resolve correctly;
  `[lint] scope` limits what is reported.

- The heal directive's Appendix B described one author's personal vault; it is now
  generic conformance notes, and Appendix A no longer points at a wrong path.
- The demo course's links were ambiguous with the raw inputs in `docs/examples/`
  (now a `skip_paths` entry).
- Lint false positives: links via `aliases:`, escaped pipes in tables, dotted note names
  (`Reading - 4.3 …`), links inside inline code, path-qualified links.

## 0.1.0 — 2026-08-24

First public release. Extracted from a personal vault used across Spring, Summer, and Fall
2026.

- Folder structure, Templater templates, Dataview dashboard, Kanban boards.
- Directives: note ingestion (keyword routing, concept enrichment, per-exam cheat sheets,
  worked-example / review / homework layers), learning mode, vault heal, exam prep.
- Commands: `/new-semester`, `/new-course`, `/ingest-notes`, `/week`, `/exam-prep`,
  `/heal`, `/archive-semester`.
- Per-course `ai-policy` gate.
- Demo course `MATH101 — Calculus I` with the raw inputs under `docs/examples/`.
- `scripts/check_vault.py` — broken-wikilink + personal-data check, run in CI.
