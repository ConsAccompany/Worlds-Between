---
name: worlds-between-release-evidence
description: "Integrate reviewed files and preserve source evidence."
version: 0.1.0
author: Worlds Between project owner, Codex
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [worlds-between, godot, project-handoff]
---

# Worlds Between integration and assets
## When to Use
Finding historical assets, integrating verified output, updating GitHub or preparing playtest builds.
## Procedure
1. Use `terminal` with `tools/rpg-2-star-ocean-the-second_hermes_project-ops_v01_20261023-034500-a7e93140.py asset-find --match <subject>` to locate vault sources. Restore only an exact alias into a separate workspace; never over the game.
2. Check Git status and remote HEAD; preserve unrelated changes. Stage explicit reviewed paths only. Compare staged raw bytes and relevant asset hashes; never git add dot, reset or force-push.
3. Run targeted combined-path checks before commit. Update existing ledger/Bible via declared CLIs; retain before/after meters and truthful failures. Transfer owners through the audit, never relabel historical work as yours.
4. Push only verified state and verify resulting remote revision. The SSH deploy key permits this repository's Git transport only; gh API writes need separate auth. Do not request broader personal credentials as a shortcut.
5. Private Site hosting is not available through this VM's tools. Preserve source/fallback and state this boundary until an authorized publishing bridge is connected.
## Pitfalls
Historical archive Git blobs differ legitimately from current scenes. Use project-ops archive-verify. Do not normalize old hash-bound evidence, restore old defaults, publish vault/private controls or infer creator playtests from automation.
## Verification
Every staged path is selected, source/hash/test receipts bind to the commit, remote revision is checked, and all remaining human/platform gates are stated.
