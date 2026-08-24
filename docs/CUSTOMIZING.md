# Customizing

## Add a note type

1. Add a row to **§2 Routing table** in `Methodology/note-ingestion-directive.md`
   (keyword → subfolder → template basis → what it enriches).
2. Add the row to `Inbox/README.md` so you remember it.
3. If it needs its own template, add `Templates/<Type>.md`.

## Rename or add folders

`CLAUDE.md` → **Folder map** is the source of truth. Update it, then grep the directives
for the old name (`Methodology/`). `Home.md` Dataview queries use `FROM "Courses"` etc. —
adjust if you rename those.

## Change the deadlines card format

`CLAUDE.md` → **Conventions**, and the `## For future Claude` block in `Boards/Deadlines.md`.
Keep the `@{YYYY-MM-DD}` token — Kanban's date feature depends on it.

## Change how Claude teaches

`Methodology/learning-mode-directive.md` §2 (voice, metaphors first, derivations shown in
full) and §3 (callout vocabulary). `System/PROFILE.md` → *How I want to be helped* is
where personal preferences go ("quiz me before explaining", "no analogies").

## Tighten or loosen the AI rules

`CLAUDE.md` → **Academic integrity** is the global floor. Per course, the `ai-policy`
frontmatter in `_Overview.md`. See `ACADEMIC-INTEGRITY.md`.

## Daily note

`Templates/Daily Note.md` is deliberately lean (focus / due-soon / log / review). Add
habits, mood, gratitude — whatever you'll actually fill in. `Home.md` → *Recent days*
lists them regardless of fields.

## Use a different AI tool

The directives are plain Markdown instructions. Point Cursor, Codex, or any agent at
`CLAUDE.md` and the file under `Methodology/` you want run. Slash commands in
`.claude/commands/` are one-paragraph prompts you can paste.

## No-AI mode

Delete `.claude/` and `Methodology/`; keep everything else. You still have: the folder
structure, Templater templates, the Dataview dashboard, the Kanban boards, the naming
contract as a manual filing guide (`Inbox/README.md`), and the Pinch Points template.
