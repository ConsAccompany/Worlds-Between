# Chicago Loop arrival block (State St × Lake St): bounded scene-art pass v04, QA note

**Status: UNAPPROVED and opt-in only (off by default).** This is one bounded scene-art pass over v03r1, for Codex visual QA and creator review. It accepts no scene art.

Counters are unchanged:
- MVP meter 40.8%;
- M2 10/12;
- science scene visuals 3/12;
- character variants 0/52;
- post-art playtests 0/2.

What was not touched:
- the Git index (nothing staged, committed or pushed);
- the Game Bible, the completion ledger and shared progress;
- Yonkers, the battle heroine and the global map;
- every v02, v03 and v03r1 file.

The one exception is a single line in the runtime Loop `.tscn` (see "Opt-in path").

Built by Claude Code (Opus 5.5) through signed-in Claude Max: `claude auth status` reports `claude.ai`, `firstParty`, `max`. No API key or credit fallback was used, and no quota limit was hit. No process was killed: every Godot, Python and Pixelorama run exited on its own.

Brief: `docs/coordination/…chicago-state-lake-v04-claude-dispatch_unapproved-v01_20261017-230000-5a7c2e90.md`.
Inputs read:
- the v03 and v03r1 QA notes and tools;
- `docs/qa/…chicago-state-lake_official-place-visual-anchors_unapproved-v01_20261017-201200-82f4c6d1.md`;
- the science-sphere visual grammar note.

There is no `AGENTS.md` in the repo.

## What v04 changes

The v04 author tool started as a copy of the v03r1 one. Each change is marked `v04`.

1. **Every pixel is authored.** Both former underpainted bands are now drawn as explicit clusters, and the generated style reference is no longer opened. The underpainted share is **0** (v03r1: 20.16%).
   - **North of the L (rows 62–94):**
     - State St continues north past the intersection: calm asphalt, the lane line, a far stop bar and crosswalk one paint step dimmer for distance, the curb and the corner sidewalk.
     - Then three facades, each with one bay rhythm, lit from the west like the plaza:
       - a buff-terracotta Chicago-school block with Chicago windows (lighter sashes either side of a darker fixed pane, no 1 px mullions);
       - a recessive brick block with punched windows;
       - a limestone block one value down, with paired windows.
   - **Under the L (rows 135–165):** the same three buildings' storefronts, shop by shop. Each has a sign fascia with one calm lettering bar, piers, display windows, a door and a bulkhead. The lit shops sit over the existing ground light pools.
2. **The station is focal.** A new static layer, `station-platform-canopy`, holds:
   - the north platform: lit coping above the track deck, a glass windbreak, posts on the girder's 32 px stiffener rhythm, a teal glass roof with a warm fascia, and lamps;
   - a glazed head house straight above the State/Lake plate. Its lit hall is the brightest place in the strip, and its teal lintel is the strip's one strong accent.
3. **Quieter fictional plaza accents.**
   - **Medallion:** re-laid as a low-contrast granite-and-bronze inlay: setts one step apart (were three), a darker bronze ring and a mid granite field. The five line colours now form one segmented ring broken at the south, with a bronze star and no flag-blue bars.
   - **Fountain, pylon and dock:** their brightest teal values are recoloured one or two steps down in place, with identical alpha (101 px changed).
   - **Teal pools:** the pylon pool is removed and the dock pool is smaller.
4. **Theatre cue: considered, not added.** The Chicago Theatre (175 N State St) stands on the east side of State, south of Lake St. In this north-facing view that is behind the camera, south-west of the plaza. A vertical sign above the L would invert the geography. A State-St-axis or south-facing view would be needed for it.

**Unchanged, byte-identical to v03r1:**
- geometry and blocks;
- the walk mask and the occlusion reveal mask;
- every y-sort prop region, pivot and alpha channel;
- the hero-visibility report;
- the deck girder, the station plate, the stair and the kiosk;
- the three read-only sites and their zh/en text, the street labels, title, badge and help.

The scene script is the v03r1 script with only its header and art path changed.

## Opt-in path

The runtime Loop `.tscn` now points at a new selector, `game/scripts/…state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd`. This is a **one-line change to a tracked file**, still unstaged. The selector `extends` the unchanged v02 script:
- **no flag:** v02;
- **`-- --chicago-state-lake-v04`** (or `v04_override = 1`): the v04 scene;
- **`--chicago-state-lake-v03r1`:** still the untouched v03r1 scene;
- **`--chicago-state-lake-v03`:** still the untouched v03 scene.

Proof that default behaviour is unchanged:
- the v04 check's `en-default-off-v02-entry` render is 0 px different from v03r1's;
- the v02 check gives 42/42 (below).

To drop v04 only, point the one `path=` back at the v03r1 selector (`…selector_unapproved-v03r1_20261017-183235-a00fabf3.gd`).

## Comparison at actual 640×360

The figures come from real Godot zh approved-heroine reference captures (same spot and scale); en gives the same numbers. Edge and isolated-pixel figures use the v04 check's own implementation for every version.

| Measure | v02 | v03r1 | **v04** |
|---|---|---|---|
| Underpainted visible share | — | 20.16% | **0%** |
| Facade strip near-black share (luma < 40) | — | 40.1% | **0.8%** |
| Facade near-black specks ≤ 14 px | — | 23 | **12** |
| Facade strip edge density (rows 62–94) | — | 0.459 | **0.333** |
| Storefront band edge density (rows 135–165) | — | 0.571 | **0.510** |
| Medallion luma std / high-chroma px | — | 47.8 / 450 | **35.0 / 63** |
| Fountain / pylon bright-teal px | — | 51 / 34 | **5 / 6** |
| Strip focal window centre (plate at x = 326) | — | x 344, 386 lit px | **x 324, 609 lit px** |
| Lit stone share (C3 vs v02) | 28.95% | 33.21% | 33.23% |
| Foliage share | 4.08% | 6.93% | 6.62% |
| Teal civic light share | 0.53% | 1.30% | 1.01% |
| Whole-view edge density | 0.819 | 0.539 | 0.512 |
| Isolated single pixels | 16.24% | 3.44% | 3.27% |
| Art palette | — | 83 | 84 (+`gl0`, `gl1` glass; `aw0` no longer used) |

A side-by-side of the real zh entry captures, v03r1 above v04, is in `outputs/chicago-loop-state-lake-v04/…zh-entry-v03r1-over-v04-640x720_comparison_20261017-232210-1f83552b.png`.

**By eye at 1×:**
- **Better than v03r1.**
  - The strip above the L now reads as a street of three buildings, not mud.
  - State St visibly continues north through the intersection.
  - The lit head house over the plate is where the eye lands first.
  - The plaza no longer has a rainbow target competing with the station.
- **Trade-off.** v03r1's strip was warmer and more atmospheric (facade mean r − b 29.7 → 17.5). v04 is clearer but cooler and more diagrammatic.

## Known weaknesses

- **Schematic facades.**
  - The three facades are regular grids, and their tops are cut by the header, so there are no cornices or skyline.
  - At 1× they can look drafted rather than painted.
  - The teal-grey glass cools the strip against the low warm sun.
- **Storefronts.**
  - The lit display windows are large, nearly flat warm fills (science grammar rule 2 risk).
  - The sign bars are abstract.
- **Far crosswalk.** Its bars are not foreshortened, so it can read as a second near crosswalk.
- **Platform logic is loose.**
  - The canopy is an invented 2537 design, not CTA's 2021 plan.
  - It sits on the north side, while the stair climbs from the plaza (south) side, and no south platform is drawn.
- **Open info notes.** As in v03r1, an open note panel covers the strip.
- **K2 is weak evidence.** v03r1's brightest window also fell within tolerance (x 344), so K2 shows the station is now clearly the brightest place (609 vs 386 lit px) but does not by itself prove the difference.
- **Small metric drops.** Foliage and teal shares dipped slightly (pylon pool removed; teal-lit granite `tl1` counts under the foliage key). Both remain above v02.
- **Still open from v03/v03r1:**
  - the invented stair, medallion and fountain;
  - the small kiosk and dock;
  - the reveal dither in motion;
  - unreviewed note wording;
  - the largest single colour (7.9%).

**Iteration, disclosed.** The source-check thresholds were fixed before any v04 capture was measured. The first v04 art failed two of them:
- **F2:** facade edge density 0.574, from 1 px mullions, single-row bands and asphalt grain;
- **K2:** the pale limestone block at x 583 was the brightest place in the strip.

I simplified the art instead of changing the gates:
- tonal sashes instead of mullions;
- fewer single-row bands on the facades and the canopy;
- sparser asphalt;
- limestone one value down;
- a brighter lit hall in the head house.

Two superseded capture sets (`…231440-c37dbb2a`, `…231531-1285c106`) were deleted. Only `…232210-1f83552b` remains.

## Files (all new, except the one-line Loop `.tscn` change)

- **Author tool:** `tools/…state-lake-block-pixel-author_unapproved-v04_20261017-230650-c0d4b7f0.py`. Its manifest pins the v03r1 author under `pass_of`.
- **Godot check:** `tools/…state-lake-block-godot-capture-check_v04_20261017-230650-eb9dfc35.gd`.
- **Source check:** `tools/…state-lake-block-pixel-source-check_v04_20261017-230650-70f6da18.py`.
- **Runtime art:** `game/assets/environments/chicago-loop-state-lake-v04/`: 7 PNGs, each with its `.import`. Import settings are identical to v03r1's.
- **Scene:**
  - `game/scenes/…state-lake-block-scene_unapproved-v04_….tscn`;
  - `game/scripts/…state-lake-block-scene_unapproved-v04_….gd`;
  - the v04 selector `.gd`;
  - the two `.uid` files.
- **Editable source** (`outputs/chicago-loop-state-lake-v04/`):
  - `…layered-source_unapproved-v04_….pxo` (pxo_version 7) and `.ora`, with 12 visible layers plus the hidden, locked `guides-walkmask`;
  - the merged preview, the walk-mask guide and the 84-colour `.gpl`;
  - the layer manifest;
  - `…pixel-source-check-report_v04_20261017-232210-1f83552b.json`.
- **Captures** (`outputs/chicago-loop-state-lake-v04/godot-runtime/…640x360_v04_20261017-232210-1f83552b.png`), real Godot 4.7.2 windowed renders, 19 tags plus the visible-hero counts JSON:
  - flag off: `en-default-off-v02-entry`;
  - entry: `zh-entry`, `en-entry` (the real NYC→Chicago flight);
  - traversal: `zh-/en-traverse-under-l-lane`, `zh-/en-traverse-crosswalk`, `zh-traverse-stair-foot`;
  - occlusion: `zh-occlusion-column-raw`, `en-occlusion-column-reveal`, `zh-occlusion-honey-locust`;
  - interaction: the kiosk, stair and pylon in zh and en;
  - reference: `zh-/en-approved-heroine-ref`.

  The v03/v03r1 checks captured their `zh-traverse-under-l-lane` tag with the en UI still set. The v04 check switches to zh first.

## Tests

- **Build:** `python -I tools/…pixel-author_unapproved-v04….py` is deterministic: a temp rebuild matches every hash.
- **Godot:** `Godot --path game -s <abs>/tools/…godot-capture-check_v04….gd -- <abs out> <stamp> <abs walkmask> <abs reveal mask> --chicago-state-lake-v04` gives **`CHICAGO_LOOP_V04_OK checks=75`**. That is the 72 v03 checks retargeted at v04, plus:
  - the v03r1 opt-in still reaches v03r1;
  - the v03 opt-in still reaches v03;
  - both are off when only the v04 flag is given.
- **Source:** `python -I tools/…pixel-source-check_v04….py --capture-stamp 20261017-232210-1f83552b` gives **`CHICAGO_LOOP_V04_PIXEL_SOURCE_CHECK 22/22`**:
  - S1–S4, G1, G2;
  - G3: the Loop `.tscn` differs from HEAD only by the selector line;
  - **R1:** bounded pass:
    - v03 and v03r1 manifest hashes unchanged, and their tracked files clean against HEAD;
    - the base-author pin equals the HEAD blob;
    - y-sort alpha, walk mask, reveal mask, geometry, props and visibility equal v03r1;
    - y-sort colour changes appear only inside the fountain, pylon and dock regions;
  - **A1:** every pixel authored;
  - H1, C1 (Godot entry equals the y-sorted layers: 0 of 157,482 px differ), C2 (all 9 occlusion spots exact against the model), C3, C4, C5;
  - C6: not noisier than v03r1;
  - **F1, F2, K1, K2** (see the table);
  - P1/P2: the Pixelorama 1.2.3 CLI split-layers export is exact for `.pxo` and `.ora`, and the real APPDATA is untouched. A Pixelorama GUI from another session, PID 37584, was running and was left alone.
- **Regressions through the new selector:** all renders went to temp, and the originals were not overwritten.
  - The v03r1 check with `--chicago-state-lake-v03r1` gives **74/74**.
  - The v03 check gives **72/72**.
  - The v02 check with no flag gives **42/42**.
  - All 17 + 17 + 8 renders are **0 px different** from their original captures.
  - **The v02 check flaked once:** in the first batch it failed "held move_up … (y=180.1)" while three source checks loaded the machine. The final step depends on frame time. Rerun alone, it passed at y=179.3.
- **Shared headless smokes, all exit 0:**
  - `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`;
  - `M2_SMOKE_OK`, `M7_SMOKE_OK`, `GLOBAL_TRAVEL_CORE_OK`;
  - `M2_WHOLE_HOUR_TRAVEL_OK checks=246`;
  - `EXPORT_DATA_INCLUSION_SMOKE_OK checks=24`;
  - `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`;
  - `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=116` (v03r1 reported 114; the difference comes from other sessions' map work, not this pass).
- **Known string-match failures** (the behaviour is proven unchanged above):
  - v03r1 source check **17/18**: `G3` fails only on `runtime_scene_uses_selector`, because the Loop now names the v04 selector.
  - v03 source check **13/15**: the same `G3` failure, plus the old art-only `C3`.
  - v02 source check: **13/13**.

## Process notes

- **Import side effect.** Both Godot `--import` runs recreated `.import` files for another session's untracked female sideview v11 and v12 PNGs. Each time I deleted only those two `.import` files; the PNGs were left alone. `git status` was diffed before and after every import.
- **Concurrent index activity.** While this pass ran, another session staged about 80 files for its own selective sync: Yonkers v03, battle v12 and global map v03r2. None of them are mine, and I staged nothing. My only change to a tracked file, the Loop `.tscn` selector line, is unstaged. A broad `git add -u` would sweep it in.
- **Scratch work** stayed under `%LOCALAPPDATA%\Temp\chi-v04-work` and was removed at the end.
