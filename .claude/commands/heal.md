---
description: "Vault-wide linking pass: draft threads, apply them with scripts/heal.py, lint, snapshot, log, commit. Use for 'heal', 'heal / lint', 'run the heal', 'weave the links'."
---
Load and execute @Methodology/vault-heal-directive.md.
Obey its §0 precedence rules: root CLAUDE.md wins on any conflict. Run phases 0–6 in
order, with the mechanics in `scripts/heal.py` (§8): you draft the threads as JSON in a
scratch file, the script validates and writes them. Pause after the Plan phase for my
confirmation on the first run in this vault only. Then `python3 scripts/check_vault.py`,
the frozen snapshot, the run-log entry, and one commit (push per `CLAUDE.md` § Git).
