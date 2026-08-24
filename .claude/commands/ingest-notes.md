Load and execute @Methodology/note-ingestion-directive.md.
Obey its §0 precedence rules: root CLAUDE.md wins on any conflict.

Default scope: every raw note under `Inbox/` without an `%% ingested … %%` marker.
If I name a course or file (e.g. `/ingest-notes MATH101`), scope to that. Route each
file by its first filename keyword per §2; stop and ask on any unrecognized keyword or
unmatched course. Check the course `ai-policy` (§8) first. Non-destructive — leave my
originals in place, marker only. Report per-file results (§6) when done, then commit.
