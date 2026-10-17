# Game Bible: stale prose and tests reconciled with the three recorded scene acceptances

Date: 2026-10-17. Base: `6859db1`. Zero-change closeout `closeout-20261017-211200-2e483288` (40.8% → 40.8%). **No new acceptance is granted.**

## Source of truth

- `approvalLedger` in the MVP progress state at `6859db1`: counters sprites 0/52, scenes **3/12**, playtests 0/2. The three accepted `scene-visual` items each have 1 unit:
  - `nyc-public-facilities-room2-scene-visual-accepted`: `docs/qa/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_scene-visual-acceptance_v01_20261017-010900-8f4a2c6e.md` (1/12).
  - `nyc-public-facilities-room1-scene-visual-accepted`: `docs/qa/rpg-2-star-ocean-the-second_nyc-public-facilities-room1_scene-visual-acceptance_v01_20261017-013027-3e7d91c4.md` (2/12).
  - `yonkers-maintenance-room2-scene-visual-accepted`: `docs/qa/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_scene-visual-acceptance_v01_20261017-013504-6a0c92d1.md` (3/12).
- Each record accepts **environment quality only**. None of them accepts character motion, a runtime sprite, another scene or either human playtest. Formal MVP acceptance stays false.
- The acceptance commits (`cb2027a`, `cf52349`, `aabbe76`) updated only the progress state. They did not update the Bible, its prose or the tests.

## What changed

- **Game Bible state:**
  - `environmentVisualReview.sceneQualityAccepted` changed from 0 to 3. `artAccepted` stays false.
  - The `status` sentence "Scene visual acceptance remains 0/11" and the claim that the Loop is "a code-drawn placeholder" now name the three accepted rooms. They also name the candidates, all unapproved:
    - Chicago Loop State/Lake v02 and WDC survey annex room 1 v02: runtime visual candidates, pushed `00199fc`.
    - City Hall Park: walkable pilots v01–v04; v05 is a test candidate; v06 is being built separately.
    - Capitol exterior: walkable v01–v08 and dome vista v01–v02, not in the runtime.
    - Runtime map: native v01r1 (`06107c8`). Map v02 is being built separately.
  - The open question on the runtime geography migration now reads "still to accept" ("仍待验收") with those candidates, instead of "still to make" ("仍待完成").
- **Progress M2 text** (summary, blocker, details[3], remaining art/map, gates anchor / map-art / visual-review):
  - "art does not exist", "美术未制作" (art not made), "地图美术未制作" (map art not made) and "场景画质 0/12" (scenes 0/12) are replaced by the unapproved-candidate wording and by scenes 3/12 (three interior rooms, environment only).
  - The text states that the three rooms are not City Hall Park, the Capitol exterior or the Loop.
  - Gate statuses are unchanged: map-art `not_started`, visual-review `human_pending`, M2 10/12.
- **Builder canon check** (`tools/…game-bible-builder…`):
  - Before: `sceneQualityAccepted === 0`.
  - Now: the Bible count and `counters.sceneVisualsAccepted` must both equal the units of the accepted `scene-visual` ledger items, using the meter CLI's unit rule. Target 12; art not accepted.
- **Tests, compared with the source of truth:**
  - Canon reconciliation:
    - Counters now expect 3/12.
    - Asserts the exact three ledger ids, one unit each, their acceptance records and the exclusions in their scope.
    - Two mutations are rejected: the Bible count set to 4, and reset to the stale 0.
  - M2 travel gates:
    - The scene counter must equal the accepted ledger units (exact three ids), and the Bible must equal the ledger.
    - The inventory must list the 12 gates and may not tick more scenes than were accepted.
    - The anchor must say "美术未验收" (art not accepted) and must not say "美术未制作" (art not made). Visual-review must say 3/12 and must not say 0/12.
    - No current M2 text may say the art does not exist or that scenes are 0/12. M2 text must name State/Lake v02, v05, v06 and 3/12.
    - The ledger card must render 3 / 12. The asset summary must render the inventory tally.
    - The server serves only `docs/`/`outputs/` .md/.png/.json evidence, and `game/scripts/survey_annex.gd` must answer 404. So one link is expected per servable cited file, and the only unlinkable cited file must be `survey_annex.gd`.
  - Meter: 40.8% = 20 + 8.33 + 7.5 + 0 + 5 + 0, with the 3/12 numerator backed by exactly the three items. Derived cases changed by +5 points from the scenes:
    - map art: 41.7%
    - pacing: 44.2%
    - reopen M4: 36.8%
    - one sprite: 41.3%
    - the /11 baseline fixture is now 3/11 → 3/12 at 40.8%.
  - Review queue: the Bible scene count must equal the ledger instead of 0.
- **Ledger:** one zero-change receipt, appended to the `6859db1` progress blob and staged index-only. The working copy got the same text edits and the identical receipt. Its other 12 local-only receipts and the local static-baseline item remain unstaged.

## Verification on the exact staged tree (temp worktree at `6859db1` + staged index)

- Canon reconciliation: PASS (5 checks; 33 canon checks; 15 mutations rejected).
- Builder `--check`: content and bytes identical.
- M2 global-travel gates and Production view: PASS (5).
- Meter: PASS (7). CLI `CHECK OK 40.8%`.
- Cross-device review queue: PASS (6). The v11 queue entries #7/#8 are intact.
- Character readiness: PASS (7).
- selout-v2 card: PASS (14).
- Site preview figures: PASS.

Counters unchanged: 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2.

## Remaining gaps (documented, not changed here)

1. **Inventory checkboxes still read 0/12.** The `visual-scene.*` checked flags are user-controlled in the Assets view. `visual-scene.city-survey-outer`, `city-survey-inner` and `outskirts-survey-inner` are the rows for the three accepted rooms. The Production asset summary and the Assets view therefore still show 场景画质 0 / 12 next to the ledger's 3 / 12.
   Ticking them is the creator's action, or a separately authorized task. That task must also refresh the readiness checklist's inventory hash, and that checklist JSON and its .md twin have unrelated local edits. The character-readiness and selout-v2 tests, and the local untracked enemy-pilot and environment-candidate tests, pin the inventory 0/12 and would change with it.
2. **App source not touched (out of scope).** It still has hard-coded legacy copy: "场景画质仍为 0/11" (scenes still 0/11) in the selout cards, and "11 项场景画质" (11 scene gates) in the M8 plan line. The approval card's fixed badge "验收数未增加 · No counter incremented" now sits next to 3 / 12.
3. **Dated snapshots kept as history:**
   - `creatorDecisions.counters` (2026-10-15, 0/11)
   - `staticBaselinesAndPilots.counters` (`15c9b73`, 0/11)
   - `sceneQualityDenominatorReview.meterImpact` (2026-10-16, 35.8%)
   - older closeout receipts at 35.8%
   - The M8 step's narrative counters (0/11) are outside the M2 scope of this task and were left unchanged.
4. **`game/scripts/survey_annex.gd`** is cited by the three acceptance items. By server policy it is shown without a link.
5. **City Hall Park v05 is local only.** Its QA note is untracked. No path to it is linked from the Bible or progress state.
