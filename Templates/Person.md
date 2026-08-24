---
date: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - person
role:
context:        # course, lab, club…
last_interaction: <% tp.date.now("YYYY-MM-DD") %>
follow_up_date:
contact_email:
location:
---

# <% tp.file.title %>

## About
<% tp.file.cursor() %>

## Office hours / contact


## What they care about (grading, style, pet peeves)


## Notes


---

## Interactions

```dataview
LIST FROM "Daily"
WHERE contains(file.outlinks, this.file.link)
SORT date DESC
LIMIT 15
```
