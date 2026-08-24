---
date: 2026-08-24
tags:
  - concept
  - demo
type: concept
ai-first: true
course: "[[MATH101 — Calculus I]]"
unit: 2
exam: 1
status: living
---

# Derivative Rules

## For future Claude
Unit 2 backbone concept for [[MATH101 — Calculus I]]: the algebraic rules for differentiating combinations of functions. Feeds [[Cheat Sheet - Exam 1]]. Demo content — fabricated course, real math.

---

## Core Ideas

1. Differentiation is **linear**: $(af + bg)' = af' + bg'$.
2. **Products don't differentiate term-by-term** — the product rule accounts for both factors changing.
3. **Composition** $f(g(x))$ differentiates as the *outer* derivative evaluated at the inner, times the *inner* derivative — the chain rule. Rates multiply.
4. Implicit differentiation is *just* the chain rule with $y = y(x)$ as the inner function.

## Key Formulas

- Power: $\dfrac{d}{dx}x^n = nx^{n-1}$
- Product: $(fg)' = f'g + fg'$
- Quotient: $\left(\dfrac{f}{g}\right)' = \dfrac{f'g - fg'}{g^2}$
- Chain: $\dfrac{d}{dx}f(g(x)) = f'(g(x))\,g'(x)$ — Leibniz: $\dfrac{dy}{dx} = \dfrac{dy}{du}\dfrac{du}{dx}$

## Problem types to recognize

- **Nested function** ("differentiate $\sin(x^2)$", "$(3x+1)^5$") → chain rule; identify outer/inner first. → **HW 3.1-3.4 #3**: $(2x^3 - x)^4$
- **Product of two non-trivial factors** ($x^2 e^x$) → product rule; don't just multiply derivatives. → **HW 3.1-3.4 #1**
- **Fraction with variable denominator** → quotient rule *or* rewrite as product with negative power. → **HW 3.1-3.4 #2**
- **Chain inside a product** ($x\sin(2x)$) → product rule first, chain rule on the factor that needs it. → **HW 3.1-3.4 #4**
- **Tangent line at a point** → derivative, evaluate, point-slope. → **HW 3.1-3.4 #5**

## Common mistakes

- Forgetting the inner derivative (writing $\cos(x^2)$ for $\frac{d}{dx}\sin(x^2)$).
- Quotient rule numerator order: it's $f'g - fg'$ ("low d-high minus high d-low").
- Treating $(f g)' = f' g'$.

## Sources / Readings

- [[Reading - 3.4 The Chain Rule]]
- [[Lecture - 4 Chain Rule]]
- [[Homework - 3.1-3.4]]

## Connections

- Builds on: definition of the derivative (Unit 1).
- Used by: related rates and implicit differentiation (Unit 3) — every related-rates problem is a chain rule in $t$.
- [[Cheat Sheet - Exam 1]]

## Questions / Follow-up

- [ ] Why the product rule looks the way it does — the "growing rectangle" picture.

%% claude-heal:start | generated 2026-08-24T00:00:00Z | DO NOT EDIT INSIDE %%
**Related (same unit):** [[Reading - 3.4 The Chain Rule]] · [[Lecture - 4 Chain Rule]] · [[Homework - 3.1-3.4]]
**Related (forward):** Unit 3 related rates — chain rule in $t$.
**Assessed on:** [[Cheat Sheet - Exam 1]]
%% claude-heal:end %%
