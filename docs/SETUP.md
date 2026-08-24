# Setup

## 1. Get the repo

Click **Use this template** on GitHub → create your repo (private is fine — your notes
will live here). Clone it:

```bash
git clone https://github.com/<you>/<your-vault>.git
cd <your-vault>
```

## 2. Open in Obsidian

Obsidian → *Open folder as vault* → pick the clone. When Obsidian asks about community
plugins, **trust** them — they ship in `.obsidian/plugins/` so nothing needs installing:

| Plugin | Why it's here |
|---|---|
| Dataview | `Home.md` dashboard, "due within 7 days" in daily notes |
| Kanban | `Boards/Deadlines.md`, `Boards/Projects.md` |
| Templater | Every template in `Templates/`; folder templates for `Daily/`, `People/`, `Projects/`, `Sources/` |
| Calendar | Click a day → daily note |

Recommended but not bundled: **Latex Suite** (fast math input) and **Obsidian Git** (auto-commit).

Open `Home.md`. The dashboard will show the demo course.

## 3. Install Claude Code (optional but it's the point)

Follow the [Claude Code install guide](https://docs.claude.com/en/docs/claude-code), then:

```bash
cd <your-vault>
claude
```

`CLAUDE.md` at the root loads automatically and imports your profile and critical facts.
Type `/new-semester` and answer the questions.

No Claude? See `docs/CUSTOMIZING.md` → "No-AI mode".

## 4. Fill in who you are

`/new-semester` does this. By hand: edit `System/PROFILE.md` and `System/CRITICAL_FACTS.md`
— replace every ⬜.

## 5. Add your courses

- With Claude: `/new-course path/to/syllabus.pdf` (or a URL, or paste the text).
- By hand: create `Courses/<CODE — Name>/`, then in Obsidian run Templater →
  *Course Overview* to make `_Overview.md`. Fill **Grade Breakdown**, **Key Dates**, and
  the **Units → Exams** table — the ingestion pipeline reads that table to decide which
  cheat sheet a note feeds. Set `ai-policy` per the syllabus (see `ACADEMIC-INTEGRITY.md`).

## 6. Delete the demo

Once `Courses/MATH101 — Calculus I/` has shown you what ingestion produces, delete it and
`People/Dr. Ada Example.md`, and remove the line from `System/index.md`. `/new-semester`
offers to do this.

## 7. Sync between machines

It's a git repo. `Inbox/` and `.obsidian/workspace.json` are gitignored, so raw drops stay
local and UI state doesn't cause merge churn. Obsidian Git or a nightly `git add -A &&
git commit -m sync && git push` both work.
