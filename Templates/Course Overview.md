---
date: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - course
type: course
ai-first: true
status: active
semester: "<% tp.system.prompt("Semester (e.g. Fall 2026)") %>"
professor: "<% tp.system.prompt("Professor") %>"
schedule: "<% tp.system.prompt("Schedule (e.g. MWF 10:00–10:50)") %>"
credits: ""
course-site: ""
textbook: ""
ai-policy: explain-only
source-dir: ""
deck-pattern: ""
deck-offset: 0
---

# <% tp.file.folder() %>

## For future Claude
Course map for **<% tp.file.folder() %>**. Holds the syllabus summary, grade breakdown, key dates, and the **unit → exam map** the ingestion pipeline reads. `ai-policy` governs what Claude may do here (see `docs/ACADEMIC-INTEGRITY.md`): `open` · `explain-only` · `filing-only` · `none`. Deck intake (`scripts/intake.py`): `source-dir` = where this course's downloads are filed (outside the vault is fine); `deck-pattern` = a regex for the deck filenames, in single quotes, with a `(?P<n>\d+)` group for the deck number and an optional `(?P<title>…)`; `deck-offset` = vault lecture number minus deck number.

---

## Quick Info

| Field | Value |
|---|---|
| Professor | [[<% tp.frontmatter.professor %>]] |
| Schedule | <% tp.frontmatter.schedule %> |
| Location | |
| Office Hours | |
| Course Site | |
| Textbook | |
| AI policy (per syllabus) | |

---

## Grade Breakdown

| Component | Weight | Notes |
|---|---|---|
| | | |

---

## Key Dates

| Date | Event |
|---|---|
| | |

---

## Units → Exams

*(The pipeline uses this to decide which cheat sheet a note feeds. One row per unit.)*

| Unit | Topics | Exam |
|---|---|---|
| 1 | | Exam 1 |

---

## Concept Notes

*(Root-level concept notes for this course — the teaching backbone.)*

---

## Lecture Notes

*(Auto-populated as notes are ingested.)*

---

## Assignments

*(Links to cards on [[Boards/Deadlines]].)*

---

## My Questions

- 
