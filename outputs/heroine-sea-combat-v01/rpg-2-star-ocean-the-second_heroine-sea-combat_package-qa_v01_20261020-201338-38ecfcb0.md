# Heroine Sea-of-Stars combat runtime package v01 — technical QA

Owner: DeepSeek (bounded support). Checkout: `work/dual06/ds-pack`. Base: `11973af6492ef60a99ca1f2eacb01e12c091ccb9`. Controller tag: `20261020-201338-38ecfcb0`.

This is a deterministic technical packing of already-authored 136x144 RGBA poses. It is **not** new art, motion approval, art approval or default adoption. No existing loader, battle code, ledger, Bible, Site or registry file was changed.

## Package

Directory: `game/data/heroine-sea-combat-v01/`

| Role | File | SHA-256 |
| --- | --- | --- |
| Runtime spritesheet | `rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet_v01_20261020-201338-38ecfcb0.png` | `f55db8cca615d4d64e8c07eb949b375cc6afb7562fc8ab9ac03062d78bd29a60` |
| Manifest (`worlds-between.combat-sprite-set/1`) | `rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-manifest_v01_20261020-201338-38ecfcb0.json` | `6a4c663d859818d8b1714c6485fc927443c316acaa0602547f0c6e367df6df78` |
| Index (`worlds-between.combat-sprite-set-index/1`) | `rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json` | `1abb5b67b3bf59c02b3c747068789a01509812aee97c105b9f5c15c7a60ffa49` |
| Source provenance | `rpg-2-star-ocean-the-second_heroine-sea-combat_source-provenance_v01_20261020-201338-38ecfcb0.json` | `d9d0a1ec0aeac0d83dcf9852b123b4e932d41e0137f4e7b79ec3e2c2cbda4e70` |

Index mapping: `hero:female` → the adjacent manifest filename. Sheet: 816x720 RGBA, 6 columns x 5 rows = 30 cells, cells 0–28 occupied, cell 29 fully transparent. Cell 136x144, pivot `[64,136]`, `logical_scale` 0.5, `display_proportion` `"0.65"`, `authored_facing` `"right"`.

## Source binding

| Source | SHA-256 |
| --- | --- |
| v01 idle/attack manifest | `a012cc3d42c4b81f6c73cdc984ccb10f15d37fcb73b2c06938a01595be790657` |
| v02 move/guard/dodge/skill manifest | `b6d8a14e4b15ab52095476764992e45ba2d3b51614033b6e67b7d7ae31965151` |
| v03 revised hit/down manifest | `66f7804ca7fa980e63c468ef8f38f2a9c8506571eb2eb902b2d70951a5700edd` |
| v01 base still `battle_still-native136…1294c865.png` | `4ce65a7915c0c0270a4ca353152b45b7d68b42672cb1483dd4f3e9cf4ac9d5e6` |

The provenance manifest freezes all **29 source PNG** hashes, all **29 PXO** hashes, all **29 ORA** hashes and the three source-manifest hashes, with effective source paths and cell origins. The verifier re-reads those files; all still match. Source files were not rewritten.

## Actions (integer 30 Hz ticks)

| Action | Frames (cell:ticks) | Total | Loop | loop_start |
| --- | --- | --- | --- | --- |
| idle | 0:8, 1:6, 2:8, 1:6 | 28/30 | yes | 0 |
| attack | 3:2, 4:2, 5:1, 6:2, 7:2, 8:2, 1:1, 0:1 | 13/30 | no | — |
| move | 9:3, 10:3, 11:3, 12:3 | 12/30 | yes | 0 |
| guard | 13:2, 14:6, 15:6 | 14/30 (2-tick intro, 12-tick loop) | yes | 1 |
| dodge | 16:4, 17:4, 0:1 | 9/30 | no | — |
| skill | 18:4, 19:3, 20:1, 21:2, 22:3, 0:1 | 14/30 | no | — |
| hit | 23:2, 24:3, 25:2, 0:1 | 8/30 | no | — |
| defeat | 26:3, 27:3, 28:3 | 9/30 | no, holds last | — |

`down` is mapped to the loader-required `defeat` action. Every action declares `tick_rate: 30`; every frame is exactly `cell` + `ticks`. No `ms` or rounded-millisecond fields exist in the package.

## Verification

- Builder: `tools/rpg-2-star-ocean-the-second_heroine-sea-combat_package-builder_v01_20261020-201338-38ecfcb0.py` (`7b294f38b5743a929ad5e1072a63a132ff0e8f54372452ca55846c4cd1b25059`). `--check` regenerated every package byte and matched all four files.
- Independent verifier: `tools/rpg-2-star-ocean-the-second_heroine-sea-combat_package-verifier_v01_20261020-201338-38ecfcb0.py` (`8a07f3e7da68a6f11db6e3506700109016aa74a19f513dc24a382d751e35a12c`). Report: `outputs/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_package-verification_v01_20261020-201338-38ecfcb0.json`.
- Result: `PACKAGE VERIFY OK`, **571 checks**, `failed_checks: []`.
- Every occupied cell was compared as decoded RGBA (`136*144*4` bytes) with its original PNG: exact equality. Rebuilding the sheet independently reproduced the sheet bytes. Cell 29 is fully transparent; sheet alpha contains only 0/255.
- All 29 cells are referenced; base cell 0 is reused by idle, attack, dodge, skill and hit. Source v02 hit/down files are not used; v03 revised hit/down are.
- Malformed-input check: nine mutations were rejected with nonzero exit (float ticks, `ms` instead of `ticks`, `loop_start` on attack, tick_rate 60, guard loop_start 0, cell-29 reference, missing skill, missing index mapping, one-pixel sheet tamper).
- Repository scope: `HEAD` is the assigned base; no tracked/staged changes; only new package/tool/QA files are untracked.

## Truthful limitations

- No Godot run. The loader `tick_rate`/`loop_start` implementation is concurrent (Claude) and was not present at verification time; the coordinator must run the combined loader/game path.
- The requested explicit one-tick base tails make attack 13/30 s, dodge 9/30 s, skill 14/30 s and hit 8/30 s, longer than the source clips / some arena visual durations. Sources were not reauthored.
- Runtime texture import/filtering was not exercised. The project default is nearest (`default_texture_filter=0`), which is required; no Godot import or render evidence is claimed.
- Art/motion remain unapproved and this package is not a default. The base still is the one referenced by v01's approved static baseline; this work grants no new approval.
- No commit, staging, ledger/Bible/Site/registry change, account or billing change.
