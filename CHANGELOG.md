# Changelog

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
