---
date: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - project
status: active
type: project
---

# <% tp.file.title %>

## Overview
<% tp.file.cursor() %>

## Architecture


## Key Decisions


## Links


## Milestones

- [ ] 

## Recent Activity

```dataview
LIST FROM "Daily"
WHERE contains(file.outlinks, this.file.link)
SORT date DESC
LIMIT 5
```
