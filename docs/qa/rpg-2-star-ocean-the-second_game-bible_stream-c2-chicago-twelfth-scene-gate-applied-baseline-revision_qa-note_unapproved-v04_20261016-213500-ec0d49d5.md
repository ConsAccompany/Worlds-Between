# Game Bible Stream C2: Chicago Loop applied as the twelfth science scene-quality gate (baseline revision 11 → 12)

Status: **staged for coordinator review. Not committed, not pushed.** Nothing is approved.
Meter **35.8%** (unchanged), M2 **10/12**, runtime sprites **0/52**, science scenes **0/12** (target was 11; none accepted), post-art playtests **0/2**.
Follows the v03 note (`…stream-c2-scene-gate-blocked-and-three-capture-git-proposal_qa-note_unapproved-v03_20261016-212130-8cf8add8.md`), which prepared and isolated-tested this candidate but left it unapplied.

## Session

- Model claude-opus-5-5 on the signed-in Claude Max subscription. `ANTHROPIC_API_KEY` was absent. No auth or quota problem came up, and no API billing was used.
- No `AGENTS.md` exists in the repository or in any parent folder.
- `origin/main` = HEAD = `a87ac16` (checked with `ls-remote`).
- Not touched:
  - `game/scripts/*`;
  - `docs/progress.md`;
  - map, Washington, battle and sprite-pilot files;
  - female locomotion files and the separate Site checkout.

## Decision and authorization

- The creator's later decision made the Chicago Loop a freely explorable block. The 11-scene target was set on 2026-10-14, before the US geography. So the Loop becomes gate 12.
- The coordinator explicitly allowed one change in the two derived character-readiness checklist files:
  - the inventory SHA-256 field (`sources.inventory.sha256`) in the JSON;
  - its 16-character Markdown short form.
- No other character content was changed.

## What was applied

The v01 candidate steps were applied to the real files. The real-tree script is generated from the candidate by exact, counted substitutions, so every edit is byte-identical to the tested candidate. That script and its generator are local in `tmp/` and not staged.

- **Meter CLI:**
  - `science-environment-art` denominator is now 12.
  - New `record --baseline-revision`.
  - A plain `record` refuses a silent denominator change.
  - A baseline revision may not change any count.
- **Progress state:**
  - `approvalLedger.counters.sceneVisualsTarget` is now 12.
  - The current M2 `visual-review` text reads 场景画质 0/12.
  - The closeout was recorded through the meter CLI on the full working file, which keeps all 93 earlier closeouts, including every Codex dated closeout:
    - id `closeout-20261017-013819-8beba0c8`;
    - kind `baseline-revision`;
    - `baselineChanges` science-environment-art denominator 11 → 12;
    - `changed: false`, 35.8 → 35.8, delta 0.
- **Inventory:** new item `visual-scene.chicago-loop-outdoor`. Its stage is `planned` and it is unchecked, so the acceptance checkbox and server acceptance stay disabled.
- **Readiness checklist:** inventory hash `04a8379778f98675…` → `7507ec9f218f69fb…` (JSON and `.md`). Nothing else changed.
- **Game Bible state:**
  - `sceneQualityTarget` is now 12.
  - The denominator review is marked `applied`, with the closeout id and `applyQa` = this note.
  - The queue's counter sentence reads 0/12.
- **Builder canon check:** 0/12. It also requires the ledger target to be 12 and the review to be applied.
- **Tests:**
  - meter (7th check: baseline-revision path);
  - canon;
  - M2 gates;
  - selout-v2;
  - review queue;
  - the two local-only card tests (counter lines only, untracked, not staged).
- **Kept as history:** dated card prose, closeouts and snapshots that say 0/11, for example the static-pilot counters as of commit `15c9b73` and the dated `docs/progress.md` entries.

Meter by formula: 20 × 5/5 + 10 × 10/12 + 10 × 3/4 + 25 × 0/52 + 20 × 0/12 + 15 × 0/2 = 20 + 8.33 + 7.5 + 0 + 0 + 0 = **35.83 → 35.8%**. Under /11 the result is the same, so the delta is 0.

## Staging method

Nothing was added with `git add .` or `-A`.

- **Whole files, by exact path** (worktree = index before the edit):
  - meter CLI, inventory, Game Bible state, builder;
  - meter, canon, M2, selout and review-queue tests;
  - this note.
- **Index-only blobs** (`hash-object` + `update-index --cacheinfo`):
  - **Progress state:** the index text plus the same two edits and the recomputed meter, keeping only the index's closeouts plus the new one. The script checked two things:
    - every index closeout is present unchanged in the worktree;
    - the staged JSON equals the worktree JSON apart from `taskCloseouts`.

    Codex's 33 newer zero-change closeouts stay in the working tree only. Staging the full working file later gives the chronological order.
  - **Readiness checklist JSON and `.md`:** HEAD plus the hash line only. Their unrelated `untracked_discovered_manifests` edits (0 → 4) are byte-identical in the working tree and stay unstaged.

## Review-queue stage proposal recheck

All six queue entries match their recorded `sha256` in both the index and the working tree:

- **`committed-at-a87ac16`:** #1, #2 and #4 are in HEAD and clean.
- **`staged-not-pushed`:** #3 NYC City Hall Park v04, #5 map v02 Northeast and #6 map v02 Chicago route card. Each one:
  - is added by exact path and absent from HEAD;
  - is a 640×360 PNG;
  - carries `unapproved` in its name.

## Verification

- **Rehearsal:** a shared clone of `a87ac16`, plus the staged proposal, plus the worktree's progress and checklist files. Apply and staging succeeded. The 3 local-only card tests could not run there because their untracked inputs don't exist in a clone.
- **Working tree, full local suite (12 runs):** `RUNNER: all passed`:
  - meter `CHECK OK 35.8%`, science-environment-art 0/12;
  - builder `--check`;
  - meter 7/7, canon 5/5, Site figures PASS, M2 5/5;
  - 3 local card tests;
  - selout 14/14, readiness 7/7, review queue 6/6.
- **Meter check on the staged progress blob** (`--state`): `CHECK OK 35.8%`.
- **Clean export of the exact staged tree** with `core.autocrlf=true` (CRLF files):
  - Method: a shared clone, `read-tree` of the real index's tree, `checkout-index -a -f`.
  - Result: all 9 tracked scripts pass. The two local-only card folders are absent, as at HEAD.
  - The export's inventory `sha256-text-lf-v1` equals the checklist's recorded hash (`7507ec9f…`).

## Open item (pre-existing, not changed here)

The readiness builder's own check mode (`…character-sprite-readiness_build-and-check…py`, no args) reports the checklist JSON and `.md` as stale:

- **At bare HEAD `a87ac16`:** committed manifests that the registry doesn't reference are missing from `unregistered_manifests`:
  - female sideview v06–v09;
  - female walk compact v01;
  - the Liang Xu south pilot.
- **In the working tree:** it also finds 9 untracked discovered manifests from other streams, while the file records 4.
- **The inventory hash is not among the differences.**
- Regenerating with `--write` would change character content, so it is left to the checklist owner.
