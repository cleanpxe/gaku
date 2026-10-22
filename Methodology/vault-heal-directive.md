---
type: claude-directive
name: vault-heal
status: subordinate
generated_by: claude
---

# Vault Self-Heal Directive

> **How to run:** From Claude Code in the vault root, say "heal" or run `/heal`
> (`.claude/commands/heal.md`). The judgment (which notes should point where, and
> why) is yours; the mechanics (validating targets, writing blocks, proving
> convergence) are `scripts/heal.py` (§8). Re-run anytime; it converges.

---

## 0. Status & precedence — read this first

This is a **subordinate directive**, not an authoritative spec. The vault's
existing `.claude/` configuration and any `CLAUDE.md` are authoritative.

- On **any** conflict — folder layout, file naming, frontmatter keys, link
  style, tag taxonomy, formatting, tool usage, query conventions — the existing
  setup **wins**. This directive only fills gaps and adds.
- Before doing anything, read and conform to: everything under `.claude/`, the
  root and any nested `CLAUDE.md`, and any `README` / conventions / `templates`
  notes in the vault. If this directive says "use X" and the vault already does
  "Y," do **Y**.
- This file is the persisted recipe. Keep it version-controlled. Do **not**
  rewrite this file during a run — reproducibility comes from it staying fixed.

---

## 1. Mission

Review the **entire** vault and **additively** weave connections across
coursework, project builds, and research, then write an **immutable
point-in-time snapshot** — in a way that re-runs cleanly and converges
("self-heal"). Even isolated notes get pulled into the graph or flagged.

---

## 2. Hard rules (non-destructive guarantees)

1. **Only ever ADD.** Never delete, rewrite, reorder, or reword
   human-authored content. Never strip an existing tag or link.
2. **All agent-authored content lives ONLY inside managed regions** (§3).
   Never write a single character outside them.
3. **Assume version control.** Treat each run as a reviewable commit; surface
   what will change, don't bulk-edit silently.
4. **Idempotent.** Re-running on an unchanged vault must converge — recompute
   managed regions *in place*, never append duplicates, never grow without
   bound.

---

## 3. The managed region

Use the vault's existing managed-block convention if one exists. Otherwise:

```
%% claude-heal:start | generated <ISO8601> | DO NOT EDIT INSIDE %%
… agent content …
%% claude-heal:end %%
```

- Obsidian renders `%% … %%` as a hidden comment, so this stays invisible in
  reading view and never clutters the human-authored note.
- **On re-run:** locate the block by its delimiters and **replace its entire
  contents**. If absent, create one — placed at the end of the note body, below
  human content. Exactly **one** heal block per note, and it is the **last thing**
  in the note.
- **Markers count only at the start of a line.** Directives and docs quote the
  marker in backticks; a detector that matches it mid-line will paste a block into
  that prose. `scripts/check_vault.py` reports a marker that isn't at line start,
  more than one block, unbalanced markers, and text after a block.
- The block's timestamp changes only when its content does, so an unchanged re-run
  is byte-identical.
- Never touch managed blocks belonging to *other* tools.

Standard block (what `scripts/heal.py` writes for a new one; the *Siblings* query
appears for notes with a `course:` field, or `type: project`):

````
%% claude-heal:start | generated <ISO8601> | DO NOT EDIT INSIDE %%

### 🔗 Connections — auto-woven (heal)

**Linked from (live backlinks):**
```dataview
LIST WHERE contains(file.outlinks, this.file.link)
```

**Siblings (live):**
```dataview
LIST WHERE course = this.course AND file.name != this.file.name SORT file.name ASC
```

**Semantic threads:**
- [[Target note]] — three to ten word reason

%% claude-heal:end %%
````

---

## 4. Connection policy — generous / semantic (Dataview hybrid)

Dataview is available, so connections split into two layers inside the managed
region. Adapt every field/tag name below to the vault's **actual** frontmatter
and taxonomy.

### (a) Live structural links — Dataview queries (auto-refresh, no re-run)

Emit queries for connections derivable from structured data: shared tags,
shared `project` / `course` / `topic` frontmatter keys, folder siblings, and
inbound backlinks. These re-evaluate every time the note is opened.

```dataview
LIST
FROM #<shared-tag>
WHERE file.name != this.file.name
SORT file.mtime DESC
```

Prefer the vault's existing query style if one is established.

### (b) Semantic links — explicit `[[wikilinks]]` (what Dataview can't derive)

Be **generous**. Link conceptually adjacent notes even with **no** shared tags:

- **prerequisite → application** (a course concept used in a build),
- **research → build** (a finding that informs a project),
- **cross-domain bridges** (coursework ↔ project ↔ research),
- shared themes, recurring entities, methods reused across contexts.

Each semantic link gets a **3–10 word "why" gloss** so the connection is
legible and auditable, e.g. `[[Note B]] — applies the diffusion math here`.

- Generosity is bounded by **relevance, not by a count**. When in doubt,
  include it *with* a rationale.
- Drift control: these live in the managed region (recomputed in place each
  run) and every added link is recorded in the run log (§7).

### Tags

Where a note's content clearly implies a tag the vault's taxonomy **already
uses**, add it (additive only). Do not coin new tags unless the existing config
permits it.

---

## 5. Maps of Content & index (living, query-driven)

- For each domain — **coursework**, **project builds**, **research** — maintain
  or refresh a MOC note using the vault's MOC convention. Its body is a managed
  region of **live Dataview tables/lists**, so it stays current automatically.
- Maintain a top-level index linking the three domain MOCs.
- **Orphans:** include a live Dataview query listing notes with no inbound or
  outbound links, so nothing stays disconnected. Re-evaluates on every open.

```dataview
LIST
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
```

---

## 6. The snapshot — immutable, point-in-time

> **CRITICAL:** the snapshot is **frozen**. Use Dataview to *compute* values
> during the run, then write **static results** into the file. Do **not** embed
> live `dataview` / `dataviewjs` / inline-DQL in a snapshot — they would
> re-render with *future* vault state and destroy the historical record.

- **One new file per run. Never overwrite a prior snapshot.**
- Naming: the vault's snapshot convention, or absent one:
  `Snapshots/<YYYY-MM-DD>-<season>.md` (e.g. `2026-06-14-summer.md`).
- Fixed template (format stays deterministic even as data varies):

```
---
type: vault-snapshot
date: <YYYY-MM-DD>
season: <e.g. summer 2026>
generated_by: claude-heal
---
# Vault Snapshot — <season>, <date>

## At a glance
- Total notes: <N>
- By domain: coursework <N> · project builds <N> · research <N> · other <N>
- Links: <before> → <after>  (+<delta> this run)
- Orphans remaining: <N>

## Active projects
- <project> — <one-line frozen status>

## Research threads
- <thread> — <one line>

## Course topics
- <topic cluster> — <one line>

## Connection map
<which domains are bridging into which; the key hub notes>

## Connections formed this run
- <source> → <target>  (why)

## Open loops / orphans
- <note still disconnected> — <suggested next link>
```

All values frozen at generation time.

---

## 7. Run log — append-only

Append a dated entry to `Snapshots/_heal-log.md` (or the vault convention):
notes touched, links added (structural query count + semantic link count), MOCs
refreshed, snapshot filename, anomalies. **Never rewrite prior entries.**

---

## 8. Execution order (deterministic process)

0. **Conform** — read existing config; detect conventions; set precedence
   (existing setup wins).
1. **Inventory** *(read-only)* — `python3 scripts/heal.py inventory` lists the notes
   in `[heal] scope` (gaku.toml) and which lack a block; read the new and changed
   notes yourself for content.
2. **Plan** *(read-only)* — draft the threads as a proposals file in a scratch
   directory (not the vault):

   ```json
   {"blocks":  {"Courses/MATH101 — Calculus I/Derivative Rules.md": [["Lecture - 4 Chain Rule", "where the chain rule is first derived"]]},
    "reverse": [["Courses/MATH101 — Calculus I/Lectures/Lecture - 4 Chain Rule.md", "Derivative Rules", "the rule table this lecture extends"]]}
   ```

   `blocks` = threads for a note's own block; `reverse` = bridges back from existing
   notes into the new ones. Path-qualify any target whose name is shared. At scale
   (dozens of new notes), split the drafting by course and merge the JSON.
   `python3 scripts/heal.py apply <file>` is the dry run: it rejects dead, ambiguous
   and self targets and glosses outside 3–10 words, and prints what will change.
   **On first run in a vault, show that summary and pause for confirmation.** Later
   runs proceed.
3. **Apply** — `python3 scripts/heal.py apply <file> --write` (`--refresh` also
   replaces glosses of threads that already exist). It refuses any write that would
   change a byte outside a block, then re-plans and must report 0 changes
   (converged). Refresh MOCs + index (live queries) by hand if the vault keeps them.
4. **Lint** — `python3 scripts/check_vault.py`; fix what the run caused.
5. **Snapshot** — compute via Dataview or the inventory, write the **frozen** static
   snapshot.
6. **Log** — append the run record, including the method (proposals file,
   counts the script printed) so the run can be reproduced. Then commit.

Same vault state ⇒ same format and same converged structure.

---

## 9. Determinism contract (what is and isn't guaranteed)

**Guaranteed:** file naming, section order, frontmatter schema, managed-region
markers, phase order, precedence, idempotent convergence (no duplication, no
bloat), append-only history.

**Not guaranteed:** an identical *set* of semantic links between runs — generous
semantic mode is judgment-based by design, and can shift with content, context,
or model version. Drift is contained by recompute-in-place (§3) plus the run
log (§7), so the *format* and *history* stay stable even when the link set
varies.

---

## Appendix A — conformance notes for gaku vaults

Defaults this directive assumes in a gaku vault. A vault's own `CLAUDE.md` overrides them.

- **Scope:** `[heal] scope` in `gaku.toml` (default `Courses/`, `Projects/`, `People/`,
  `Synthesis/`, `Sources/`). Never write blocks into `Inbox/` (raw drops are the
  student's), `Boards/`, `Daily/`, `Templates/`, `System/`, `docs/`, `Snapshots/`, or root
  files (`Home.md`, `CLAUDE.md`, `README.md`).
- **Structural queries:** notes with `course: "[[…]]"` get the course-siblings query;
  `type: project` notes get `LIST WHERE type = "project" …`; everything else gets
  backlinks only.
- **Shared names:** every course has an `_Overview.md`, so link it path-qualified
  (`[[MATH101 — Calculus I/_Overview]]`) or link the course by its alias
  (`[[MATH101 — Calculus I]]`). The script rejects ambiguous targets.
- **Renames between runs:** use `scripts/rename_note.py`; it rewrites links inside heal
  blocks too, so no thread goes dead. `python3 scripts/heal.py check` lists any that did.
- **Snapshots:** `Snapshots/<YYYY-MM-DD>-<season>.md` (frozen) + append-only
  `Snapshots/_heal-log.md` (union-merged in `.gitattributes`, so two machines don't
  conflict on it).
- **MOCs** are optional. If the vault keeps them, put them in `Synthesis/` with
  `type: moc`.
