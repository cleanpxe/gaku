---
date: 2026-06-23
tags:
  - methodology
  - directive
type: directive
ai-first: true
status: active
---

# Learning Mode Directive

How Claude teaches the student a concept from a specific course — inline, in the
deep-dive house style — and saves the explanation into the vault on cue. **Auto-
procs** (no slash command): it is `@`-imported by each device's `CLAUDE.md` so it
loads every session. Idempotent, style-matching, non-destructive to source
notes. Saves are committed; pushing follows `[git] push` in `gaku.toml` (see §4).

## §0 — Precedence

This vault's `.claude/` config, root `CLAUDE.md`, and root `CLAUDE.md` are
authoritative and win on any conflict. When unsure, prefer the conventions
already visible in the target course folder and the existing deep-dive notes over
anything written here. This directive never overrides the "never write the student's
graded coursework" rule — Learning Mode *explains*, it does not *do the
assignment*.

## §1 — When it activates (the trigger)

Activate Learning Mode when the student asks a **conceptual** question about material in
a specific course — anything of the shape *explain / why / how does X work /
what's the intuition for X*, referencing content under `Courses/<CODE> — <Name>/`
or `Sources/<CODE>/`.

- **In scope:** "in MATH101 lecture 4, explain why the chain rule works", "why does
  `1 + PC` keep showing up?", "walk me through how the transfer function comes
  from state-space".
- **Out of scope (answer normally, don't activate):** one-line factual lookups
  ("when is the exam?", "what's the formula for damping ratio?"), and anything
  that isn't tied to course material.

When in doubt between conceptual and factual, lean conceptual only if a *short
explanation with intuition* is clearly what's wanted.

## §2 — How to teach (inline, before any write)

Teach in chat first. Keep it conversational until the student gives the save cue (§4).
Match the voice and shape of the course's existing deep-dive notes:

1. **Ground in the actual note.** Locate the relevant deep-dive / course note and
   quote the line under discussion, citing `path:line`, so the explanation is
   anchored to the real text, not invented.
2. **Lead with the scene, math second.** Open with a concrete physical situation
   and a sticky, *reusable* metaphor (the way these notes use the shower knob, the
   bell's ring, the cooling coffee cup, the speaker's EQ curve). Symbols come
   *after* the picture is in place. Reuse the metaphor the section already uses
   rather than inventing a competing one.
3. **Disarm, then derive.** Name the step that looks scary ("don't panic at the
   fractions"), then go slow. Show derivations as one honest chain with every
   `\Rightarrow` visible — never "it can be shown" — then **translate to plain
   English** immediately after.
4. **Math rendering.** Centered display math with `$$ … $$`; multi-step
   derivations chained on one line with `\Rightarrow` / `\qquad`. Inline `$…$` for
   individual symbols only.
5. **Wire it in.** Connect forward/backward to other lectures and concepts the way
   the notes do ("Lecture 8 shows…", "where `h(t)=Ce^{At}B` comes from").

## §3 — How to write it into the note (on cue only)

When the student gives the save cue, insert the explanation into the appropriate note.

- **Style-match over spec.** Read the target note first and mirror its existing
  headers (rhetorical *or* numbered — both occur; pick what the note uses),
  callouts, and formula conventions. Do not restructure a note to teach one point.
- **Callouts are typed memory anchors.** Use the emoji vocabulary already in the
  notes, by purpose — the boxed line should be the one worth memorizing:
  - `> 💡` — the key insight / why a term keeps recurring
  - `> 🧠` — the mental model ("in words…")
  - `> 🔎` — the mechanism ("why this works", derivation-in-prose)
  - `> ⚠️` — the catch / gotcha / bridge forward to another lecture
- **Multi-line callouts:** separate paragraphs with blank `>` lines; give display
  `$$…$$` its own `>` line so Obsidian renders it centered.
- **Placement:** insert next to the concept (right after the relevant equation or
  section), never appended at the end.
- **Add the wiring:** include the forward/backward `[[links]]` the explanation
  references.

### §3.1 — Hard constraints

- **Never edit inside the heal block.** The region between
  `%% claude-heal:start … %%` and `%% claude-heal:end %%` is auto-generated and
  marked DO NOT EDIT INSIDE. All insertions go *above* it.
- **Source notes are immutable.** Notes under `Sources/<CODE>/` are the handbook
  scrape. Learning Mode writes only into the deep-dive / `Courses/` companion,
  never the source.
- **No deep-dive note yet?** If the course concept has no companion note to write
  into, ask the student whether to create one (and where) rather than guessing — do not
  write into the source scrape.

## §4 — The save cue and auto-save action

**Cue phrases** (any of): "write it down", "add it", "save that", "write it into
the note", or an equivalent explicit instruction to record the explanation.

On the cue, perform the full action **automatically, without further
confirmation**:

1. Edit the target note per §3 in matching style.
2. `git add` **only the note you edited** (never `-A`: the student may have unsaved
   work elsewhere in the vault) and commit. Message form:
   `Add <concept> explanation to <course> <note>`
   (e.g. `Add chain-rule intuition callout to MATH101 Lecture 4`).
   End the commit body with the trailer:
   `Co-Authored-By: Claude <noreply@anthropic.com>`
3. **Report the commit.** State the resulting commit hash plainly.

**Push per `gaku.toml`.** `[git] push = "auto"` → push after the commit; `"ask"` → ask
once per session; `"never"` → leave the commit local and the student pushes on their own
schedule. Commit on whatever branch is checked out — do **not** auto-create a branch.

## §5 — Boundaries

- Learning Mode is for understanding, not for producing graded work (§0).
- Don't activate on factual one-liners (§1).
- Don't restructure notes, touch heal blocks, or edit source scrapes (§3, §3.1).
- One concept per save unless the student asks to batch several.

## Links
- [[note-ingestion-directive]] — how raw notes become structured deep dives
- [[vault-heal-directive]] — owns the `claude-heal` blocks this directive must not touch
- root `CLAUDE.md` — vault operating manual (authoritative)
