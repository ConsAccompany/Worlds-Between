# Chicago Loop arrival block (State St × Lake St): bounded material-depth pass v05, QA note

**Status: UNAPPROVED, test-harness opt-in only.** This is one bounded art pass over v04 for Codex visual QA and creator review. It accepts no scene art.

Counters are unchanged:
- MVP meter 40.8%;
- M2 10/12;
- science scene visuals 3/12;
- character variants 0/52;
- post-art playtests 0/2.

What was not touched:
- the Git index (nothing staged, committed or pushed);
- the Game Bible, the completion ledger and shared progress state;
- every Washington, Yonkers, battle and map file;
- every v02, v03, v03r1 and v04 file;
- **the shared runtime Loop `.tscn`.** It still names the v04 selector, exactly as v04 left it (unstaged). See "Opt-in path".

Built by Claude Code (Opus 5.5) through signed-in Claude Max: `claude auth status` reports `claude.ai`, `firstParty`, `max`. No API key or credit fallback was used, and no quota limit was hit. No process was killed. Every Godot, Python and Pixelorama run exited on its own.

Brief: `docs/coordination/…chicago-state-lake-v05-material-depth-claude-dispatch_unapproved-v01_20261017-234000-7d2e6a1c.md`.

Inputs read:
- the v04 QA note and v04 tools;
- the science-sphere visual grammar note;
- `docs/qa/…chicago-state-lake_official-place-visual-anchors_unapproved-v01_20261017-201200-82f4c6d1.md`;
- the real v04 zh/en 640×360 captures.

There is no `AGENTS.md` in the repo.

## What v05 changes

The v05 author tool started as a copy of the v04 one, and each change is marked `v05`. Only three static layers change: `backdrop-facade-north` (19,627 px), `backdrop-underdeck-storefronts` (9,127 px) and `station-platform-canopy` (2,871 px, all in the windbreak rows 82–89).

### Far facades (rows 62–94)

- **Warm haze.** The facades have their own terracotta, brick and limestone ramps plus warm-neutral glass. These replace the shared stone ramp and the teal-grey glass. No value in the new ramps is as bright as the lit station hall: each has luma < 150 or r − b ≤ 40.
- **One credible shadow plane.** A taller block west of State St, off camera, shades the lower floors in the low west sun. The hard edge steps down one row every 36 px eastward (`canyon_row`). So the strip has a sunlit upper plane over one shadow plane instead of an even grid.
  - Open terracotta columns: sun 103 / shade 69 mean luma (v04: 98.5 / 99.2, no plane).
  - Open limestone columns: sun 130 / shade 96 (v04: 119 / 124).
- **Window depth.**
  - An L of recess shadow on the glass from the lintel and the west jamb.
  - A lit sill, and a shadow row under the terracotta sills in sun.
  - A lit east reveal on the brick windows.
  - Pale blinds drawn down in about 30% of sunlit windows: broad shapes, not per-pixel noise.
  - Lit interiors only on the shadow side.
- **State St north.** The far half is one asphalt value lighter, and the far crosswalk uses the dim paint value with a worn top row. The corner sidewalk takes the same shadow line.

### Storefronts under the deck (rows 135–165)

- **Soffit and signs.** Two soffit shadow rows sit over the fascias. Lit shops have back-lit letter blocks (two or three words). Some dark shops have one plain plate.
- **Piers.** They are lit on the west face and shade the glass east of them.
- **Lit shops.** Each shows several values instead of one flat warm fill:
  - a dim ceiling with pendant lamps;
  - a lit back wall, brightest in the middle of each pane;
  - a shelf band in shadow;
  - a counter, and a figure in some shops;
  - a door rail.
  - Mullions now fall every ~16 px.
- **Dark shops.** One broad diagonal reflection band.
- **Awnings.** Two shallow ones, green and brick-red, each with its shadow on the glass.

### Windbreak

The canopy windbreak shows the facade behind it through its glass, in two dark warm-neutral values. Before, it was one flat dark band.

The roof, posts, lamps, coping and the head house are unchanged: lit hall, teal lintel and State/Lake plate. The station focal point is the same pixels as v04.

### Unchanged, byte-identical to v04

- the ground and its light and shadow layer;
- the deck girder and the station plate;
- every y-sort layer (regions, pivots, alpha and colour);
- the walk mask and the occlusion reveal mask;
- the geometry and the hero-visibility report;
- the three read-only sites and their zh/en text, street labels, title, badge and help.

The scene script is the v04 script with only its header and art path changed. There is no day/night logic in this scene, so none was changed.

## Opt-in path (shared `.tscn` not edited)

A new selector, `game/scripts/…state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd`, extends the unchanged v02 script. It routes as follows:
- **v05 flag** (`-- --chicago-state-lake-v05`) or `v05_override = 1`: the v05 scene;
- otherwise the v04 selector's rules: v04, then v03r1, then v03;
- **no flag:** v02.

**It is not wired into the game.** The runtime Loop `.tscn` was left alone because another session may be using it. During this pass a new WDC dispatch and a WDC v12 selector appeared in the tree.

The v05 Godot check proves the path through an explicit harness. It builds an in-memory copy of the Loop scene: same root name and type, with the v05 selector as root script. That copy takes over the Loop scene path in the resource cache (`PackedScene.take_over_path`), and nothing is written to disk. This is exactly what a one-line `path=` change would do. The check then:
- flies NYC→Chicago from the world map;
- saves, returns, loads and resumes;
- exits with Esc, all through that path;
- hands the path back to the real scene at the end.

The same check proves the real, unedited Loop `.tscn` still plays v02 even with the v05 flag. That `en-default-off-v02-entry` render is **0 px different** from v04's.

**To wire v05 later:** change the one `path=` in the Loop `.tscn` from the v04 selector to the v05 selector. The default stays v02.

## Comparison at actual 640×360

All figures come from real Godot captures (zh approved-heroine reference; en gives the same numbers).

| Measure | v03r1 | v04 | **v05** |
|---|---|---|---|
| Facade strip mean r − b (warmth) | 29.7 | 17.5 | **22.1** |
| Facade luma spread p95 − p5 (plaza: 143) | 114 | 127 | **119** |
| Facade near-black share / specks ≤ 14 px | 40.1% / 23 | 0.8% / 12 | **0.8% / 12** |
| Facade band edge density / isolated px | 0.459 / 0.0052 | 0.333 / 0.0002 | **0.415 / 0.0002** |
| Storefront band edge density / isolated px | 0.571 / 0.0272 | 0.510 / 0.0212 | **0.555 / 0.0221** |
| Largest one-colour warm-light region (storefronts) | — | 121 px (door + side light) | **61 px** |
| Strip focal window (plate x = 326) | x 344, 386 lit px | x 324, 609 lit px | **x 324, 609 lit px** |
| Focal margin over the best window ≥ 80 px away | — | 1.17× | **6.09×** |
| 8×8 coarse/fine luma ratio, facade (reported only) | 0.854 | 0.893 | 0.904 |
| 8×8 coarse/fine luma ratio, storefronts (reported only) | 0.731 | 1.057 | **0.805** (lower) |
| Whole-view edge density / isolated px | 0.539 / 0.0344 | 0.512 / 0.0327 | 0.528 / 0.0328 |
| Visible colours / art palette | 607 / 83 | 608 / 84 | 626 / 103 |

Comparison images: `outputs/chicago-loop-state-lake-v05/…zh-entry-v04-over-v05-640x720_comparison_20261018-000240-1d1b9337.png` is the real 1× pair. `…zh-entry-rows60-169-v04-over-v05-2x-display-only_comparison_…png` is a 2× enlargement for display only.

### By eye at 1×, v04 above v05

- **Better.**
  - The far plane now reads as warm buildings in evening air behind the dark L, not a cool drafted grid.
  - The sunlit-upper / shaded-lower split gives the strip one big value shape.
  - The lit hall stands out more. In v04 the best window away from the station had 521 warm-lit px against the hall's 609; in v05 it has 100, because the far facades are hazy and partly in shadow.
  - Under the deck, the lit shops read as interiors (lamps, counter, a figure) instead of orange slabs.
  - The two awnings and the reflection bands break the run of identical shopfronts.
- **Trade-offs.**
  - The facade is busier than v04: edge density 0.333 → 0.415. It is still below the v03r1 strip that Codex called busy (0.459), with no added speckle.
  - The storefront band's 8×8 coarse/fine ratio fell (1.057 → 0.805). By that measure, the lit and dark shops form weaker broad clusters than v04's flat fills.
  - The difference from v04 is modest at 1×: the strip is only 14–33 rows tall above the L.

## Remaining visual flaws

- **Still grids.** The facades are regular bay grids with no cornice, skyline or roofline. The header cuts every building at row 62. The terracotta in sun has low window/wall contrast and can look soft.
- **Stepped shadow edge.** The 36 px stair-steps cut across windows. On the limestone block (x 540–640) the step pattern can read as a rendering band rather than a cast shadow.
- **Windbreak.** The see-through glass adds a band of busy dark pattern behind the canopy posts. A calmer single reflection would do.
- **Storefronts.** The pendant lamps and figures repeat a similar rhythm, and the lit shops still share one colour family. The awnings are thin (4 rows) and barely read at 1×.
- **Still open from v04:**
  - the unforeshortened far crosswalk (now dimmer, but the same bar geometry);
  - the loose platform logic (north-side canopy, invented 2537 design, no south platform);
  - the invented stair, medallion, fountain, kiosk and pylon;
  - the open info note covering the strip;
  - the reveal dither in motion;
  - the largest single colour (7.95%).

## Iteration, disclosed

The gate thresholds were set after measuring v04 captures and v05 merged previews while the art was iterated. They were fixed before any v05 Godot capture was measured.

- **Coarse/fine dropped as a gate.** I first considered "8×8 coarse/fine ratio above v04" as a broad-cluster gate. Breaking up flat fills lowers it, so I report it instead of gating on it, and list it as a trade-off above.
- **Preview simplification.** During preview iteration I simplified the art to stay under the v03r1 busy-strip edge density:
  - one terracotta pier and spandrel value per light plane;
  - two-value pilasters;
  - no limestone under-sill shadow;
  - no fascia shadow row;
  - the v04 bulkhead;
  - fewer blinds.
- **One capture-measured failure.** The first capture set (`…20261017-235820-ba4b502c`) failed **L1** by one pixel: 73 px against the 72.6 limit. In lit shops, the pier-shadow column joined the dim ceiling and the shelf rows into one region. I changed that column to a dark warm value (`wd0`), rebuilt, reimported and recaptured, and did not change the gate. That set was deleted. Only `…20261018-000240-1d1b9337` remains.

## Tests

### Build

`python -I tools/…pixel-author_unapproved-v05_20261017-234337-84862412.py` is deterministic: a temp rebuild matches every hash (S1).

### Godot

`Godot --path game -s <abs>/tools/…godot-capture-check_v05_20261017-234337-3eea25e0.gd -- <abs out> 20261018-000240-1d1b9337 <abs walkmask> <abs reveal mask> --chicago-state-lake-v05` gives **`CHICAGO_LOOP_V05_OK checks=79`**: the 75 v04 checks retargeted at v05, plus four more.

- **The four new checks:**
  - the shared Loop `.tscn` still names the v04 selector;
  - the real Loop runs v02 even with the v05 flag;
  - the harness takes over the Loop path;
  - the v05 selector without opt-in plays v02.
- **Older opt-ins:** the v04, v03r1 and v03 opt-ins each still reach their untouched scenes, and all three are off when only the v05 flag is given.
- **Coverage:**
  - the map flight;
  - collision equal to the walk mask (0 mismatches) and the reveal mask;
  - the legacy pins and 18 solids;
  - held walks north, along the under-L lane and over the crosswalk;
  - the plinth block;
  - nine occlusion spots;
  - the three zh/en notes, with no time or clue change;
  - old save spots;
  - save, load and resume in v05;
  - Esc to the map.

### Source

`python -I tools/…pixel-source-check_v05_20261017-234337-dda76e45.py --capture-stamp 20261018-000240-1d1b9337` gives **`CHICAGO_LOOP_V05_PIXEL_SOURCE_CHECK 25/25`**:
- S1–S4, G1, G2;
- **G3:** the shared Loop untouched, the selector chain, the v02 baseline unchanged and git-clean;
- **R1:** a bounded pass over v04, defined above;
- A1;
- H1;
- C1: the Godot entry equals the y-sorted layers, 0 of 157,482 px different;
- C2: the visible hero matches the model at all nine spots;
- C3, C4, C5;
- C6 vs v04;
- F1, N1, K1, K2, W1, L1, H2;
- **P1/P2:** the Pixelorama 1.2.3 CLI split-layers export is exact for `.pxo` and `.ora` (12 layers each, the hidden guide not exported), and the real APPDATA is untouched. Another session's Pixelorama GUI, PID 37584, was running and was left alone.

Report: `outputs/chicago-loop-state-lake-v05/…pixel-source-check-report_v05_20261018-000240-1d1b9337.json`.

### Reachability

`python -I tools/…walk-reachability-check_v05_20261017-234337-5c1e93d7.py` gives **4/4**:
- all 64,225 walkable px form one region from the spawn;
- the kiosk, stair and pylon spots are reachable;
- every capture spot is reachable;
- the walk grid and blocks equal v04's.

### Capture diffs vs v04

Every changed pixel in zh/en entry, the reference, the kiosk note and the column occlusion lies in rows 62–94 and 135–165. Outside them, 0 px differ.

### Not run

The shared headless smokes and the v02/v03/v03r1/v04 checks were not run. No shared script, scene or data file changed, and the default-off render is proven identical.

## Process notes

- **Import side effects.** Both Godot `--import` runs recreated `.import` files for another session's untracked PNGs: the female sideview v11 and v12, and WDC capitol-west v11 flat and walkmask. The second run also made a `.uid` for another session's new WDC v12 selector. Each time, I deleted only the files that run had created. `git status` was diffed before and after every import and every Godot run.
- **Scratch work** stayed under `%LOCALAPPDATA%\Temp\chi-v05-work`.

## Files (all new; nothing tracked was modified)

- **Author tool:** `tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v05_20261017-234337-84862412.py`. Its manifest pins the v04 author under `pass_of`.
- **Godot check:** `tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-godot-capture-check_v05_20261017-234337-3eea25e0.gd`.
- **Source check:** `tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-source-check_v05_20261017-234337-dda76e45.py`.
- **Reachability check:** `tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-walk-reachability-check_v05_20261017-234337-5c1e93d7.py`.
- **Runtime art:** `game/assets/environments/chicago-loop-state-lake-v05/`: 7 PNGs, each with its `.import`. Import params are identical to v04's.
- **Scene:**
  - `game/scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn`;
  - `game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.gd`;
  - `game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd`;
  - the two `.uid` files.
- **Editable source** (`outputs/chicago-loop-state-lake-v05/`):
  - `…layered-source_unapproved-v05_….pxo` (pxo_version 7) and `.ora`, with 12 visible layers plus the hidden, locked `guides-walkmask`;
  - the merged preview, the walk-mask guide and the 103-colour `.gpl`;
  - the layer manifest;
  - the source-check and reachability reports;
  - the two comparison images.
- **Captures** (`outputs/chicago-loop-state-lake-v05/godot-runtime/…640x360_v05_20261018-000240-1d1b9337.png`): real Godot 4.7.2 windowed renders, 19 tags plus the visible-hero counts JSON:
  - flag off: `en-default-off-v02-entry`;
  - entry: `zh-entry`, `en-entry`;
  - traversal: `zh-/en-traverse-under-l-lane`, `zh-/en-traverse-crosswalk`, `zh-traverse-stair-foot`;
  - occlusion: `zh-occlusion-column-raw`, `en-occlusion-column-reveal`, `zh-occlusion-honey-locust`;
  - interaction: the kiosk, stair and pylon in zh and en;
  - reference: `zh-/en-approved-heroine-ref`.

## Addendum 2026-10-18: G3 r1 (sync to main)

- **Wiring.** For the synchronisation to main, the Loop `.tscn` now names the v04 selector in the committed tree. That is the same one-line hunk v04 left unstaged. With no flag the Loop still plays v02. v05 is still not wired.
- **Old G3.** The old G3 compared the Loop `.tscn` with HEAD and required them to differ, so it would fail as soon as that line was committed.
- **G3 r1** in the source check no longer reads HEAD. It requires:
  - the Loop `.tscn` to be exactly the one-script Loop scene naming the v04 selector, with no v05 selector and no other hook or node;
  - the v04 selector to match its pinned sha256-text-lf `6c288141…`;
  - the v04 selector to keep its `--chicago-state-lake-v04` flag, `v04_override := -1` and the fall-through to the v02 script;
  - the v05 selector routes, as before.
- **Mutation test.** A throwaway test (11/11) confirms G3 r1 passes on the real files and fails for: v05, v03r1 or v02 in the Loop, an extra node or resource, a renamed flag, a default flipped on, a removed fall-through, and a one-byte selector edit.
- The gate key is now `G3_opt_in_wiring_exact_v04_hook_default_off_v02_unchanged`.
