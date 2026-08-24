Bootstrap a new semester in this vault. Follow root CLAUDE.md.

1. Ask me, in one message: name, school/program, year, timezone, term name + start/end
   dates, the list of courses (code + title; syllabus file/URL if I have it), and standing
   commitments (lab, job, club). Accept partial answers; leave the rest ⬜.
2. Fill `System/PROFILE.md` and `System/CRITICAL_FACTS.md`.
3. For each course: run the `/new-course` procedure (`.claude/commands/new-course.md`) —
   with the syllabus if given, otherwise create the `_Overview` shell with TBDs.
4. If the demo course `Courses/MATH101 — Calculus I/` and `People/Dr. Ada Example.md`
   still exist, ask whether to delete them (recommend yes once I've seen them).
5. Create `Synthesis/Schedule Pinch Points.md` from `Templates/Pinch Points.md` once two
   or more courses have dates.
6. Create `Inbox/<CODE>/` for each course (they're gitignored — local only).
7. Update `System/index.md`, append to `System/log.md`, commit `Bootstrap <term>`.
8. Print a 5-line "what to do next" (take notes → Inbox → `/ingest-notes`; `/week` on
   Sundays; `/exam-prep` two weeks out).
