# Global map v03: selective candidate sync and review queue

Status: integration request. Map art remains **unapproved**; M2 10/12, overall 40.8%, scenes 3/12, sprites 0/52, playtests 0/2 until creator acceptance.

Read AGENTS.md, repo status, Game Bible state/ledger and `docs/qa/rpg-2-star-ocean-the-second_global-map_native-art-pass_qa-note_unapproved-v03_20261017-175314-e8b8f8af.md`. Codex has visually inspected the actual 640×360 zh/en globe, Northeast, Chicago flight card and Washington car card. v03 visibly clarifies the two flight endpoints and land/lake/coast hierarchy. Preserve its listed defects and the inherited `background-visual-check` button-geometry failure explicitly; do not call this all-pass. No design or travel-rule changes.

Perform a **serialized, exact-file Git integration** of the map v03 candidate and any required uncommitted v02 prerequisites into the authorized `ConsAccompany/Worlds-Between` main branch. First audit every candidate diff and the very dirty shared worktree. Run targeted map/travel checks and a clean-clone or clean-index reproducibility check before push. Stage only exact map scripts, relief data, test/source tools, QA/evidence and a small selection of actual Godot screenshots needed for cross-device review. Never `git add .` or stage unrelated Chicago, City Hall, character, battle art, server or other sessions' changes. Do not reset others' edits.

Add one accurate Game Bible visual-review item for the map with a pinned GitHub raw URL to a real v03 Godot screenshot; label it technical candidate/unapproved and describe the inherited test failure. Update a zero-change task receipt and recompute the six category meters without raising any acceptance counter. After a successful fast-forward push, report commit SHA, exact files, tests and review image URL. If conflicts or a non-fast-forward occur, re-read current state and integrate safely; do not force push. Do not contact the creator for a decision mid-session.

Claude Max firstParty subscription only. Confirm `ANTHROPIC_API_KEY` absent before work. Never API billing, credits, auto-reload, purchased credits or paid fallback; stop if quota/auth blocks work.
