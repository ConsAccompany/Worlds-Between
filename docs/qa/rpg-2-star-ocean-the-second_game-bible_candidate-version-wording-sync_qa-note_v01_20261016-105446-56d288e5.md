# Game Bible candidate-version wording sync: City Hall Park v01–v02, Washington walkable v01–v05

- Status: wording/receipt sync only. No art, gameplay, gate status or counter changed. Sprites 0/52, scenes 0/11, human playtests 0/2, M2 9/12 and the 35.0% meter are unchanged. No candidate is accepted or wired into the runtime.
- Trigger: `main` f02adcd committed the unapproved, nonruntime NYC City Hall Park walkable pilot v02 (run 59848a60) and Washington Capitol West walkable camera v05 (run ca6ec5f1). The tracked state text still named City Hall Park v01 only and Washington walkable v01–v04, so the cloud Site was stale.

## Corrections

1. **Progress state** (`outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`). M2 remaining-item (en), M2 blocker remaining (zh) and the anchor gate detail (zh) now read: Washington walkable west grounds v01–v05, separate dome cinematic vista v01–v02, City Hall Park walkable pilots v01–v02; none accepted or in the runtime.
2. **Game Bible state** (`outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json`). The "MVP 美术技术路线" open question and `environmentVisualReview.washingtonDC.unapprovedCandidates` now list walkable v01–v05 (cinematic stays v01–v02). The v05 Codex audit (`docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-v05-codex-visual-audit_unapproved-v01_20261016-064427-00f04ea5.md`) was added to that record's evidence. `runtimeIntegrated`, `artAccepted` and `highPrecisionPixelSceneAuthored` stay false. The Bible carried no City Hall Park candidate-version claim, so none was added.
3. **Builder** (`tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js`). Canon check 25 hard-coded walkable v01–v04 and would have rejected the corrected state. Only its expected list and wording changed, to v01–v05. Every other condition (not runtime, not accepted, no "尚未制作") is unchanged.

## Independent Codex audits closed out (zero change)

- `closeout-20261016-105441-f6e8d8a2`: [NYC–Chicago air corridor visual audit](rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-corridor_visual-audit-unapproved-v01_20261016-064519-bb294d29.md). With Chicago selected, the route card names New York as origin but the map shows no origin marker or connection. Map art stays unapproved; M2 map-art gate stays open.
- `closeout-20261016-105441-fe3db0fb`: [Female battle static v05 identity/readability audit](rpg-2-star-ocean-the-second_protagonist-female_battle-static-v05-identity-readability-audit_unapproved-v01_20261016-064516-5c1f320e.md). Pack roll, emblem, collar/cuff and ponytail do not resolve at 0.65. The frame is an unapproved static candidate; sprites stay 0/52.

## Checks

- Builder `--check`: contentEqual true, bytesEqual true, 25 canon checks.
- Meter `check`: CHECK OK 35.0%; sprites 0/52, scenes 0/11, human playtests 0/2; MVP accepted false.
- Tests PASS: builder canon reconciliation (5), M2 global travel (5), character readiness (7), selout v2 (14), meter (6).

## Limitations

- The captures each audit cites (map runtime captures run 49d78162 for the Great Lakes route card, the female v05 frame and its two party captures) are uncommitted local files from other workstreams. They were not committed here. The tracked evidence is the two audit notes.
- The hosted Site reads GitHub `main`; whether it shows the new wording must be checked on the live Site after push.
