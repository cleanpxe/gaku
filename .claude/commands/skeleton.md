---
description: "Deck-first lecture — file the downloaded deck, render its slides, write the fill-in skeleton and say it's ready, then do the full ingest. Use for 'skeleton', 'skeleton first', 'downloaded lecture <n>', 'move and ingest', 'the deck is up'."
argument-hint: "[CODE] [deck name or lecture number]"
---
Run §4E of @Methodology/note-ingestion-directive.md for: $ARGUMENTS
Obey its §0 precedence rules: root CLAUDE.md wins on any conflict. Check the course
`ai-policy` (§8) first.

1. `python3 scripts/intake.py` and show me the plan in one line per file. If it matches
   what I asked for, run it with `--apply --render`. Re-downloads are reported, not filed.
   Anything unmatched or ambiguous: ask, don't guess.
2. Write the skeleton to `Inbox/<CODE>/Lecture - <N> <title>.md` in the shape of
   `Templates/Lecture Skeleton.md`, then tell me `skeleton ready: <path>` — I may be
   sitting in the lecture. Do this before anything slow.
3. Then the long ingest per §4 and §4A, merging into a `status: scaffold` note if one
   exists (§5).
4. `python3 scripts/check_vault.py`, then commit `<CODE>: ingest L<N> <title>, skeleton
   first` (push per `CLAUDE.md` § Git).
