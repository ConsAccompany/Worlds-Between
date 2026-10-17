# Washington survey annex room 1: v02 quality pass (one bounded pass)

**Status:** technically verified by Claude, **UNAPPROVED**, not creator reviewed. It covers only the Washington, D.C. ruins survey annex room 1 (遗址外环 / Ruin Outer Ring, destination `scifi.ruins`). v02 is runtime-wired in the working tree only; nothing is staged, committed or pushed.

The counters do not change:
- science scenes: **3/12**
- complete character sprites: **0/52**
- timed human playtests: **0/2**
- weighted estimate: **40.8%**

Shared progress state was not edited.

## Why v02

Codex judged v01 (`65b9618f`) coherent and functional but not ready for scene acceptance:
- it was far flatter and lower in detail than the creator-accepted NYC and Yonkers rooms;
- the heroine walked through rubble and fixtures;
- the English title ran under the Save button.

v01's sources, runtime PNGs and captures are kept unchanged as the baseline. Check gate S5 re-hashes all 16 v01 files against the v01 manifest, and all 16 v01 captures are still present.

## How the plate was made (attribution)

The scene is **not** hand-painted end to end. Most of it is an imported, palette-reduced underpainting, with hand corrections layered on top.

- **Source:** the Codex-generated nonruntime art-direction reference `outputs/…capitol-civic-interior-art-direction-reference_nonruntime-v01_20261017-032700-a82fde43.png` (sha256 `c3f627da731f…`; prompt in the matching `-prompt_` .md). It was used as a composition and detail guide and as the underpainting source.
- **Recomposition:** box-filtered into 640×360 in two bands, so the wall, the window and the Capitol dome sit below the 62 px UI header:
  - wall: reference rows 0–300 map to y 58–152;
  - floor: reference rows 300–941 map to y 152–360;
  - x scale: 640/1672.
- **Grade:** moves the room into the accepted interiors' value range.
  - The floor is darkened, falling off toward the near edge and the sides, and its sun shafts are compressed.
  - Shadows are cooled and lights warmed.
  - The bench band behind the clue-label row is darker (feathered), which v01 showed labels need.
  - Floor grout contrast is raised, then a light unsharp pass is applied.
- **Palette reduction:** PIL median cut with 8 k-means iterations to 64 colours, no dither.
- **Cluster pass:** each isolated pixel is folded into the nearest-coloured neighbouring cluster when the RGB step is under 34. High-contrast single-pixel accents are kept.
  - Isolated-pixel fraction: 33.6% before, 14.7% after; 108,442 pixels were folded.
  - The remaining isolated pixels are mostly deliberate accents (ivy leaves, brass glints) and neighbouring near-shades.
- **Hand layers**, drawn pixel by pixel in the author tool:
  - palette-preserving re-toning for the bench-foot shadow and the contact shadows under the rubble and stubs;
  - the east stairwell door: a stair opening entered from the south and descending north into teal light, with re-toned floor-stone kerbs and bronze rails;
  - teal survey accents: a beacon on the window sill and status lights on two brass posts.
- **Provenance in the visible play area** (y 62–317, 163,840 px):
  - 155,689 px come from underpainting layers;
  - 8,151 px come from hand layers.

  These counts are recorded in the manifest and re-verified by the check.
- **Merged plate:** 84 colours in total (64 underpaint plus hand colours).
- **Fixtures** are fully hand-drawn: no underpainting, generation or resampling.

## Scene layers (Pixelorama `.pxo` v7 and `.ora`, binary alpha, bottom to top)

1. `exterior-sky-dome-foliage-underpaint`
2. `back-wall-columns-niches-underpaint`
3. `floor-marble-inlay-underpaint`
4. `rubble-ivy-midground-underpaint`
5. `hand-floor-and-bench-corrections`
6. `hand-east-stairwell-door`
7. `hand-survey-teal-accents`
8. `foreground-stubs-occluder`

The underpaint layers keep their full region, so hiding a hand layer shows the underpainting beneath it. Layer 8 is also exported on its own as the runtime foreground overlay.

## What the room now shows at 640×360

**Capitol / neoclassical identity kept and strengthened**
- Fluted columns.
- Dark-wood niches holding brass survey instruments: a lantern, an armillary, a globe and a telescope.
- Brass-and-teal pipework.
- A broken centre window framing a clear Capitol dome and colonnade.
- Far civic colonnades through the open sides.
- Temperate ivy and shrubs.
- Rubble piles at both flanks.
- A cracked limestone floor with teal and brass inlay borders and the three inlaid clue pads.

**Three reworked fixtures**
- Each is 64×64 at clue + (−32, 2), in 4 layers, with 23–30 opaque colours from the shared ramps and a light source at the upper left.

| Clue | Fixture | Reads as |
|---|---|---|
| `scifi.ruins:0` 分层墙面 / Layered Wall | `layered-wall` | A cut wall specimen on a pallet. A broken sunlit top over dressed sandstone with a walkway moulding sits on a dark sealing course over older brick in running bond. The same teal age tag is fixed to both layers. A tripod survey camera, lens glinting, faces the cut. |
| `scifi.ruins:1` 残缺索引 / Broken Index | `broken-index` | An oak card catalogue with bevelled drawers, brass card holders and pulls. One drawer slot is empty, one drawer is pulled out with gaps in its cards, and cards lie on the floor. A survey reader lists identifiers with an amber missing run. |
| `scifi.ruins:2` 编号四七 / Code Forty-Seven | `code-47` | A verdigris-streaked bronze junction box on a stone plinth with a stamped cream "47" plate, beside a relay node whose display also reads 47. The node's cable and plug lie on the floor below the old box's empty socket. |

## Runtime change

All changes are in `game/scripts/survey_annex.gd` and are gated to `room == 1 and destination_id == "scifi.ruins"`. Compared with HEAD, the diff is +92/−11.

- The plate and fixture preloads point to v02. New const `WDC_ROOM_ONE_FOREGROUND`.
- **Collision:** `WDC_ROOM_ONE_BLOCKERS` holds 12 feet-point rectangles:
  - the bench and back wall (y < 156);
  - the west column and rubble, and the east column, drapery and rubble;
  - the east stairwell;
  - the two corner stubs and the east low rubble;
  - three fixture footprints (y 210–228).

  Movement slides along each axis. A start inside a blocker (for example, an older v01 save on the rubble) can walk out freely.
- **Occlusion (y-sort):**
  - A front `Node2D` is added after the heroine.
  - When she is behind a fixture's base line (y < 228, within 48 px in x), that fixture is skipped in the room's `_draw` and drawn on the front node instead. Its contact shadow is never drawn twice.
  - The clue marker's disc stays under her, and its ring and icon strokes are redrawn on top.
  - The front node always draws the corner-stub foreground overlay. The exit and next-room marker discs are cut out of the overlay, so door markers are never clipped.
- **Inspect zone:** clue interactions keep the original 45 px radius and add a rectangle x ±40, y 150–250 around each fixture, so a fixture can be inspected from its front now that it is solid.
- **Shared marker code:** clue-marker drawing moved into `_draw_clue_marker()` with identical draw calls. Other rooms are pixel-identical (gate C7).
- **English header:** the existing room-specific 14 px title rule now also covers `scifi.ruins` room 1 in English, and the title ends at x 378 (Save starts at 418). The Chinese header and every other room's text and layout are unchanged.
- **Unchanged:** clue IDs and positions, text, doors, save/load, room 2 and other destinations.
- **To revert to v01:** point the four preloads back at the v01 file names and remove the `WDC_ROOM_ONE_FOREGROUND`, `WDC_ROOM_ONE_BLOCKERS` and `WDC_FIXTURE_BASE_Y` consts, the `wdc_*` variables and functions and their call sites, and the header condition. The v01 PNGs and `.import` files are still in place.

## Evidence

All files are in `outputs/wdc-sr1-v02_71300729/`. The 14 Godot captures are in `captures/` and come from real Godot 4.7.2, windowed, Compatibility renderer, 640×360. As in v01, the heroine is the capture-only creator-approved female south idle at 48 logical px.

**Captures (zh and en are separate files)**
- `zh-entry`, `en-entry`: (87, 261).
- `zh/en-near-clue-0/1/2`: in front of each fixture at y 238. `near-clue-1` is the same pose as v01's `lane-index`.
- `zh-occlusion-behind-index`: (292, 204). The cabinet covers her lower body while her head and shoulder stay visible.
- `en-obstacle-west-stub`: (30, 258). The west wall top and ivy pass in front of her feet.
- `en-after-load`: (402, 262).
- `zh-other-city-room1`, `zh-other-outskirts-room1`, `zh-other-ruins-room2`.

**Focused Godot checks**

Tool: `tools/…godot-capture-and-check_v02_20261017-160235-bf5f7fe7.gd`. All print OK; full run `WDC_V02_ALL_OK`.
- **Header:** en is 14 px with its right edge at 378 < 418; zh is 18 px with its right edge at 317.
- **Occlusion state:** front mask is 2 behind the cabinet and 0 in front of it.
- **Interactions 3×3:** real `interact` registers `scifi.ruins:0/1/2` from behind (top), from the side and from the front, with matching overlay titles. No overlay opens on the lane between fixtures.
- **Lane walk:** held `move_right` goes from the exit to x ≥ 578 at a constant y of 261.
- **Collision, with held input:**
  - cabinet from the front stops at y 228.7;
  - layered wall from the west stops at x 128.0;
  - code-47 from the east stops at x 514.3;
  - bench between fixtures stops at y 156.3;
  - west rubble stops at x 85.0;
  - east rubble stops at x 569.0;
  - stairwell stops at x 584.0;
  - west stub stops at y 261.0;
  - near edge stops at the old y 305 clamp.

  A diagonal move slides along the cabinet front, and a start inside the rubble escapes.
- **Reachability flood fill (1 px grid):** 74,577 reachable cells from the spawn. Reachable targets: the exit, the next-room door, all three clue inspection areas, the save spot (402, 262) and the room-2 return spot (555, 257).
- **Save/load:** a clue inspection writes an auto save, and a manual save is taken in English at (402, 262). After a new run, loading restores destination, room 1, clue 0, language and position, with "1/6", and the front layer is rebuilt. The auto save loads too. Test saves were deleted.
- **Doors:** next opens room 2 (no front layer there). Back returns to room 1 at (555, 257), which is not blocked. The exit marker leaves the annex.

**Pixel, source, provenance and Pixelorama check: 15/15 PASS**

Tool: `tools/…pixel-source-pixelorama-check_v02_20261017-160235-e3b74490.py`. Report: `…pixel-source-pixelorama-check-report_v02_20261017-160235-e3b74490.json`.

| Gate | Result |
|---|---|
| S1 | Scene (8 layers), foreground (1 layer) and fixtures (4 layers each) are exact across PNG, ORA, `.pxo` and runtime copies. |
| S2 | Layer alpha is binary and the merged plate is opaque. Underpaint layers use only the 64 underpaint colours; hand layers use only hand or underpaint colours. The declared palette equals the merged plate's 84 colours. Provenance matches the manifest, and the reference hash matches. |
| S3 | The rebuild is deterministic. |
| S4 | The foreground overlay equals the plate's top layer, pixel for pixel. |
| S5 | The v01 baseline is untouched. |
| C1 | The plate renders 1:1: about 132–133k checked background pixels are exact per shot, and the after-load shot is exact. |
| C2 | Opaque fixture pixels are exact; shadow blend error is ≤ 0.83. |
| C3 | No fixture pixels fall in label boxes or the y 236–290 lane. Marker rings and the footer are unchanged against v01. |
| C4 | The en title-to-Save gap is plain header. The zh header is pixel-identical to v01. |
| C5 | All 605 heroine texels in front of fixtures are identical to v01. |
| C6 | Occlusion: 907 cabinet pixels are exact over her box, with 487 of her pixels visible. At the stub, 581 foreground pixels are exact and about 69 of her texels are hidden. |
| C7 | NYC room 1, Yonkers room 1 and Washington room 2 are pixel-identical to the v01 run. |
| P1 | Pixelorama 1.2.3 headless `--split-layers` gives exact layers for all 5 `.pxo` and 5 `.ora` files. |
| P2 | The scene and foreground flat exports are exact. |
| P3 | The real Pixelorama APPDATA is untouched; each run used a temporary APPDATA. |

- **Report only:** fixture flat exports differ by ±1 on the semi-transparent contact shadow. This is the known Pixelorama CLI rounding, the same as v01.
- **Regression:** `game/tests/m7_smoke.gd`, run headless, printed `M7_SMOKE_OK` and left no changes in the working tree.

## v02 against v01 and the accepted rooms (actual game view)

**Metrics** (zh captures, play area):

| Room | Wall mean luminance | Floor mean luminance | Floor std | Mean saturation | Edge density |
|---|---|---|---|---|---|
| NYC room 1 (accepted) | 77 | 109 | 34 | 95 | 23.8 |
| Yonkers room 1 (accepted) | 78 | 105 | 33 | 53 | 28.5 |
| WDC v01 | 133 | 120 | 42 | 70 | 29.2 |
| WDC v02 | 80 | 94 | 39 | 71 | 30.2 |

**Judgment:** v02 is a clear step up from v01. It has a deep, textured back wall with instrument niches and a legible dome, painted rubble, ivy and a stone floor in the accepted rooms' value range, so it reads as a lived-in civic interior rather than a diagram. The heroine no longer walks through rubble or fixtures, and the English header fits. I judge it to be in the same quality class as the accepted NYC and Yonkers rooms, so it stays **runtime-wired as an UNAPPROVED candidate for creator review**. Acceptance is the creator's call.

## Candid unresolved problems

1. **Underpainting origin.** About 95% of the visible plate comes from the Codex-generated reference via palette reduction. It is attributed as such and is not hand-painted. The reference was itself an edit of the old m8-concept plate, so the composition descends from it.
2. **Style seam.** The hand-drawn fixtures are crisper and slightly more saturated than the softened, quantized background. They pop as interactables, as the NYC fixtures do, but the seam is visible.
3. **Floor.** The floor is large, and its centre is fairly even grey stone. It is slightly darker than the accepted rooms (94 against 105–109).
4. **Stairwell.** The east stairwell door is small at 1×. Its "Go deeper" label carries much of the read.
5. **Residual speckle.** 14.7% of pixels are still isolated after the cluster pass. Most are deliberate accents or neighbouring near-shades, but some soft "painted" noise remains on the floor.
6. **Occlusion details.**
   - Behind a fixture, the marker disc sits under the fixture's top instead of over it: 22 cabinet pixels inside the disc change while she is behind it.
   - Fixtures sort by one base line (y 228).
   - Rubble piles are blockers only. She cannot get behind them, so they need no sorting.
7. **Collision feel.** Collision is an axis-separated rectangle slide. Rectangles are hand-fitted to the art, with ~6 px of side padding on fixtures.
8. **Header.** The 14 px English title is smaller than other rooms' 18 px, the same compromise already used for NYC room 2. "Return outside" still overflows its 98 px button in every room; that is shared text, unchanged here.
9. **Room 2.** Washington room 2 still uses the old m8-concept plate, so there is a style jump when going deeper. It is out of scope.
10. **Godot import side effect.** `--import` created `.import`/`.uid` files for other sessions' untracked files (the female sideview v11 PNG and the Chicago Loop v02 PNGs and script). Each time they were deleted, and the working tree status matched the pre-import snapshot.

## Files (all new unless marked)

**Runtime**
- `game/assets/environments/wdc-survey-room1/…_capitol-interior-scene_unapproved-v02_20261017-160235-71300729.png` (+ `.import`), sha256 `228c29d0…b82d0c2e`.
- `game/assets/environments/wdc-survey-room1/…_foreground-occluder_unapproved-v02_20261017-160235-71300729.png` (+ `.import`).
- `game/assets/props/wdc-annex-room1/…_{layered-wall,broken-index,code-47}-pixel-fixture_unapproved-v02_20261017-160235-71300729.png` (+ `.import`).
- `game/scripts/survey_annex.gd` (modified).

**Sources** (`outputs/wdc-sr1-v02_71300729/`)
- Scene, foreground and three fixtures, each as merged `.png`, `.ora` and `.pxo`.
- `…_scene-and-fixtures-manifest_unapproved-v02_20261017-160235-71300729.json`: sha256 values, provenance counts and the underpainting attribution.
- The check report and `captures/`.

**Tools**
- `tools/…capitol-interior-author_unapproved-v02_20261017-160235-71300729.py`
- `tools/…godot-capture-and-check_v02_20261017-160235-bf5f7fe7.gd`
- `tools/…pixel-source-pixelorama-check_v02_20261017-160235-e3b74490.py`
