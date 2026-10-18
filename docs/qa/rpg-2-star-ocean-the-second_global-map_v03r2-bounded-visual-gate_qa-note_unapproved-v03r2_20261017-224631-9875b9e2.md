# Global map v03r2: bounded visual gate (UNAPPROVED map art)

Date: 2026-10-17. Tag `v03r2_20261017-224631-9875b9e2`. Status: **unapproved map-art candidate**. This is the one visual pass the [v03r2 dispatch](../coordination/rpg-2-star-ocean-the-second_global-map-v03r2-claude-dispatch_unapproved-v01_20261017-224600-92f6c04d.md) asks for, on the targets in Codex's [v03r1 native judgment](rpg-2-star-ocean-the-second_global-map_v03r1-codex-native-visual-judgment_unapproved-v01_20261017-194711-66d8a7b4.md). It builds on the [v03r1 QA note](rpg-2-star-ocean-the-second_global-map_zoom-label-clamp_qa-note_unapproved-v03r1_20261017-184737-5ef3676e.md).

What this pass does not claim:
- No scene, sprite, map-art or M2 acceptance. M2 stays 10/12 and the meter 40.8%.
- Nothing is staged, committed or pushed.
- No Game Bible, completion ledger, Yonkers or character file was touched.
- There is no `AGENTS.md` in the repo or its parents. This pass followed the dispatch, the Codex judgment and the existing code.

Environment: Claude Code (Opus 5.5) signed in through claude.ai Max (first-party). `ANTHROPIC_API_KEY` was absent, and no API billing, credit or paid fallback was used. Only Godot processes this session started ran, and none were stopped by name.

## Changes, by Codex target

**1. Land / water value hierarchy (relief rebake plus runtime colours)**
- New bake `tools/…us-east-relief-bake_m2-map-art-native-v03r2_…py`, offline from the same 77 pinned tiles.
- Palette:
  - Land bands are lifted 12% toward parchment `#d8d2a8`, so they are lighter and a little less saturated (`COLOR_LAND` `#6d855c` → `#7a8e65`).
  - Sea shelf steps and `COLOR_OCEAN` are one step darker (`#0f2b38` → `#0d2632`).
  - Shadow inks are slightly deeper (0.24 / 0.40).
- Texture:
  - Shade speckle cleanup now needs 4 neighbours instead of 3.
  - Northeast thresholds are higher (t1 0.085).
  - The band dither margin is 0.14 instead of 0.22.
  - A 5-cell smoothing was tried first and rejected: it blurred the Pennsylvania ridge-and-valley into blobs.
- Geometry is unchanged: same grids, boxes and strip fit. Land, water and coast-band cells are identical to v03 (source check).
- Runtime:
  - Roads are quiet pale stone (major α 0.34, minor α 0.13) instead of gold, so the trip line is the only gold line.
  - The grid dots are fainter (α 0.16 → 0.12).
  - Regional views get a stepped 8-band edge shade under the grid, routes and markers.

**2. Northeast route and Great Lakes focal path**
- The trip line is heavier (5 px casing, 3 px gold) and has a gold chevron toward the destination.
- When the card's strip shows the origin (origin off the view or under the card), the map now draws the destination's end of the same line as a **focal path**. It is the true great circle for a flight, or a straight line for a car trip, with no road geometry. It runs from the reticle toward the origin and stops at the card edge, the frame, or 140 px. Its chevron points on.
  - Chicago flight card: it meets the card edge, so the eye travels Chicago → line → strip.
  - Reverse card (party in Chicago): a 140 px pointer west.
- Plates keep clear of the drawn trip line, so the Chicago plate moves off its route. The origin's own plate is exempt, because its line leaves from under it.

**3. Selected marker and card edge**
- The selected reticle is brass: a 1 px ring on a dark 3 px halo, with four brass ticks.
- The selected plate's slots start 4 px farther out. v03r1's Chicago plate cut 1.5 px into its ring (recorded 9.5 px vs ring 11).
- Opening a card pans the view by the shortest whole-pixel step **only if** the reticle would come within 14 px of a fixed control, the card or the frame edge.
  - Display only: markers stay on their coordinates, the zoom is kept, and nothing is charged.
  - At default zoom no card pans (checked).
  - Zoomed (1.5×) Washington pans 49 px up and sits clear of the view buttons; v03r1 had 10.4 px to the region button and 11.6 px to the frame edge.
- **Edge tabs:**
  - A place whose dot is just outside the frame (within 64 px) now gets a whole plate at the frame edge with a brass leader, instead of a half-clipped plate. In the zoomed card this is New York City, and the focal path points at it.
  - A place whose dot is under the card gets a brass pointer at the card edge, instead of v03r1's 3 px leader stub.

**4. Teal / brass science UI** (the clue-badge language of the exploration scenes)
- Card: brass rim, brass corner brackets, a teal header rule with a brass tab, and a teal inner bevel.
- Depart: brass-rimmed plate with brass text.
- Cancel: teal plate.
- Trip line: teal plate; the chosen option takes a lifted fill and a 3 px brass bar.
- `+`, `−`, Globe and region: square teal-edged plates. The current view reads as the active tab (lifted fill, brass text).
- Focus: a 1 px ring outside each plate.
- The header and footer buttons stay as on the exploration scenes.

**Unchanged:**
- Geography, place coordinates, routes, travel minutes, dates, modes, click and Depart handling, bilingual labels.
- `world_map_text.gd`, the route core and the travel data (equal to git HEAD).
- No airport naming.

## Captures: real Godot 4.7.2, native 640×360, windowed

Tool: `tools/…global-map_v03r2-visual-gate_capture-check_test-only-v03r2_…gd` gives `MAP_V03R2_VISUAL_GATE_OK 896 checks, 10 captures`. A second run reproduced all 10 byte for byte. Files are `outputs/rpg-2-star-ocean-the-second_global-map_v03r2_<state>-640x360_test-only-v03r2_20261017-224631-9875b9e2.png`, with the manifest and checks JSON beside them.

| State | zh (sha256 first 16) | en |
| --- | --- | --- |
| Globe | `globe-zh` `1cd32de87f71d0cf` | `globe-en` `b59bffb6bcd56be2` |
| Northeast browse | `us-northeast-zh` `6126c875053866ef` | `us-northeast-en` `35edcb3eb111159e` |
| Washington car card | `us-northeast-card-washington-car-zh` `61d4435a751e77a3` | `…-en` `1caed57033b53b8f` |
| Washington car card, 1.5× | `us-northeast-zoom-card-washington-car-zh` `e4c1a0702b1e2dda` | `…-en` `a337f4e326df50c1` |
| Chicago flight card | `us-great-lakes-card-chicago-air-zh` `db6c3d8583c68442` | `…-en` `bdc8093f859ed467` |

The tool checks, in zh and en:
- **Plates:**
  - in the frame and clear of fixed controls, the card, other markers and other plates;
  - click targets apart, both languages named, within 64 px of the marker;
  - a selected plate clear of its reticle;
  - rendered proof that the controls and card pixels are untouched by plates, and that every plate is drawn.
- **Reticle:** clear of controls, card and frame; all four ticks drawn; no pan at default zoom.
- **Trip line:**
  - drawn: at least 40% of samples along the path find gold, measured 65–100%;
  - it starts at the reticle;
  - the focal path stays left of the card and ends at an edge or its cap.
- **Card:**
  - brass, teal and option styles present;
  - opaque;
  - text at 10–11 px or more, inside CARD_RECT;
  - the Chicago card keeps every line.
- **Trips:**
  - pinned values: car to Washington 300 min, flight to Chicago 360 min;
  - date-only arrival, generic modes, whole hours;
  - no airport words;
  - previews, zooms, pans and language swaps charged nothing.
- **Coordinates:** the four places are pinned to the travel data.

**Before (same tool, temp copy of `game/` with the v03r1 scripts, sha256-text-lf-v1 `8fdc130c4a4500ec` = v03r1; [log](../../outputs/rpg-2-star-ocean-the-second_global-map_v03r2_before-v03r1-run_test-only-v03r2_20261017-224631-9875b9e2.log)):**
- Result: 22/896 fail.
- 14 failures are v03r2 features that v03r1 lacks.
- 8 are real v03r1 defects: the selected plate cuts into the reticle (Chicago, Washington), and the zoomed Washington reticle sits 10.4 px from the region button and 11.6 px from the frame edge.
- Its Northeast browse and Chicago captures are byte-identical to v03r1's pinned outputs.

**Measured values** (Rec. 709 luma of captured pixels on a 5 px grid away from UI, plates and coasts; zh, en within 0.001):

| | v03r1 | v03r2 |
| --- | --- | --- |
| Northeast land / sea | 0.523 / 0.193 (step 0.330) | 0.542 / 0.173 (step **0.369**) |
| Great Lakes land / lake | 0.523 / 0.313 (step 0.210) | 0.545 / 0.298 (step **0.247**) |
| Land texture (mean 1 px luma step), Northeast / Great Lakes | 0.0077 / 0.0055 | 0.0067 / 0.0037 |
| Relief speckle in the bake (land cells with a differing land neighbour), Northeast / Great Lakes | 0.397 / 0.371 | 0.326 / 0.255 |

## Regressions (Godot 4.7.2, final tree)

Summary log: [`outputs/…_v03r2_regressions_…log`](../../outputs/rpg-2-star-ocean-the-second_global-map_v03r2_regressions_test-only-v03r2_20261017-224631-9875b9e2.log). There was no `SCRIPT ERROR` in any log.

- **Headless:**
  - `GLOBAL_EARTH_MAP_SMOKE_OK 212`
  - `GLOBAL_MAP_TRAVEL_INTEGRATION_OK 114`
  - `GLOBAL_TRAVEL_CORE_OK`
  - `M2_WHOLE_HOUR_TRAVEL_OK 246`
  - `EXPORT_DATA_INCLUSION_SMOKE_OK 24`
  - `US_SCIENCE_MIGRATION_SMOKE_OK 32`
  - `COMMERCE_WEEKLY_SETTLEMENT_OK 149`
  - `M2_SMOKE_OK`, `M6_SMOKE_OK`, `M6_RESTART_OK`
  - `WORLD_MAP_VISUAL_CHECK_OK captures=0`
- **Windowed** (captures to temp):
  - `ROUTE_CARD_READABILITY_OK 119`. v03r1 had 117: the zoomed state now pans, so different degree labels are checked.
  - `STATUS_BACKING_READABILITY_OK 203`
  - `WORLD_MAP_VISUAL_CHECK_OK captures=2 buttons=3`
- **On a temp copy of the final `game/`:** the pointer regression and the two earlier tools write into `outputs/` or their own folders, so they ran there.
  - `CANVAS_POINTER_REGRESSION_OK` (real window clicks).
  - v03r1 zoom tool: `MAP_V03R1_ZOOM_LABEL_OK 449`. v03r1 had 503; New York's dot is now off-frame in the zoomed state, so that tool skips its plate.
  - v03 capture tool: **FAIL 5/1873, all expected:**
    - 4× "no route line on the map beside or under the card". This is v03's rule, which the focal path reverses on purpose: 211 gold px on the Chicago card, 231 on the reverse card.
    - 1× the v03 JSON's flat colours differ from the new `COLOR_LAND` / `COLOR_OCEAN`.
    - Its real Depart click still arrives in Chicago, is charged once in whole hours, and fires one `travel_completed`.
- **Source check** `tools/…v03r2-visual-gate_source-check_…py --cache-dir <tile cache>`: `SOURCE_CHECK_OK 40`.
  - The rebake is identical (sha256-text-lf-v1).
  - Palette roles and geometry match v03.
  - Tiles and attribution are unchanged.
  - The map text, route core and travel data equal git HEAD.
  - Roads are not gold.
  - The manifest matches the capture bytes.

## Files (local, unstaged)

| File | State | sha256-text-lf-v1 (first 16) |
| --- | --- | --- |
| `game/scripts/scifi_world_map.gd` | modified over v03r1 (+342 / −46) | `87489682dd3df423` |
| `game/scripts/world_map_data.gd` | `RELIEF_PATH` → v03r2 JSON (comment + 1 line) | `7e06250b9ba6e846` |
| `game/data/world-map/…us-east-relief-layer_m2-map-art-native-v03r2_….json` | new | `565d38e19ce9a1ec` |
| `tools/…us-east-relief-bake_m2-map-art-native-v03r2_….py` | new | `41107c71411741d1` |
| `tools/…v03r2-visual-gate_capture-check_test-only-v03r2_….gd` | new (test-only) | `426c951292b5d46e` |
| `tools/…v03r2-visual-gate_source-check_test-only-v03r2_….py` | new (test-only) | `e6ba0a6786ef7e9c` |
| `outputs/…_v03r2_*` | 10 captures, manifest, checks JSON, source-check JSON, regressions log, before-run log | see above |

## Open, for Codex's native judgment

1. **Focal path is a contract change.** v03 deliberately drew no map line while the strip shows. v03r2 draws a capped one. Codex should judge whether it clarifies or doubles the strip.
2. **The zoomed-card pan** moves the view 49 px when the card opens. It acts only when the reticle is boxed in, but it is still a view jump.
3. **Land is lighter and calmer.** The flat Great Lakes interior is now quieter still. The focal path, reticle and edge shade carry that view; no relief or features were invented.
4. **The edge shade** (8 bands, α 0.035 each) is subtle at 1×. It is visible mainly in corners.
5. **Globe:** only the controls and a darker sea changed. Sphere colours are as v01r1.
6. **Header and footer chrome** keep the exploration scenes' plain buttons, for consistency across screens.
7. The v03 and v03r1 tools now fail or skip by design, as listed above.

Reproduce (display needed, about 20 s): `work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to the v03r2 capture tool>`. Set `WB_MAP_V03R2_OUT=<folder>` to write elsewhere.
