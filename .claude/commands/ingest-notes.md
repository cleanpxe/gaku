---
description: "File raw course material into the vault: typed note, concept enrichment, cheat sheet. Use for 'ingest', 'ingest <course> <thing>', 'ingest new lecture', 'file these notes', 'items in folder'."
argument-hint: "[CODE or file]"
---
Load and execute @Methodology/note-ingestion-directive.md.
Obey its §0 precedence rules: root CLAUDE.md wins on any conflict.

Default scope: every raw note under `Inbox/` without an `%% ingested … %%` marker, plus
anything new in each course's `source-dir` (§0.5) — run `python3 scripts/intake.py` first
to see what was downloaded. If I name a course or file (e.g. `/ingest-notes MATH101`),
scope to that. Route each file by its first filename keyword per §2; stop and ask on any
unrecognized keyword or unmatched course. Check the course `ai-policy` (§8) first.
Non-destructive — leave my originals in place, marker only. Report per-file results (§6),
run `python3 scripts/check_vault.py`, then commit (push per `CLAUDE.md` § Git).
