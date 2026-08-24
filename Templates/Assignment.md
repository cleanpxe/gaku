---
date: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - assignment
type: assignment
ai-first: true
course: "[[<% tp.system.prompt("Course folder name (e.g. MATH101 — Calculus I)") %>]]"
due: "<% tp.system.prompt("Due date (YYYY-MM-DD)") %>"
status: in-progress
weight: ""
---

# <% tp.file.title %>

## For future Claude
Logistics note for a graded assignment. Help with understanding requirements, outlining, and reviewing — never produce the graded work itself (see the course's `ai-policy`).

---

## Requirements

*(What exactly is being asked?)*

<% tp.file.cursor() %>

---

## Relevant Concepts / Readings

- 

---

## My Plan

1. 

---

## Submission Checklist

- [ ] Requirements met
- [ ] Cited correctly
- [ ] Proofread
- [ ] Submitted
