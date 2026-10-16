# NYC → Chicago air-route inset — test-only visual candidate (QA note)

- **Status:** TEST-ONLY visual candidate, **unapproved**. No runtime file was edited. M2 stays unaccepted. The MVP meter, stage and Game Bible state are unchanged. Nothing was staged or committed.
- **Answers:** [NYC–Chicago air corridor visual audit](rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-corridor_visual-audit-unapproved-v01_20261016-064519-bb294d29.md). With Chicago selected, the Great Lakes view showed only Chicago. The card read "From: New York City · Air · Flight 1177.1 km", but nothing on the map showed the trip's direction or span.
- **Worker:** Claude (signed-in Claude Max, `firstParty`). No API key, paid API, credits or generation service was used. Every image is a real Godot 4.7.2 render (Compatibility, NVIDIA RTX 3080), with no `--headless`.

## Source

`tools/rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-inset_visual-test-candidate_test-only-v01_20261016-065443-adea3798.gd` (sha256 `d2a61126…bde9f73e9`).

```
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to the tool> -- v01r1
```

The tool opens the real `scifi_world_map.tscn` from a fresh run at New York (2537-05-25 08:00). It selects Chicago in the Great Lakes region and picks the core's air option. It then adds an `AirRouteInsetTestOnly` Control to the live map's `MapFrame` at run time. Everything the inset shows comes from the running game:

- Endpoint coordinates and labels come from `map.find_place()` (world-travel data) and `MapData.text(place, "map_label", lang)`.
- Land and lakes come from the shared `us_east` geodata layer (`region_land_rings`).
- The caption reuses only existing `MapText` strings: `mode_air` plus `air_km`, with the figure taken from the selected core option. **No new player-facing text was added.**
- The inset shows only while the NYC→Chicago card is open with an air or air+car option selected, and hides when the card closes.

Design:

- **Inset position:** a 190×94 canvas-px box (canvas rect 200,194 → 390,288). It sits left of the route card, below the Chicago marker label and above the main map's scale bar. The regional camera, markers and card are untouched.
- **Projection:** equidistant cylindrical, centred on the city midpoint, 7.57 km/px. The cities are 151 px apart.
- **Air line:** the true great circle (slerp), drawn dashed (4 on / 3 off) in pale ice-white with a dark edge. It bows 3 px north of the chord. A small plane glyph at mid-route points west, toward Chicago. This stroke and icon language is deliberately separate from the solid amber road strokes the region view uses for roads.
- **Endpoints:** New York gets the gold party-here ring and Chicago the white selected ring, matching the map's own marker language.

**Revision (once, as allowed):** v01 passed every automated check, but the visual review found two problems, which v01r1 fixes:

1. The bare endpoint labels sat on the coastline. At 640×360, "New York City" ran over the Long Island coast. v01r1 puts them on dark backing plates, the same `COLOR_LABEL_BG` style the map markers use.
2. The main map's "100 km" bar sits 14 px below the inset, so it read as the inset's scale (the inset is about 7.6× smaller in scale). v01r1 adds the inset's own 250 km bar at the left of the caption row and right-aligns the caption.

The rectangle, label sides and arc are unchanged. **v01r1 is the candidate.** v01 is kept for comparison.

## Captures (`outputs/`, all `…_test-only-v01_20261016-065443-adea3798.png`)

| Variant | zh 1280×720 | en 1280×720 | zh 640×360 | en 640×360 |
|---|---|---|---|---|
| **v01r1 (candidate)** | `…air-inset_v01r1-zh-1280x720_…` | `…air-inset_v01r1-en-1280x720_…` | `…air-inset_v01r1-zh-640x360_…` | `…air-inset_v01r1-en-640x360_…` |
| v01 (pre-revision) | `…air-inset_v01-zh-1280x720_…` | `…air-inset_v01-en-1280x720_…` | `…air-inset_v01-zh-640x360_…` | `…air-inset_v01-en-640x360_…` |
| Baseline, inset hidden, same frame | `…v01r1-baseline-no-inset-zh-1280x720_…` | `…-en-1280x720_…` | `…-zh-640x360_…` | `…-en-640x360_…` |

The full prefix is `rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-inset_`. The check reports are `…air-inset_checks-v01r1_…json` (108/108) and `…air-inset_checks-v01_…json` (102/102). All 8 v01r1 PNGs and all 4 zh/en × 2-size candidate frames were opened and inspected. The zh 1280 and en 640 insets were also inspected as 2× crops.

## Checks (v01r1: `AIR_INSET_OK v01r1 108 checks, 8 captures`, exit 0)

- **Route state:**
  - The card status is `ready`, from `earth.us.ny.new-york-city` to `earth.us.il.chicago`, with `route.air.nyc__chicago` selected (mode `air`).
  - The core's air figure is 1177.1 km. The great circle between the travel-data coordinates is 1144.5 km, so the core figure is 2.8% longer. That is plausible for a flight track, and the core figure stays a labelled estimate.
  - The caption shows the core's 1177.1 km in both languages: "飞机 · 航程 1177.1 km" / "Air · Flight 1177.1 km".
- **Path:**
  - The arc starts on New York's projected coordinates and ends on Chicago's (< 0.01 px).
  - It runs monotonically west and stays at least 6 px inside the inset map area.
  - It bows north of the chord, has ≥ 10 dashes, and the plane glyph points west.
- **Collision:** checked in both languages. The inset clears all of the following:
  - the route card;
  - the status panel;
  - the +/−, Globe and Great Lakes buttons;
  - the calendar label;
  - the scale bar and its text;
  - the header and the bottom strip;
  - the Chicago marker button;
  - every regional degree label (`annotation_label_rects()`, including 41°N at the card edge).

  It lies fully inside `MapFrame`. Inside the inset:
  - each endpoint label stays inside the map area and clears the arc, the plane and the other endpoint;
  - the two labels don't overlap;
  - the caption fits (zh 90 px / en 91 px of 182);
  - the 250 km bar (33 px) clears the caption, and its length matches the projection.
- **Legibility:**
  - Endpoint labels are 10 canvas px (20 px at 1280×720) and the caption is 9 px.
  - Contrast on the inset background is 17.1:1 for text and 10.3:1 for subtext.
  - Pixel checks on every rendered frame found the dashed line (219–1335 light pixels, depending on size) and the inset border.
- **Click** (real `InputEventMouse*` pushed through the window at 1280×720):
  - Clicking the Chicago marker opens its card, and the inset appears.
  - A click in the middle of the inset changes no route state, preview or camera and charges no time. The inset is `MOUSE_FILTER_IGNORE` all the way down.
  - The Depart button isn't covered.
  - Clicking Cancel closes the card, clears the core preview and hides the inset.
- **No calendar charge:** `calendar_minutes` stayed at 298421760 (2537-05-25 08:00) from start to end, and the party stayed at New York. `calendar_advanced` and `travel_completed` fired 0 times. No travel preview was left pending. Depart was never pressed.
- **Runtime untouched:**
  - Comparing `git status` before and after showed only this tool's outputs, plus unrelated files from other sessions (`mvp-progress_state…json` modified, a female battle-static v06 audit added). No `game/` path changed and no `.uid` was written.
  - `global-map-travel_integration-regression` (headless) passed: `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=105`.

## Visual findings (v01r1)

- **Resolved:** the trip now has a visible origin, direction and span on the card view. It reads New York (gold here-ring, east) → dashed great-circle → Chicago (selected ring, west), with the Great Lakes for orientation, in both languages at both sizes. The labels are now on plates, and the inset's own scale bar removes the 100 km ambiguity.
- **Residual, not revised:**
  - At 640×360 the plane glyph is only about 5 px and reads as an arrowhead. The direction is still clear.
  - The "250 km" text baseline sits about 1 px lower than the caption's.
  - The inset duplicates Lake Michigan close to the real one on the main map. The border and the scale bar separate them, but an art pass might prefer a darker or desaturated inset land tone.
  - The inset covers some empty Illinois/Indiana land on the main map; no marker or label is hidden.
- **Not done:** the globe view still has no air arc. At minimum zoom the two cities are only about 23 px apart there, so an arc would add little. That is left for an art decision.

## Integration path (if approved later — not done here)

This would need a map-art owner and creator approval:

- move `AirInset` into `scifi_world_map.gd`, or into a small sibling script;
- gate it on `route_state` (ready, with an air or air+car option);
- extend `global-map-route-card_readability-check` with the collision list above.

No new strings are required.
