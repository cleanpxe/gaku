---
description: "Create a course from its syllabus: overview, every deadline on the board, professor note, pinch points. Use for 'new course', 'add <course>', 'here is the syllabus for'."
argument-hint: "<syllabus PDF / URL / paste>"
---
Create a course from its syllabus. Input: $ARGUMENTS — a PDF path, a URL, pasted text,
or nothing (then ask me to paste the syllabus or describe the course).

Follow root CLAUDE.md. Steps:

1. **Extract**: course code + title, term, professor (+ email, office hours), schedule,
   location, course site, textbook, credits, grade breakdown, every dated deliverable,
   exam format/dates, the unit/topic sequence, and any language about AI or collaboration
   policy. Quote the AI-policy language verbatim if present.
2. **Ask me** only for what the syllabus doesn't say and the vault needs: the folder name
   if the title is ambiguous, and which `ai-policy` value to set (`open` · `explain-only`
   · `filing-only` · `none`) — propose one based on the syllabus language.
3. **Create** `Courses/<CODE — Name>/_Overview.md` from `Templates/Course Overview.md`
   (fill frontmatter incl. `ai-policy`; fill Quick Info, Grade Breakdown, Key Dates, and
   the **Units → Exams** map — the ingestion pipeline depends on that table).
4. **Deadlines**: one card per dated deliverable on `Boards/Deadlines.md` → 📥 Upcoming,
   in date order, 🔴 for exams / ≥15% / no-late items, 🟡 for 5–15%, 🟢 otherwise;
   ⚠️ on every card if `ai-policy: none`. Detail line: time, platform, weight, course link.
5. **People**: `People/<Professor Name>.md` from `Templates/Person.md` with course,
   office hours, email. Same for named TAs.
6. **Propagate**: `System/index.md`, `Home.md` needs nothing (Dataview), `System/CRITICAL_FACTS.md`
   active-courses line, `System/log.md` entry.
7. **Pinch points**: if `Synthesis/Schedule Pinch Points.md` exists, re-derive it with the
   new course folded in; if this is the second course of the term, create it from
   `Templates/Pinch Points.md`.
8. Report what was created and any TBDs (unposted dates), then commit
   `<CODE>: ingest syllabus`.

Never invent dates. Unknown → "TBD" in the overview and no card.
