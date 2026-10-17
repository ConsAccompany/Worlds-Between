# Global map: native 640×360 art pass (UNAPPROVED candidate)

Date: 2026-10-17. Status: **unapproved map-art candidate**. It answers the [first map-art gate brief](rpg-2-star-ocean-the-second_global-map_first-art-gate-visual-brief_unapproved-v01_20261016-231801-a4c79e20.md). The gate stays open until Codex and the creator have looked at the screenshots below.

No counters changed: the cloud meter stays **40.8%**, M2 **10/12**, accepted scene visuals **3/12**, complete sprites **0/52** and human playtests **0/2**. Nothing was staged or committed. Progress state, the Game Bible, room scenes and character art were not touched.

## What changed

It is a runtime art pass over the live map script. No pre-rendered skin is used, and the v01/v02 candidate assets are neither read nor changed.

1. **Value families.**
   - Sea is dark `#102f3d`.
   - Inland lakes (the geodata's hole rings) get their own mid value, `#2f6476`. Lakes used to share the sea colour.
   - Land is a lighter sage, `#677a59`.
   - These apply to the globe, both regional views and the route inset.
2. **Relief from real elevation data.** A baked relief layer covers the `us_east` geodata box. It is a 1728×966 palette PNG inside a 172 KB JSON file.
   - Land: four elevation bands (<120 m, <230 m, <450 m, higher), each with NW-lit hillshade.
   - Sea: an inner (> −60 m) and an outer (> −200 m) coastal shelf.
   - It is masked by the map's own Natural Earth land and lake rings, so relief never crosses a drawn coast.
   - The elevation is smoothed over 3 cells, and isolated shade pixels are dropped. Only coherent landforms remain: the Valley-and-Ridge arcs, the Allegheny Front, the Poconos, the Catskills, the Adirondacks, and the Lake Chicago plain and moraine steps.
   - It is drawn as one texture per regional land layer with nearest filtering, so the pixels stay crisp.
   - The source is the Tilezen/Mapzen Terrarium z7 tiles; their headers list only SRTM, GMTED2010 and ETOPO1 files (corrected 2026-10-17, see the correction below). Attribution: <https://github.com/tilezen/joerd/blob/master/docs/attribution.md>. Each tile's sha256 is recorded in the layer JSON.
   - No terrain, borders, airports or roads were invented.
3. **Quieter grid.**
   - Grid alpha went from 0.75 to 0.10, and the equator from 0.9 to 0.22.
   - Degree labels use a dimmer tone. Latitude labels take priority; a longitude label that would print over one is left out. The new frame put 41°N on the longitude row, where it overprinted 71°W.
   - The measured luma step across a sea meridian fell from **0.104** (HEAD capture) to **0.045**.
4. **Labels.**
   - Name plates gain a 1 px edge in the status-panel style.
   - The registry's display sides changed: New York City is now `below_left` and Yonkers is `above_right`. Their plates sit diagonally apart (37 px gap at the default view) instead of stacking.
   - The Northeast `frame_px` is now `[205, 38, 207, 178]`, and the pan box's east edge is 70.0°W instead of 70.5°W. Scale stays near the old value, so the New York City and Yonkers dots stay 19 px apart. Their click targets never overlap, which the earth-map smoke requires.
   - With the card open, the selected New York City ring sits 7.8 to 9.8 px clear of the card and the Yonkers dot 6.5 px clear. Before, the Yonkers dot touched the card edge.
   - Washington stays right of the view buttons.
   - Coordinates are unchanged.
5. **Chicago route inset.**
   - Size goes from 190×94 to 196×108, with a header strip: "飞行路线 / Flight path", or "车行路线 / Drive route" for a car trip.
   - It has a 2 px drop shadow, a gold flight path (6/3 dashes, 2 px core on a 4 px dark casing) and a larger white aircraft.
   - It uses the same lake and sea palette as the map.
   - Its place, mode, distance and scale texts are unchanged and still match the card.

Route preview, confirm and cancel, whole-hour durations, date-only arrivals, the calendar, saves and the route adapter contract are not modified.

## Files (local, unstaged)

| File | State | sha256 (text-LF / bytes), first 16 |
| --- | --- | --- |
| `game/scripts/scifi_world_map.gd` | modified | `1fe3feac71daca37` |
| `game/scripts/world_map_data.gd` | modified (relief loader) | `d2445b332ab1d7a6` |
| `game/scripts/world_map_text.gd` | modified (+2 bilingual keys) | `631910917605c4c6` |
| `game/data/world-map/…place-registry_m2-us-science-v02_…eeaa6baa.json` | modified (label sides, NE frame and pan box, note) | `e66d1ec923c1b430` |
| `game/data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v01_20261017-015515-7bf04753.json` | new | `2e4c870159d3c2fd` |
| `tools/rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-v01_20261017-015515-aa01b973.py` | new (bake tool) | `80e73aff2b327987` |
| `tools/rpg-2-star-ocean-the-second_global-map_native-art-pass_capture-check_test-only-v01_20261017-015515-1f607c6e.gd` | new (capture and check) | `f2fdfc6125decc24` |

## Evidence: real Godot 4.7.2, native 640×360, windowed

All captures are in `outputs/`. Each name is `rpg-2-star-ocean-the-second_global-map_native-art_<state>-640x360_test-only-v01_20261017-015515-1f607c6e.png`.

| State | zh | en |
| --- | --- | --- |
| (a) Northeast browse: NYC, Yonkers, Washington | `us-northeast-zh` (`935d0ac08c1a4a63`) | `us-northeast-en` (`c91b4d3bdbc6f680`) |
| (d) Car route card, NYC → Washington | `us-northeast-card-washington-car-zh` (`92cb95d689647b6d`) | `us-northeast-card-washington-car-en` (`39140119ca7b233e`) |
| (b) NYC → Chicago flight card and inset | `us-great-lakes-card-chicago-air-zh` (`1bec4e4df769fc7f`) | `us-great-lakes-card-chicago-air-en` (`35b3db0270ed3ba8`) |
| (c) Chicago → NYC return card and inset (after a real Depart) | `us-northeast-card-nyc-from-chicago-air-zh` (`1fe7566424ef6dd2`) | `us-northeast-card-nyc-from-chicago-air-en` (`7a0448c0a668b6ce`) |
| Globe (palette only) | `globe-zh` (`6da5282e591095bf`) | `globe-en` (`4a3b69500982aa4f`) |

The checks are in `outputs/rpg-2-star-ocean-the-second_global-map_native-art_checks_test-only-v01_20261017-015515-1f607c6e.json`: **NATIVE_MAP_ART_OK 1291 checks, 10 captures, 0 failures** (checks JSON text-LF sha256 `a598408b5591d872`). They cover:
- markers on their travel-data coordinates;
- degree labels that never print over each other;
- click targets and plates that never overlap;
- markers clear of fixed controls and the card;
- whole-hour durations, date-only arrivals and no airport words on the card or inset;
- inset geometry, header and gold-pixel count (235 to 247 px);
- real mouse clicks (Washington and Chicago markers, inset click-through, Cancel);
- one real Depart that charges the card's whole hours exactly once.

Measured luma means on the live frame, sampled on an 8 px lattice away from coasts and UI:

| View | Land | Lake | Sea |
| --- | --- | --- | --- |
| Northeast | 0.474 | — | 0.210–0.211 |
| Great Lakes | 0.475 | 0.353 | — |

Northeast land shows 11 distinct sampled colours from the relief.

## Focused regressions (Godot 4.7.2, final tree)

**Headless:**
- `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
- `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=106` (105 on the first run of this session; the test file itself is unchanged)
- `GLOBAL_TRAVEL_CORE_OK`
- `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
- `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` (the new relief JSON is under `data/`)
- `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
- `M2_SMOKE_OK`
- `M6_SMOKE_OK`
- `M6_RESTART_OK`

**Windowed:**
- `ROUTE_CARD_READABILITY_OK 117 checks` (captures sent to temp). A first dedupe that dropped latitude labels failed 8/117 ("latitude labels kept beside the card"), and it was fixed before this run.
- `STATUS_BACKING_READABILITY_OK 203 checks` (captures sent to temp; 205 before the degree-label dedupe, since its per-label checks count drawn labels)
- `GLOBAL_MAP_CAPTURE_OK 22`. Its 22 stamped PNGs were moved out of `outputs/` to a temp folder. This ran before the degree-label dedupe and was not repeated.

**Not passing:**
- `scifi-world-map_background-visual-check` fails with `button geometry scifi.city`. This is the same failure it gives at HEAD: old hard-coded pre-migration geometry. It is not caused by this pass.
- The 5a17c3e9 route-inset tool was **not** rerun. Its inset pixel check counts the old white line. A rerun would also overwrite its stored captures, which the pushed 5a17c3e9 QA note cites. The new tool replaces its checks.

## Remaining visual defects and open questions

1. The Great Lakes view is still a mostly even green field around Chicago. This is true geography (the lake plain is flat). Only subtle band steps show there, so the Chicago card frame stays visually quiet.
2. The relief grid has 64 cells per degree and is drawn with nearest filtering, so it does not map 1:1 onto screen pixels. At the default zoom some cells double or drop, and at the 6× maximum zoom each cell becomes a 6 px block. It is not hand-cleaned pixel art.
3. The degree labels are dim, alpha 0.62. They are readable, but they are low-contrast over relief. In the Northeast view, 72°W touches a small island east of Long Island, and 71°W is hidden on the 41°N row.
4. The inset header is 9 px gold text. It is legible at 1×, but small.
5. Margins are tight by design: the New York City ring is 7.8 px from the card, the Yonkers dot 6.5 px, and Washington's selected ring 1.5 px from the view button. A future frame or zoom change needs to recheck them.
6. In the return view, the inset covers central Pennsylvania. This is intended: the inset is the route proof.
7. The 1 px light coast line also outlines the lakes. A softer lake shore could be tried.
8. The globe changes only in palette. Its region boxes and labels are as before.
9. The v01/v02 map-art candidate manifests record the registry's old hash, so their checkers will now report drift. Those candidates stay unapproved and unchanged.
10. The relief source carries an attribution requirement (Tilezen sources list). Codex should confirm this is acceptable next to the public-domain Natural Earth data.

## Reproduce

From the repo root:
- **Bake** (about 15 s; downloads 77 tiles into a temp cache): `python -I tools/…us-east-relief-bake_…aa01b973.py --cache-dir <temp dir>`.
- **Capture and check** (about 40 s, needs a display):
  ```
  work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <abs path to tools/…native-art-pass_capture-check_…1f607c6e.gd>
  ```
  Delete this tag's outputs before re-capturing.

## Correction (2026-10-17, map-art v02)

This note first listed USGS NED/3DEP among the relief sources. No baked tile's `x-amz-meta-x-imagery-sources` header lists a 3DEP/NED (or CDEM) file; they list only SRTM, GMTED2010 and ETOPO1. The source line above, the relief JSON's `attribution` string and the bake tool's docstring and `attribution` string were corrected in place. Their sha256 values in the Files table are therefore the pre-correction values. The corrected values (first 16) are: relief JSON `62511f95bbf5231d`, bake tool `ed55dbd949e691bf`. The PNG layer and every other field are unchanged. The runtime no longer reads this layer; see [native art pass v02](rpg-2-star-ocean-the-second_global-map_native-art-pass_qa-note_unapproved-v02_20261017-165006-dacc5102.md).
