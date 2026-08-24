---
date: 2026-08-24
tags:
  - cheat-sheet
  - demo
type: cheat-sheet
generated_by: claude-ingest
ai-first: true
course: "[[MATH101 — Calculus I]]"
exam: 1
status: living
---

# Cheat Sheet - Exam 1

## For future Claude
Per-exam recall layer for [[MATH101 — Calculus I]] Exam 1 (Units 1–2), built by ingestion (§4A of the directive). One `##` subsegment per approach, in unit order; each keyed by title so re-ingestion replaces in place. Derivations dropped; use-it-now form kept. Demo — only the Unit 2 chain-rule subsegment is populated.

---

## Chain rule

*§3.4 · [[Reading - 3.4 The Chain Rule]] · [[Lecture - 4 Chain Rule]] · Unit 2*

> [!formula] Chain rule
> $$ \frac{d}{dx}f(g(x)) = f'(g(x))\,g'(x) \qquad \frac{dy}{dx} = \frac{dy}{du}\frac{du}{dx} $$
> $f$ = outer · $g$ = inner · multiply outer' (at inner) by inner'

**Use when** — the function is a composition: something *inside* something ($\sin(\cdot)$, $e^{(\cdot)}$, $(\cdot)^n$, $\sqrt{\cdot}$ with a non-$x$ argument).

**Approach**
1. Name the inner $u = g(x)$; rewrite as $y = f(u)$.
2. $f'(u)$, then $g'(x)$.
3. Multiply, substitute $u$ back.

**Cases**
- General power: $\frac{d}{dx}[g]^n = n g^{n-1} g'$
- $e^{g}$ → $e^{g} g'$ · $\sin g$ → $\cos g \cdot g'$ · $\ln g$ → $g'/g$
- Triple nest: peel one layer at a time, multiply all three.

**Common problem-set scenarios** *(assigned — from [[Homework - 3.1-3.4]])*
- Polynomial to a power: **HW 3.1-3.4 #3** $(2x^3-x)^4$
- Product with a chain inside: **HW 3.1-3.4 #4** $x\sin 2x$ — product first, chain on the factor
- Tangent line through a square root: **HW 3.1-3.4 #5**

**Watch**
- The #1 exam error: forgetting $g'(x)$.
- $\sin^2 x \ne \sin(x^2)$.
- After differentiating, **factor** — graders and later steps both want it.

---

## Product & quotient rules

*§3.2 · Unit 2*

> [!formula] Product · Quotient
> $$ (fg)' = f'g + fg' \qquad \left(\frac{f}{g}\right)' = \frac{f'g - fg'}{g^2} $$

**Use when** — two non-constant factors multiply / divide.

**Approach** — write $f, f', g, g'$ in a 2×2 grid before assembling; it prevents order errors.

**Common problem-set scenarios** *(assigned)*
- **HW 3.1-3.4 #1** $x^2 e^x$ · **HW 3.1-3.4 #2** $\frac{x}{x^2+1}$

**Watch** — quotient numerator order ("low d-high minus high d-low"); a fraction with a *constant* numerator is faster as a negative power + chain.
