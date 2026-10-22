# gaku 2.0 roadmap

2.0 is the template catching up with how a gaku vault gets used once a semester is
under way. The first slice is on the `gaku-2.0` branch (see `CHANGELOG.md`); the rest is
below, roughly in order of value.

## Done in the first slice

- [x] Tested scripts for the mechanical steps: `check_vault.py` (rewritten), `heal.py`,
  `intake.py`, `rename_note.py`, shared `gakulib.py`, `tests/`.
- [x] `gaku.toml` settings, with the push policy the first of them.
- [x] Deck-first lectures: `/skeleton`, ingestion §4E, `Templates/Lecture Skeleton.md`,
  per-course intake fields.
- [x] Exam reviews, recordings, handouts, inline `claude draw …` directives, scaffolds.
- [x] Phrasebook + trigger-phrase command descriptions.
- [x] Course-coded exam names; lint fails on ambiguous links.
- [x] Template hygiene: heal appendix, attachment folder, Mermaid snippet, union-merged logs.

## Next

### Study layers (replaces most of `/exam-prep`)

Per-course opt-ins in `_Overview` frontmatter, each with a template and a directive section:

- [ ] **Deep dives** — a teaching companion per lecture (`deep-dives: true`) or per unit
  (`deep-dives: unit`) with predict–run–explain experiments, linked both ways, grounded in
  the textbook with section and page citations.
- [ ] **One-page sheet** — the handwritten exam sheet as a copy-out scaffold, versioned.
- [ ] **Living reference sheet** — one entry per function / formula / term, appended by
  every ingest, with an index regenerated between markers.
- [ ] **Mistake list** — misses from self-tested problems, folded into the cheat sheet.
- [ ] `/exam-prep` keeps its first question (where does this exam actually come from?) and
  then routes to the layers the course opted into.

### Project mode

For a team or client project instead of courses (`/new-project`):

- [ ] `Project/` in place of `Courses/`; a tracked `Notes/` inbox; type folders created on
  first use, never pre-scaffolded.
- [ ] Decision records with `amends` / `supersedes`, a decisions index, and `status:
  proposed` until a human accepts.
- [ ] Ledgers keyed by ID (results, risks, literature) that re-ingest replaces row by row.
- [ ] A "who does what" table in place of `ai-policy`, and the rule that a `[VERIFY]`-tagged
  number never reaches a deliverable.
- [ ] `scripts/export.py` — Markdown → PDF (strip frontmatter, comments, wikilinks, the
  For-future-Claude block) and numbered review-folder packaging.
- [ ] `.gitignore` presets that keep raw data, CAD and media out of git.

### Picking up where you left off

- [ ] `System/Pickup.md` — the next session's starting point, with a word cap that
  `check_vault.py` enforces (handoff notes grow without bound otherwise).
- [ ] A digest-shaped daily note: Decided · Waiting on · Open questions · Watch-outs.
- [ ] `CRITICAL_FACTS.md` gets a `last-checked:` date and a size check.

### Deadlines with one source of truth

- [ ] Key Dates in each `_Overview` generate the board's cards (and, optionally, calendar
  events), so the board, the overviews and the calendar can't drift apart.
- [ ] A lint check for open cards past their date and cards in the wrong lane.

### Shipping

- [ ] Package the directives, commands and scripts as a Claude Code plugin, so a vault
  keeps only `CLAUDE.md`, `gaku.toml` and content, and fixes arrive by update instead of
  copy-and-drift. Bump the version on every release.
- [ ] An upstreaming step: each heal run lists rules that live only in Claude's memory, and
  routing-table proposals still waiting, so they land in a directive.

## Not planned

Write transactions with journals, claim ledgers, a retrieval index and log folding: they
exist in heavier knowledge-base systems, and in practice went unused even where they were
installed. A study vault needs links that resolve and notes that converge, which the
scripts above already check.

## Migrating a vault to 2.0

1. Copy `scripts/`, `tests/`, `gaku.toml` and the updated `Methodology/`, `.claude/` and
   `Templates/` files.
2. `python3 scripts/check_vault.py` — fix the errors, starting with ambiguous links. For
   each exam-keyed note, `python3 scripts/rename_note.py "<path>" "<Type> - <CODE> <exam>"
   --apply` rewrites its links.
3. Add `source-dir` / `deck-pattern` / `deck-offset` to the courses whose decks you download.
4. Set `[git] push` in `gaku.toml`.
