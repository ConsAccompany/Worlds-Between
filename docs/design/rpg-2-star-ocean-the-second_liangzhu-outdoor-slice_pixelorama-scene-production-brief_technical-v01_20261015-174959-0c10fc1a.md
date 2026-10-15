# Liangzhu outdoor slice: technical scene-production brief (Pixelorama)

2026-10-15. Status: **technical brief only**. It covers one walkable outdoor slice (earthen terrace, canal, bridge, reeds) of the Archaeological Ruins of Liangzhu City at the approved 48-logical-pixel heroine scale. Codex paints the pixel art and controls Pixelorama. This brief creates no image asset, and the test harness draws only flat debug geometry.

## What is decided and what is not

| Item | State |
| --- | --- |
| Liangzhu **terrain direction**: earthen terraces, waterways, wetland, survey-station feel (concept v01) | Accepted as direction only ([pixel-transition review](../qa/rpg-2-star-ocean-the-second_liangzhu-ruins_pixel-art-transition-visual-review_unapproved-v01_20261015-015717-fd5d169d.md)). |
| **Pixelorama** for the Liangzhu **outdoor** high-precision pixel scene | **Approved by the creator, 2026-10-15.** This permits the workflow only. It does not accept any art or composition. |
| 48-logical-pixel display scale; female selout v8 south idle **static** frame | Approved, each only in its recorded scope. |
| Composition of this slice (shapes, coordinates, route) | **Pending.** The coordinates below are tentative test values. |
| Painted pixel art, palette, layers | **Not made.** Art acceptance is pending. Scene visuals stay **0/11**, sprites **0/52** and playtests **0/2**. |
| First city (Shanghai is provisional) and world start year | Still pending. This brief does not depend on either. |

The runtime ruins scene still uses the pale stone-plaza background, and it was not edited. Concepts v01–v04 and the 1672×941 v02 image are references only. **None of them may be used as a runtime plate.** The 1672×941 size cannot map to the 640×360 canvas by an integer factor.

## 1. Dimensions and pixel grid

| Space | Size | Note |
| --- | --- | --- |
| Pixelorama source canvas, one screen | **1280 × 720 px** | 1 source texel = 1 window pixel. |
| Godot logical canvas (`project.godot`) | **640 × 360** | `canvas_items` stretch, `integer` scale. All gameplay coordinates are in this space. |
| Review window | **1280 × 720** | Integer 2× of the logical canvas. |
| Conversion | **source px = 2 × logical px** | Logical (x, y) → source (2x, 2y). |

Why 1280×720 and not 640×360: the approved heroine is drawn at window-pixel density. Her 96 visible texel rows are shown at 0.5 scale, giving 48 logical px and 96 window px. A 640×360 background would draw each texel as a 2×2 block beside a sprite with 1×1 texels. That mixed density is what this brief avoids.

Grid rules:
- Draw collision-relevant edges (bank lips, terrace risers, bridge edges, reed bases) on **even source px**, so they fall on whole logical px.
- Only the 1280×720 review window is in scope. At other window sizes the integer scale changes (for example 3× at 1920×1080). Then a 0.5-scaled texel covers 1.5 window px, and both the heroine and the scene lose 1:1 texels. That is a separate display decision and is not solved here.

## 2. Heroine reference, ground pin and 2× window mapping

- Source: [selout v8 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png), sha256 `ccf9d2a2…68b6fd`; manifest sha256-text-lf-v1 `3ba35811…10ed`.
- The cell is 80×112. The visible bounding box is x 13–55 and y 8–103 (**43 × 96**), with 2,419 opaque texels.
- **Ground pin:** cell texel **(34, 104)**. That is visible column 21 (the centre column of 43) on the first row below the boots.
- **Display:** `Sprite2D`, `centered = false`, `offset = (-34, -104)`, `scale = (0.5, 0.5)`, nearest filter, static. The node position is the foot pin in logical px.
- **Window mapping:** a foot at integer logical (fx, fy) puts the visible box at window **(2·fx − 21, 2·fy − 96, 43, 96)**. The harness checks this exact rectangle and 2419/2419 exact texels.
- Keep foot positions on whole logical px when a still frame is reviewed. The body occupies logical rows fy − 48 to fy.

## 3. Layer stack: Pixelorama layers and exported PNGs

Each layer is a separate, editable Pixelorama layer in one `.pxo`. Each is exported as its own **full-canvas 1280×720 RGBA PNG** with the same origin and no trimming or offset. Alpha is **binary (0 or 255)**: no soft edges, no blend modes and no layer opacity. Layer names map to file names: `rpg-2-star-ocean-the-second_liangzhu-outdoor-slice_<layer>_unapproved-v01_<stamp>-<id>.png`.

| Order | Layer | Godot draw | Contents |
| --- | --- | --- | --- |
| 1 | `ground-base` | z −100 | Wet field, earth paths, terrace top and back, towpath. Opaque everywhere. |
| 2 | `water` | z −80 | Canal surface. Any later shimmer goes on a separate animated layer. |
| 3 | `banks-risers` | z −70 / −60 | Bank lips, terrace south and west risers, ramp. |
| 4 | `ground-decals` | z −40 | Flat detail: cracks, survey stakes lying flat, the exit trail. |
| 5 | `bridge-deck` | z −30 | The walkable deck surface. |
| 6+ | **one layer per occluder baseline group**, named with its baseline, e.g. `fg-bridge-rail-north-b238`, `fg-bridge-rail-south-b260`, `fg-reeds-west-b292`, `fg-reeds-canal-ne-b146`, `fg-reeds-canal-s-b300` | z = baseline | Anything that can stand in front of an actor. |
| — | `guide-collision`, `guide-pins`, `ref-concept` | not exported | Guides only. Hidden at export. Concept images are placed here for reference and never exported. |

Why one occluder per layer: Godot sorts actors against a whole layer by one z value. A layer that holds objects with different baselines would sort wrongly against an actor standing between them.

In Godot, each PNG is a `Sprite2D` at position (0, 0) with `centered = false`, `scale = (0.5, 0.5)` and its z value from the table.

## 4. Import settings (nearest, no resampling)

`.import` parameters for every scene PNG:

```
compress/mode=0              # Lossless
mipmaps/generate=false
process/size_limit=0
process/premult_alpha=false
detect_3d/compress_to=0      # never switch to VRAM compression
```

`fix_alpha_border=true` (the default) only changes the RGB of fully transparent texels, which is harmless with binary alpha.

On every scene `Sprite2D`:
- Set `texture_filter = TEXTURE_FILTER_NEAREST` explicitly and keep texture repeat off. **`scifi_exploration_area.gd` sets its root `Node2D` to `TEXTURE_FILTER_LINEAR` (line 96), and children inherit that.** Without an explicit nearest filter, the scene layers would be smoothed.
- The only allowed scale is 0.5. No `Image.resize`, no fractional positions and no camera zoom.

Acceptance check for real layers: the same texel-fidelity method the harness uses on the heroine. Every opaque layer texel must appear unchanged at window px (x, y).

## 5. Collision and footprint

- **Footprint:** samples at foot + (±7, −4), (0, −4), (±7, +2), (0, +2) logical px, so 14 wide by 6 deep. A position is walkable only if every sample lies inside a walkable region and outside every solid base.
- **Movement:** a 2-px sweep with axis slide, the same pattern as `scripts/city_navigation.gd`, at 140 logical px/s.
- **Water, bank lips (6 logical px), terrace risers and reed bases are solid.** Reed foliage above the base is not a wall. The bridge deck and the ramp are the only links across the canal and up the terrace.
- **Minimum clearances:**
  - an east–west bridge needs a deck depth of at least 6 + 2×4 logical px (this slice: 18, so the foot runs from y 242 to 254);
  - a north–south passage such as the ramp needs a width of at least 14 + 2×8 logical px (this slice: 40).
- **Walkable foot band:** y 110–306. The 48 px body then stays below the runtime header (rows 0–62), and the footprint stays above the footer (from row 318).
- Painted land edges and collision edges must agree within 1 logical px. Before scene review, trace the collision from the painted bank/riser rows on the hidden `guide-collision` layer.

## 6. Foreground occlusion and depth

- **Actors:** `z_index = int(foot_y)`. **Occluders:** `z_index = baseline`, where the baseline is the logical row of the occluder's ground contact (base or post foot).
- An actor is drawn in front when foot_y ≥ baseline. Collision keeps feet from ever sitting exactly on an occluder base row.
- **Reeds:** from the nearest walkable spot behind a clump, the clump may cover at most the **lower 50 %** (24 logical rows) of the 48 px body. Formula: covered rows = (max foot y behind) − (reed top). This slice measures 21 rows, or 43.8 %. A taller clump must sit off-route, or it needs a silhouette or outline treatment, which is not designed here.
- **Bridge rails:** the north rail (baseline 238) is always behind an actor on the deck. The south rail (baseline 260) may cover only the boots, at most 6 logical rows from the deck's south edge. The harness measures window rows 500–505: 61 texels at foot y 253, and 0 at mid-deck.
- Occluders must not cover an interaction marker or its label at the activation position. The layout must be re-checked once the markers are placed.

## 7. Test-only tentative slice coordinates (logical px; source = 2×)

| Region | Polygon / rectangle | Walkable |
| --- | --- | --- |
| West bank path | (24,150)–(236,306) | yes |
| Bridge deck | (226,238)–(310,256); drawn the same | yes |
| East towpath + lower ground | (304,150) (380,150) (380,246) (616,246) (616,306) (304,306) | yes |
| Ramp | (404,222)–(444,250) | yes |
| Earthen terrace top | (388,106)–(616,226) | yes |
| Canal water | x 242–298, full height | no |
| Bank lips | x 236–242 and 298–304 | no |
| Terrace risers | south y 226–246, x 384–640; west x 380–388 | no |
| Wet field | north of y 142, west of the canal | no |
| West reed base | (176,284)–(226,292); top y 260; baseline 292 | no |
| Exit zone | (596,130)–(616,200) on the terrace | — |

**Route:** entry (82,270) → (150,248) → bridge west end (222,248) → mid-deck (268,248) → east end (316,248) → towpath (360,276) → ramp bottom (424,270) → ramp top (424,216) → terrace (500,170) → exit (604,166). Simulated length 600 logical px, about 4.3 s at 140 px/s.

## 8. Existing ruins interactions: preserve in full integration (not remapped here)

The current runtime values come from `scifi_exploration_area.gd`, in logical px. All of them must keep working when a real Liangzhu scene replaces the plate. **This slice does not move, re-wire or re-test any of them.** The harness only reports where each point would fall.

| Interaction | Runtime point / radius / gate | On this slice |
| --- | --- | --- |
| Player spawn; battle return and resume positions | (82,260); `battle_return_position`, `resume_area_position` | walkable |
| Ji records marker (unlocks Ji's recruit) | (320,250), r 43; `ji_records_checked` | walkable (towpath) |
| Survey entrance → `survey_annex.tscn` | (548,142), r 43 | walkable (terrace) |
| Field assist, Ji Cheng | (505,275), r 40 | walkable |
| Field traces 0 and 1 | (115,245) and (470,115), r 34 | walkable |
| Ji Cheng NPC, recruit dialogue | (200,145), r 50; locked until records | **in the wet field (blocked)** |
| Sentry enemy, encounter → battle | (420,225); contact < 23, safe > 43 | **at the ramp top. It would block the only ramp and force the encounter, which breaks the avoidable-enemy rule** |
| Machine bypass zone and marker | x > 545 and y < 205; marker (575,105) | the marker is above the terrace (blocked) |
| Save button, back to map, Esc, ambient loop, discovery cue, bilingual labels | UI | not part of the slice |

Full integration must therefore add a second avoidance route or move the patrol. That is a design change for later, and this brief does not make it.

## 9. Capture route

From the repository root, run windowed (headless capture can hang):

```
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/rpg-2-star-ocean-the-second_liangzhu-outdoor-slice_technical-wireframe-walk-occlusion-harness_test-only-v01_20261015-174959-0c10fc1a.tscn
```

The harness forces a 640×360 canvas, `canvas_items` stretch with integer scale, and a 1280×720 window. It captures the viewport texture, saves each PNG under `outputs/` and reloads it to confirm 1280×720. Success prints `LIANGZHU_SLICE_WIREFRAME_OK`.

For painted layers later: make a **new** uniquely named harness copy. It should load the exported PNGs in place of the debug `Polygon2D`s, at the same z values. Keep every collision, route and occlusion check, and add per-layer texel fidelity. Any capture with debug geometry is a technical wireframe and is never visual evidence.

## 10. Visual review criteria for the future painted slice (creator decides)

1. The terrain reads as Liangzhu earthworks and wetland, not a stone plaza. Earth terraces, canal and reeds dominate, and survey equipment stays secondary.
2. Texel density matches the heroine. Her outline treatment and value structure fit the scene, with no mixed 2×2 blocks.
3. The v8 silhouette reads clearly on the bright earth, the deck and the terrace. In particular the lower body must not merge with warm earth, as v6 and v7 did on paving.
4. Walkable and solid ground are clear without debug lines. Bank lips, risers, the ramp and the bridge edges match the collision within 1 logical px.
5. Reeds and rails occlude convincingly and do not hide the heroine beyond the 50 % and boots limits.
6. No interaction point lands in blocked terrain or under foliage once the markers are placed.
7. Edges are crisp at 1280×720: no smoothing, no half-pixel offsets, no semi-transparent fringes.

## Harness run result (2026-10-15, run 20261015-174959-0c10fc1a)

The run used Godot 4.7.2 stable, windowed, opengl3 (Compatibility) on an RTX 3080, and passed **44/44 checks**: `LIANGZHU_SLICE_WIREFRAME_OK checks=44`, exit 0. All seven captures are **1280×720**, both in memory and reloaded from disk. The root stretch transform is 2×, and the debug edges at logical x 242 and y 226 / 142 land on even window px (484, 452, 284). Every capture carries an on-screen "TECHNICAL WIREFRAME ONLY · visually unapproved" banner.

| State | Foot | Result |
| --- | --- | --- |
| entry | (82,270) | rect (143,444,43,96); 2419/2419 exact |
| bridge-mid | (268,248) | 2419/2419 exact; the north rail stays behind |
| bridge-south-edge | (268,253) | the south rail covers 61 texels, window rows 500–505 only |
| reeds-behind | (200,278) | reeds cover 122 texels, rows 522–555 only, and only with reed pixels |
| reeds-front | (200,300) | 2419/2419 exact; the heroine is in front |
| terrace-exit | (604,166) | 2419/2419 exact; inside the exit zone |
| overview-annotated | (82,270) | walkable and solid outlines, route trail, bilingual labels, runtime UI zones |

Collision probes:
- the canal edges stop the foot at x 228 and 312;
- the deck edges stop it at y 242.17 and 253.83;
- the riser stops it at 250.83;
- the terrace west face stops it at 395.5;
- the reed base stops it at 281.67;
- the ramp carries the foot to y 110.17.

The route completed in 258 frames with 0 wet frames. A 2-px grid search finds entry and exit connected with the deck and **disconnected without it**.

Outputs (`outputs/`, stem `rpg-2-star-ocean-the-second_liangzhu-outdoor-slice_technical-wireframe-<state>_test-only-v01_20261015-174959-0c10fc1a`):

| File suffix | sha256 |
| --- | --- |
| `entry.png` | `c64c068f50c4e4404e7593f5503fe498954f56c5cc8ca43dfba6761717908465` |
| `bridge-mid.png` | `aa284fad6db1d9c082b87d26a1fdb1a8b137229ebfbfe08295cce42adc7f4be3` |
| `bridge-south-edge.png` | `2bd1ab4d220f1d89b9c620346a6d63f5375508f38acaabfcf84409869fbce96e` |
| `reeds-behind.png` | `c03a294f2d32e0cc4085b81f46c124d8aafe9c8883119d04fcc88832e79e37de` |
| `reeds-front.png` | `8be5b31a8b3075d3c6038cf107608d1d1948e78fde14343b28faf765c4b1a49c` |
| `terrace-exit.png` | `d3ace32b1923667c689b301fe255ef841d65d2e2f7feacd9f92954421221c855` |
| `overview-annotated.png` | `96526814f4eabba05688701d04bf97334b15944290a5a295d17ad678229ec7b7` |
| `qa-report.json` | `87fca4d6864caecccd660fa3abee04c0e8d5e6af28ecf28dc2f4305f018cccb0` |

There is one capture set. The on-screen labels are bilingual and the harness has no player-facing localized text, so separate zh and en runs add nothing.

**Limits:**
- The captures use flat debug colours and say nothing about art, palette or composition.
- Only one screen and the static south frame were tested.
- Collision is a footprint point test, not physics.
- The runtime ruins scene still clamps to a rectangle and is unchanged.

The run left the runtime script hash and the v8 PNG byte-identical. A working palette file, `outputs/rpg-2-star-ocean-the-second_liangzhu-terrace-canal_working-palette_unapproved-v01_20261015-135239-71d6c4e9.gpl`, appeared in the worktree from another session. This brief neither uses nor reviews it.
