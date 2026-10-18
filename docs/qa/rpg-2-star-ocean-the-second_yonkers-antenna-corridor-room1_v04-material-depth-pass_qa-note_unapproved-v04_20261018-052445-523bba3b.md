# Yonkers antenna corridor room 1 v04 material-depth pass (UNAPPROVED)

Date: 2026-10-18. Tag `20261018-052445-523bba3b`. Status: **UNAPPROVED, nonruntime, off by default**. This is a bounded recolour pass over the committed v03 (`15709be4`, c20118d). It answers the defects Codex found in the actual v03 640×360 entry capture.

## What changed (colour only; no alpha or coordinate moves)

| Defect in v03 | v04 change | Layer, px changed |
|---|---|---|
| Wall blocks repeat mechanically, flat | Each masonry block (bounded by mortar, y 108–155) gets an upper-left catch-light and a lower-right recess edge. Its value steps with one upper-left light, plus a small fixed per-block variance. | back-parapet-masonry, 9,107 |
| Wear reads as either none or noise | Rising damp in named clusters at the four pilaster feet and below the three junction boxes, with an irregular top contour. Six spalls by the doors and the junction boxes. | back-parapet-masonry (included above) |
| Slab values dead even | Each deck slab steps lighter or darker with the same light. Back arrises are lit (broken every third pixel); front seams are shaded. | deck-slabs, 34,503 (mostly under the walkway and props) |
| Sparse contact depth at plinths | All three plinth feet get 2–3 shade steps on their first rows, then a cast tail to the lower right that breaks up as it leaves the plinth. | cast-shadows, 478 |
| No material separation at the dish mount | Plinth B is shaded as a stone drum: lit left band, core shadow right, darkest edge, rounded foot corners. It gets a dark stone seat under the steel turntable, a lit steel rim on the upper left and a slate lower-right rim. The brass bolts are kept. | antenna-b-dish, 727 |

The flat composite differs from v03 in 15,988 px, none above y 108. Sky, wall kit, walkway, detail, doors, front parapet, antennas A and C, and the foreground are byte-identical to v03. Every pixel stays in the v03 palette (65 colours), and alpha is binary. No generated, traced or resampled image was used.

Two render iterations were used:
1. The first pass read correctly, but the contact shadows and the plinth core shadow were too faint.
2. The second pass deepened the contact rows and the drum core and widened the slab variance. Work stopped there.

## Preserved

- **Composition and coordinates:** every layer's alpha equals v03, except cast-shadows, which only gains pixels. Antenna sprite boxes, anchors (163/320/477, 210) and clue ids are equal to v03.
- **Markers and interaction:** markers, interaction radii, collision and the walk lane are untouched. They live in `survey_annex.gd`, which is unchanged.
- **Runtime:** v04 is not wired. `survey_annex.gd` still loads the v03 plate; nothing under `game/` was written. The default and accepted rooms are unchanged.
- **v03 originals:** all v03 sources, exports and the v03 author are unchanged against HEAD and hash as their manifest records.
- **Counters:** scenes 3/12, sprites 0/52, M2 10/12, playtests 0/2. The meter `check` gives CHECK OK 40.8%. No approval flag, Bible or progress JSON was changed.

## Files (exact dependencies)

- **Author:** `tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-author_unapproved-v04_20261018-052445-523bba3b.py`. It imports, unchanged, `tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-author_unapproved-v03_20261017-224447-15709be4.py`. Requires Python 3 + numpy + Pillow; deterministic.
- **Check:** `tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-source-check_unapproved-v04_20261018-052445-523bba3b.py`. It reuses `source_checks` / `pixelorama_checks` from `tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixel-source-pixelorama-check_unapproved-v03_20261017-224447-15709be4.py` and reads the v03 manifest and `game/scripts/survey_annex.gd`.
- **Outputs** in `outputs/yonkers-room1-v04_523bba3b/`:
  - layered editable source, 13 layers: `…_material-depth-scene-layers_unapproved-v04_….pxo` (Pixelorama pxo v7) and `.ora`;
  - native 640×360 flat PNG: `…_material-depth-native-640x360-flat_unapproved-v04_….png`;
  - manifest with sha256 values: `…_material-depth-scene-manifest_unapproved-v04_….json`;
  - check report: `…_material-depth-source-check-report_unapproved-v04_….json`;
  - `nonruntime-exports/`: the plate, the three antenna crops and the foreground, for a later opt-in Godot check only.

## Verification

- **Source check: GATES 7/7 PASS**
  - S1: binary alpha, palette, 13 layers
  - S2: manifest hashes
  - S3: exports equal the layers, opaque plate
  - S4: ORA/PXO structure and bytes
  - V1: alpha and coordinates equal v03
  - V2: v03 originals and runtime untouched
  - V3: changes limited to the wall, deck, shadow and dish layers, none above y 108
- **Pixelorama CLI round trip: PENDING locally.** There is no Pixelorama binary in the cloud container; it was skipped, not passed.
- **Godot capture: PENDING locally.** There is no Godot binary in the cloud container. No runtime or in-engine verification was done. A local check would need an opt-in path that loads `nonruntime-exports/`, with the default kept on v03.
- **Art judgment:** a 2× crop comparison with v03 was reviewed in this session only. Codex and the creator have not inspected v04.
