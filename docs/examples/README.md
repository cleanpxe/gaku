# Example: what goes in, what comes out

`inbox/MATH101/` holds three raw notes exactly as a student might drop them into
`Inbox/MATH101/` — plain text, ASCII math, no frontmatter, no links.

`/ingest-notes MATH101` turns them into what you see under
`Courses/MATH101 — Calculus I/`:

| Raw drop | Became | Also touched |
|---|---|---|
| `Lecture - 4 Chain Rule.md` | `Lectures/Lecture - 4 Chain Rule.md` | `Derivative Rules.md` (Sources, Core Ideas) |
| `Reading - 3.4 The Chain Rule.md` | `Readings/Reading - 3.4 The Chain Rule.md` | `Derivative Rules.md`; `Cheat Sheets/Cheat Sheet - Exam 1.md` → *Chain rule* subsegment |
| `Homework - 3.1-3.4.md` | `Homework/Homework - 3.1-3.4.md` | `Derivative Rules.md` → *Problem types*; cheat sheet → *assigned* scenarios |

Everything in the demo course is fabricated. Delete it when you no longer need the reference.
