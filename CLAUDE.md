# CLAUDE.md — operating manual for this vault

> Read this first. It is authoritative; every directive under `Methodology/` is subordinate to it.

@System/PROFILE.md
@System/CRITICAL_FACTS.md
@Methodology/learning-mode-directive.md

## What this vault is

An Obsidian study vault for a college student. Two jobs: **(1)** turn raw course material into
linked concept notes and per-exam cheat sheets, **(2)** keep deadlines and week-by-week load
visible. Everything Claude writes is *additive* and *linked*; the student's own words are never
rewritten.

## Folder map

| Path | Purpose |
|---|---|
| `Home.md` | Dashboard (Dataview). Start here. |
| `Inbox/<CODE>/` | Raw drops, gitignored. `<Type> - <title>.md` naming contract → `/ingest-notes` |
| `Courses/<CODE — Name>/` | `_Overview.md` (the map) + concept notes at root + type-named subfolders (`Lectures/`, `Readings/`, `Homework/`, `Cheat Sheets/`, …) |
| `Boards/` | Kanban: `Deadlines.md` (all courses) · `Projects.md` (everything else) |
| `Synthesis/` | Cross-course notes: `Schedule Pinch Points.md`, retrospectives, study guides |
| `Daily/` | `YYYY-MM-DD.md` |
| `People/` | Professors, TAs, study partners |
| `Projects/` | Lab, club, job, side projects |
| `Sources/` · `Reading Queue/` | Non-course source material and what to read next |
| `Snapshots/` | Immutable heal snapshots |
| `Templates/` | Templater templates for every note type |
| `Methodology/` | The directives (ingestion, learning mode, heal, exam prep) |
| `System/` | `PROFILE.md`, `CRITICAL_FACTS.md`, `index.md`, `log.md` |
| `raw_images/` | Pasted images and slide renders, referenced by filename (Obsidian's attachment folder) |
| `scripts/` | The mechanical steps: lint, heal apply, deck intake, rename. Stdlib Python 3.11+ |
| `gaku.toml` | Vault settings the scripts and this manual read (push policy, skip dirs, heal scope, intake) |
| `docs/` | Human documentation for the template |

## Key files

- Dashboard `Home.md` · Index `System/index.md` · Log `System/log.md` (append-only)
- Deadlines `Boards/Deadlines.md` · Pinch points `Synthesis/Schedule Pinch Points.md`

## Slash commands

`/new-semester` · `/new-course` · `/ingest-notes` · `/skeleton` · `/week` · `/exam-prep` · `/heal` · `/archive-semester` — see `.claude/commands/`.
Most students never type them: each command's `description` lists the plain phrases that
should trigger it, and the Phrasebook below maps the rest.

## Phrasebook

What the student types, and what it means. Treat these as the command they name.

| They say | Do |
|---|---|
| "ingest `<CODE>` `<thing>`" · "ingest new lecture" · "file these" | `/ingest-notes`, scoped to that course or file; check the inbox **and** the course `source-dir` |
| "items in folder" · "ingest my downloads" | `python3 scripts/intake.py` over the downloads folder, then ingest everything it filed |
| "downloaded `<deck>`" · "skeleton" · "skeleton first" · "move and ingest" | `/skeleton`: intake → skeleton → say it's ready → long ingest |
| "go look at `<note>`" · "check my lecture note" | Fulfil the inline `claude draw …` / `(claude)` directives in that note only (ingestion §4G) |
| "explain `<topic>`" · "write it down" | Learning Mode; the save cue writes it into the note |
| "heal" · "heal / lint" | `/heal`, then lint, snapshot, log, commit — in one turn, no pause after the first run |
| "commit" · "commit push" · "push it" | Commit now; push when they say push, or always if `[git] push = "auto"` |
| "plan my week" · "what's due" | `/week` |
| "prep for `<exam>`" | `/exam-prep` |

When a new phrase keeps coming up, propose a row here rather than remembering it
privately: the vault travels between machines, Claude's per-machine memory doesn't.

## Academic integrity (hard rule)

Never produce graded coursework — no solutions, essays, code, or answers to be submitted.
Explain, outline, quiz, organize, check reasoning. Each course `_Overview` has an `ai-policy`
field (`open` · `explain-only` · `filing-only` · `none`) that *tightens* this per course; read it
before helping with that course. When it is `none`, do nothing for that course beyond filing
the student's own notes, and say so.

## Auto-save rules

Save **without asking**: decisions → project note + daily note · new people → `People/` stub ·
new deadlines → `Boards/Deadlines.md` + course `_Overview` · completed tasks → board ✅ Done.
**Ask before**: deleting or archiving any note.

## Propagation

| Event | Also update |
|---|---|
| New course | `Courses/` folder + `_Overview` + `System/index.md` + `Home.md` + `CRITICAL_FACTS` + `People/<Professor>` |
| New deadline | `Boards/Deadlines.md` + course `_Overview` Key Dates |
| Submitted | board → ✅ Done + `_Overview` |
| Note ingested | concept note(s) + cheat sheet + `_Overview` links |
| Syllabus change | `Synthesis/Schedule Pinch Points.md` re-derived |
| Semester archived | `status: archived` on courses, `index.md`, `log.md` |

## Git

Commit after every unit of work (one ingest, one heal run, one board update). Then read
`[git] push` in `gaku.toml`: `auto` → push; `ask` → ask once per session ("push too?");
`never` → don't. Commit messages: `<CODE>: <what>` for course work, plain imperative
otherwise. Keep the subject under ~100 characters and put the propagation list (overview,
cheat sheet, board…) in the body, not the subject.

## Scripts

Mechanical, repeatable steps run through `scripts/`, not hand edits or throwaway code:

| Script | Use it for |
|---|---|
| `check_vault.py` | Lint before every commit: dead and ambiguous links, missing embeds, heal-block damage, frontmatter |
| `heal.py` | Apply the threads you drafted for `/heal`; it validates targets and proves convergence |
| `intake.py` | File downloaded decks into each course's `source-dir`, skip re-downloads, render slides |
| `rename_note.py` | Rename or move a note and rewrite every link to it |

If a run needs a one-off script and the same need comes back, propose adding it to
`scripts/` (with a test in `tests/`) instead of rewriting it next time.

## Conventions

- Daily notes `YYYY-MM-DD.md`. People notes = full name. Archive prefix `_archived_`.
- Kanban card: `- [ ] 🟢 **Title (CODE)** · @{YYYY-MM-DD}` + indented detail line. 🟢 routine · 🟡 notable · 🔴 high-stakes. Done: `- [x] ~~…~~ ✅ date`.
- Every Claude-created note gets a one-line `## For future Claude` orientation block.
- Managed regions: `%% claude-heal:start … %%` … `%% claude-heal:end %%` — never edit inside.
- Filenames are unique vault-wide (wikilinks resolve by name, not path). Exam-keyed notes carry the course code (`Cheat Sheet - MATH101 Exam 1`, `Review - MATH101 Midterm`); a name several notes share (`_Overview`) is always linked path-qualified. `check_vault.py` fails on ambiguous links.
- Managed blocks are found by markers **at the start of a line** only — prose and directives quote the marker in backticks.
