---
date: 2026-08-24
tags:
  - lecture
  - demo
type: lecture-note
ai-first: true
course: "[[MATH101 — Calculus I]]"
topic: "Chain rule"
unit: 2
exam: 1
---

# Lecture - 4 Chain Rule

## For future Claude
Ingested from `Inbox/MATH101/Lecture - 4 Chain Rule.md` (see `docs/examples/inbox/` for the raw input). Verbatim student notes below; enriches [[Derivative Rules]].

---

## Core Ideas

1. Composite function = "function of a function"; peel the outer layer, keep the inner intact, then multiply by the inner's derivative.
2. Leibniz form $\frac{dy}{dx} = \frac{dy}{du}\frac{du}{dx}$ — the $du$'s "cancel" (mnemonic, not a proof).
3. Rates multiply: if $u$ changes 3× as fast as $x$, and $y$ changes 2× as fast as $u$, then $y$ changes 6× as fast as $x$.

---

## Notes

*(verbatim from lecture)*

Prof started with $y = (3x+1)^2$. Expand: $9x^2 + 6x + 1$, derivative $18x + 6 = 6(3x+1)$. Point: the $3$ is the derivative of the inside.

Then $y = (3x+1)^{100}$ — can't expand. Need a rule.

**Chain rule.** If $y = f(u)$ and $u = g(x)$ then
$$\frac{dy}{dx} = f'(g(x)) \cdot g'(x)$$

Examples on board:
- $\frac{d}{dx}\sin(x^2) = \cos(x^2)\cdot 2x$
- $\frac{d}{dx}e^{5x} = 5e^{5x}$
- $\frac{d}{dx}\sqrt{1 - x^2} = \frac{1}{2}(1-x^2)^{-1/2}\cdot(-2x) = \frac{-x}{\sqrt{1-x^2}}$

Gear analogy: two gears, ratio 3:1 then 2:1 → overall 6:1. That's the multiplication.

> 💡 The most common exam error is *stopping after the outer derivative*. Always ask "what's the derivative of the inside?"

---

## Key Terms

| Term | Definition |
|---|---|
| Composite function | $f(g(x))$ — output of $g$ fed into $f$ |
| Outer / inner | $f$ / $g$ in $f(g(x))$ |

---

## Questions / Confusions

- Why is it OK to "cancel" $du$? (Prof: it isn't a fraction, but the limit argument makes it work.)

---

## Connections

- [[Derivative Rules]] · [[Reading - 3.4 The Chain Rule]] · [[Cheat Sheet - Exam 1]]

---

## Follow-up

- [ ] Do the gear analogy with actual numbers for HW 3.
