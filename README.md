# gaku 学 — a study vault for college

> Drop raw notes in. Get linked concept notes, per-exam cheat sheets, and a deadlines board
> out. An [Obsidian](https://obsidian.md) vault with an optional
> [Claude Code](https://claude.com/claude-code) pipeline that does the filing for you.

Built and used across three semesters of an engineering degree. Works with zero AI; gets
much better with it.

## Why

Note systems die at week 6 because filing is boring. gaku splits the work: **you** capture
(lecture, reading, homework — messy is fine); **the pipeline** files, links, captions your
images, and distills. Every raw note becomes a typed note, enriches a concept note, and
updates the cheat sheet for the exam it will appear on.

## What you get

- **One folder per course** — a map (`_Overview.md`), concept notes at the root, and
  type-named subfolders (`Lectures/`, `Readings/`, `Homework/`, `Cheat Sheets/`…) that stay
  navigable all semester.
- **A naming contract** — `Lecture - 4 Chain Rule.md` in `Inbox/MATH101/` is everything the
  pipeline needs to know.
- **Per-exam cheat sheets** that grow as you ingest — every formula in a callout, every
  approach tied to the homework problems that use it.
- **Deadlines board + pinch points** — not just *what's due* but *which weeks collide*.
- **A dashboard** (Dataview): due soon, active courses, cheat sheets, stub concepts.
- **Deck-first lectures** — download the slides, say "skeleton": the deck is filed,
  re-downloads are caught, slides are rendered, and a fill-in skeleton is waiting before
  class starts.
- **Self-healing links** — `/heal` weaves cross-course connections into hidden managed
  blocks. It never touches your words.
- **Scripts for the mechanical parts** — lint, heal, intake and rename are tested,
  standard-library Python, so the AI does judgment and the scripts do bookkeeping.
- **Academic-integrity by design** — a per-course `ai-policy` field the pipeline obeys.

## Quickstart

1. **Use this template** → clone your new repo.
2. Open the folder in Obsidian as a vault; trust the bundled plugins (Dataview, Kanban,
   Templater, Calendar).
3. Open `Home.md`. Poke around the demo course, `Courses/MATH101 — Calculus I/`, to see what
   ingestion produces (`docs/examples/` shows what went *in*).
4. With Claude Code: `cd` into the vault, run `claude`, then `/new-semester`.
   Without: fill the ⬜ in `System/PROFILE.md` + `System/CRITICAL_FACTS.md`, and create
   `Courses/<CODE — Name>/_Overview.md` from the Templater template.
5. Take notes → `Inbox/<CODE>/<Type> - <title>.md` → `/ingest-notes`.

Full walkthrough: [`docs/SETUP.md`](docs/SETUP.md).

## The naming contract

| Filename prefix | Goes to | Also updates |
|---|---|---|
| `Lecture - ` | `Lectures/` | concept notes |
| `Reading - ` / `Chapter - ` | `Readings/` | concept notes, cheat sheet |
| `Homework - ` | `Homework/` (your solved set, post-submission) | concept *problem types*, cheat sheet *assigned* scenarios |
| `Examples - Ch N` | `Examples/` | cheat sheet worked examples |
| `Review - Ch N` | `Reviews/` | audits the concept note |
| `Review - <exam>` | `Reviews/` (the instructor's exam review) | audits that exam's cheat sheet |
| `Video - ` / `Handout - ` | `Videos/` / `Handouts/` | concept notes, cheat sheet |
| `Assignment - ` | `Assignments/` (logistics, pre-completion) | Deadlines board |
| `Exam N` / `Quiz N` | `Assessments/<CODE> Exam N` | Deadlines board |
| `Lab - ` | `Labs/` | concept notes |
| `Note - ` | course root — it *is* a concept note | — |

Unknown prefix → the pipeline **stops and asks**. It never guesses.

## Slash commands (Claude Code)

| Command | What it does |
|---|---|
| `/new-semester` | Wizard: who you are, term, courses → profile, facts, folders, boards |
| `/new-course <syllabus>` | Syllabus (PDF / URL / paste) → `_Overview`, every deadline on the board, professor in `People/`, pinch points re-derived |
| `/ingest-notes [CODE]` | File everything in `Inbox/` per the contract; enrich concepts; update cheat sheets |
| `/skeleton [CODE] [deck]` | Deck-first: file the downloaded deck, render slides, write a fill-in skeleton, then ingest |
| `/week` | This week's deliverables, pinch level, order of attack → daily note |
| `/exam-prep <CODE> <n>` | Finds where the exam *actually* comes from, audits coverage, writes a day-by-day ladder + recall drills |
| `/heal` | Vault-wide linking pass + immutable snapshot |
| `/archive-semester` | Statuses, boards, retrospective |

You rarely need to type them: each command lists the plain phrases that trigger it
("ingest MATH101 lecture 5", "skeleton first", "heal / lint"), and `CLAUDE.md` has a
Phrasebook for the rest.

And **Learning Mode** needs no command: ask *"explain the chain rule from lecture 4"*, get
taught in chat, say **"write it down"** and it's saved into the note and committed.

## A semester in gaku

```
Week 0      /new-semester  →  /new-course × N  →  look at the pinch points, wince
Every week  capture → Inbox/ → /ingest-notes → /week
Exam        /exam-prep — the cheat sheet has been building since week 1
Finals      /archive-semester
Next term   Use this template again
```

## Folder map

| Path | Purpose |
|---|---|
| `Home.md` | Dashboard |
| `Inbox/` | Raw drops (gitignored) — [naming contract](Inbox/README.md) |
| `Courses/<CODE — Name>/` | `_Overview.md` + concept notes + typed subfolders |
| `Boards/` | `Deadlines.md` · `Projects.md` (Kanban) |
| `Synthesis/` | `Schedule Pinch Points.md`, retrospectives, cross-course study guides |
| `Daily/` · `People/` · `Projects/` · `Sources/` · `Reading Queue/` | Second-brain standards |
| `Snapshots/` | Heal snapshots |
| `Templates/` | Templater templates for every note type |
| `Methodology/` | The directives: ingestion · learning mode · heal · exam prep |
| `System/` | `PROFILE.md` · `CRITICAL_FACTS.md` · `index.md` · `log.md` |
| `CLAUDE.md` | Operating manual — the authoritative spec every directive defers to |
| `gaku.toml` | Settings: push policy, lint, heal scope, intake |
| `scripts/` · `tests/` | Lint, heal, intake, rename — and their tests |
| `docs/` | [Setup](docs/SETUP.md) · [Workflow](docs/WORKFLOW.md) · [Customizing](docs/CUSTOMIZING.md) · [Academic integrity](docs/ACADEMIC-INTEGRITY.md) · [FAQ](docs/FAQ.md) |

## Academic integrity

The directives refuse to produce graded work: they explain, outline, quiz, and organize.
Each course's `_Overview` carries `ai-policy: open | explain-only | filing-only | none`
and every command reads it first. **Check your school's and each professor's policy —
you're responsible for it, not the vault.** Details and a template email in
[`docs/ACADEMIC-INTEGRITY.md`](docs/ACADEMIC-INTEGRITY.md).

## Other AI tools

The directives are plain Markdown. Point any agent at `CLAUDE.md` and the file in
`Methodology/` you want run. No AI at all? Delete `.claude/` and `Methodology/` — the
Obsidian half stands on its own.

## Contributing

Issues and PRs welcome — especially new note types for disciplines the routing table
doesn't cover well (labs, studio critiques, case briefs, language drills). Run
`python3 scripts/check_vault.py` and `python3 -m unittest discover -s tests` before
opening a PR. What's planned: [`docs/ROADMAP-2.0.md`](docs/ROADMAP-2.0.md).

## License

MIT — see [`LICENSE`](LICENSE). Bundled Obsidian plugins keep their own licenses; see
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
