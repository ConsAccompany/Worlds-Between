# Heya EAST walk/run + phase-aware stops — provider receipt (UNAPPROVED)

- Task: `content.char.heya.walk-east` (batch 176, run `h176ew01`).
- Status: source production boundary only. **No canonical completion, commit, ledger credit, inspection/approval credit, runtime adoption or art approval is claimed.**
- Scope: new files only under `outputs/heya-ew176/`, `game/assets/characters/heya-native-v01/east-walk/`, and `tools/rpg-2-star-ocean-the-second_heya_walk-east*`. No pre-existing project asset was replaced; three metadata files inside this run's fresh output were replaced through `tools/wb_safe_replace.py` with verified backups. Git index/commits and shared ledger/Bible/registry were not touched.
- Exact changed-path list and per-file hashes: `outputs/heya-ew176/provider-receipt.json` (`changed_paths`, `output_hashes`, `package_hashes`).

## Tools (raw SHA-256 and text_lf_v1)

- `tools/rpg-2-star-ocean-the-second_heya_walk-east-independent-check_v01_20261024-154500-h176ew01.py` — raw `83eaa9129c3857242697231627681ebd98f77de7bea67cc9a1caf6d948ca8727`, text_lf_v1 `83eaa9129c3857242697231627681ebd98f77de7bea67cc9a1caf6d948ca8727`
- `tools/rpg-2-star-ocean-the-second_heya_walk-east-source-author_unapproved-hew176-v01_20261024-154500-h176ew01.py` — raw `9f11b70d382c529cb9a3ebbecc9f8e246ba53b4e1dbae5df87e33257d0f2e20a`, text_lf_v1 `9f11b70d382c529cb9a3ebbecc9f8e246ba53b4e1dbae5df87e33257d0f2e20a`
- `tools/rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-fit_test-only-v01_20261024-154500-h176ew01.gd` — raw `9eece6e8807d9f33a562c8d6219306025580eb96d12e42000b329bbd26dbf3c4`, text_lf_v1 `9eece6e8807d9f33a562c8d6219306025580eb96d12e42000b329bbd26dbf3c4`
- `tools/rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-fit_v01_20261024-154500-h176ew01.py` — raw `9498ed3e9253bfeead276fd9b637819c7d8928e5786e5a39c4424d736ecbde58`, text_lf_v1 `9498ed3e9253bfeead276fd9b637819c7d8928e5786e5a39c4424d736ecbde58`

Text normalization: `sha256_text_lf_v1` = SHA-256 after CRLF→LF and lone CR→LF; PNG/PXO/ORA/JSON are raw byte hashes. The source manifest declares this normalization.

## Deterministic rebuild and independent source checks

- Author `build`: `WROTE 91 files`; `REBUILD 91/91 DETERMINISTIC True`; `SOURCE 21/21`; `RESULT PASS`.
- Independent checker: `36/36 PASS`; `15/15` negative controls rejected. Output: `outputs/heya-ew176/independent-3/`.
- Native Pixelorama headless export: `41/41` frames RGBA-exact, exit 0, no timeout. **Application-clean gate FAILS separately with 4 `custom_samplers` shader diagnostics; GUI SaveAs/reopen is UNVERIFIED.**

## Contact / slip (retained honestly)

- `walk_max_world_slip_src_at_40ms_boundaries`: `0.8`
- `walk_max_world_slip_logical_at_40ms_boundaries`: `0.4`
- `walk_planted_foot_world_excursion_src_60fps_samples`: `10.667`
- `walk_planted_foot_world_excursion_logical_60fps_samples`: `5.333`
- `flight_phases`: `[4, 5, 10, 11]`
- `grounded_phases_each_foot`: `[4, 4]`
- `stop_bridge_grounded_slip_src_max`: `0.0`
- Held-frame slip is real and retained: the planted foot travels with the moving host 11.2 source / 5.6 logical px per 40 ms held frame (10.667 src / 5.333 logical excursion over 60 fps samples). NOT footlocked and NOT slip-free. Stop bridges are host-stopped and show zero grounded slip. No threshold was weakened.

## Phase-11 stop/start/repress continuity

- `derived_forward_prestop_phase`: `11`
- `selected_bridge`: `phase11`
- `forward_prestop_equals_selected`: `True`
- `reverse_prestop_equals_selected`: `True`
- `forward_stop_endpoints_continuous`: `True`
- `reverse_stop_endpoints_continuous`: `True`
- `capture_sequence_continuous`: `True`
- `hardcoded_phase7_used`: `False`
- The fit derives the entry phase from frozen timing (`STOP_MS-1`), selects `phase11`, and asserts pre-stop == bridge entry == restored walk frame. No hardcoded phase 7 is used.

## Bounded Godot fit and M1

- Test-only Godot fit: PASS, 12 captures, 2.959 s, Dummy audio, OpenGL3, Xvfb 640x360. Proof: `outputs/heya-ew176/fit/capture` and `outputs/heya-ew176/fit/`.
- Fit is not normal-host integration and does not establish default adoption.
- M1 generic headless smoke: `M1_SMOKE_OK`, `CHECKED_RUN PASS`, exit 0, 0.671 s; log `outputs/heya-ew176/m1-smoke-r2.runner.log`. This does not prove the east-walk package is integrated.

## Neutral endpoint + east-specific identity

- Existing four-direction idle east f00 `game/assets/characters/heya-native-v01/idle/east/rpg-2-star-ocean-the-second_heya_idle-east-f00_unapproved-i159-v01_20261024-140235-a159i001.png` is byte-equal to the east static neutral (`273e5e854121fa8ec92dc74e28a67be35920da6442fc20571ff053453fdf9dd4`). All 12 stop bridges end on that exact neutral/static footprint (independent checker).
- East is not an unverified horizontal mirror: exact RGBA diff vs flipped west walk has a minimum of **1261 changed texels** across 12 phases ([1372, 1314, 1314, 1378, 1382, 1398, 1379, 1286, 1261, 1359, 1372, 1383]).

## Fit provenance

- Fit py/GD adapted from the repaired north-fit pattern (derives pre-stop phase) rather than the west fit, which hardcoded phase7. The west author/checker were reused; the phase-11 derivation was preserved from the north repair.

## Safe replacements (metadata-only rebuild)

- Only the source manifest, file-list and build check-result changed (text/tool-hash metadata). All 41 PNGs, PXO/ORA and runtime/package JSON bytes were unchanged; the three differing destinations were replaced through tools/wb_safe_replace.py with verified backups.
- `outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-source-manifest_unapproved-h176ew01-v01_20261024-154500-537dec83.json`: before `63e83bcd30dcaeb728935f0c824a76f6ff36ca6186590306d5921f998c72998f` → after `f46220dea0b4f403641e81eeab32f0a99b1c8bef3ff8b7bec4a55c6d85544d43`; backup `outputs/development-backups/dec99f201f804976b2c0e71615a69752/original`.
- `outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-file-list_unapproved-h176ew01-v01_20261024-154500-d27681ce.json`: before `a3a5be45c746d09240058dff11d11737a3c46cf01e0f856e71ae1d8cd25f4ae5` → after `5ca31b86242e37d34f8af27f646a6e47058f941cd008e9835f97df9680fe268a`; backup `outputs/development-backups/e4ddffcec4cb45639febfa7d825ab016/original`.
- `outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-check-result-build_unapproved-h176ew01-v01_20261024-154500-54687ffd.json`: before `1b39aa708167497397b24235860681f2e2622dc7e1a860cf904a5668013f309a` → after `e67293c694d073331a60ab7faca358743dbb525dd4cd04aee7f14ccfae412322`; backup `outputs/development-backups/a93ef847b13e4d98acb09bfc30c48383/original`.
- Fresh staging outputs/heya-ew176/staging-r2 built 91 files deterministically; 87 identical, 3 metadata files replaced through wb_safe_replace.py; independent-3 then passed 36/36 with 41/41 native export equality.

## Original failures retained

- **first generated author import**: `AttributeError: module 'wb_heya_east_static_v01' has no attribute 'EAST'` — cause: adapter typo W.EAST from broad direction rename; fix: pin assertion changed to W.WEST; no input modified.
- **author build after pin fix**: `FileNotFoundError: .../game/assets/characters/heya-native-v01/east/rpg-2-star-ocean-the-second_heya_east-static_unapproved-v01_20261024-131500-22034c8f.png` — cause: stale west NEUTRAL block survived the first adapter generation; fix: NEUTRAL/NEUTRAL_NATIVE block replaced with installed east pins.
- **first independent checker run**: `FAIL exactly one source manifest [] then IndexError at mrel = mans[0]` — cause: author VAR still unapproved-hww167-v01 so manifest filename did not match checker prefix; fix: VAR set to unapproved-h176ew01-v01; prevar outputs tar-backup and fresh rebuild.
- **independent checker native step**: `FileNotFoundError: .../Pixelorama-Linux-64bit/Pixelorama` — cause: Pixelorama executable is Pixelorama.x86_64; fix: PIXELORAMA set to Pixelorama.x86_64; source/negative checks had already passed.
- **first M1 smoke**: `ERROR: Failed to open 'user://logs/godot2026-10-24T15.26.50.log' ... CHECKED_RUN FAIL diagnostic exit=-9 missing ['M1_SMOKE_OK']` — cause: no writable session-local HOME/XDG dirs; fix: session-local HOME/XDG under outputs/heya-ew176/godot-home; retry passed.

## Backups

- `outputs/heya-ew176/backups/east-walk-prevar_20261024-154500.tar.gz` — raw `b00d723563019c3b452d950736b4b38aff082b2251428609111034b1d972e689`, 69364 bytes.
- `outputs/heya-ew176/backups/heya-ew176-prevar_20261024-154500.tar.gz` — raw `8a029759dc16329cccd3b2ac0f7a90b1fb2e130548bf4a6afcd26d80728c3f7b`, 114310 bytes.
- The first build (wrong VAR hww167) was tar-backed up under outputs/heya-ew176/backups before removal, and tar listings were verified (49 and 48 entries). Per-file extraction comparison was not rerun; these were freshly generated by this run, not pre-existing project bytes, and no pre-existing asset was replaced.

## Limitations / not claimed

- Pixelorama application-clean gate is separate and FAILS with 4 custom_samplers shader diagnostics; exact headless export equality passes 41/41; GUI SaveAs/reopen is UNVERIFIED.
- Held-frame slip retained (not footlocked, not slip-free); see contact_slip.
- Single 12-phase cycle serves walk/run at host normal speed; no separate run cycle.
- A-line dress hem is torso-only and not lifted; lifted boots can pass behind the static hem (static-texel limit, disclosed).
- Braid/scarf/coat/apron/bag ride head/torso with no secondary motion.
- Godot fit is a test-only overlay with Dummy audio/OpenGL3, not ordinary actor integration or normal-host proof.
- M1 is a generic normal-game smoke, not evidence that the east-walk package is integrated or adopted.
- No default/runtime adoption, no save/reload, no human art/motion approval, no creator playtest.
- Label text clips at the right viewport edge and state-label contrast is weak in the test capture.
- Not claimed: canonical task completion; scoped commit or staged-byte verification; audited ledger transition; production percentage increase; inspection/approval credit; normal-host integration; default adoption; human art or motion approval.

## Exact independent rerun

- build: `/home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-east-source-author_unapproved-hew176-v01_20261024-154500-h176ew01.py build`
- deterministic_check: `/home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-east-source-author_unapproved-hew176-v01_20261024-154500-h176ew01.py check`
- independent: `PIXELORAMA=/home/kel/projects/worlds-between/tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64 /home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-east-independent-check_v01_20261024-154500-h176ew01.py --out outputs/heya-ew176/independent-recheck`
- fit: `/home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-fit_v01_20261024-154500-h176ew01.py`
- m1: `HOME=$PWD/outputs/heya-ew176/godot-home/home XDG_CONFIG_HOME=$PWD/outputs/heya-ew176/godot-home/config XDG_DATA_HOME=$PWD/outputs/heya-ew176/godot-home/data XDG_CACHE_HOME=$PWD/outputs/heya-ew176/godot-home/cache XDG_RUNTIME_DIR=$PWD/outputs/heya-ew176/godot-home/run TMPDIR=$PWD/outputs/heya-ew176/godot-home/tmp /home/kel/projects/worlds-between/tooling/venv/bin/python -B tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 60 --expect M1_SMOKE_OK --log outputs/heya-ew176/m1-smoke-r2.runner.log -- /home/kel/projects/worlds-between/tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64 --headless --audio-driver Dummy --path game --script res://tests/m1_smoke.gd`

Run from `/home/kel/projects/worlds-between/repo`. The fit tool chooses a fresh `capture-rN`; the checker requires a new `--out` directory.

## Current blocker

- None at the source-production boundary. Coordinator still required: inspect/diff these new files, rerun the exact commands, verify staged bytes, make the scoped commit, perform the audited ledger transition, and request creator art/motion review. No commit or integration was performed here.
