---
date: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - daily
---

# <% tp.date.now("YYYY-MM-DD") %> — <% tp.date.now("dddd") %>

## Focus

1. <% tp.file.cursor() %>
2. 
3. 

## Due within 7 days

```dataview
TABLE WITHOUT ID file.link AS "Assignment", course AS "Course", due AS "Due"
FROM "Courses"
WHERE type = "assignment" AND status != "done" AND due <= date(today) + dur(7 days)
SORT due ASC
```

## Log



## Review

**Went well:** 

**Didn't:** 

**Tomorrow's #1:** 
