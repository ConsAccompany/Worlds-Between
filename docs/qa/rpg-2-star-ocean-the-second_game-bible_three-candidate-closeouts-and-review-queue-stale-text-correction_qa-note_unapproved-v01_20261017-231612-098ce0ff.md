# Three verified candidates: closeouts, Game Bible queue correction, and selective staging proposal

Date: 2026-10-17, 23:16–23:40 EDT. Tag `20261017-231612-098ce0ff`. Status: **all three candidates UNAPPROVED**. Nothing was staged, committed, pushed or deployed by this task (`git diff --cached` is empty).

Dispatch: `docs/coordination/rpg-2-star-ocean-the-second_three-candidate-closeout-and-bible-queue-claude-dispatch_unapproved-v01_20261017-231000-0e3a6f94.md`. Run by Claude Code Opus 5.5 through signed-in Claude Max (first-party); no API key, billing, credits or fallback; no quota stop was hit. The repo and its parents have no `AGENTS.md`; the dispatch, the closeout usage note and the existing naming convention were followed.

## Meters (recomputed, unchanged)

`node tools/…mvp-completion-meter_recompute-and-task-closeout-cli_…js check` → **CHECK OK 40.8%** on the working tree and on the proposed index state.

| Category | Weight | Count | Points |
|---|---|---|---|
| core-gameplay | 20 | 5/5 | 20 |
| global-world-travel (M2) | 10 | 10/12 | 8.33 |
| science-playable-content | 10 | 3/4 | 7.5 |
| character-art (full sprites) | 25 | 0/52 | 0 |
| science-environment-art (accepted scenes) | 20 | 3/12 | 5 |
| final-integrated-validation (human timed playtests) | 15 | 0/2 | 0 |

Weighted total 40.83 → **40.8%**. No gate, counter, weight or denominator changed.

## Closeouts (zero-change receipts)

| Closeout | Subject |
|---|---|
| `closeout-20261018-032000-48f99554` | Yonkers antenna room 1 v03 (15709be4) |
| `closeout-20261018-032001-569dd838` | Female battle static v12 (74401c3e) |
| `closeout-20261018-032002-1b55b4a2` | Global map v03r2 (9875b9e2, over v03r1 5ef3676e) |
| `closeout-20261018-032003-e63be377` | Game Bible review-queue stale-text correction |

Each is 40.8% → 40.8%, `changed: false`. The first three cite the candidate's QA note, its check report or log, the evidence index and this note. The dispatch asked for three closeouts; the fourth follows the usage note's rule that every completed task gets a receipt.

The evidence index is `outputs/rpg-2-star-ocean-the-second_mvp-completion-ledger_yonkers-v03-battle-v12-map-v03r2-closeout-evidence-index_v01_20261017-231612-47a0716c.json`. It pins 132 files (sha256-text-lf-v1 for text, sha256-bytes for binaries), each with its git state and a `proposedStage` flag. It also records the Codex 640×360 judgments as Codex reported them in the dispatch:
- **Yonkers v03:** clearer concave dish and HUD-safe antennas, but still geometric next to the accepted interiors.
- **Battle v12:** better mass and boot contrast, but still the narrowest party member, with a blocky pack and legibility trade-offs.
- **Map v03r2:** better land/water and card hierarchy, but the Great Lakes land is broad and low on detail.

This task did not re-judge the art.

### What was re-verified here, and what was not

- **Battle v12:** all 11 sha256 values in the QA note's table match the files.
- **Map v03r2:** all 6 sha256-text-lf-v1 values for the scripts, data and tools match.
- **Yonkers v03:** the 8 runtime and source hashes in the manifest match.
- **Runtime dependencies:** every `res://` path in the working `survey_annex.gd`, `scifi_world_map.gd` and `world_map_data.gd` is either in HEAD or in the proposed file set.
- **Not re-run:** the Godot, Pixelorama and Python gates. Their results (YK1_V03_ALL_OK, 16/16; check 50/50 and CAPTURE PASS ×4; 896/896, SOURCE_CHECK_OK 40) are the authors' recorded results.

## Game Bible correction (`environmentVisualReview.crossDeviceReviewQueue`)

No queue item was removed or reordered. For every item, `file`, `gitBlob`, `sha256`, `syncState`, `qa`, `creatorApproved`, `runtimeIntegrated` and `artAccepted` are unchanged; the edit script refused to write if any of them moved. Badges still derive from the flags. Nothing is approved.

- **#3 City Hall Park v04** was captioned "still under review". It is now a **rejected historical comparison**: the label, stored badge and caption changed, and `creatorReview` was added (2026-10-16, `rejected`, `historical-comparison-only`). The evidence is the tracked note `docs/qa/…nyc-city-hall-park_style-alignment-visual-direction_unapproved-v01_20261016-225800-2a4e7c91.md`: "City Hall Park v04 looks unlike the other science-region scenes. Withdraw v04 from final scene-quality review."
- **#7 and #8, battle heroine v11,** were captioned "shown for creator feedback only". They now say it was **reviewed and rejected for more static polish**: the stored badge and captions changed, and `creatorReview` was added (2026-10-17, `rejected-more-static-polish`, creator answer "继续精修静止帧"). The evidence is `docs/qa/…battle-static-v11-creator-feedback-and-v12-visual-target_unapproved-v01_20261017-193755-c7a93e12.md`. The required caption phrases are kept ("Unapproved static pilot", "only the 0.65 proportion is approved", "Not a complete character sprite; no animation").
- **#1 selout v8** said only "motion … remain open". It now names the latest creator-reviewed locomotion, **south run v04**: the creator chose "继续打磨跑动或停步", so it needs a smoother run and stop. The later local v05/v06 have not been creator-reviewed. A `motionStatus` field was added. The evidence is `docs/qa/…south-run-v04-native-godot-stills-codex-visual-review_unapproved-v01_20261016-222301-2a46573f.md`.
- **#10 map v03** gained `laterLocalPasses`. Its QA notes now record that v03r1 and v03r2 supersede v03 in the working tree. If they are committed, the live map draws v03r2 art, and this capture stays the committed v03 record. Neither pass is accepted, and M2 stays 10/12. The caption and the inherited-failure record are unchanged.
- **Queue level:** a `corrections` record was added (items 1, 3, 7, 8, 10, with this note). `updatedAt` changed. Builder `--check`: contentEqual true, bytesEqual true, 33 canon checks.

The queue test (`tests/game-bible-review-queue/…8a86c60c.js`) gained assertions for all of the above. Its #10 relief check now accepts the v03 relief or the v03r2 relief that supersedes it. Without that change, the test fails on the current working tree because of v03r2.

## Exact selective staging proposal (not executed)

### 1. Index-only patch for the progress state

`outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json` has unrelated uncommitted hunks from another workstream:
- 11 closeouts from 02:58 to 05:06Z;
- the `decisions` reorder;
- the NYC room 2 static-baseline approval.

Do **not** `git add` this file. Apply the index-only patch instead:

```
git apply --cached outputs/rpg-2-star-ocean-the-second_mvp-progress-state_three-candidate-closeouts_index-only-patch_unapproved-v01_20261017-231612-47a0716c.patch
```

The patch runs from HEAD blob `2e0638d` to `69976d21c5f2570e6cb8306b25e9e0e28f6e38f9`, with +105/−5 lines. It contains only:
- the four closeouts, appended after `closeout-20261017-230630-70c7d978`;
- `updatedAt`;
- `completionMeter.updatedAt`;
- `completionMeter.lastUpdated`.

`git apply --cached --check` passed, and the index was left untouched. After it is applied, the remaining working-tree diff of that file is exactly the other workstream's hunks.

### 2. Whole files by explicit path

Each of these tracked files was clean at HEAD, or its diff against HEAD belongs only to the named candidate.

**Game Bible correction:**
- `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json`
- `tests/game-bible-review-queue/rpg-2-star-ocean-the-second_game-bible_cross-device-review-queue_check_v01_20261016-210902-8a86c60c.js`
- `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v11-creator-feedback-and-v12-visual-target_unapproved-v01_20261017-193755-c7a93e12.md` (read by the test)
- `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-run-v04-native-godot-stills-codex-visual-review_unapproved-v01_20261016-222301-2a46573f.md` (read by the test)
- this note
- the evidence index

**Yonkers antenna room 1 v03, runtime-wired:**
- `game/scripts/survey_annex.gd`. Whole file. Its diff against HEAD is the Yonkers room-1 v02 structure plus the v03 asset paths, and nothing else.
- The 5 v03 PNGs and their 5 `.import` files under `game/assets/environments/yonkers-antenna-room1/` and `game/assets/props/yonkers-antenna-room1/`.
- The 3 tools: author `.py`, Godot check `.gd`, gate `.py`.
- From `outputs/yonkers-room1-v03_15709be4/`: manifest, `.pxo`, `.ora`, flat PNG, Godot log, gate report, accepted-room replay log.
- 6 of the 30 captures: zh/en `entry`, zh `entry-runtime-heroine`, zh `b-dish-from-lane`, zh `occlusion-behind-a`, zh `returned-from-room2`.
- The QA note.
- Prerequisite for the gate's L1 layout check: the v02 manifest and the v02 Godot log under `outputs/yonkers-room1-v02_c1f6a38e/`.

**Female battle static v12, nonruntime:**
- the PNG, `.pxo`, `.ora` and manifest under `game/assets/characters/combat-sideview-pilots/`;
- the 3 tools;
- the 4 captures and their 4 capture manifests;
- the QA note.

**Global map v03r2, plus the v03r1 prerequisite (runtime map art):**
- `game/scripts/scifi_world_map.gd` and `game/scripts/world_map_data.gd`. Whole files; they hold v03r1 and v03r2 changes only.
- The v03r2 relief JSON.
- `game/tests/…background-visual-check_m8-v01_20261014-143900-239f6b80.gd`, the v03r1 rewrite.
- The 3 v03r2 tools and the v03r1 zoom tool.
- From v03r2: capture manifest, checks JSON, source-check JSON, regressions log, before-run log, and the 5 zh captures.
- From v03r1: capture manifest, checks JSON, regressions log, the 4 before/after logs, and the v03r1 QA note.
- The v03r2 QA note.
- Optional: the Codex v03r1 judgment `…66d8a7b4.md`.

The full list of 80 paths is the set of entries in the evidence index whose `proposedStage` is not `false`, plus this note and the index. Unstaged files stay hash-pinned in the index:
- Yonkers: 24 captures and the 8 `acc/` replay captures;
- map: the en captures and the v03r1 captures;
- the dispatches;
- the session log.

### 3. Explicitly excluded

- **`game/scripts/battle_arena.gd`.** v12's captures need its uncommitted `arena_override` band, but the file also carries other workstreams' hunks (Zhao combat frames and more). v12 stays nonruntime, and its captures are not clean-clone reproducible, as the v12 note already says.
- **Other workstreams' dirty files:**
  - `scifi_exploration_area.gd` (City Hall v05/v07, outskirts fixtures);
  - `growth_*`, `docs/progress.md`, the app/server JS, the readiness checklist;
  - the Chicago placeholder `.gd`;
  - the Chicago Loop `.tscn`. Another session switched it to a v04 selector at 23:13 EDT, during this task.

## Tests

On the **proposed index state**, in a temporary HEAD worktree with only the files above plus the patch; the worktree was then removed:

| Test | Result |
|---|---|
| meter CLI `check` | CHECK OK 40.8% (last closeout e63be377) |
| Bible builder `--check` | contentEqual, bytesEqual, 33 canon checks |
| review-queue check | RESULT PASS (new stale-text pass line included) |
| mvp-completion-meter check | RESULT PASS (7 checks) |
| builder canon-reconciliation check | RESULT PASS (5 checks) |
| m2-global-travel gates check | RESULT PASS (5 checks) |
| character-readiness view check | RESULT PASS (7 checks) |
| selout-v2 review card check | RESULT PASS (14 checks) |
| site preview-figures check | SITE_PREVIEW_FIGURES PASS |

On the **current working tree**:
- The meter check, the meter test and builder `--check` pass.
- The review-queue check passes the new correction assertions. It then fails at #11, "the Loop scene runs the opt-in selector", because of the other session's 23:13 Chicago `.tscn` edit.
- The m2-global-travel check fails on the other workstream's uncommitted `nyc-public-facilities-room2-static-environment-baseline` approval.

Neither failure comes from this task's files, and both pass on the proposed index state.

## Consequences if the proposal is applied

- Yonkers room 1 (outskirts) plays the v03 art in the default runtime.
- The live world map draws v03r2 art.

Both stay UNAPPROVED. Scenes stay 3/12 and M2 stays 10/12, and the map-art gate stays open. v12 changes nothing at runtime.

## Process notes

- I accidentally ran the Bible builder in write mode (`--help` is not an option). It changed only `updatedAt`; I restored the file from HEAD before the real edit.
- Only temp files under `%TEMP%` and one temp worktree, since removed, were created outside the repo.
- No Godot, Pixelorama or Python process was started.
