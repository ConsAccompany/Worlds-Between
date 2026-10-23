# M7 smoke repair — Claude report (2026-10-23)

Worker: Claude Code. This is a report only. For this report I edited no game files and ran no Godot tests. The previous bounded repair session ran out of turns after it patched `game/tests/m7_smoke.gd`. All evidence below comes from the logs and diff that exist now.

## Scope / state
- Base: `8a00eeaf` (the receipt records `testedBase` 8a00eeaf9e302fc538aad0daf6f48515cc177901).
- Changed by this repair: `game/tests/m7_smoke.gd` only. sha256 `74542ad80660b364cd96f15d4481fb414d29889947028fbbca64b39f0703cd2f`, which matches the receipt's `sourceSHA256`.
- Runtime unchanged: `git diff --stat` shows only `game/tests/m7_smoke.gd` and `outputs/...game-bible_state_v01_20261013-195422-b8c16d42.json`. The Bible JSON was already modified at session start, and this repair did not touch it. Nothing under `game/scripts`, scenes, assets or defaults changed.

## Sequence (log evidence)
1. **Original RED** `m7-red_20261023-unmodified-8a00eeaf.log` (sha256 0f19f5aa…44ae86): unmodified test at 8a00eeaf → `ERROR: M7 smoke check failed: field station opens scifi.ruins`. Cause: the ordinary default now loads the v12 Capitol-west ruins. Its survey, records, NPC and assist anchors differ from the test's legacy hard-coded coordinates `(320,250)`, `(200,145)` and `(548,142)`.
2. **Initial preload compile error** `m7-red2_20261023-dialogue-assert-legacy-coords.log`: `SCRIPT ERROR: Compile Error: Identifier not found: AppState` at `res://scripts/battle_arena.gd:339`. A `preload()` of the v12 area script compiled its dependency chain before the AppState autoload existed. Fix: the path is stored as `RUINS_V12_PATH` and loaded at run time with `load(...).get_script_constant_map()` inside `_run()`.
3. **Added recruitment guard RED** `m7-red3_20261023-dialogue-assert-legacy-coords.log`: `M7_RUINS_ANCHORS legacy` then `ERROR: M7 smoke check failed: ruin recruitment dialogue opens` (m7_smoke.gd:127). The new `_recruit_dialogue_ready()` guard checks `dialogue_open`, `dialogue_mode == "recruit"`, overlay visible and invite button enabled. It now runs before each `invite_button.pressed.emit()` for city, outskirts and ruins. A test that stands at the wrong spot can no longer pass by emitting the button signal directly. Note: this log says `legacy`. In that iteration the v12 check had not detected v12, or had not been wired yet. The log alone does not show which.
4. **Direct prop-anchor failure** `m7-green_20261023-v12-anchors.log`: `M7_RUINS_ANCHORS v12`, recruitment passes, then `ERROR: M7 smoke check failed: survey returns to entrance` (m7_smoke.gd:250 backtrace). Standing exactly on the raw `V12_*` constants failed. Those constants mark props, so the hero was not on a walkable foot position. The return/entrance interaction did not complete.
5. **Final walkable-anchor GREEN** `m7-green2_20261023-v12-walkable-anchors.log` (sha256 0439ceea…b33cd7), verified: `M7_RUINS_ANCHORS v12` twice (both routes), two `PLAYTEST_RECEIPT` lines, then `M7_SMOKE_OK`. No ERROR or SCRIPT ERROR lines. Fix: every ruins anchor (`V12_SURVEY`, `V12_RECORDS`, `V12_NPC`, `V12_ASSIST`, `V12_TRACES[0..1]`) goes through the area's existing `_v12_safe()`. That function picks the nearest walkable mask point with a deterministic ring search (v12 script lines 289+). The test then stands there, as a player would. The legacy coordinates stay as the fallback when `v12_active` is false.

## Commands
- My original repair-session commands are not recorded in these logs, so I won't reconstruct them.
- The coordinator's independent receipt `independent-receipt-20261023-054232.json` records the form: `godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64 --headless --audio-driver Dummy --path repo/game --script res://tests/m7_smoke.gd`.

## Coordinator independent run (for reference, not my evidence)
- Accepted: original-red (expected failure reproduced, same log hash 0f19f5aa…), recruit-negative (expected `ruin recruitment dialogue opens`), m7-green, m1, city-navigation, city-reentry.
- **Not accepted:** `m8_city_integration_smoke.gd` → `CITY_INTEGRATION_FAILED: native pixel actor male` (line 69), missing `M8_CITY_INTEGRATION_OK`. `allAccepted: false`. I have not investigated whether this predates the M7 change. The diff touches only m7_smoke.gd, so it is probably unrelated, but that is not verified.

## Limits
- Test-only repair. It shows the M7 path works with the v12 ruins default. It is not art, motion or creator approval of v12, which is still labelled unapproved/opt-in-selector in its filename.
- `_v12_safe` comes from the runtime under test, so the test trusts its walkable search. The legacy fallback branch is exercised only by the negative fixture, not by the current default.
- No QA or ledger points are claimed. No ledger, Bible, registry, Git index, defaults, assets, accounts, commits, pushes, workers or schedules were touched.
- Creator dependencies remain: artistic and scope acceptance of the v12 ruins and of the overall MVP path.
