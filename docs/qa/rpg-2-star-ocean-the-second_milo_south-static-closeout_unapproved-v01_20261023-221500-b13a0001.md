# Milo south native static — independent production verdict

Canonical task: `content.char.milo.static-south`. Coordinator: Hermes. Producer: Claude via the authorized provider adapter only (prior attempt 12 authored the package; batch 13 adapter session rechecked it without source edits). Recorded 2026-10-23T22:14:21Z. Base/tested revision `d539a85508a471db0077a93d20ba72231b477943` plus the exact new files below. Hashes are SHA-256 of raw bytes; no text normalization. Filename tag is a batch identifier, not the exact execution time.

## Verdict and scope

PASS for the existing source-production criterion, conditional on the scoped source commit. Native 80×112 south PNG with opaque body rows 8–103 (96 source pixels at scale 0.5 = 48 logical pixels), pivot (40,104), layered PXO and ORA, declared palette, manifest, reproducible existing-pipeline author and independent checker are delivered. The rejected 32×48 placeholder is neither changed nor credited.

This is NOT runtime integration, normal actor assignment, full art approval, motion approval or a human playtest. The unapproved asset directory retains `.gdignore`; existing defaults, game configuration, scoring denominators, thresholds and creator gates are unchanged. Native application-clean status is FAIL, not waived; export equality is a separate source-format check. No inspection/creator task is credited by this batch.

## Raw source pins

- PNG `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-static_unapproved-v01_20261023-215823-28a012bd.png`: `3822b31805729f3091a61b3e073ade723f613049db4622364dc162a5101fa473`.
- PXO `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-edit_unapproved-v01_20261023-215823-aaf32a0b.pxo`: `400c634f35c8aa43cce6ddf607968ac9a8041edd7c5caf4b582083164004c51f`.
- ORA `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-edit_unapproved-v01_20261023-215823-e1afaba2.ora`: `1545d66ca66296e44d37466526f262431a03740f93b8935161dd91408de56b2c`.
- Full asset, capture and log pins: `outputs/milo65/independent13/rpg-2-star-ocean-the-second_milo_independent-verification_v01_20261023-221500-b13a0001.json`.
- Producer contract, editable roles, deviations and historical failures: `outputs/milo-s01/rpg-2-star-ocean-the-second_milo_south-static-qa-note_unapproved-v01_20261023-215823-51a12dd6.md`.

## Independent reruns

1. Existing Milo author `check`: exit 0, `MILO_SOUTH_V01_ALL_OK`, 9 isolated texels, 35 colours, 11 contributing visible roles, deterministic rebuild, all five files match. Raw reused-tool pins pass. Log `outputs/milo65/independent13/author-check.log`.
2. Existing independent Milo checker: exit 0, `MILO_S01_INDEPENDENT 29 / 29`, failures empty; includes corrupted-hash, tampered-PNG and visible-guide negative controls. Output `outputs/milo65/independent13/source/` and `source-check.log`. Checker does not import the author; it reuses the established ORA reader.
3. Fresh Pixelorama PXO and ORA exports, Dummy audio and 120-second subprocess deadlines: exit 0 each; independent decoded RGBA comparison is exact (80×112, zero differing pixels). Export PNG hash is `2449291595b4684100ace8eabb28360f08bc782ad8367b7d66912bea9161ef26` for both; byte difference from authored PNG is encoding, not pixel change. Original native files unchanged. Logs and exports: `outputs/milo-s01/logs/independent13-pxl/`.
4. Existing generic `native-static_scene-fit-capture` through checked runner under Xvfb, Dummy audio, OpenGL, 110-second deadline: exit 0, `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS`, 4.039 seconds. Log `outputs/milo65/independent13/fit.runner.log`. Four EN/ZH city/ruins captures and source-hash manifest in `outputs/milo65/independent13/fit/`; all declared hashes checked. Historical marker name is unchanged. This harness sets its own test viewport to 640×360 without changing project settings.
5. Unchanged normal game baseline M1 through checked runner, headless, Dummy audio, 60-second deadline: `M1_SMOKE_OK`, exit 0, no runtime diagnostics. Log `outputs/milo65/independent13/smoke.runner.log`. This is targeted regression evidence, not the full pre-playtest suite.

## Visual observations, not acceptance

Hermes viewed the actual source and all four independently rendered captures. White/grey coat, square case on screen left, navy clothing and bright green screen-right wristband are visible. The silver hair patch and small green accents are clearer in the source than at gameplay scale. The medicine-case cross remains partially obscured by the hand; face/case details are tiny at half scale. Both English and Chinese test labels render. The white coat stays identifiable against city and ruins backgrounds.

These are static overlays at a fixed screen position, not Milo-controlled gameplay. The ruins captures are daylight exterior views, not dark-context evidence. The overlay does not validate collision, occlusion, sorting, interaction, actor assignment or motion. No artistic acceptance is inferred from metrics or these captures.

## Retained failures and limitations

- Prior author check failed isolated-texel threshold: 97 vs maximum 24; producer fixed drawing noise rather than relaxing gates. Prior check2 failed absent disk outputs. Both exact logs remain under `outputs/milo-s01/logs/check1` and `check2`.
- Pixelorama repeatedly reports four `custom_samplers` shader errors; ORA additionally reports dummy-texture/resource/ObjectDB leaks, child-index bounds errors, null `rp_node`, and scroll-container ancestor error. Preserved in old and independent export logs. Therefore application-clean check remains FAILED despite exact source exports. Milo-specific GUI SaveAs/reopen is UNVERIFIED. No clean-native-app claim is made.
- Godot fit emits an unsupported V-Sync warning only; no `SCRIPT ERROR` or `ERROR:` lines. Checked runner passes. No full gameplay integration is claimed.
- Adapter returned process exit 0 but classified batch 13 as `permission_denied` due to three denied shell commands. Provider continued using permitted Python and produced the logs. Coordinator treated this as an operational failure, not a pass receipt, and reran required checks independently. Account/usage records remain outside Git. No paid fallback or alternate provider was launched.
- Producer note's final statement that all of `outputs/milo65/` was untouched is stale: it wrote `provider13/` there. Its pre-existing independent baseline log and unrelated `outputs/ldisplay64/` were preserved.
- Initial staged whitespace check failed on a printed trailing space in each of the three frozen `diag1/diag2/diag3` logs. Their raw bytes were preserved; a narrowly scoped diagnostic-log attribute excludes end-of-line whitespace checking for those logs only. Source/test thresholds were not changed.

## Integration and meters

Commit the explicitly reviewed source, checks, retained QA failures and independent evidence first; compare every staged blob to the tested raw working bytes. Then credit only this existing 3-point task through the audited ledger CLI and finish the existing Bible task-progress record. The source commit is recorded by the Bible closeout and ledger note, not embedded self-referentially here.

Canonical displayed production before 61.1% → after 61.1% (+0.0 percentage points at the ledger's one-decimal precision); content points 660 → 663 of frozen 1881. Unrounded gain is 0.09569377990430622 percentage points. Inspection 21.6% → 21.6%; creator approval 7.8% → 7.8%. No new task/version points.

Next bounded production item: Milo west native static under its existing ledger criterion, only after this source boundary is committed. Remaining art review, other directions, animation and runtime adoption retain their existing gates. Hosted Site publication is unavailable on this VM and is not claimed.
