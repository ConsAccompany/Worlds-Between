# Milo north static v01: source verdict after hand repair 1 (UNAPPROVED, not integrated)

Task `content.char.milo.static-north`, batch 38. Source production evidence only: no creator art approval, no runtime/default adoption, no actor integration, no motion claim. HEAD `9c2fc393`. Nothing staged or committed. West, south, ledger, Bible, registry, defaults and runtime untouched (every batch38 `summary.json` records `pinsUnchanged: true` over north + south + west + tools).

**Status: source gates PASS.** Author check `MILO_NORTH_V01_ALL_OK`; independent checker **41/41** with negative controls behaving as required; native Pixelorama PXO and ORA exports pixel-exact (0 differing texels); checked Godot fit `CHECKED_RUN PASS`. Native application diagnostics are non-zero and listed separately below; they are not an application-clean result.

The original failure remains on record unchanged: `docs/qa/rpg-2-star-ocean-the-second_milo_north-static-checkpoint_unapproved-v01_20261023-225642-1b612f93.md` (sha256 `5eca5124…8c3`, identical to its backup copy) and `outputs/milo-n01/logs/source1/` (proof `fedc94d5…fd6c`, 40/41, `north_case_screen_right` failed: 14 opaque texels at x≤22 in rows 63..76, limit <10, caused by the hanging screen-left hand at x 21..22).

## What changed (art, not tests)

The checker is unchanged: `tools/rpg-2-star-ocean-the-second_milo_north-static-source-check_v01_20261023-225642-1b612f93.py` sha256 `96d7aac23180bf5d1627bd2c02af050a32a134cbb69c5008ef427c0a1b88e2bf`, the same as at the failing run. Thresholds and contract were not edited.

Author `tools/rpg-2-star-ocean-the-second_milo_north-static-author_unapproved-v01_20261023-225642-1b612f93.py` went from `96bf480f…dcde` to `8453d78278e10accaff3b9a13a72203f87d58562d6d00b82dde502a4dd93dff4`. Its only change is to the arm loop. The screen-left hand (rows 63..69, below the wristband) is drawn at x 23..27 instead of 21..25, tucked against the hip. Forearm rows 58..62, the wristband, and the screen-right hand (x 55..59) are unchanged. That repair (named "repair 1") was made at 23:06 by an earlier interrupted run, which first moved the pre-repair package to `outputs/milo-n01/backup-pre-hand-repair_v01_20261023-repair1/` (`backup-manifest.json` lists sha256, size and mtime per file). That run left `build2`, `check2`, `source2`, `pxl2`, `compare2`, `batch34-*` logs, plus an incomplete `fit2/` (captures for city only, no `fit.log` or `summary.json`; interrupted). All of these are retained unchanged.

This batch found disk == deterministic rebuild for all 5 north files (`batch38-check`), so the generated files were **not** stale. No regeneration, overwrite or new backup was needed, and no source file was written in batch 38.

## Source (game/assets/characters/milo-native-v01/north/)

| file | sha256 (raw bytes, no normalization) |
|---|---|
| `rpg-2-star-ocean-the-second_milo_north-static_unapproved-v01_20261023-225642-5968ba0c.png` | `cf1e559885f2a87c31a3c6cf9feee953d95c8c1ca138ecd9bd8d6838bee8da61` |
| `rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-7f054cac.pxo` | `9d9004e65b032f68e06a0b064cf623c7996cdd7c679ef36d7c8a37ab0108baee` |
| `rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-af5a9058.ora` | `a7a691f63f3c776293cc6fede97b1895c7f48a961c3825a9d6368a1a426895cf` |
| `rpg-2-star-ocean-the-second_milo_north-palette_unapproved-v01_20261023-225642-a3a9c89f.json` | `e837c5f76ad17caa7d2b9c269cec261c4813dc2238d6297514ae3d3aaf02554d` (unchanged by repair) |
| `rpg-2-star-ocean-the-second_milo_north-manifest_unapproved-v01_20261023-225642-163cf811.json` | `0cb2b25f115117795dbc2788e9a2f448218c0899b8f2fc9929154ddb324402b1` |

The source is 80x112, body rows 8..103, 48 logical px at density 2. Pivot is (40,104), inside the feet span. It has binary alpha, a transparent border, and 31 colours, all from the palette shared with south (south files match their pinned manifest and the palette colours are identical). There are 11 genuine role layers, plus a hidden `guides` layer. Identity: case and silver accent on screen right, green wristband on screen left, no face features (back view).

## Batch 38 commands and results (from repo/, logs under outputs/milo-n01/logs/)

`O=outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py`

| command | log dir | result |
|---|---|---|
| `python3 -I $O check batch38-check` | `batch38-check/` | rc 0. `MILO_NORTH_V01_ALL_OK`, `hard_failures: []`, `deterministic_rebuild: true`, `disk_matches_rebuild` true ×5, south unchanged, tool pins ok |
| `python3 -I $O source batch38-source` | `batch38-source/`, proof `independent/…independent-source-proof_v01_20261023-225642-1b612f93.json` (`f0dea37f51311a66afb65d8ba24201dd4a1b04c6286c0e85845fb6fbb08ffb61`), corrupt-hash control `independent/…corrupt-hash-control_test-only…json` (`8c5cb98b…e6`) | rc 0. **`MILO_N01_INDEPENDENT 41 / 41`, `FAILURES []`** |
| `python3 -I $O pixelorama batch38-pxl` | `batch38-pxl/` | rc 0 for both. Sources byte-unchanged |
| `python3 -I $O compare batch38-compare batch38-pxl` | `batch38-compare/` | `MILO_NORTH_PXL_EXPORT_PIXEL_EXACT`. PXO and ORA exports are both `6b48418d2a0bb3a612018287093165ac77aa585b8b432d273ca173575902a985`, RGBA 80x112, 0 differing texels |
| `python3 -I $O fit batch38-fit` | `batch38-fit/` (`fit.log`, `fit.runner.log`, `fit/`) | `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS exit=0`, elapsed 3.7 s, Dummy audio, opengl3/llvmpipe, Xvfb 640x360 |

Independent checker details: every predicate group passed. That covers identity, spec, canvas, rows, 48 logical px, pivot, alpha, border, palette, south pin and tamper refusal, ORA/PXO composition, roles, labels, guides, corrupt hash and tampered PNG. The north predicates (`no_face_features`, `head_hair_cover`, `wristband_screen_left`, `case_screen_right`, `silver_screen_right`, `no_front_opening`) also passed.

Negative controls each still fail at least one predicate:
- Milo south fails all 6.
- Mirrored south fails face, hair, case and front opening.
- Mirrored north fails wristband, case and silver.

Colour difference vs Milo south is 50.55%, and vs mirrored south 62.76% (requirement ≥40%). Silhouette mask difference, direct/mirrored, is 671/687 vs Jiang south, 773/799 vs Lin Que south and 801/829 vs Lin Que north (requirement ≥400).

### Native application diagnostics (separate; not clean application success)

- Pixelorama PXO export: 4× `ERROR: Condition "!actions.custom_samplers.has(...tex_builtin)"` (shader compiler).
- Pixelorama ORA export: 11 error lines and 1 warning:
  - the same 4 shader errors
  - 3× `get_child` index out of bounds
  - `Required object "rp_node" is null`
  - `Must be an ancestor of the control`
  - 12 leaked Dummy texture RIDs
  - 16 resources still in use at exit
  - `WARNING: 160 ObjectDB instances were leaked`
- Godot fit: `WARNING: Could not set V-Sync mode` (Xvfb/llvmpipe driver). There is no other error in the captured log.

## Fit captures (outputs/milo-n01/logs/batch38-fit/fit/, test-only static overlays)

| file | sha256 |
|---|---|
| `…source-fit-city-en_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `043f4e2834dc66000a9c13ee5016096ffaf2716d77d4d62b148be393a813e891` |
| `…source-fit-city-zh_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `175e508ddebdefda68eb9a4c9a04104140795d07c93665a17b83a9af9e8ec863` |
| `…source-fit-ruins-en_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `92ea5a6f02f370905625ec2547a89a70e6ae291f92db12255411c368e6db3880` |
| `…source-fit-ruins-zh_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `bb0dbac20f011f028456aaabcb8dfd0261e6f12b0a845ac011395d7402d0ef09` |
| `…source-fit-manifest_test-only-v01_n01-20261023-225642-1b612f93.json` | `40d86af360923bea81bdd15fe10fc494df87b1de11bf0bc8cb2b03d702d628b2` |

## Limitations and observations

- Automated gates are not an art judgement. This agent glanced at the x6 author preview (`outputs/milo-n01/author/…preview-x6…d85132de.png`, `b8969f31…097b`) and the city-en capture. Observation for the coordinator's review: with the repair, the screen-left hand sits about 2 px inward of the forearm/wristband line and overlaps the coat edge, so the wrist reads slightly offset. This is a visual judgement for the coordinator/creator; it was not changed.
- The read-only scratch diagnostic `outputs/milo-n01/scratch/milo_north_batch34_repair_diag.py` (it verifies the backup and measures the texel delta between the original and repaired PNGs) was **not run** in batch 38: the shell invocation was denied by permission policy and was not worked around. Backup integrity therefore rests on the earlier backup manifest. The checkpoint doc hash was re-verified against it here.
- The fit step uses static overlays from the generic fit script. It is not actor integration and not evidence for dark scenes.
- North only. No east/west, motion, runtime wiring, default change, ledger/Bible/registry update, or approval.

## Bounded next action

Coordinator: independently re-run `check`/`source` with the orchestrator above, inspect the north PNG and captures (including the screen-left hand placement), and if accepted, stage only the 5 north files, the north author, the north checker, the north orchestrator/contract and this note. Ledger credit and creator art review remain separate.
