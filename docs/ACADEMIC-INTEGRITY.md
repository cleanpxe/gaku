# Academic integrity

This vault is built to help you **learn**, not to do your work. That is a design
constraint, not a disclaimer — the directives enforce it — but *you* are responsible for
following your school's and each professor's policy. Read the syllabus. When in doubt, ask.

## What the pipeline does

- Files your own notes, links them, captions your images.
- Distills *your* notes and readings into concept notes and cheat sheets.
- Explains concepts, checks your reasoning, quizzes you.
- Tracks deadlines and plans weeks.

## What it refuses to do (globally, `CLAUDE.md`)

- Write, solve, or code anything you would submit for a grade.
- Produce answers to assigned problems before you have submitted them.

Note the distinction the ingestion pipeline makes: `Assignment - …` is a **pre-completion
logistics** note (requirements, plan, checklist); `Homework - …` is your **post-submission
solved set**. The second is exam-prep gold; the first is never solved for you.

## Per-course `ai-policy`

Set in each `_Overview.md` frontmatter. `/new-course` proposes a value from the syllabus
language and asks you to confirm.

| Value | Meaning | Ingestion | Concept notes / cheat sheets | Learning Mode | Exam prep |
|---|---|---|---|---|---|
| `open` | Professor explicitly allows AI study tools | ✓ | ✓ | ✓ | ✓ |
| `explain-only` | **Default.** Study help yes; submitted work never | ✓ | ✓ | ✓ | ✓ |
| `filing-only` | Professor restricts AI to *organizing your own notes* | ✓ verbatim | ✗ | ✗ | audit + logistics only |
| `none` | Professor prohibits AI use for the course | ✗ | ✗ | ✗ | ✗ |

Cards for `none` courses carry ⚠️ on the deadlines board so you don't reach for the
wrong tool at 11pm.

## Ask, don't assume

If a syllabus is silent, a one-line email works:

> Hi Professor ___, I keep my class notes in a note-taking system that uses an AI
> assistant to organize and cross-link *my own* notes and quiz me on them. It does not
> produce any work I would submit. Is that consistent with your policy for the course?

Put the answer in the `_Overview` "AI policy (per syllabus)" row.
