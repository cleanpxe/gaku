# FAQ

**Do I need Claude Code?**
No. The Obsidian side (folders, templates, dashboard, boards, naming contract) works on its
own. Claude Code is what makes filing, linking, and cheat sheets automatic. See
`CUSTOMIZING.md` → "No-AI mode" / "Use a different AI tool".

**Why is `Inbox/` gitignored?**
Raw drops are messy, often huge (PDF scans, transcripts), and sometimes contain things you
don't want in a repo. The *processed* notes are what's worth versioning.

**Do I have to name files exactly `Lecture - …`?**
The first word before ` - ` is the routing keyword; the rest is free. `Lecture - wk3 tues
whatever.md` works. The pipeline stops and asks on anything it doesn't recognize.

**A note fits two courses.**
Put it under the course it was assigned in. Add a `[[link]]` to the other course's
concept note; `/heal` will find the connection anyway.

**My course has no exams / no textbook.**
Leave the Units → Exams table with one row mapping to "Final" or "Project". Cheat sheets
key on that value. Chapter-based keywords (`Chapter`, `Examples - Ch N`, `Review - Ch N`)
are just optional.

**Can I use this for grad school / self-study / a bootcamp?**
Yes — a "course" is anything with a syllabus-shaped structure. For pure self-study,
write the `_Overview` yourself with the units you intend to cover.

**What is `%% claude-heal %%`?**
A hidden managed block (`/heal` writes it) at the bottom of notes holding auto-generated
cross-links. Obsidian hides `%% … %%` in reading view. Never edit inside; everything
else in the note is yours.

**It created a note I didn't want.**
Delete it. Everything is git — `git log`, `git revert`. Run `/heal` afterward so
snapshots and links reconverge.

**Where does the cheat sheet get its "Common problem-set scenarios"?**
Three tiers, and the sheet labels them: general subject knowledge (scaffold) → textbook
worked examples (`Examples - Ch N`) → your assigned, solved homework (`Homework - …`,
labeled *assigned*). The last tier is the one that predicts exams.

**How big can this get?**
A four-course semester lands around 300–500 notes. Obsidian and Dataview are fine at
that scale. Images are the thing to watch — untrack `raw_images/` if it gets heavy.
