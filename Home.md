---
tags:
  - home
aliases:
  - Dashboard
ai-first: true
type: home
---

# 🎓 Home

> [[Boards/Deadlines|📅 Deadlines]] · [[Synthesis/Schedule Pinch Points|🔥 Pinch Points]] · [[Boards/Projects|🛠️ Projects]] · [[System/index|🗂️ Index]] · [[Inbox/README|📥 Inbox]]

---

## Due soon

```dataview
TABLE WITHOUT ID file.link AS "Assignment", course AS "Course", due AS "Due", weight AS "Weight"
FROM "Courses"
WHERE type = "assignment" AND status != "done"
SORT due ASC
LIMIT 10
```

## Active courses

```dataview
TABLE WITHOUT ID file.link AS "Course", professor AS "Professor", schedule AS "Schedule", ai-policy AS "AI policy"
FROM "Courses"
WHERE type = "course" AND status = "active"
SORT file.folder ASC
```

## Cheat sheets

```dataview
TABLE WITHOUT ID file.link AS "Sheet", course AS "Course", exam AS "Exam"
FROM "Courses"
WHERE type = "cheat-sheet"
SORT course ASC, exam ASC
```

## Concept notes still stubs

```dataview
LIST FROM "Courses"
WHERE type = "concept" AND status = "stub"
SORT file.folder ASC
LIMIT 15
```

## Recent days

```dataview
LIST FROM "Daily"
SORT file.name DESC
LIMIT 7
```

## Vault stats

```dataviewjs
const courses = dv.pages('"Courses"').where(p => p.type === "course" && p.status === "active");
const concepts = dv.pages('"Courses"').where(p => p.type === "concept");
const assignments = dv.pages('"Courses"').where(p => p.type === "assignment" && p.status !== "done");
dv.paragraph(`📚 **${courses.length}** active courses · 🧠 **${concepts.length}** concept notes · 📝 **${assignments.length}** open assignments · 📄 **${dv.pages("").length}** notes`);
```
