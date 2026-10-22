---
date: 2026-06-14
tags:
  - methodology
  - directive
type: directive
ai-first: true
status: active
---

# Note Ingestion Directive

How to ingest the student's raw course notes into the structured vault. Invoked by
`/ingest-notes`, `/skeleton`, or plain phrasing ("ingest MATH101 lecture 5", "skeleton
first" — see the Phrasebook in `CLAUDE.md`). Idempotent, non-destructive, course-aware.

## §0 — Precedence

This vault's existing `.claude/` config and `CLAUDE.md` are authoritative and win
on any conflict with this directive. When unsure, prefer the conventions already
visible in the target course folder and `Templates/` over anything written here.

## §0.5 — Input sources (what "ingest" runs over)

Ingestion runs over **all concerning course material on input**, from any of:

1. **Raw drops** in `Inbox/<COURSE>/…` — fresh, un-filed notes (the inbox).
2. **Existing in-vault material** already filed under `Courses/<CODE> — <Name>/` —
   lecture notes, reading notes, chapter notes, concept notes, etc.
3. **The course's source folder** — the `source-dir:` in its `_Overview` frontmatter,
   usually outside the vault: slide decks, handouts, review PDFs, recordings, downloaded
   from the LMS. `scripts/intake.py` files new downloads there (§4E). When asked to
   "ingest the new lecture", look in the inbox **and** the source folder before
   concluding there is nothing new.

For **(1)** run the full per-file procedure (§4): create the typed note, enrich
concepts, build the cheat sheet. For **(2)** the typed note already exists, so
**skip creation** — read it in place and apply only the *derived* layers: concept
enrichment (§4.4) and cheat-sheet generation (§4A). Never duplicate or relocate
existing notes. The cheat sheet treats both input kinds identically.

## §1 — Naming convention (the contract)

Every raw note is named `<Keyword> - <remainder>.md`:

- **First keyword** (before the first ` - `) = the **type** of information.
- **Remainder** = the title / content descriptor (often a section number + topic,
  e.g. `1.5 Average Shear Stress`).

The keyword routes the file. The remainder becomes the note title and seeds
frontmatter (chapter/section/unit when a number is present).

## §1.5 — Folder layout (type-named subfolders) — **anti-bloat rule**

A course folder must stay **navigable at a glance**. Only the *map* lives at the
course root; every ingested artifact goes in a **type-named subfolder**:

```
Courses/<CODE> — <Name>/
├── _Overview.md          ← the map (root)
├── <Concept Note>.md     ← concept notes stay at ROOT — they are the backbone
├── Readings/             ← Reading - … (incl. Chapter drops)
├── Lectures/             ← Lecture - …
├── Homework/             ← Homework - …
├── Assignments/          ← Assignment - …
├── Assessments/          ← Exam <n>, Quiz - …
├── Labs/                 ← Lab - …
├── Examples/             ← Examples - Ch <n>
├── Reviews/              ← Review - Ch <n> · Review - <CODE> <exam>
├── Videos/               ← Video - … (recordings, §4F)
├── Handouts/             ← Handout - … (worksheets, posted problem sheets)
├── Cheat Sheets/         ← Cheat Sheet - <CODE> <exam> (§4A)
└── Coursebook/           ← per-chapter explainers, when a course has a textbook
```

**Why concept notes stay at root:** they are the course's teaching backbone,
navigated constantly and linked from everywhere; burying them defeats the point.
Everything else is *source material* or a *derived layer* — those are what bloat
a folder, so those get subfolders.

**Rules:**
- **Create the subfolder on demand.** Don't pre-create empty ones; make the
  folder the first time a note of that type is ingested for that course.
- **Wikilinks are unaffected.** Obsidian resolves `[[Note Name]]` by filename, not
  path, so moving a note between folders never breaks a link — provided filenames
  stay **unique vault-wide**. Verify uniqueness before any rename.
- **Exam-keyed notes carry the course code.** Every course has an "Exam 1" and a
  "Midterm", so a cheat sheet, exam review, prep plan or assessment note names its
  course: `Cheat Sheet - MATH101 Exam 1`, `Review - MATH101 Midterm`,
  `Assessments/MATH101 Exam 1.md`. A bare `[[Cheat Sheet - Exam 1]]` is ambiguous the
  moment a second course has one, and `scripts/check_vault.py` fails on ambiguous links.
  The same goes for any other generic name: path-qualify `[[MATH101 — Calculus I/_Overview]]`.
- **Don't repeat the folder name in the filename.** The subfolder already states the
  type, so a redundant prefix is noise in link text and the file switcher. Routing-table
  types keep their `<Type> - <title>` prefix (it's load-bearing for uniqueness across
  ~12 courses — `Reading - 1.5 …` vs another course's `1.5 …`). Purpose-built folders
  whose members are already unique drop it: `Coursebook/Ch 4 Processes.md`, **not**
  `Coursebook/Coursebook - Ch 4 Processes.md`.
- **Never relocate the student's existing notes as a side effect of an unrelated
  ingestion.** If a course predates this rule and is still flat, say so in the §6
  report and *offer* to migrate — migration is its own explicitly-approved task.
- Embeds still resolve from `raw_images/` by filename regardless of note depth.

## §2 — Routing table (keyword → handling)

| Keyword | Note type | Destination (§1.5) | Template basis | Also enriches |
|---|---|---|---|---|
| `Reading` | source / literature | `Readings/Reading - <title>.md` | Literature Note | matching concept note(s) |
| `Chapter` | source / literature (whole textbook chapter) | `Readings/Reading - Ch <n> <topic>.md` | Literature Note | matching concept note(s) |
| `Lecture` | lecture | `Lectures/Lecture - <title>.md` | Lecture Note | matching concept note(s) |
| `Homework` / `HW` | worked-solutions | `Homework/Homework - <range>.md` | Problem Set (§4D) | concept *Problem types* + cheat-sheet *Common problem-set scenarios* |
| `Assignment` | assignment (logistics) | `Assignments/Assignment - <title>.md` | Assignment | linked concepts |
| `Exam` / `Quiz` | assessment | `Assessments/<CODE> Exam <n>.md` / `Assessments/<CODE> Quiz <n>.md` | Assignment | linked concepts |
| `Lab` | lab | `Labs/Lab - <title>.md` | Lecture Note (adapted) | linked concepts |
| `Example` / `Examples` | worked-example | `Examples/Examples - Ch <n>.md` | Worked Examples (§4B) | concept *Problem types* + cheat-sheet approach subsegments |
| `Review - Ch <n>` | review-summary (textbook) | `Reviews/Review - Ch <n>.md` | Review (§4C) | verifies concept *Core Ideas / Key Formulas*; links cheat sheet |
| `Review - <exam>` | exam review (instructor's) | `Reviews/Review - <CODE> <exam>.md` | Review (§4C.2) | **audits the exam's cheat sheet** |
| `Video` / `Recording` | video | `Videos/Video - <title>.md` | Lecture Note (adapted) | concept notes + cheat sheet (§4F) |
| `Handout` / `Worksheet` | handout | `Handouts/Handout - <title>.md` | Lecture Note (adapted) | concept *Problem types* |
| `Note` / `Notes` | topic / concept | `<title>.md` — **course root** | Concept | — (it *is* the concept) |

**Unrecognized keyword → STOP and ask the student** how to route it. Never guess a type.
Once they answer, propose adding the new keyword to this table.

## §3 — Course inference

Raw drops live under `Inbox/<COURSE>/…`; match `<COURSE>` to a folder in
`Courses/<CODE> — <Name>/` by code prefix (e.g. `ENG217` → `ENG217 — Strength of
Materials`). If no course folder matches, STOP and ask before creating one. For
existing in-vault material (§0.5 case 2) the course **is** the containing
`Courses/<CODE> — <Name>/` folder, and the note's type comes from its filename
keyword or its frontmatter `type`.

## §4 — Per-file procedure

For each raw file:

1. **Parse** `<Keyword> - <remainder>` → type + title. Pull any section/chapter
   number from the remainder.
2. **Resolve** the target course folder (§3), the routing row (§2), and the
   type-named subfolder (§1.5) — creating that subfolder if it doesn't exist yet.
3. **Create the typed note** at its §1.5 destination:
   - Frontmatter from the template basis: `date`, `tags`, `type`, `ai-first: true`,
     `course: "[[<CODE> — <Name>]]"`, plus `chapter` / `section` / `unit` / `exam`
     when inferable from the title or the course `_Overview`.
   - A one-line **`## For future Claude`** orientation block.
   - The **verbatim content**, with all `![[Pasted image …]]` figure embeds
     preserved exactly (images resolve from `raw_images/` by filename).
   - **Figure pass (vision) — always read the images.** Open every embedded image
     and add a one-line *italic caption* directly under its embed describing what it
     shows. Fold any **figure-only** content (free-body-diagram layout, sign
     conventions, geometry/dimensions, boxed equations not in the prose) into the
     concept enrichment (§4.4) and the cheat sheet (§4A). Never treat an embed as
     opaque. For existing in-vault material (§0.5 case 2), add captions in place.
4. **Enrich the matching concept note(s)** (for `Reading` / `Lecture` / etc.):
   - Add a link under a **`## Sources / Readings`** section (create it if absent).
   - Fold any *genuinely new* core idea or formula into `## Core Ideas` /
     `## Key Formulas`. Do **not** duplicate what's already there.
   - **Never edit inside `%% claude-heal:start … end %%` blocks.**
5. **Update the exam cheat sheet** — distill the source's *approaches* into the
   per-exam recall layer (§4A).
6. **Cross-link both ways**: typed note links to the concept(s); concept links back
   to the typed note.
7. **Mark the original as ingested** (see §7) — never rewrite or move it.

## §4A — Cheat-sheet generation (per-exam recall layer)

Every ingested source's *approaches* are folded into a rich, problem-set-ready
cheat sheet — every formula highlighted for fast spotting and application.
Derivations are dropped; pragmatic use is kept.

**One file per exam (the "major unit group"):** `Cheat Sheets/Cheat Sheet - <CODE> Exam <n>.md`
(§1.5) — distinct from the `Assessments/<CODE> Exam <n>.md` logistics note. Claude-owned.

- Frontmatter: `type: cheat-sheet`, `generated_by: claude-ingest`, `ai-first: true`,
  `course: "[[<CODE> — <Name>]]"`, `exam: <n>`, `status: living`.
- **Exam assignment:** read the `exam` / `unit` of the matching concept note and the
  course `_Overview` unit→exam map. If a source maps to no exam, **STOP and ask**.

**One `## <Approach>` subsegment per approach**, ordered by unit. Each subsegment:

- Title note line: `*<source ref> · [[Reading - …]] · Unit <n>*`
- **Highlighted formula** — an Obsidian callout with display math so it pops:
  ```
  > [!formula] <name> = <expr>
  > $$ <clean MathJax LaTeX> $$
  > <symbol> = <meaning> · …
  ```
- **Use when** — the trigger situation(s).
- **Approach** — terse numbered steps (from the source's "Procedure for Analysis").
- **Cases** — concrete plug-ins / variants.
- **Common problem-set scenarios** — typical setups to recognize. This section may
  draw on general subject knowledge beyond the source; the header flags that. Never
  fabricate specific textbook numbers.
- **Watch** — averaging caveats, sign/unit gotchas, validity limits.

Write clean MathJax LaTeX (`\dfrac`, `\,`, `\text{}`, `aligned` blocks). Latex Suite
is installed for authoring; generated math must render under Obsidian's MathJax.

**Idempotency:** key each subsegment by its `##` title — re-ingesting **replaces**
that section in place and inserts new ones in unit order; never duplicate. The sheet
is course content, so heal may add its own EOF block — keep the cheat-sheet sections
and the heal block out of each other's way.

## §4B — Worked-example ingestion (`Example` / `Examples`)

Worked examples are **applied theory** — solved instances that demonstrate *how* a
formula is used. They are the empirical backing for the two weakest distilled
sections: the concept note's **Problem types to recognize** and the cheat sheet's
**Common problem-set scenarios** (which otherwise lean on general knowledge and must
not fabricate textbook numbers). An `Examples` file therefore flows into the
*distilled* layers, with an archival note as the verifiable source.

Textbooks (Hibbeler) number examples **by chapter** (`14.1`, `14.2`, …), not by
section — so the archive is **one file per chapter**.

For each `Examples` file:

1. **Archive** → `Courses/<CODE> — <Name>/Examples/Examples - Ch <n>.md` (§1.5), a worked-example note:
   - Frontmatter: `type: worked-example`, `ai-first: true`, `course`, `chapter`,
     and `exam` / `unit` **inherited from the matching concept note** (Ch 14 → Exam 1).
   - A one-line `## For future Claude` block + (for image-only drops) the same
     `> [!note] Image-only raw note` flag used for screenshot-only readings.
   - **Figure pass (vision) — always read the images** (§4 step 3 rules apply).
   - One **`### Example <n>.M`** block per example, transcribed at **setup+steps+answer**
     depth: **Given · Find · figure caption · the decisive solution step(s) · boxed
     answer**. Not full verbatim (that's the Reading's job); enough to learn the pattern.
2. **Refine the concept note** — under **`## Problem types to recognize`**, bind each
   example to its type as `→ **Ex <n>.M**: <one-line setup>`; add a *new* problem type
   when an example doesn't fit an existing one. Don't duplicate; never edit inside
   `%% claude-heal %%` blocks.
3. **Refine the cheat sheet** — in the **matching `## <Approach>` subsegment** (§4A),
   add or refresh a **`**Worked examples**`** mini-index: one line per example —
   *`Ex <n>.M` · setup · solved-for · the key move*. Tighten **Approach** / **Cases** /
   **Watch** only where an example exposes something the scaffold missed. This converts
   *Common problem-set scenarios* from general-knowledge scaffold to textbook-grounded.
4. **Cross-link** the archive ↔ concept note ↔ cheat sheet ↔ the relevant
   `Reading - <section>` notes, both ways.
5. **Exam mapping** — inherit from the concept note's `exam` (same rule as §4A). If a
   chapter maps to no exam, **STOP and ask**.

**Idempotency:** archive keyed by `### Example <n>.M`; concept/cheat-sheet entries keyed
by example ref (`Ex <n>.M`). Re-ingesting **replaces** the matching block/line in place,
inserts new ones in example-number order, and makes no edits when nothing changed.

## §4C — Review ingestion (`Review`)

A `Review` drop is the **textbook's own end-of-chapter summary** — a verbatim recap of a whole chapter, not new theory and not worked examples. It is *summary literature*: archive it faithfully, then use it to **audit** the distilled layers (the concept note may have drifted or missed a formula the book emphasizes).

For each `Review` file:

1. **Archive** → `Courses/<CODE> — <Name>/Reviews/Review - Ch <n>.md` (§1.5), a review note:
   - Frontmatter: `type: review`, `ai-first: true`, `course`, `chapter`, `sections`, and `exam` / `unit` **inherited from the matching concept note** (same rule as §4A/§4B). If a chapter maps to no exam, **STOP and ask**.
   - A one-line `## For future Claude` block + (for image-only drops) the `> [!note] Image-only raw note` flag.
   - **Figure pass (vision) — always read the images** (§4 step 3 rules apply). Transcribe the recap **verbatim** under one `### <heading>` per summary section, each embed keeping its italic caption with the boxed formulas.
2. **Audit the concept note** — read it against the review. Fold in any *genuinely missing* core idea or formula the textbook review stresses; never duplicate, never edit inside `%% claude-heal %%` blocks. The review is the book's authority on "what mattered this chapter."
3. **Cross-link** the review ↔ concept note ↔ readings ↔ cheat sheet, both ways.

**Idempotency:** archive keyed by `### <heading>`; re-ingesting replaces the matching block in place. The review does **not** create cheat-sheet subsegments (the readings/examples own those) — it only links to them.

### §4C.2 — Exam reviews (`Review - <exam>`)

An **instructor's exam review** — a review session, a narrated video, or a posted slide
PDF — is the strongest signal of what the exam covers. Its value is the **diff against the
cheat sheet**, not the transcript. Check for it on the day it unlocks; a review ingested on
exam day is mostly wasted.

1. **File** `Reviews/Review - <CODE> <exam>.md` (`type: review`, `exam`, `course`):
   - a **numbered checklist** of every point in the instructor's order, each linked to the
     cheat-sheet subsegment it lands in (`[[Cheat Sheet - <CODE> <exam>#<subsegment>]]`);
   - a **coverage table**: stressed · touched · not mentioned, against every cheat-sheet
     subsegment;
   - for a video, the lightly corrected transcript (§4F); for a PDF, the slide captions
     and a 20-question self-test built from them.
2. **Audit the cheat sheet:** add a `> [!success] Audited against [[Review - <CODE> <exam>]]`
   callout at its top, and under each subsegment one `**Review adds (<date>)**` line for
   anything the review phrased or stressed that the sheet lacked. Subsegments the review
   never mentions get no edit — the coverage table records the gap.
3. Add a `[[Review - <CODE> <exam>]]` Sources bullet to each concept note it touches.

**Idempotency:** the checklist and table are rewritten in place; `Review adds` lines are
keyed by date and replaced on re-ingest.

## §4D — Problem-set ingestion (`Homework` / `HW`)

A `Homework` / `HW` drop is a **worked-solution problem set** — the student's *actually-assigned* problems, solved out (often authored Markdown with KaTeX + inline figures, a numbered problem list, and a quick-reference answer table). This is the **empirical backbone** of exam prep: where §4B textbook `Examples` are illustrative, homework problems are *what actually gets tested*, so they are the strongest grounding for the cheat-sheet **Common problem-set scenarios** and the concept note's **Problem types to recognize**.

**Distinct from `assignment` (logistics).** The `Assignment` keyword (§2) routes *pre-completion* planning notes — due dates, requirements, submission checklist, "don't solve it for them." A `problem-set` note is the *post-completion* solved artifact. They complement each other; never merge them.

For each `Homework` / `HW` file:

1. **Archive** → `Courses/<CODE> — <Name>/Homework/Homework - <range>.md` (§1.5) (**one note per assignment**, preserving the set as a unit — it has its own answer table; keep the drop's section-range label, e.g. `14.4-14.6`, `15.2++`):
   - Frontmatter: `type: problem-set`, `ai-first: true`, `course`, `sections` (the range), and `exam` / `unit` **inherited from the matching concept note(s)**. If the range maps to no exam, **STOP and ask**.
   - A one-line `## For future Claude` block.
   - **Figure extraction — always.** Decode every inline base64 / `data:image` figure to `raw_images/Homework-<range>-figNN.png` and rewrite to `![[…]]` embeds; then **vision-read each** and add an italic caption (§4 step 3 rules apply). Never leave base64 in the archive.
   - **Preserve the full worked solutions** verbatim — the authored Given/Find/Solution + multi-part answers + the answer table. (Unlike §4B Examples, which are compressed; homework is already well-written and exam-gold, so keep it whole.)
2. **Refine the concept note(s)** — under **`## Problem types to recognize`**, bind each homework problem to its type as `→ **HW <range> #M**: <one-line setup>`; add a *new* problem type when a problem doesn't fit. Don't duplicate; never edit inside `%% claude-heal %%` blocks.
3. **Refine the cheat sheet** — in the matching `## <Approach>` subsegment, refresh **Common problem-set scenarios** from the homework, flagged as **assigned** (the strongest grounding — converts the scenario list from general-knowledge/textbook scaffold to actually-tested). Add a **`**Homework problems**`** mini-index keyed by `HW <range> #M` where useful.
4. **Cross-link** the problem set ↔ concept note(s) ↔ cheat sheet ↔ the relevant `Examples - Ch <n>` and `Reading - <section>` notes, both ways.
5. **Exam mapping** — inherit from the concept note's `exam` (same rule as §4A/§4B). A set spanning sections in different exams maps to all of them.

**Idempotency:** archive keyed by `## <problem heading>`; concept/cheat-sheet entries keyed by `HW <range> #M`. Re-ingesting replaces the matching block/line in place, inserts new ones in problem order, and makes no edits when nothing changed.

## §4E — Decks and skeletons (deck-first lectures)

Many courses post the slide deck before class. The pipeline then runs **deck first**: the
deck becomes a fill-in skeleton the student annotates live, and the full lecture note is
written around it. Order matters, because the request often lands minutes before class.

1. **Intake.** `python3 scripts/intake.py` plans, `--apply --render` files: it matches each
   download to a course by the `deck-pattern` in its `_Overview`, reports byte-identical
   re-downloads instead of filing them twice, moves the deck into `source-dir`, and renders
   slides to `raw_images/<CODE>-L<N>-slide-NN.png`. `N` = deck number + `deck-offset`
   (LMS numbering often starts at 0 or skips a week). A download no pattern matches is
   reported — ask, never guess.
2. **Skeleton first.** Write `Inbox/<CODE>/Lecture - <N> <title>.md` from
   `Templates/Lecture Skeleton.md`, then **tell the student it is ready** before doing
   anything else. Shape, deck order:
   - a one-paragraph italic header: deck filename, page count, what the vault already
     has on this topic, and what to listen for;
   - per slide or slide group: a bold `**p. N — topic.**` line, a *Variables:* list before
     any equation that introduces symbols (symbol — name — role), the derivation **one
     equation per line** as centered display math (`$$…$$`), every end result in
     `\boxed{}`;
   - the deck's figures where the deck places them, each with a one-line italic caption
     (figure number, page, what to look for). Raster figures come out with
     `pdfimages -png`; crop vector figures from a 150-dpi `pdftoppm` render. Name them
     `raw_images/<CODE>-L<N>-fig<k>-<slug>.png`;
   - deck errors corrected in place and flagged in an italic line under the equation;
   - under every block, one or two prompts ("did the professor say why …?") and a
     trailing empty `-` so the student can type live.
3. **Then the long ingest** — the lecture note from the deck (every slide image embedded
   and captioned), concept enrichment, cheat sheet — per §4.
4. **After class**, re-ingesting the annotated skeleton merges the student's additions
   into the lecture note (their words verbatim, attributed) and reconciles the cheat sheet.

**Names.** If the filename topic and the cover title differ, name the note after the one
the student uses and record the other in `source:`. Decks with hidden slides: cite by PDF
page and say so.

## §4F — Recordings (`Video` / `Recording`)

A lecture recording, a narrated review, or a short course video. Transcribe it when a
local speech-to-text tool is available (e.g. whisper); otherwise ask for the transcript.

- One note per recording: `Videos/Video - <title>.md`, `type: video`: **Core Ideas**,
  anything on screen reconstructed from the narration (code, board work), a lightly
  cleaned transcript, and a **Reconciliation** section against the matching lecture note
  or worksheet — where the instructor's answer differs from the vault's, the instructor
  wins and the difference is flagged.
- Then: source lines in the cheat sheet, Sources bullets in the concept notes, a table
  row in the course `_Overview`.
- Re-ingesting rewrites the note in place.

## §4G — Live directives (`claude draw …`)

While typing raw notes in class, the student may leave instructions inline:
`claude draw the feedback loop`, `table of the cases here (claude)`, `explain PID here
claude`. When asked to "check" or "go look at" a note:

- scope strictly to the named file; fulfil **only** the tagged lines — a Mermaid block for a
  diagram, a table for a table, short prose or LaTeX for an explanation — then delete the
  directive line;
- leave every untagged line alone: no reformatting, no cleanup, no "fixing" shorthand;
- **never poll** the file on a timer. The student is typing in it; wait to be asked.

**Diagram style.** `graph LR`, this init line directly under the fence, single-line terse
labels, one italic caption under the closing fence:

```
%%{init: {'flowchart': {'nodeSpacing': 22, 'rankSpacing': 34, 'padding': 3, 'curve': 'basis'}, 'themeVariables': {'fontSize': '12px'}}}%%
```

Centering is done once, by `.obsidian/snippets/mermaid-center.css`, not per diagram.

## §5 — Idempotency

Re-running on the same file **updates** the existing typed note, re-checks the
concept enrichment, and re-syncs the cheat-sheet subsegment rather than creating
duplicates. Match by destination filename / subsegment title. If nothing changed,
make no edits.

**Scaffolds.** A course may carry pre-built `status: scaffold` lecture notes (expected
content from the textbook, read-ahead links, questions to bring). On ingest, **merge into
the scaffold** instead of creating a second note: keep its *Expected content* / *Read
ahead* / *Questions to bring* sections (tick what the lecture answered), fill in the deck
and class sections, set `status: ingested`, and if the real lecture's number or title
differs, rename it with `python3 scripts/rename_note.py` (it rewrites every link).
Cheat-sheet subsegments marked *Expected — not yet lectured* are reconciled in place when
the lecture arrives: drop the flag, add the source line, and note anything the lecture
states differently from the book under **Watch**.

## §6 — Report

After a run, report per file: type detected, course matched, note created/updated
(**with its §1.5 destination path**), which concept notes were enriched, and which
exam cheat sheet / subsegments were updated. For deck-first runs, also: what intake
moved, re-downloads it skipped, slides rendered, and when the skeleton was announced.
Flag any file that was stopped on (§2/§3/§4A), plus any subfolder created for the first
time. End with `python3 scripts/check_vault.py` and report its result.

If the touched course is still **flat** (predates §1.5), note that in the report and
offer a migration — do not migrate unasked.

## §7 — Inbox lifecycle

`Inbox/` is gitignored — it is the student's local drop zone, and its contents never
enter version control. After a file is successfully ingested, prepend a single line
to it so re-runs can skip it:

```
%% ingested <YYYY-MM-DD> → <destination path> %%
```

(Obsidian hides `%% … %%` comments in reading view.) A file that already carries this
marker is skipped unless the student explicitly asks to re-ingest it or the file's
modification time is newer than the marker date. Never delete inbox files; the student
clears the inbox on their own schedule.

A vault may choose to **track** its inbox in git (to keep raw notes across machines): say
so in `CLAUDE.md`, remove `Inbox/*` from `.gitignore`, and commit the student's raw-note
edits in their own commit, separate from Claude's ingest.

## §8 — Academic-integrity gate

Before ingesting a course, read the `ai-policy` field of its `_Overview.md`:

| `ai-policy` | Ingestion | Concept enrichment / cheat sheets | Learning Mode |
|---|---|---|---|
| `open` | yes | yes | yes |
| `explain-only` (default) | yes | yes | yes — explain, never produce graded work |
| `filing-only` | yes | **no** — file verbatim, link, stop | no |
| `none` | **no** — say so and stop | no | no |

If the field is missing, treat it as `explain-only` and mention that in the §6 report.
