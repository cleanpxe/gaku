---
tags:
  - methodology
  - directive
type: directive
ai-first: true
status: active
---

# Exam-Prep Directive

Invoked by `/exam-prep <COURSE> <exam>`. Turns "I have an exam" into a plan that is
geared to where the exam *actually* comes from. Subordinate to root `CLAUDE.md`.

## §0 — The lesson this encodes

Building full prep machinery for every course is wasted effort. Exams are drawn from a
small number of sources — lecture slides, the homework, the textbook's problems, a
posted review, old exams — and the *mix differs per course*. Find the mix first, then
gear effort: full pipeline only where it pays.

## §1 — Inputs

1. `Courses/<CODE — Name>/_Overview.md` — grade breakdown, Units → Exams map, syllabus
   language about the exam (format, open/closed book, calculator, what it covers).
2. `Assessments/Exam <n>.md` if it exists (logistics, posted review).
3. `Cheat Sheets/Cheat Sheet - Exam <n>.md` if it exists.
4. Every concept note whose `exam` matches, and the typed notes that link to them.
5. `Boards/Deadlines.md` + `Synthesis/Schedule Pinch Points.md` — how many days,
   what else collides.
6. The student, when the notes don't say — ask the **source-of-truth question**
   directly: *"Has the professor said or shown where exam questions come from?
   Old exams, homework, lecture examples, textbook?"*

## §2 — Output: one note, `Assessments/Exam <n> — Prep Plan.md`

Frontmatter: `type: exam-prep`, `course`, `exam`, `exam-date`, `ai-first: true`,
`generated_by: claude-exam-prep`, `status: living`.

Sections, in order:

1. **Verdict — where this exam comes from.** One paragraph. Cite the evidence
   (`_Overview` line, syllabus quote, student's answer). Rank the sources.
2. **Coverage audit.** Table: unit/topic → concept note (link, `status`) → cheat-sheet
   subsegment (yes/no) → homework/examples bound (count). Highlight gaps in **bold**.
3. **The ladder** — a day-by-day plan from today to the exam date, sized to the days
   available and the pinch-point load. Each rung is one concrete action
   ("re-solve HW 3 #4–#7 cold", "ingest the posted review → `Review - Ch 4`",
   "quiz me on unit 2 formulas"). Front-load gap-filling, end with cold recall.
4. **Recall drills** — 10–20 short prompts Claude can quiz the student with, drawn
   only from the concept notes and cheat sheet (never fabricated numbers).
5. **Day-of checklist** — logistics from `Assessments/Exam <n>.md`: time, room,
   allowed materials, ID, calculator.

## §3 — Rules

- Respect the course `ai-policy`. On `filing-only` produce only sections 2 and 5.
  On `none`, stop.
- Never produce graded work. Quizzing and checking the student's reasoning is fine;
  solving assigned problems for them is not.
- Idempotent: re-running updates the existing plan in place and re-audits coverage.
- Add a card `🔴 **Exam <n> (CODE)** · @{date}` to `Boards/Deadlines.md` if missing.
- Log a line in `System/log.md`.
