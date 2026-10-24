# Milo east static v01: source QA verdict (UNAPPROVED)

Task `content.char.milo.static-east`, batch 45. This continues the interrupted attempt 43 pipeline (same author, same tag `20261024-000137-e4a1c7d2`). Nothing was re-scaffolded. Base revision `1f0519de8080a6c57298838cfa8b68963b2a3bde`. **Production evidence only.** This note gives no human art approval, says nothing about native GUI reliability, adds no motion and does not change any runtime default. Nothing was written to the ledger, Bible, registry, Git index or commits.

## Verdict

The source checks pass: the deterministic author check, the new independent checker (56/56), pixel-exact Pixelorama PXO and ORA exports, and four EN/ZH fit captures from the checked Godot runner. Pixelorama application diagnostics are listed separately below. They are not clean. The committed south and north packages were byte-identical before and after every step (`pinsUnchanged: true`, and `git status` shows no south/north changes). The dirty west package was read only and used only as a negative control.

## Source files (sha256 of raw bytes; written by the attempt-43 `build1`; this batch did not change them)

| file (game/assets/characters/milo-native-v01/east/) | sha256 |
|---|---|
| rpg-2-star-ocean-the-second_milo_east-static_unapproved-v01_20261024-000137-820dcbf2.png | af45b51d44c0b409267c2995ec196593cbf0fca6cbb178c01b65e6f0d749e070 |
| rpg-2-star-ocean-the-second_milo_east-edit_unapproved-v01_20261024-000137-8799fd7f.pxo | a854453e33abcfe03437a7c0cc90f50a72660772a983f78792cf802aa620b17a |
| rpg-2-star-ocean-the-second_milo_east-edit_unapproved-v01_20261024-000137-a77ff61f.ora | 56171d13a062b1eff9a48201b3338c06d861365cbbf318af5af865258d484b78 |
| rpg-2-star-ocean-the-second_milo_east-palette_unapproved-v01_20261024-000137-29b43d49.json | c322e69c1ca22a79347e1981d82bc5d4cab6b8e4dc901a3a88add70ff3b01333 |
| rpg-2-star-ocean-the-second_milo_east-manifest_unapproved-v01_20261024-000137-1a15f1d2.json | dc77dec5f89b68754782bef12c158fbccda29ba314bf998cbab1da3ab936db44 |

Tools: author `tools/rpg-2-star-ocean-the-second_milo_east-static-author_unapproved-v01_20261024-000137-e4a1c7d2.py` `4999198d…cdada3`; new checker `tools/rpg-2-star-ocean-the-second_milo_east-static-source-check_v01_20261024-000137-e4a1c7d2.py` `789a9797e32243c9e37b55548d8e74789bb2cd515f99a9a6cf2233a9f5b8c5c3`; orchestrator `outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py` `85ed593a…f87`. The contract with thresholds fixed before authoring is `outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-style-source-contract_unapproved-v01_20261024-000137-e4a1c7d2.md`.

Identity (Bible character-04): the source has a white/grey short medical coat, a medicine case on the near (right) hip, a green wristband on the far (left) wrist, a silver right-temple accent, an 80x112 canvas, body rows 8..103, pivot (40,104), display scale 0.5 = 48 logical px, 34 colours, 10 genuine role layers, 18 isolated texels, and a hidden guides layer.

## Reproduce (from repo/; each step refuses to reuse an existing log dir)

```
python3 -I outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py check <dir>
python3 -I outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py source <dir>
python3 -I outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py pixelorama <pxldir>
python3 -I outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py compare <dir> <pxldir>
python3 -I outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py fit <dir>
```

## Results (logs under outputs/milo-e01/logs/)

| step | log dir | rc | result |
|---|---|---|---|
| build (attempt 43) | build1 | 0 | `MILO_EAST_V01_ALL_OK`, deterministic rebuild, `hard_failures: []` |
| author check | check1 | 0 | `MILO_EAST_V01_ALL_OK`, disk equals rebuild, south/north manifests match, tool pins OK |
| independent source | source1 | 0 | `MILO_E01_INDEPENDENT 56 / 56`, `FAILURES []`; proof `source1/independent/rpg-2-star-ocean-the-second_milo_east-independent-source-proof_v01_20261024-000137-e4a1c7d2.json` `b7f3f500…d42d7` |
| pixelorama | pxl1 | 0 / 0 | PXO and ORA sources unchanged |
| compare | compare1 | 0 | `MILO_EAST_PXL_EXPORT_PIXEL_EXACT`; both exports `395ede84c500caa98381466c4a6adfde95bda71bd99b82b2bca76b9f1f87604b`, 0 differing texels |
| fit | fit1 | 0 | `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS exit=0 elapsed=5.563`, Xvfb, `--audio-driver Dummy`, opengl3/llvmpipe |

Fit captures (`fit1/fit/`): city-en `d0febddf…d2228`, city-zh `7ddcdb92…90a5`, ruins-en `2dff717d…3d00`, ruins-zh `4599f0be…a7f8`, manifest `c85550ec…1f10`. These show a static overlay through the generic fit script. They do not show actor integration.

### Independent east predicates (the real image must pass all; each control must fail at least one)

Real-image values against the contract thresholds:

| predicate | value | threshold |
|---|---|---|
| iris components | 1 | exactly 1 |
| iris x mean vs head mid | 44.67 vs 39.0 | iris x > head mid |
| skin/face at front (right) edge, rows 18..30 | 10 of 13 rows | >= 8 |
| hair/silver at back (left) edge, rows 12..26 | 15 of 15 rows | >= 10 |
| silver texels, rows 8..26 | 50 | >= 16 |
| case green, rows 64..76, x <= 40 | 40 | >= 12 |
| wristband green mean x, rows 58..64 | 48.0 | > 44 |
| mirror IoU | 0.5885 | <= 0.80 |

East-not-mirror/recolour colour difference: vs mirrored stored west 1086/1525 opaque texels (71%, minimum 35%); vs south 1299/1525 (85%, minimum 40%).

All six controls are rejected: mirrored east, Milo south, Milo north, stored west, mirrored stored west and Lin Que east. The mirrored stored west is the blind-mirror shortcut. It passes eye, face, hair and asymmetry but fails silver (7), case-green (4) and wristband x (38.0). Lin Que east is a weak control because it uses a different palette, so every colour predicate fails trivially. The not-mirror/recolour gates pass (east opaque colour difference vs mirrored west >= 35%, vs south >= 40%), as does the own-silhouette alpha difference >= 400 against Jiang south and Lin Que south/east/west. The retained controls are also rejected or detected: corrupt hash, tampered PNG, visible guides, tampered south manifest and tampered north manifest.

## Diagnostics disclosed separately (not app-clean)

Pixelorama 1.2.3 headless logged application diagnostics even though the exports are pixel-exact:
- PXO: 4 ERROR lines (one distinct: `Condition "!actions.custom_samplers.has(...)"`)
- ORA: 11 ERROR lines and 1 WARNING (RID/resource/ObjectDB leaks at exit, `children_cache` index out of bounds, `Must be an ancestor of the control`, `Required object "rp_node" is null`)

The PXO export uses Pixelorama's internal project name (`milo-east-idle-static-v01.png`). Godot logged a V-Sync warning under Xvfb. All raw output is in the step `.log` files.

## Not verified / remaining human gates

- Native Pixelorama GUI open/edit reliability (only headless export was exercised).
- Human creator art approval of the east profile. Status stays `UNAPPROVED`.
- Runtime/actor adoption and motion are out of scope.
- The ledger/registry production credit belongs to the coordinator.
