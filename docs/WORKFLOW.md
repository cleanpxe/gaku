# Workflow

## A week

| When | Do |
|---|---|
| In class / while reading | Take notes however you like. Save as `Inbox/<CODE>/<Type> - <title>.md`. Paste images into `raw_images/`. |
| After a homework is **submitted** | Drop your solved set as `Inbox/<CODE>/Homework - <sections>.md`. This is the most valuable input — it's what the exam is built from. |
| Evening or every few days | `/ingest-notes`. Read the report; open the concept note it enriched. |
| Sunday | `/week`. Look at the pinch level. Move cards. |
| Stuck on a concept | Ask in chat: *"explain the chain rule from lecture 4"*. Learning Mode teaches inline; say **"write it down"** and it saves the explanation into the note and commits. |

## An exam

| When | Do |
|---|---|
| ~2 weeks out | `/exam-prep <CODE> <n>`. Answer the *where does this exam come from?* question honestly. Read the coverage audit — the bold gaps are your study list. |
| Following days | Work the ladder. Ingest the posted review (`Review - Ch N`) and any released old exams. |
| Night before | Read `Cheat Sheets/Cheat Sheet - Exam <n>.md` top to bottom. Have Claude quiz you from the recall drills. |
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

## What the pipeline never does

- Rewrite your words. Typed notes carry your content verbatim; enrichment is additive.
- Edit inside `%% claude-heal %%` blocks by any tool other than `/heal`.
- Guess. Unknown filename prefix or unmatched course → it stops and asks.
- Produce graded work. See `ACADEMIC-INTEGRITY.md`.
