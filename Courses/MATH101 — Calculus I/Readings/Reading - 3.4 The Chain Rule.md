---
date: 2026-08-24
tags:
  - reading
  - demo
type: reading
ai-first: true
course: "[[MATH101 — Calculus I]]"
chapter: 3
section: "3.4"
unit: 2
exam: 1
---

# Reading - 3.4 The Chain Rule

## For future Claude
Ingested from `Inbox/MATH101/Reading - 3.4 The Chain Rule.md`. Student's reading notes on the textbook section, verbatim. Enriches [[Derivative Rules]]; feeds the *Chain rule* subsegment of [[Cheat Sheet - MATH101 Exam 1]].

---

## Notes

**Theorem (Chain Rule).** If $g$ is differentiable at $x$ and $f$ is differentiable at $g(x)$, then $F = f \circ g$ is differentiable at $x$ and
$$F'(x) = f'(g(x))\,g'(x).$$

**Procedure for analysis (book's box):**
1. Identify the inner function $u = g(x)$ and the outer $y = f(u)$.
2. Differentiate the outer with respect to $u$.
3. Differentiate the inner with respect to $x$.
4. Multiply; substitute $u = g(x)$ back.

**General power rule** (chain + power): $\dfrac{d}{dx}[g(x)]^n = n[g(x)]^{n-1}g'(x)$.

**Longer chains:** $\dfrac{d}{dx}f(g(h(x))) = f'(g(h(x)))\,g'(h(x))\,h'(x)$ — peel one layer at a time.

Watch: $\frac{d}{dx}\sin^2 x$ means $(\sin x)^2$ → $2\sin x\cos x$; not the same as $\sin(x^2)$.

---

## Connections

- [[Derivative Rules]] · [[Lecture - 4 Chain Rule]] · [[Homework - 3.1-3.4]]
