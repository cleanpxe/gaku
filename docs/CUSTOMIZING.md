# Customizing

## Add a note type

1. Add a row to **§2 Routing table** in `Methodology/note-ingestion-directive.md`
   (keyword → subfolder → template basis → what it enriches).
2. Add the row to `Inbox/README.md` so you remember it.
3. If it needs its own template, add `Templates/<Type>.md`.

## Settings (`gaku.toml`)

| Key | Default | Meaning |
|---|---|---|
| `[git] push` | `"ask"` | After committing, Claude pushes (`"auto"`), asks (`"ask"`), or leaves it to you (`"never"`). With `"auto"`, also allow `Bash(git push *)` in `.claude/settings.json`. |
| `[vault] skip_dirs` / `skip_paths` | `["Inbox"]` / `[]` | Not linted; links resolve into them only when nothing else matches. |
| `[lint] personal_scan` | `true` | Flag emails, LMS URLs and home paths. Turn off in a private vault. |
| `[lint] allow` | `[]` | Substrings of lint lines to suppress. |
| `[heal] scope` | Courses, Projects, People, Synthesis, Sources | Folders that get heal blocks. |
| `[intake] from` / `extensions` / `dpi` | `~/Downloads` / `["pdf"]` / `110` | Where downloads land, which files intake looks at, slide render resolution. |

## Deck intake for a course

In the course `_Overview.md` frontmatter:

```yaml
source-dir: "~/School/FA26/MATH101"
deck-pattern: 'Lecture (?P<n>\d{2}) (?P<title>.+?)(?: \(\d+\))?\.pdf'
deck-offset: 1
extra-patterns: ['MATH101 Homework \d+.*\.pdf']
```

- Single quotes, so the backslashes stay literal.
- `(?P<n>…)` is the deck number; vault lecture number = `n + deck-offset` (an LMS that
  numbers from 0, or a course whose first deck is the syllabus). `(?P<title>…)` is optional.
- The trailing `(?: \(\d+\))?` accepts the browser's ` (1)` re-download suffix.
- **Make patterns specific.** `Lecture (?P<n>\d+)` alone also matches another course's
  `Lecture 6 - EDA.pdf`. When two courses' patterns match one file, intake reports it as
  ambiguous and moves nothing.
- `extra-patterns` files (homework PDFs, MATLAB files…) are moved as they are, not rendered.

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
