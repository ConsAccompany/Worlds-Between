# Game Bible Stream C2: three-capture Git proposal staged; Chicago twelfth gate blocked by a character-file hash lock

Status: **staged for coordinator review. Not committed, not pushed.** Nothing is approved.
Meter **35.8%**, M2 **10/12**, runtime sprites **0/52**, science scenes **0/11** (not changed in this batch), post-art playtests **0/2**.
Follows the v02 note (`…stream-c-review-queue-render-wdc-v08-sync-and-chicago-gate-decision_qa-note_unapproved-v02_20261016-210902-ba97998b.md`).

## Session

- Model claude-opus-5-5 on the signed-in Claude Max subscription. `ANTHROPIC_API_KEY` was absent. No auth or quota problem came up, and no API billing was used.
- No `AGENTS.md` exists in the repository or in any parent folder.
- `origin/main` = `a87ac16` (checked with `ls-remote`). HEAD = `a87ac16`.
- Not touched:
  - `game/scripts/*` (including `scifi_world_map.gd`);
  - Washington art, battle scripts and character files;
  - `docs/progress.md`;
  - other streams' files.

## 1. Chicago Loop as gate 12: blocked, not applied

**No conflicting creator instruction was found.** Nothing after the 2026-10-15 Chicago decision fixes the target at 11.
- The 2026-10-15 reconciliation note says only that counters are unchanged at 0/11.
- The 2026-10-16 dispatch asks for the reconciliation.
- Under this batch's rule, the later playable scope controls.

**The batch is blocked by a technical conflict between two instructions:**
- "update the inventory", and
- "do not edit character files".

Why they collide:
- Adding the twelfth `visual-scene.*` item changes the asset inventory.
- The inventory's `sha256-text-lf-v1` hash is pinned in the character sprite readiness checklist (`game/data/character-visuals/…53da3710.json`, `sources.inventory.sha256`). Its `.md` twin shows the first 16 characters.
- The selout-v2 Game Bible test asserts that hash.
- That test is part of the 14-script suite. Without the refresh it fails with "readiness checklist records the current inventory hash" (reproduced in an isolated copy).
- The checklist also carries another stream's uncommitted edits (`untracked_discovered_manifests` 0 → 4).

An atomic revision therefore cannot land without editing a character file. A partial revision would leave the inventory/production summary at 0/11 while the ledger said 0/12, which the M2 test (inventory tally = ledger counter) rightly rejects. So **nothing of the 11 → 12 change is in the working tree or the index.**

### Prepared candidate (tested in isolation only)

Files, all local and unstaged in `tmp/`:
- Apply script: `rpg-2-star-ocean-the-second_stream-c2_twelfth-scene-gate-apply_candidate-v01_20261016-212130-8cf8add8.js`. It refuses to run inside the real repository.
- Patch against the staged proposal: `…twelfth-scene-gate_candidate-patch-vs-staged_v01_20261016-212130-8cf8add8.diff`. 12 files, +141/−56.

What it changes:
- **Meter CLI:**
  - `science-environment-art` denominator becomes 12.
  - New `record --baseline-revision`. It writes a dated closeout of kind `baseline-revision` with `impact.baselineChanges` (11 → 12).
  - A plain `record` now refuses a silent denominator change.
  - A baseline revision may not change any count.
  - Closeout "before" ratios now use the stored denominator.
- **Progress:**
  - `approvalLedger.counters.sceneVisualsTarget` becomes 12.
  - The current M2 `visual-review` text becomes 0/12.
  - The CLI writes the closeout, with impact `changed: false`, 35.8 → 35.8, delta 0.
- **Inventory:** new item `visual-scene.chicago-loop-outdoor`. Its stage is `planned`, so the acceptance checkbox and server acceptance stay disabled.
- **Readiness checklist:** **one field only**, `sources.inventory.sha256`, plus the matching 16-character prefix in the `.md`. This needs the checklist owner's approval.
- **Game Bible state:**
  - `sceneQualityTarget` becomes 12.
  - The denominator review is marked applied, with the closeout id.
  - The queue's counter sentence becomes 0/12.
- **Builder canon check:** 0/12. It also requires the ledger target to be 12 and the review to be applied.
- **Tests:**
  - meter (adds a 7th check for the baseline-revision path);
  - canon;
  - M2 gates;
  - selout-v2;
  - review-queue;
  - the two local-only card tests (counter lines only).
- Dated card prose and closeouts that say 0/11 stay as history.

Isolated result: a `--shared` clone of `a87ac16`, plus this staged proposal, plus the candidate. All 9 tracked scripts pass:
- meter `CHECK OK 35.8%`, science-environment-art `0/12`;
- builder `contentEqual`/`bytesEqual` true, 33 canon checks;
- meter test 7/7, canon 5/5, Site figures PASS, M2 5/5, selout 14/14, readiness 7/7, review queue 6/6.

Meter by formula: 20 × 5/5 + 10 × 10/12 + 10 × 3/4 + 25 × 0/52 + 20 × 0/12 + 15 × 0/2 = 20 + 8.33 + 7.5 = **35.83 → 35.8%**, unchanged.

To apply later, after approval: re-run the apply script's steps on the real files. The progress closeout must be recorded on the real progress state, which has more Codex closeouts than HEAD, so do not paste the diff's progress hunk.

## 2. Cross-device gallery: three actual Godot captures staged

All six queue entries were verified (path exists; sha256; Git blob):

| # | Capture | sha256 | Git blob | Sync state |
|---:|---|---|---|---|
| 1 | selout v8 city-bright (approved static still only) | `0b8e67ac75539fdac46e7843687d660d0dfa98697f7bf229b0079437351d9e65` | `bd3add4a` | committed-at-a87ac16 |
| 2 | battle v10 ruins 640 | `50687caf05283c4f379a1ec36ff806819b5d47a06d684f58273b4e29f2df1d8c` | `cd5598dc` | committed-at-a87ac16 |
| 3 | NYC City Hall Park v04 640 | `9f61420cc4c40d214056f9a2b8a1dac38cc981f82971d6156237a7b16b43a42a` | `9848c949` | **staged-not-pushed** |
| 4 | WDC Capitol west v08 640 entry | `b566a88a4c666c81d5f3b5cea33956685e966c2dbbd1ffa3ad4fa9b4f3c3deab` | `bb022ebe` | committed-at-a87ac16 |
| 5 | Map v02 Northeast zh 640 | `50e59f16614240dd7c6b91452dab0964b1dbcdcc94d36439b0e2b52075ec355f` | `8e637f16` | **staged-not-pushed** |
| 6 | Map v02 Chicago route card zh 640 | `0c9fb5d11186bed7f18ce65b78428c1ddbb63facf8773a5fe1b78b7f7ef96778` | `62a01a9b` | **staged-not-pushed** |

The same sha256 values are recorded in the Game Bible state (`items[].sha256`).
- #3, #5 and #6 also match the evidence index `2f06d687`.
- #1, #2 and #4 match their blobs at `a87ac16`.
- All three staged files carry `unapproved` in their names and badges.
- They were added by exact path. Nothing else from `outputs/nyc-chp-v04_…/`, no concept and no placeholder sprite was staged.

New sync state, `staged-not-pushed`:
- Meaning: the exact blob is in the local index only. It is not committed, not pushed and not visible on other devices.
- The app badge reads "已暂存为 Git 候选 · 尚未推送，其他设备不可见".
- `syncStateRule` records that the coordinator changes it to `committed-at-<sha>` only after the push and a raw-URL check.
- An unknown sync state now renders "同步状态未知" rather than a GitHub claim.

## Staged set and verification

Staged by explicit path or `update-index --cacheinfo`. Partial files are HEAD plus Stream C hunks only. The unrelated 2026-10-14 environment/enemy cards, the GIF allowlist and Codex's newer zero-change closeouts stay unstaged in the working tree. The blob list is in the hand-off report.

Tests run 2026-10-16 ~21:20–21:35 ET:
- **Working tree:** 14-script suite, `RUNNER: all passed`.
- **Clean export:** a `--shared` clone of `a87ac16` plus the exact staged diff, `git apply --index`, with `core.autocrlf=true`. 9/9 tracked scripts pass. The 3 local-only card tests are absent there, as they are at HEAD.
- **Baseline:** the same clone at bare HEAD passes 8/8.
