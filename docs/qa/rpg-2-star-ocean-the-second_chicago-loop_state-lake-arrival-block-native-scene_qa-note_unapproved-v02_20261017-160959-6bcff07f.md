# Chicago Loop arrival block (State St × Lake St): visual-density pass v02, QA note

**Status: UNAPPROVED. Runtime candidate awaiting Codex visual review.** The creator has not reviewed it, and nothing here accepts scene art. Counters are unchanged:
- science scene visuals **3/12**;
- complete character variants **0/52**;
- post-art human playtests **0/2**;
- MVP meter **40.8%**.

Shared progress, the Game Bible and the completion ledger were not edited. Nothing was staged, committed or pushed. The v01 files are untouched and remain the audit baseline: its assets, editable source, tools, captures and its scene script.

## What changed versus v01

Codex's review of v01 said:
- the storefronts were flat colour rectangles;
- the paving repeated mechanically;
- the trees read as broccoli;
- the L girder hid almost all architecture;
- a car stood mid-lane, leaving a 6 px walking strip;
- the planters were mirror pairs.

v02 rebuilds the whole block around the nonruntime art-direction reference `outputs/…chicago-loop_elevated-rail-walkable-block-art-direction-nonruntime-v02_20261016-195030-8c456a73.png`. That reference is untracked; the build pins its sha256 `73b57deb…761be4`.

**How the base was made.** The base is a *quantized underpainting*, not the raw image. The author tool does this:
1. Box-downscales the reference to 640×360.
2. Recomposes the rows for gameplay:
   - the facade above the L now fills rows 62–94, with shopfronts, lit windows and an arched entrance;
   - the open-tie deck is shortened from 51 to 40 rows (95–134), so a 44 px hero at walk top 178 stays clear of the girder;
   - the lit facade bases show under the deck at rows 135–151.
3. Repairs visible generator defects by copying clean neighbouring texture:
   - white splotches on the far State St roadway;
   - a noisy block where the crosswalk meets the plaza.
4. Lifts the info kiosk 32 rows and shortens its screen by 17 rows. It now stands under the deck edge.
5. Applies a light unsharp mask, then quantizes to one 128-colour median-cut palette with k-means refinement and no dither.
6. Runs two passes that fold isolated low-contrast pixels into their neighbours, so the single pixels that remain are deliberate (rivets, flowers, highlights).
7. Adds hand-placed native pixel art:
   - a cast-iron and slat bench;
   - a State/Lake station plate with the five Loop line colours (the text is the runtime label);
   - a Chicago-flag banner on the curb lamp.

**Fixes for the specific v01 complaints:**
- **Mid-lane car removed.** The legacy smoke-test pins now land on the kiosk and the bench:
  - (440,195) is solid at the kiosk;
  - (410,190) is solid at the bench, so a slide from (400,180) still ends at (410,180).
- **Walking strip.** The under-L walkway is now part of one broad pedestrian plaza, 68 px deep from walk top 178 to the column plinths at 246, instead of a 6 px strip.
- **Planters** are no longer a mirror pair. There are two small flower boxes at different columns, a terrace planter and a cypress, all with different shapes.
- **Trees** are large foliage crowns instead of small rounded blobs.

**Street labels.** The plaza lies east of State St, so the Lake St label now reads **"E Lake St · 200 N"** (v01 said "W Lake St"). "N State St · 0 E/W" sits at the State St corner. "State/Lake" sits on the station plate. The labels are now painted under the hero and props (drawn before the y-sort node), so the heroine is never covered by text.

**Runtime decision: v02 is wired into the runtime.** I judged that it clears the brief's bar against v01 (details under "Honest comparison"), so the one-line wiring went ahead.
- The change: the runtime Loop scene `game/scenes/…chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn` now points its script at `game/scripts/…chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd`.
- To revert, point that one `path=` line back to the v01 script. The v02 assets then go unused.
- The bilingual title, hint, badge, note and help text are unchanged, and so are the save/resume, Esc/World-map and kiosk behaviour.

## Files (all new, except the one-line `.tscn` change)

- **Runtime art** (`game/assets/environments/chicago-loop-state-lake-v02/`): 7 PNGs plus their `.import` files.
  - `ground-far`: opaque, flattened from four static source layers.
  - Six y-sort layers with binary alpha. Pivot rows in brackets:
    - `ysort-curb-lamp` (180.5)
    - `ysort-kiosk-bench` (195.5)
    - `ysort-l-columns` (254.5)
    - `ysort-planters` (256.5)
    - `ysort-forecourt` (300.5)
    - `ysort-foreground-tree` (330.5)
- **Scene script:** `game/scripts/…state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd`, plus its `.uid`.
- **Test scene:** `game/scenes/…state-lake-block-scene_unapproved-v02_….tscn`. It was used for the pre-wiring check; the final evidence comes from the runtime scene.
- **Editable source** (`outputs/chicago-loop-state-lake-v02/`):
  - `…layered-source…55667f46.pxo` (Pixelorama, pxo_version 7) and `.ora`, holding the same 11 layers:
    - `ground-plaza-street`
    - `facade-north`
    - `deck-l-girder`
    - `station-plate`
    - the 6 y-sort layers
    - a hidden, locked `guides-walkmask`
  - the merged preview, walk-mask guide, a `.gpl` palette (146 colours: 128 underpainting + 18 hand-placed), the hash manifest and the check report.
- **Tools:**
  - `tools/…state-lake-block-pixel-author_unapproved-v02_20261017-160959-55667f46.py`
  - `tools/…state-lake-block-godot-capture-check_v02_20261017-160959-4c432d04.gd`
  - `tools/…state-lake-block-pixel-source-check_v02_20261017-160959-7af12ce1.py`

## Evidence (real Godot 4.7.2 windowed renders, 640×360, runtime scene)

The captures are in `outputs/chicago-loop-state-lake-v02/godot-runtime/…-640x360_v02_20261017-162405-1bdb3cd5.png`:
- `zh-arrival`, `en-arrival`;
- `zh-behind-l-column`;
- `zh-kiosk-board`, `en-kiosk-board`;
- `zh-approved-heroine-ref`, `en-approved-heroine-ref`: the approved selout v8 heroine at 48 px, at the same spot and scale as v01's reference;
- `en-approved-heroine-under-l`.

The v01 baseline captures for comparison are in `outputs/chicago-loop-state-lake-v01/after/`.

## Test commands and results

**Godot behaviour and capture check:** `Godot --path game -s <abs>/tools/…godot-capture-check_v02…gd -- <abs out> <stamp> res://scenes/…district-placeholder-scene_m2-v02….tscn <abs walkmask png>` gives **`CHICAGO_LOOP_V02_OK checks=42 runtime_scene=true`**. It covers:
- arrival and labels:
  - zh/en labels unchanged;
  - real English street names;
  - street labels painted under the hero;
- collision:
  - `walkable()` equals the authored mask (63,947 px, 0 mismatches);
  - the legacy pins;
  - 14 solid probes;
  - head clearance under the deck;
- held-input walks:
  - north from the spawn to the L;
  - west across the whole plaza and the State St crosswalk;
  - a column plinth blocks a walk south;
- occlusion:
  - behind a column, 0 hero pixels show; in front, 360;
  - behind the kiosk, 0 show; in front, 216;
  - the bench hides her feet while her head stays visible;
  - the forecourt and tree layers always draw over the hero;
- the kiosk:
  - E opens the board in zh/en with no time or clue change;
  - E again closes it;
  - E away from the kiosk does nothing;
- eight old placeholder/v01 save spots resume on walkable ground;
- Save returns to the Loop scene and spot;
- Esc returns to the map.

**Pixel/source check:** `python -I tools/…pixel-source-check_v02…py --capture-stamp 20261017-162405-1bdb3cd5 --report …` gives **13/13**. It covers:
- hashes and a byte-identical rebuild;
- an opaque ground, binary alpha and the static layers partitioning the canvas;
- every colour in the `.gpl`;
- the ORA and PXO layers exact, with the guide hidden and locked;
- the GDScript geometry, pivots and pins match the author tool;
- the runtime scene is wired to v02;
- the Godot arrival render equals the layers outside the hero and labels (0 differing pixels);
- v02 is denser and less repetitive than v01 (see below);
- a Pixelorama 1.2.3 CLI `--split-layers` round trip is exact for both `.pxo` and `.ora`, run with an isolated temp APPDATA; the real `%APPDATA%\pixelorama` was untouched.

**Unchanged shared regressions, headless, all exit 0, rerun with v02 wired:**
- `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
- `M2_SMOKE_OK`
- `M7_SMOKE_OK`
- `GLOBAL_TRAVEL_CORE_OK`
- `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
- `EXPORT_DATA_INCLUSION_SMOKE_OK`
- `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
- `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=108`

## Honest comparison to v01 at actual 640×360 scale

Measured on the zh arrival captures, visible rows 62–317:

| Measure | v01 | v02 |
|---|---|---|
| Largest single-colour share | 8.2% | 2.9% |
| Distinct 16×16 blocks | 79% | 100% (no exact repeats) |
| Neighbour-change density | 0.42 | 0.82 |
| Visible colours, UI included | 686 | 775 |

By eye at 1×, v02 reads much closer to the reference and to the accepted NYC and Yonkers rooms:
- a riveted, rusted deck with amber lamps;
- shopfronts with lit interiors and a bronze arched entrance above it;
- lit bases below it;
- slab paving with the L's striped shadow;
- a crosswalk with brick ramps;
- real foliage;
- a terrace with a fountain.

The 48 px heroine stays clear on the mid-tone paving. Treat this as my assessment, not acceptance.

## Defects and risks (candid)

1. **Provenance.**
   - Most pixels come from a quantized *generated* reference, not hand-placed clusters. Only the bench, the station plate and the flag banner are hand-pixelled.
   - Fine speckle in the paving and stone survives the cleanup. The 0.82 neighbour-change density is partly that grain, not only detail.
   - A strict pixel-art review may still call the look "filtered".
2. **Fragile rebuild.** The rebuild needs the untracked reference PNG, Pillow 12.3.0 and numpy 2.3.5. Median cut and k-means can change between Pillow versions, and the hash lock would then fail.
3. **Hero hidden by columns.** Directly behind a 22 px column shaft the heroine is fully hidden (v01: nearly hidden). This is correct occlusion, but she can vanish for a step.
4. **Repair seam.** The crosswalk-end repair leaves a lighter vertical slab strip with a faint seam at about x=121, rows 186–264.
5. **Composition limits.**
   - There is still no sky or rooftop line; the header covers rows 0–61.
   - The deck stays the dominant horizontal band.
   - The centre of the plaza is a large open paving field.
   - There are no people, trains or motion.
   - The fountain court is cut off at the right edge.
6. **Smaller walkable area.** It is 63,947 px versus v01's 76,778. The raised terrace, the fountain court (x≥518 north and x≥574 south) and the south parapets are solid. The explorable extent is still one block, which remains an open creator decision.
7. **Kiosk.** It is generator-derived, shortened and moved. Its screen detail is impressionistic. The English board still wraps as "(State/ Lake" (pre-existing).
8. **Accuracy.** The facades, arched entrance, terrace and fountain are generic stand-ins from the reference, not the real buildings at State and Lake. The pedestrian Lake St plaza is a 2537 art-pilot choice, not canon.
9. **Old tool no longer runs against the runtime.** The v01 capture-check tool expects v01 geometry, such as its parked car. Re-point the `.tscn` to the v01 script to rerun the v01 audit.
10. **Unchanged wording.** The badge and note ("Technical placeholder · Art not accepted"; "buildings and block scale are placeholders") are still true and were deliberately left alone.
11. **Import side effect.** Godot `--import` again wrote a `.import` file for another session's untracked female sideview v11 PNG (`…873fe1e6.png`). It was deleted. No other out-of-scope files changed.
