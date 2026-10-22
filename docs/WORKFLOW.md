# Workflow

## A week

| When | Do |
|---|---|
| Deck posted before class | Download it, then say **"skeleton"** (or `/skeleton`). Intake files the deck, renders the slides, and writes a fill-in skeleton to `Inbox/<CODE>/` within a minute or two — then the full lecture note follows. |
| In class / while reading | Take notes however you like, in the skeleton or a fresh `Inbox/<CODE>/<Type> - <title>.md`. Pasted images land in `raw_images/`. Leave instructions inline — `claude draw the feedback loop` — and say "go look at my note" when you want them done. |
| After a homework is **submitted** | Drop your solved set as `Inbox/<CODE>/Homework - <sections>.md`. This is the most valuable input — it's what the exam is built from. |
| Evening or every few days | `/ingest-notes`. Read the report; open the concept note it enriched. |
| Sunday | `/week`. Look at the pinch level. Move cards. |
| Stuck on a concept | Ask in chat: *"explain the chain rule from lecture 4"*. Learning Mode teaches inline; say **"write it down"** and it saves the explanation into the note and commits. |

## An exam

| When | Do |
|---|---|
| ~2 weeks out | `/exam-prep <CODE> <n>`. Answer the *where does this exam come from?* question honestly. Read the coverage audit — the bold gaps are your study list. |
| Following days | Work the ladder. Ingest the instructor's review **the day it unlocks** (`Review - <exam>`: it audits the cheat sheet against what the review stresses) and any released old exams. |
| Night before | Read `Cheat Sheets/Cheat Sheet - <CODE> Exam <n>.md` top to bottom. Have Claude quiz you from the recall drills. |
| After | Note in the prep plan where the questions *actually* came from. `/archive-semester` reads this for the retrospective. |

## A semester

```
/new-semester            → profile, facts, one /new-course per syllabus, pinch points
   ↓ every week
Inbox → /ingest-notes → /week
   ↓ every exam
/exam-prep
   ↓ occasionally
/heal                    → weaves cross-course links, writes a snapshot
   ↓ finals
/archive-semester        → statuses, retrospective, clean boards
```

Next term: **Use this template** again (clean), or `git clone` your own vault and
`/archive-semester` + `/new-semester` (keeps old courses for reference — useful when a
course builds on a previous one).

## Deck-first lectures

```
~/Downloads/Lecture 05 Chain Rule.pdf
   ↓ python3 scripts/intake.py --apply --render     (or just say "skeleton")
<source-dir>/Lecture 05 Chain Rule.pdf  +  raw_images/MATH101-L5-slide-01.png …
   ↓ /skeleton step 2                                 ← "skeleton ready" — annotate it live
Inbox/MATH101/Lecture - 5 Chain Rule.md
   ↓ /skeleton step 3 (the long ingest)
Courses/MATH101 — Calculus I/Lectures/Lecture - 5 Chain Rule.md + concept notes + cheat sheet
   ↓ after class: "ingest MATH101 lecture 5" again
your annotations merged in
```

Intake only moves what a course's `deck-pattern` matches, never files a byte-identical
re-download twice, and never deletes anything. Run it without `--apply` to see the plan.

## Scripts

All in `scripts/`, standard-library Python 3.11+, safe to run any time:

| Command | Does |
|---|---|
| `python3 scripts/check_vault.py` | Lint. Dead and ambiguous links, missing embeds, damaged heal blocks. CI runs it. |
| `python3 scripts/intake.py` | Plan (or `--apply`) filing of downloaded course files. |
| `python3 scripts/rename_note.py OLD NEW` | Rename a note and fix every link to it. |
| `python3 scripts/heal.py inventory` | Which notes have heal blocks. `/heal` uses `apply`. |
| `python3 -m unittest discover -s tests` | The scripts' own tests. |

## What the pipeline never does

- Rewrite your words. Typed notes carry your content verbatim; enrichment is additive.
- Edit inside `%% claude-heal %%` blocks by any tool other than `/heal`.
- Guess. Unknown filename prefix or unmatched course → it stops and asks.
- Produce graded work. See `ACADEMIC-INTEGRITY.md`.
