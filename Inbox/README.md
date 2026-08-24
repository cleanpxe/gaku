# Inbox — the naming contract

Drop raw notes here as `Inbox/<COURSE CODE>/<Type> - <title>.md`. Messy is fine; the
filename is all the pipeline needs. Everything in this folder except this README is
**gitignored** — it never leaves your machine.

| Filename starts with | Becomes | Also updates |
|---|---|---|
| `Lecture - ` | `Lectures/Lecture - …` | matching concept note(s) |
| `Reading - ` or `Chapter - ` | `Readings/Reading - …` | matching concept note(s) |
| `Homework - ` or `HW - ` | `Homework/Homework - …` (your *solved* set) | concept *Problem types* + cheat sheet |
| `Examples - Ch N` | `Examples/Examples - Ch N` | cheat-sheet worked examples |
| `Review - Ch N` | `Reviews/Review - Ch N` | audits the concept note |
| `Assignment - ` | `Assignments/Assignment - …` (logistics, pre-completion) | Deadlines board |
| `Exam N` / `Quiz - ` | `Assessments/…` | Deadlines board |
| `Lab - ` | `Labs/Lab - …` | matching concept note(s) |
| `Note - ` | course root — it *is* a concept note | — |

Anything else → the pipeline **stops and asks**. It never guesses.

Then run `/ingest-notes` (everything) or `/ingest-notes MATH101` (one course). Ingested
files get a `%% ingested <date> → <path> %%` line prepended so re-runs skip them; delete
them whenever you like.

Pasted images: put them in `raw_images/` and embed with `![[filename.png]]` — the
pipeline reads every image and captions it.

No Claude? Use the same table to file notes by hand into `Courses/<CODE — Name>/`.
