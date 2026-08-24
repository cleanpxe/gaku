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
| `raw_images/` | Pasted images, referenced by filename |
| `docs/` | Human documentation for the template |

## Key files

- Dashboard `Home.md` · Index `System/index.md` · Log `System/log.md` (append-only)
- Deadlines `Boards/Deadlines.md` · Pinch points `Synthesis/Schedule Pinch Points.md`

## Slash commands

`/new-semester` · `/new-course` · `/ingest-notes` · `/week` · `/exam-prep` · `/heal` · `/archive-semester` — see `.claude/commands/`.

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

## Conventions

- Daily notes `YYYY-MM-DD.md`. People notes = full name. Archive prefix `_archived_`.
- Kanban card: `- [ ] 🟢 **Title (CODE)** · @{YYYY-MM-DD}` + indented detail line. 🟢 routine · 🟡 notable · 🔴 high-stakes. Done: `- [x] ~~…~~ ✅ date`.
- Every Claude-created note gets a one-line `## For future Claude` orientation block.
- Managed regions: `%% claude-heal:start … %%` … `%% claude-heal:end %%` — never edit inside.
- Filenames are unique vault-wide (wikilinks resolve by name, not path).
- Commit, don't push. Commit messages: `<CODE>: <what>` for course work, plain imperative otherwise.
