# Game Bible: inventory scene rows and app labels reconciled with the three recorded scene acceptances

Date: 2026-10-17. Base: `76f4b07`. Zero-change closeout `closeout-20261017-212408-75d23aab` (40.8% → 40.8%). **No new acceptance is granted.**

This closes gaps 1 and 2 left by `docs/qa/rpg-2-star-ocean-the-second_game-bible_three-scene-acceptance-stale-prose-and-test-reconciliation_qa-note_unapproved-v01_20261017-211048-1e6fcfd1.md`. Before this change the Production asset summary and the Assets view showed 场景画质 0 / 12 (from the inventory checkboxes), next to the ledger card's 3 / 12.

## Source of truth (unchanged)

`approvalLedger` in the MVP progress state: sprites 0/52, scenes **3/12**, playtests 0/2. Its three accepted `scene-visual` items, one unit each, accept **environment quality only**:

| Ledger item | Room | Inventory row | Record |
| --- | --- | --- | --- |
| `nyc-public-facilities-room2-scene-visual-accepted` | NYC public facilities room 2 (`scifi.city` room 2) | `visual-scene.city-survey-inner` | `docs/qa/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_scene-visual-acceptance_v01_20261017-010900-8f4a2c6e.md` |
| `nyc-public-facilities-room1-scene-visual-accepted` | NYC public facilities room 1 (`scifi.city` room 1) | `visual-scene.city-survey-outer` | `docs/qa/rpg-2-star-ocean-the-second_nyc-public-facilities-room1_scene-visual-acceptance_v01_20261017-013027-3e7d91c4.md` |
| `yonkers-maintenance-room2-scene-visual-accepted` | Yonkers signal maintenance room 2 (`scifi.outskirts` room 2) | `visual-scene.outskirts-survey-inner` | `docs/qa/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_scene-visual-acceptance_v01_20261017-013504-6a0c92d1.md` |

The row mapping follows the records: room 1/room 2 of `scifi.city` are the archive outer/inner survey rooms; room 2 of `scifi.outskirts` is the relay inner survey room.

## What changed

- **Asset inventory** (`outputs/…asset-inventory_state…7d1e0a8b.json`): exactly those three rows now have `checked: true`, a note restating the environment-only scope, and `sceneVisualAcceptance` pointing at the record. No other row and no other field changed (`updatedAt` kept). The tally is now 场景画质 3 / 12; the other nine scene rows (map, city, outskirts, ruins, the outskirts outer and both ruins survey rooms, battle arena, Chicago Loop) stay unchecked.
- **Readiness checklist inventory lock**: `sources.inventory.sha256` (sha256-text-lf-v1) `7507ec9f…` → `13c3652e994cd16d2440c00e74207e92682053e1453a117a41a242f48eb44214`, and the same 16-character prefix in the `.md` twin. Only those two lines were staged; both files keep their unrelated local edits unstaged.
- **Game Bible app** (only these two phrases were staged; the file's unrelated local cards stay unstaged):
  - Approval card badge "验收数未增加 · No counter incremented" → "验收数只计已验收台账条目 · Counts only accepted ledger items".
  - The approved selout v8 card's exclusion "任何环境或场景画质闸门（仍为 0/11）" now says v8 does not count toward scene quality and that scene quality is 3/12 only from the three separately accepted interior environments.
- **Tests**:
  - M2 global-travel gates: the inventory tick count must equal the ledger units, the ticked rows must be exactly the three ids, each ticked row must cite its ledger record; the new badge is pinned and the old badge and v8 "仍为 0/11" must be absent.
  - selout-v2: inventory scenes `[3, 12]` and page counter 场景画质 3 / 12 (was 0 / 12).
- **Ledger**: one zero-change receipt (this closeout), appended to the `76f4b07` progress blob and staged index-only; the identical receipt is appended to the working copy. Other local receipts stay unstaged.

Not approved by this task: any character motion or sprite, City Hall Park, the Capitol, Chicago Loop, the map, WDC survey annex room 1, or either playtest. Counters unchanged: 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2.

## Verification

Run in a temporary worktree holding the exact staged tree (`76f4b07` + index):

- Builder canon reconciliation: PASS (5). Builder `--check`: content and bytes identical, 33 canon checks.
- M2 global-travel gates and Production view: PASS (5); ledger card 0/52 · 3/12 · 0/2, asset summary 场景画质 3 / 12.
- Meter: PASS (7); CLI `CHECK OK 40.8% (last closeout closeout-20261017-212408-75d23aab)` on both the staged and the working-copy state.
- Cross-device review queue: PASS (6); 8 images served byte-identical, including the two reviewed v11 captures (#7/#8, committed at `53a912f`).
- Character readiness view and server: PASS (7). selout-v2 card: PASS (14). Site preview figures: PASS.
- Content-hash portability (after a throwaway local commit, `PYTHON` set): PASS (5); the new inventory lock equals the LF blob hash.
- Readiness Python builder (check mode): its regenerated checklist differs from the committed one only by unrelated newly discovered character manifests (battle v06–v11, compact walk v01, Liang Xu v01); the inventory lock line is identical. That staleness predates this task and was not changed.

## Remaining labels left as dated history

- The selout v1/v2/v4/v5/v6 candidate cards and the idle-refine card say "场景画质仍为 0/11" as of their dates (2026-10-14/15); the M8 plan line says "11 项场景画质". These are historical candidate records, not current counters, and were not changed.
- Dated snapshots in the Bible and progress state (creatorDecisions 0/11, staticBaselinesAndPilots 0/11, 35.8% receipts) are history.
- Local untracked tests (`tests/game-bible-enemy-pilots/`, `tests/game-bible-environment-candidates/`) pin inventory 0/12 and were not changed or committed.
