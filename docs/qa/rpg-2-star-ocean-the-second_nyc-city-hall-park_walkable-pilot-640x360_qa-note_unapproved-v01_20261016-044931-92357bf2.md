# NYC City Hall Park — 640×360 walkable Pixelorama pilot v01 — QA note

**Status: UNAPPROVED. Test-only pilot, not accepted art.** Nothing is wired into the runtime: no scene, script, data, test, default or camera setting changed. Science scene art acceptance stays **0/11**. No Game Bible, meter, `docs/progress.md`, Washington art, growth code, battle art or Git change was made. Only the creator's visual review can accept this scene.

- Run: `nyc-chp-v01_20261016-044931-92357bf2` (Workstream C, independent art implementation).
- Author: Claude (Claude Code, Opus 5.5) on the claude.ai Max subscription, firstParty only. No API key, no image model and no paid fallback were used.

## Scope delivered

- **One** 640×360 logical-pixel camera composition. This matches `game/project.godot` exactly: a 640×360 viewport in a 1280×720 window at integer 2×.
- The same slice rendered by Godot at **1280×720**: one establishing view plus two layering-proof views.
- No other camera views and no batch output.

## Inputs and how they were used

- Audit: `docs/qa/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-art-direction-visual-audit_unapproved-v03_20261015-221543-c74a12e0.md`.
- Concept: `outputs/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-art-direction-nonruntime-v03_20261015-221543-c74a12e0.png`. It was viewed by eye for **geography, path and zone cues only**:
  - City Hall and its cupola to the north;
  - the fountain plaza to the south-west;
  - a central north–south walk;
  - fenced lawn panels and a statue lawn to the east;
  - Broadway on the west edge;
  - discreet science fixtures.
- The build tool **never opens the concept image**. No continuous-colour pixel and no generated figure is used.
- The only character pixels are the approved v8 female south idle frame (`game/assets/characters/pixelorama-pilots/…south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png`). It is sampled 2:1 to a **48-logical-px** actor for scale and layering.

## Authoring route (disclosed)

This is **not a Pixelorama GUI paint pass**: the session had no desktop or computer-use access to the GUI.

- Every landmark, path, lawn, tree, lamp, prop, collar and pin is an explicit hand-written table entry in the tool.
- The tool rasterises those tables into 80 hand-picked palette colours across 18 named layers.
- Pixelorama 1.2.3 then re-exports the `.pxo` and `.ora` headless, and the exports are compared texel by texel.
- The `.pxo` opens in the Pixelorama GUI as 18 editable layers, so a GUI polish pass can start from it.
- **Creator decision still open:** whether this table-driven route is acceptable for a high-precision scene, or whether a GUI pass is mandatory.

## Files

Tool: `tools/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-pilot-640x360_pixelorama-build_unapproved-v01_20261016-044931-92357bf2.py`, sha256 `a2a6587148ae5964d6e2b42fc39ecbb0afe9635ed1c0af8ee5f5683263c8b266`.
- Usage: `preview <tempdir>` | `build` | `check [--write-report]`.
- Run it with the runtime Python and `-I -B`.

Candidate directory: `game/assets/environments/candidates/nyc-chp-v01_20261016-044931-92357bf2/` (sha256 per file, bytes):

| file (prefix `rpg-2-star-ocean-the-second_nyc-city-hall-park_`, suffix `_unapproved-v01_20261016-044931-92357bf2`) | sha256 |
|---|---|
| `scene-18layer….pxo` (native pxo_version 7) | `dfdf479f8668e5cffa2b55321ccda15504fd78843e2c7d6245b574a0dc8a6d60` |
| `scene-18layer….ora` | `71b4f8fda099b06092a1e16e2d6f67268a6f196ab9a6c62de3cbb1b6e9543dc2` |
| `scene-flat-640x360….png` | `f962a903fb64509e7809ce8478ea28bdc7495bd6c424dce270442427d7ca5d09` |
| `scene-palette….gpl` (80 colours) | `8ae35eef7966464bf3ad8f81383d865b67ab9b0511495cba45287cc9c7d03cd5` |
| `scene-walkmask….png` (collision mask: opaque = walkable foot texel) | `5edbef6900625b33c032209ad3cebaef9353914d4af066de6890c4acd02cbed3` |
| `scene-walkability….json` (8 px cell grid, pins, pivots, collars, exits, route) | `ceea633b233993a799aa7dcd9d944b5b4451aae255ae8b6af2df67085cc9616f` |
| `scene-manifest….json` | `928865f97340fe024fc6c4428829abffc16eceda0a9df70cd1703f04f40d7d34` |

Output directory: `outputs/nyc-chp-v01_20261016-044931-92357bf2/`. Each view is a separate file; there are no comparison sheets.

| file | sha256 |
|---|---|
| `…godot-render-1280x720-axis….png` (heroine on the central walk, foot 320,292) | `375b913968929ed133275625b108882fc84a321bf31f6f646c6e18e7af872d37` |
| `…godot-render-1280x720-behind-fountain….png` (foot 172,236) | `d929a1d42fff97153d202f093c2da7ebe8b57b7ae6242a98cd52982085aab2f8` |
| `…godot-render-1280x720-behind-tree….png` (foot 410,274) | `b8b1ea1fe6c384fab3dfcc22dad8dd69f4f291e62ca973fca7e64e8c42230933` |
| `…technical-check-report….json` | `74b1460e30731ba5b567d53946b5a40dabf866c5cc69c3d2419996959ccbc436` |

The longest absolute path is 252 characters, under MAX_PATH (260).

## Composition and layer stack

Top of the frame is north. The camera is a top-down 3/4 view lit from the south-west, so shadows fall up and to the right.

**Backdrop, rows 0–169 (not walkable).** This part uses forced perspective:
- a dark north grove band;
- City Hall (x 150–489) with:
  - two storeys, a two-tier six-column portico and end pavilions;
  - the roof balustrade;
  - the cupola with a clock and a gilded Justice figure, tip at row 0;
- the forecourt with U.S. and NYC flags;
- flank trees;
- the hedge and picket belt (rows 150–167);
- the gate piers (x 284–291 and 348–355) with teal scanner strips and an access light line.

**Walkable park, rows 172–359, at heroine scale:**
- a 56 px granite central walk (x 292–347);
- the fountain plaza: radial granite rings, radii 92×58, basin 46×26 centred on (172,270);
- NYC hexagonal-paver walks;
- the statue circle (470,266);
- the south plaza (rows 338–359);
- lawns with hoop fences and five flower beds.

**Not walkable:** Broadway on the west (maglev guideway, tram, glass shelter with a map screen, crosswalk) and the Park Row sidewalk on the east (NYC subway entrance, lamp).

Layers, bottom to top:

| # | layer | runtime role |
|---|---|---|
| 1 | `north-groves` | base (opaque) |
| 2 | `streets` | base |
| 3 | `city-hall` | base |
| 4 | `forecourt-flank` | base |
| 5 | `park-ground` | base |
| 6 | `ground-detail` | base |
| 7 | `fountain-basin` | base |
| 8 | `cast-shadows` | base |
| 9 | `props-low` | base |
| 10 | `tree-nw-ysort` | Y-sort, pivot row 214 |
| 11 | `lamps-n-ysort` | Y-sort, pivot row 230 |
| 12 | `trees-ne-ysort` | Y-sort, pivot row 244 |
| 13 | `statue-ysort` | Y-sort, pivot row 268 |
| 14 | `fountain-ysort` | Y-sort, pivot row 272 (centrepiece + 2 plaza lamps) |
| 15 | `lamps-s-ysort` | Y-sort, pivot row 312 |
| 16 | `tree-se-ysort` | Y-sort, pivot row 322 |
| 17 | `fg-occlusion` | overlay above actors |
| 18 | `guides` | hidden + locked |

Proposed runtime draw order:
1. Merge layers 1–9 into one base.
2. Y-sort the seven `*-ysort` layers together with the actor by pivot row. The actor is drawn last on ties.
3. Draw `fg-occlusion` on top.

## Technical gates: 35/35 PASS (`check --write-report`)

These are technical gates only. Passing them is not art acceptance.

**Raster integrity**
- All 18 layers are 640×360 with binary alpha.
- The base layer is opaque.
- Art layers use palette colours only; the flat image uses 77 of the 80 colours.
- The build is deterministic.
- The `.pxo` stack is the 18 named layers, and the guides layer is hidden.

**Walkability**
- The walk mask covers 36,172 texels, 30.1% of rows 172–359.
- Feet are only on paving: none in the backdrop, the fountain basin or the lawns.
- All 14 pins are on walkable texels and reachable from `spawn_south`.
- Exits: `exit_broadway_gate` (70,270) and `exit_park_row` (596,350).
- Interaction: `city_hall_gate` (320,178); the forecourt itself is not walkable.

**Heroine route**
- 1,525 one-pixel steps.
- Waypoints: spawn → central walk → fountain north ring (behind the fountain) → Broadway gate → fountain south → south plaza → statue circle (behind the statue) → east walk → Park Row exit → lamp front/behind → City Hall gate.
- Every step is walkable on both the Python mask and the **exported mask PNG loaded in Godot**. There are 0 blocked steps and 0 jumps over 1 px.

**Occlusion and visibility**
- Depth audit: zero walkable feet where a base item (fences, benches, bins, bollards, pylon, Broadway gate piers) would wrongly cover the actor from behind. Derived collars handle this.
- Seven Y-sort cases are correct. Behind cases (sprite covers the actor):
  - fountain: 57 of 57 overlapping texels;
  - statue: 64 of 64;
  - SE tree canopy: 46 of 46;
  - north lamp: 65 of 65.

  Front cases (actor covers the sprite):
  - fountain lamp: 63 overlapping texels;
  - statue plaque: 338;
  - north lamp: 61.
- Every walkable foot keeps at least 1/3 of the actor visible. The worst case is 0.75, at (468,260) behind the statue.

**Fleck and cluster metrics**
- There are 0 isolated bright flecks in rows 150–359. A ground-only despeckle pass changed 20 texels where a lamp post or fence half-covered a 2-px slab highlight.
- The whole frame has 23 isolated bright texels, all in the backdrop: window glints, flags and cupola.
- Single-texel colour islands: 4.63% in the park rows and 2.35% in the backdrop.

**Pixelorama 1.2.3 headless round-trip**
- `APPDATA` was redirected to a fresh temp dir per run, with a kill-switch on the real `%APPDATA%\pixelorama`. Isolation held.
- The `.pxo` flat export is exact and identical across two runs.
- The `.pxo` and `.ora` `--split-layers` exports match all 17 art layers byte-exact, and the split composite equals the flat image.
- The `.ora` flat export is exact.
- The hidden guides layer is not exported.
- Source copies were unchanged.
- Each run took about 4 s.

**Godot 4.7.2: two throwaway projects under `%TEMP%`, `APPDATA` redirected, nothing written to `game/`**
1. *Headless texel gate.*
   - The layer PNGs extracted from the `.ora` load SHA-256-exact.
   - Runtime-stack stills at 269 feet (every 6th route step plus all pins) hash-match the Python stack.
   - The actor is 48 px tall.
2. *Windowed render gate (real GL Compatibility renderer).* It uses Sprite2D layers, a `y_sort_enabled` node (sprite position.y = pivot, actor last) and the fg overlay, in a 640×360 viewport, 1280×720 window, integer stretch, with nearest filtering.
   - The three captures are 1280×720 and have **0 differing pixels** against the Python stack scaled 2× nearest.
   - Note: this gate opens a real window on the desktop for a few seconds.

## Exact visual defects (open; reasons this stays UNAPPROVED)

Coordinates are logical px in the 640×360 frame.

1. **Forced-perspective scale seam.**
   - City Hall storeys are 28 rows tall (upper storey rows 68–95) and the doors are 23 rows (rows 104–126), against a 48-row heroine. The building reads at roughly half the heroine's scale, like a model.
   - The grand stair (rows 135–148) is at building scale, but the granite forecourt walk between the piers (x 294–345, rows 150–169) is at heroine scale. The two scales meet at row 149.
   - Washington dome-west v01 has the same class of defect.
2. **Facade is a rule-based interpretation.**
   - There are 12 identical window bays (x 160–479; arched upper windows 15 rows, lower windows 13 rows) plus a six-column portico.
   - Bay counts, column count, cornice profile and cupola proportions were **not checked** against the official LPC City Hall site plan or elevations cited in the v01 audit.
   - The green "science hub" banners on the portico (x 291–296 and 343–348, rows 70–92) are invented game fiction.
3. **Three horizontal stripes.** The north grove band (rows 0–60), the facade block and the straight hedge/picket belt (rows 150–167, x 64–603) stack into three full-width horizontal bands that split the frame. The belt has no break except at the gate.
4. **Empty lawns.**
   - The NW lawn (about x 64–290, rows 172–230) and the NE lawn (about x 350–570, rows 172–250) read as flat green fields at 1280×720.
   - The 56 px light/dark zones still show as soft patches.
   - The blade tufts are one tone step apart and almost invisible at 2×.
5. **Tree sameness.**
   - Every leaf-cluster crown (4 walkable-area trees, 4 flank trees, 2 corner fg crowns and the 28 grove-band crowns) comes from one 10-lobe template. At most two lobes are dropped per tree.
   - Trunks are straight 6-px bark columns (lollipop read), e.g. the NE trees at rows about 220–244.
6. **No Lower Manhattan context above City Hall.**
   - Rows 0–60 are generic dark woodland: no Tweed Courthouse, no sky, no skyline.
   - NYC identity rests on City Hall itself, the U.S./NYC flags (17×11 px each), Broadway, hex pavers and the subway entrance.
7. **Statue.** The figure at (470,268) is 9 px wide with a 21-row figure on a 17-row pedestal. It reads only as "a bronze figure": no Nathan Hale likeness, and the plaque is a dark rectangle.
8. **Fountain.**
   - The centrepiece at (172,270) is a generic two-tier tazza, not modelled on the actual City Hall Park fountain.
   - The falling water sheets (x 156–159 and 184–187, rows 256–267) are alternate-pixel c2/c3 dashes that read as dotted lines.
9. **Lamp shadows read as cracks.** The 1-px cast-shadow lines run about 26 px up-right from each lamp base, e.g. (295,230) → (321,215), across the granite walk.
10. **No heroine contact shadow.** The actor floats slightly on the light granite in all three captures. This is a runtime/actor concern, but it is visible here.
11. **Weak foreground framing.** `fg-occlusion` is only 603 texels: canopy slivers in the bottom corners (about x 0–40 and x 600–639, rows about 345–359). There is almost no near-depth framing.
12. **Tram dominates the left edge.** The cream tram roof (x 7–33, rows 22–130) is the brightest large mass on the left and competes with City Hall. It is static and has no motion or sound cue.
13. **East edge is thin.** The Park Row sidewalk (x 606–639) is mostly blank. The subway-entrance globes (x 609–613 and 629–633, rows 198–205) are 5×6 green blobs, and there is no signage.
14. **Diagonal hex walk edges stair-step.** The NE diagonal (226,240) → (298,200) has stair-stepped 1-px curb pixels (p5 and p2) along both edges, and its junction with the central walk is abrupt.
15. **Busy central walk.** The 2×1 slab highlights make the central walk slightly speckled. The continuous teal inlay at x 319–320 reads as a seam splitting the walk.
16. **Forecourt border reads as a dotted line.** The flower border along the plinth (rows 138–142) is a regular bloom rhythm every 5 px.
17. **Weak lighting on the building.**
   - Projections cast only 3-px shadow strips (x 198–200 and 358–360).
   - City Hall casts nothing onto its forecourt.
   - The south-west sun reads clearly on the trees but weakly on the building.

## Process notes

- Godot ran only in temp projects. A `git status --porcelain` diff from before to after shows only this run's two new directories. A third new entry, `wdc-dome-west-v02_20261016-044903-cdb4ebdb/`, belongs to another session (Washington); it was not touched.
- The tool itself was already untracked before the build snapshot.
- The temp dirs (`wb-chpgate-*` and `wb-chpgodot-*`) were removed.
- The real `%APPDATA%\pixelorama` was untouched, and no Godot `app_userdata` was created.
- The candidate directory sits under `game/` like the earlier Washington candidates. If someone opens the Godot editor, it may generate `.import` files there.
- During this session, this run's own first build was deleted and rebuilt under the same run ID. That build had an empty `fg-occlusion` layer because the corner canopies sat entirely below the frame. Nothing from that build was reviewed or used.

## Requested creator decisions

1. Is the table-driven Python route acceptable, or must the next pass be painted in the Pixelorama GUI from this `.pxo`?
2. Is the forced-perspective City Hall at about half heroine scale acceptable? The alternative is a taller frame or a crop that shows only the central portico at heroine scale.
3. Should the next pass source exact facade, fountain and statue geometry from the official LPC plan (defects 2, 7 and 8)?
4. Is any foreground framing and background skyline wanted (defects 6 and 11)?

Until those reviews happen, scene art stays **0/11** and this pilot remains **UNAPPROVED**.
