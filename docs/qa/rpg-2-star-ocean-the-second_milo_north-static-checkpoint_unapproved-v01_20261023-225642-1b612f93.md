# Milo north static v01: source checkpoint (UNAPPROVED, not integrated)

Task `content.char.milo.static-north`. This is source production evidence only. It gives no creator art approval, no runtime/default adoption, no actor integration and no motion claim. Base HEAD `9c2fc393`. Nothing is staged or committed. West, south, ledger, Bible, registry and defaults were not touched.

**Status: one retained HARD failure in the independent checker (`north_case_screen_right`, details below). It was not waived, the threshold was not changed and the art was not edited to pass it.** The coordinator still needs to inspect the images and decide.

## Source (game/assets/characters/milo-native-v01/north/)

| file | sha256 (raw bytes) |
|---|---|
| `rpg-2-star-ocean-the-second_milo_north-static_unapproved-v01_20261023-225642-5968ba0c.png` | `8439c9d29118196c9aafd04ee390743eab5aab4746a98bed1447e8bd64a94892` |
| `rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-7f054cac.pxo` | `05454c1a656be5ea43ba4654566b78095bbff5028815b652e22522cb0f7d49f7` |
| `rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-af5a9058.ora` | `2868a06328944d48d4d542f23361e7a8b15278ca8f5af2e4a46d3261946bcee1` |
| `rpg-2-star-ocean-the-second_milo_north-palette_unapproved-v01_20261023-225642-a3a9c89f.json` | `e837c5f76ad17caa7d2b9c269cec261c4813dc2238d6297514ae3d3aaf02554d` |
| `rpg-2-star-ocean-the-second_milo_north-manifest_unapproved-v01_20261023-225642-163cf811.json` | `d60fdd22997ee0e3e44a96c02d1970c7c0909615e8c4f135b6916a3176ffc9e7` |

The source is 80x112, body rows 8..103, density 2 with display scale 0.5, giving 48 logical px. Pivot is (40,104), inside the row-103 feet span x 29..51. It has binary alpha, a transparent border, 31 colours (all from the palette shared with south) and a hidden `guides` layer.

Tools: author `tools/rpg-2-star-ocean-the-second_milo_north-static-author_unapproved-v01_20261023-225642-1b612f93.py` (`96bf480f…dcde`). It uses the existing hash-pinned south author and the v8pair serializers in memory. Independent checker `tools/rpg-2-star-ocean-the-second_milo_north-static-source-check_v01_20261023-225642-1b612f93.py` (`96d7aac2…e2bf`). The checker imports no Milo author; it reuses only the Jiang ORA parser/compositor and the structure of the committed south checker. Contract: `outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-style-source-contract_unapproved-v01_20261023-225642-1b612f93.md`. Orchestrator: `outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py`. It records before/after pins for north, south, west and the tools in each log dir's `summary.json`.

## Evidence (all logs under outputs/milo-n01/logs/)

| step | log | result |
|---|---|---|
| author build | `build1/build.log` | rc 0, `MILO_NORTH_V01_ALL_OK`, `hard_failures: []`, deterministic rebuild, disk == rebuild for all 5 files, south files match pinned manifest, palette identical |
| author check | `check1/check.log` | rc 0, `MILO_NORTH_V01_ALL_OK`, `PINS_UNCHANGED True` |
| independent checker | `source1/source.log`, proof `source1/independent/rpg-2-star-ocean-the-second_milo_north-independent-source-proof_v01_20261023-225642-1b612f93.json` | **rc 1, 40/41: FAILURES `['north_case_screen_right']`** |
| Pixelorama export | `pxl1/pixelorama-pxo.log`, `pxl1/pixelorama-ora.log` | rc 0 both; sources byte-unchanged |
| exact RGBA compare | `compare1/compare.log` | `MILO_NORTH_PXL_EXPORT_PIXEL_EXACT`. PXO and ORA exports each have 0 differing texels (both `420e47b8…0581`) |
| fit capture | `fit1/fit.log`, `fit1/fit.runner.log`, captures `fit1/fit/` | `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS exit=0` |

Earlier logs `preview1/`, `preview2/` show rc 1. The only reason is `disk_matches_rebuild: null`, because the files were not written yet; `hard_failures` was `[]` in both runs. They are kept unchanged.

### Independent checker detail

- These passed: identity/spec/hashes/portrait, canvas, rows, 48 logical px, pivot, binary alpha, border, palette, identity colours, south manifest pinned, south files match it, palette identical to south, and the tampered south manifest was refused. ORA composition, merged image and mimetype passed. 11 genuine role layers, anchor roles contribute, guides are hidden, and the visible-guides control was detected. PXO composition, roles, labels and `pxo_labels_north` passed, as did the PXO guides and size gates. The corrupt hash was refused and the tampered PNG was detected.
- North predicates: `no_face_features`, `head_hair_cover`, `wristband_screen_left`, `silver_screen_right` and `no_front_opening` passed. **`case_screen_right` FAILED.** In rows 63..76, 140 opaque texels are at x≥58, which meets the ≥40 requirement. But 14 are at x≤22, and the limit is <10. A read-only scratch diagnostic (`outputs/milo-n01/scratch/milo_north_case_region_diag.py`) shows the 14 texels come from the hanging screen-left hand/arm at x 21..22, rows 63..69 (2 × 7). They are not the case. The case itself sits on screen right. The contract's off-side bound did not account for the hanging left hand. Fixing this needs one of two decisions: an art change that pulls the left hand in to x ≥ 23, or a contract revision approved by the coordinator. Neither was done here.
- Negative controls: each control fails at least one predicate, as required. Milo south fails all 6. Mirrored south fails face/hair/case/front-opening. Mirrored north fails wristband/case/silver.
- Not a mirror or recolour: the colour content differs from Milo south by 50.18% of north opaque texels and from mirrored south by 62.55% (requirement ≥40%). Silhouette mask difference (direct/mirrored) is 685/697 against Jiang south, 787/813 against Lin Que south and 815/843 against Lin Que north (requirement ≥400).

### Application diagnostics (kept separate; an exact export does not make a run clean)

- PXO export: 4× `ERROR: Condition "!actions.custom_samplers.has(...tex_builtin)"` (shader compiler).
- ORA export: the same 4 shader errors; 3× `get_child` index out of bounds; `rp_node` null; `Must be an ancestor of the control`; 12 leaked Dummy texture RIDs; 16 resources still in use at exit; `WARNING: 160 ObjectDB instances were leaked`.
- Fit run: `WARNING: Could not set V-Sync mode` (Xvfb/llvmpipe). No other errors appear in the tail captured in the log.

## Fit captures (outputs/milo-n01/logs/fit1/fit/, 640x360, Xvfb, Dummy audio, opengl3/llvmpipe)

| file | sha256 |
|---|---|
| `rpg-2-star-ocean-the-second_milo_source-fit-city-en_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `09a4165f1c8102d468bfbd6c64854d1e750cdb697b5a36e501d9b291dcf1cae6` |
| `rpg-2-star-ocean-the-second_milo_source-fit-city-zh_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `dbf8413c4a19306e273adb9230f2023f68f56ddfa15bbb4dd1c3188182ea4308` |
| `rpg-2-star-ocean-the-second_milo_source-fit-ruins-en_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `356610e84580b4bff9be7f3713f9dc8d8133bce213de197179db054c65ee4c3d` |
| `rpg-2-star-ocean-the-second_milo_source-fit-ruins-zh_test-only-640-v01_n01-20261023-225642-1b612f93.png` | `2223a504c1a62767a12434eef86ca67f70ff02f50f3e1a4171227f5f222a65e6` |
| `rpg-2-star-ocean-the-second_milo_source-fit-manifest_test-only-v01_n01-20261023-225642-1b612f93.json` | `b6b5a0287e919aba9bb26f9c3e1a4f26fd07c3374aac87c8f82b624c7f3d310a` |

These are static overlays from the existing generic fit script. They are not actor integration and not evidence for dark scenes.

## Limitations

- No visual review was done by this agent; the coordinator will inspect the actual PNG and the captures. The automated gates are not an art judgement.
- The independent checker is not green (see above). Production is not complete until the coordinator resolves the case predicate.
- North only. No east/west, motion, runtime wiring, default change, ledger/Bible/registry update, or approval.
- Scratch files in `outputs/milo-n01/scratch/` are QA aids, not source.

## Re-run (from repo/)

```
python3 -I outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py check <new dir>
python3 -I outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py source <new dir>
python3 -I outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py pixelorama <new dir>
python3 -I outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py compare <new dir> <pixelorama dir>
python3 -I outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py fit <new dir>
```
