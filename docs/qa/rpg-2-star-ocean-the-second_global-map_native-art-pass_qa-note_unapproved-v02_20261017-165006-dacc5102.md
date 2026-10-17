# Global map: native art pass v02, relief depth, route focus and source correction (UNAPPROVED candidate)

Date: 2026-10-17. Status: **unapproved map-art candidate**. It answers the [first map-art gate brief](rpg-2-star-ocean-the-second_global-map_first-art-gate-visual-brief_unapproved-v01_20261016-231801-a4c79e20.md) and Codex's review of [v01r1](rpg-2-star-ocean-the-second_global-map_native-art-pass_qa-note_unapproved-v01r1_20261017-022144-f9b0d28b.md). That review found the geography and the five sphere colours functional, but the regional land and water flat and the UI closer to a technical planning screen than to the accepted science-region scenes.

The map-art gate stays open. Codex makes the visual judgment before creator review. No counter changed: M2 stays 10/12 and the MVP estimate stays 40.8%. The progress state, Game Bible, Chicago and Washington rooms, City Hall, character art and the Git index were not touched. Nothing was staged, committed or pushed.

This pass ran in Claude Code (Opus 5.5) signed in through claude.ai with a Max subscription (`apiProvider: firstParty`). `ANTHROPIC_API_KEY` was not set, and no quota or auth error occurred.

## What changed (one pass)

1. **Relief and water depth, from the existing sourced data only.**
   - The v02 relief layer replaces v01's single 64 × 84 cells-per-degree grid. It has three layers, each baked so that one cell is exactly one screen pixel at its view's default zoom (measured 1.0000 × 1.0000):
     - `us_northeast`: 706 × 635 cells;
     - `us_great_lakes`: 647 × 698 cells;
     - `route_inset`: 308 × 175 cells, area-averaged over 6 × 6 samples, for the NYC ↔ Chicago inset frame.
   - This removes v01's doubled and dropped relief cells (v01 defect 2).
   - **Land:**
     - seven hypsometric bands from real elevation: < 100, 200, 300, 450, 700 and 1000 m, and above;
     - each band has five hillshade tones (deep shadow, shadow, flat, lit, high lit; light from the north-west);
     - band edges use a 2 × 2 ordered dither;
     - shade specks with fewer than three like neighbours are removed.
   - The ridge-and-valley Appalachians, the Catskills and Poconos, and the Allegheny front now read at 1×. The Great Lakes view stays quieter because the land there is genuinely flat.
   - **Sea:** shelf depth from real bathymetry: > −20 m, > −60 m and > −200 m. Deeper water is the flat `COLOR_OCEAN`. A three-cell shore band follows the map's own Natural Earth coastline.
   - **Lakes:** a three-cell shore band from the same lake rings. No lake bathymetry is claimed.
   - **Coast:** one transparent cell on each side of every coast and lake shore, so the map's own polygons and coast line own the exact edge. The coast line is now pale sand `#c4c194`, so shores read as beaches.
   - **Flat colours:**
     - sea `#0f2b38` (was `#102f3d`);
     - lake `#2c6375` (was `#2f6476`);
     - land `#627856` (was `#677a59`).
   - **Measured value families on the live frame:**

     | View | Land luma | Sea luma | Lake luma | Distinct land colours sampled |
     | --- | --- | --- | --- | --- |
     | Northeast browse | 0.479 | 0.194 | — | 24 (v01r1 sampled fewer; its threshold was ≥ 5) |
     | Great Lakes card | 0.474 | — | 0.347 | 10 |
     | Northeast reverse card | 0.486 | 0.228 | — | 22 |

2. **Grid stepped back.**
   - The graticule is now 1 px dots every 4 px, at alpha 0.16 (equator 0.30).
   - Measured weight at the −72° meridian at sea, with shelf texture subtracted: 0.0197 mean luma step, against 0.0445 for the v01r1 solid line in the same column and frame.
   - Degree labels are dimmer (alpha 0.50). The label logic is unchanged, so the readability test's latitude-label count still holds.
3. **Labels: clearer NYC / Yonkers.**
   - Each plate has a 2 px kind accent (teal for cities, slate for other places), a slightly more opaque plate and a 1 px leader from the marker rim to the plate.
   - Markers follow the scenes' badge style: a navy disc, a teal core and a 1 px shine. Cities are one size larger (Yonkers' dot is smaller than New York City's).
   - The NYC / Yonkers plates stay 37 px apart, as in v01r1, in both languages.
4. **Selected-city and route focus.**
   - The selected place gets a white ring with four gold ticks, all inside the 11.5 px radius the layout checks use. Its plate edge and accent turn gold.
   - While a card is open, the other places' names step back to the subtext colour. Their plates, markers and click targets are unchanged.
   - A car trip with both ends on the view (New York → Washington) draws a dotted gold connector with a dark casing between the two markers. It is a straight schematic line, as in the inset, with no road geometry.
5. **NYC ↔ Chicago flight inset, made decisive.**
   - A gold frame with a dark inner line and a gold rule under the header.
   - A pixel aircraft glyph before "飞行路线 / Flight path".
   - The inset's own relief layer, at one cell per inset pixel.
   - A 3 px gold flight path on a 5 px casing: 370–381 gold pixels, up from at least 120.
   - Badge endpoints: the party's gold ring at the origin, and the selection ring with ticks at the destination. Edged name plates.
   - Fixed: the header label was 23 px tall in v01 and v01r1, because it was sized before the inset entered the tree. The text sat on the rule. It is now 13 px and checked.
6. **Chrome and card.**
   - 1 px rules where the header and footer meet the map.
   - The route card has a header band behind the place names, an inner bevel line and a 2 px drop shadow outside its own rectangle. The card stays opaque and CARD_RECT-sized, as the readability test requires.
   - The palette is the scenes' navy `#0d1723`, teal `#79cfc0` and gold `#f0d68a`.
7. **Globe.**
   - The coastline is a dark outline (alpha 0.6), because the sand line speckled at 110m detail.
   - The grid is dotted.
   - The five sphere colours are unchanged and measured the same as r1: science `#5f8f76`, magic `#7e6d96`, wuxia `#97695a`, nature `#86904c`, culture `#a08b63`.

Preserved and re-checked:
- real coastlines (the same Natural Earth rings) and marker coordinates;
- the five sphere colours;
- the Chicago inset route proof (arc endpoints on the travel coordinates, a dashed great circle, the aircraft pointing at the destination, caption distance equal to the card's);
- all click targets;
- whole-hour travel and date-only UI;
- bilingual card facts;
- Save, Depart and Cancel.

No airport names, schedules, times of day, fantasy borders or invented terrain were added.

## Source correction (3DEP/NED overclaim)

- **Observed sources.** At bake time, the v02 bake tool reads the `x-amz-meta-x-imagery-sources` header of each of the 77 z7 tiles. All 77 tiles' sha256 values match the v01 pins. The headers list only `srtm`, `gmted` and `etopo1`. The bake fails if any other source family appears.
- **v02 relief JSON:**
  - `observed_imagery_source_families`: `["etopo1", "gmted", "srtm"]`;
  - each tile's own families are recorded;
  - the attribution lines are "Mapzen", "Global ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration" and "Global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological Survey.";
  - an `attribution_note` says why Tilezen's 3DEP clause is omitted.
- **Why the wording is adapted.** [Tilezen's attribution page](https://github.com/tilezen/joerd/blob/master/docs/attribution.md) gives its lines as example language and asks users to follow each source's terms. Its USGS line combines "United States 3DEP (formerly NED) and global GMTED2010 and SRTM". Only the 3DEP clause was dropped; the provider credits for Mapzen, USGS and NOAA all remain.
- **In game.**
  - The credits panel (zh and en) uses the corrected USGS line and states that the tiles hold only SRTM, GMTED2010 and ETOPO1 data.
  - The relief plate still reads "地形数据：Mapzen · USGS · NOAA" / "Relief data: Mapzen · USGS · NOAA".
  - The checks confirm by real click that the panel names every required provider and contains no "3DEP", "NED" or "CDEM".
- **v01 records corrected in place:**
  - the relief JSON's `attribution` string (sha256 `2e4c870159d3c2fd` → `62511f95bbf5231d`);
  - the v01 bake tool's docstring and `attribution` string (`80e73aff2b327987` → `ed55dbd949e691bf`);
  - the v01 QA note's source line, with a correction section listing these hashes;
  - a one-line pointer added to r1 defect 7.

  The v01 PNG layer and every other field are unchanged. The runtime no longer reads the v01 layer.

## Files (local, unstaged)

| File | State | sha256 (text-LF / bytes), first 16 |
| --- | --- | --- |
| `game/scripts/scifi_world_map.gd` | modified (palette, dotted grid, markers, plates, leaders, connector, card dressing, chrome rules, inset art and header fix) | `3abb64b9a1a45b80` |
| `game/scripts/world_map_data.gd` | modified (`RELIEF_PATH` v02; `region_relief(layer_id)` per view) | `a9bbef41ae12957c` |
| `game/scripts/world_map_text.gd` | modified (`credits_body` zh/en: corrected USGS line) | `68400bef1ac32496` |
| `game/data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v02_20261017-165006-dacc5102.json` | new (3 layers, observed sources) | `9050fc4e2d992ac7` |
| `tools/rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-v02_20261017-165006-dacc5102.py` | new (bake) | `9bc02ea14d7f8da7` |
| `tools/rpg-2-star-ocean-the-second_global-map_native-art-pass_capture-check_test-only-v02_20261017-165006-dacc5102.gd` | new (fork of the r1 tool) | `7a8628207ee4c5c1` |
| v01 relief JSON / v01 bake tool / v01 QA note / v01r1 QA note | modified (source correction only) | see above |

The layer PNGs' sha256 values (first 16) are:
- `us_northeast` `0d441be206ab1515`;
- `us_great_lakes` `5614554ed4146f78`;
- `route_inset` `abae7f9e8e38031b`.

## Evidence: real Godot 4.7.2, native 640×360, windowed

Captures are in `outputs/`, named `rpg-2-star-ocean-the-second_global-map_native-art_<state>-640x360_test-only-v02_20261017-165006-dacc5102.png`. The capture manifest lists each one with its full sha256: `outputs/…native-art_capture-manifest_test-only-v02_20261017-165006-dacc5102.json`.

| State | zh | en |
| --- | --- | --- |
| Globe | `globe-zh` (`29761e7c1ccbfba1`) | `globe-en` (`cc0c6baa35fb4e17`) |
| Northeast browse | `us-northeast-zh` (`a674fee0075b4fd1`) | `us-northeast-en` (`b9dd228e8ab40d46`) |
| Car card, NYC → Washington | `us-northeast-card-washington-car-zh` (`651715300e2f9316`) | `…-en` (`5b559f219b2dcda5`) |
| NYC → Chicago flight card and inset | `us-great-lakes-card-chicago-air-zh` (`fc374a3333d797fa`) | `…-en` (`4bc82a980f133fbe`) |
| Chicago → NYC return card and inset | `us-northeast-card-nyc-from-chicago-air-zh` (`d80dba9bf9677950`) | `…-en` (`43fe8748fea379b0`) |
| Map credits panel | `map-credits-zh` (`6defe8c8eb90ae22`) | `map-credits-en` (`13fe57522eacd37a`) |

**Checks:** `outputs/…native-art_checks_test-only-v02_20261017-165006-dacc5102.json`, **NATIVE_MAP_ART_OK 1783 checks, 12 captures, 0 failures**. A second full run reproduced all 12 captures byte for byte (see "Reproducibility"). The run includes all r1 checks, adapted, plus:
- **Relief:**
  - the v02 relief JSON schema;
  - observed sources ⊆ {SRTM, GMTED2010, ETOPO1};
  - 77 tiles pinned;
  - no 3DEP/NED/CDEM claim;
  - flat colours equal to the map constants;
  - one texel per screen pixel on both regional views and in the inset.
- **Value families:** land at least 0.15 luma above sea and at least 0.08 above lakes; lakes at least 0.08 above sea; at least 12 distinct land colours where sea is sampled.
- **Grid:** dotted, with the weight above; still visible (peak step 0.086).
- **Card focus:** gold plate edge and full-white name for the selected place, stepped-back names for the others, all still clickable.
- **Pixels:** reticle ticks on the selected marker in all six card captures; the car connector (20 of 39 samples gold, with gaps); at least 200 gold pixels on the inset flight path; a gold top edge on the inset frame; the header text box inside its strip.
- **Real clicks (from v01r1):** markers, Cancel (no charge), the inset (inert), credits and Back, and Depart (charged once, whole hours, exactly one `travel_completed`).
- **New real click:** the header Save button opens `save_screen.tscn` in save mode, returning to the map, with no time charged.

## Regressions (Godot 4.7.2, final tree)

**Headless:**
- `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
- `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=108`
- `GLOBAL_TRAVEL_CORE_OK`
- `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
- `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`
- `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
- `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149`
- `M2_SMOKE_OK`, `M6_SMOKE_OK`, `M6_RESTART_OK`

None of these logs contains a `SCRIPT ERROR`. The integration count is 108; r1 recorded 106 in the dirty tree and 105 in a clean one, and the count follows the shared working tree.

**Windowed:** `ROUTE_CARD_READABILITY_OK 117 checks` and `STATUS_BACKING_READABILITY_OK 203 checks`, with captures sent to a temp folder.

**Pre-existing failure:** `scifi-world-map_background-visual-check` fails with `button geometry scifi.city`. It fails identically on a clean `git archive HEAD` export, so the cause is its stale marker geometry, not this pass. Do not report this as all-pass.

## Remaining defects and open questions (candid)

1. **Still partly a planning UI.** The regional land and water are no longer flat, and the inset now reads as the route. The rest still reads as UI rather than scene art:
   - the route card's body (stacked label lines, an option box, Depart/Cancel);
   - degree labels, the scale bar and the credit plate;
   - stock-theme zoom and view buttons.

   These buttons match the scenes' header buttons, but they are not map-specific art. Whether this is now close enough to the accepted science scenes is Codex's call. The brief asks for one pass, so I stopped here rather than make more micro-variants.
2. **The Great Lakes view is still low-contrast.** Illinois and Indiana are genuinely flat. Only 10 distinct land colours are sampled there, against 24 in the Northeast. The moraines and the lake shore band carry the view; nothing was invented.
3. **The car connector is a straight schematic line.** New York → Washington crosses the Delaware valley. It could be read as an over-land or over-water path. It matches the inset's dotted car convention (no road geometry), but Codex may prefer no main-map line.
4. **Relief is 1:1 only at each view's default zoom.**
   - Zooming in shows nearest-filtered blocks: 1.25× to 6× per cell.
   - The inset layer is baked for the NYC ↔ Chicago frame. Any future inset pair would draw it at a non-1:1 scale.
5. **The coast band shows flat colour.** The one transparent cell along every coast shows the flat polygon colour between the sand line and the shore band. In tight inlets such as Chesapeake tributaries, this reads as a thin dark ring.
6. **Dithering and hillshade are procedural.** They come from real data, with speck cleanup, but are not hand-cleaned pixel art. At 1× the dithered band edges read as a fine texture.
7. **Layout margins are unchanged from v01r1.**
   - New York City is 7.8 px from the card on the reverse card; Yonkers is 6.5 px.
   - The reverse-card inset still covers part of Pennsylvania and western New York.
   - The 1 px leaders are short (3–7 px) and mostly visible only up close.
8. **Dimmed names can hurt readability.** While a card is open, the non-selected names (for example Yonkers and Washington) drop to the subtext colour by design. That lowers their contrast while still readable; Codex may judge it too quiet.
9. **The globe still shows sphere colour only.** The r1 open questions are unchanged: the Russia, Turkey and Greenland neutrals, and stair-stepped sphere borders inside shared rings.
10. **The superseded tools no longer pass against the current tree.** `MapData.region_relief()` now takes a view ID (`us_northeast`, `us_great_lakes`, `route_inset`), not the geodata key `us_east`. The v01 and v01r1 capture-check tools therefore fail their relief checks against this tree, and their pinned colours no longer match either. They are records of their candidates, not regressions. Use the v02 tool.

## Reproducibility

- **Bake:**

  ```
  python -I tools/rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-v02_20261017-165006-dacc5102.py --cache-dir <dir for the z7 tiles>
  ```

  - It reuses or downloads the 77 pinned tiles and sends one HEAD request per tile for the source header.
  - It printed `RELIEF_BAKE_OK layers=3 families=['etopo1', 'gmted', 'srtm']`.
  - A trial bake to a temp path matched the committed-path bake in every field but `retrieved_on`.
- **Capture and check** (about 45 s, needs a display):

  ```
  work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to the v02 capture-check tool>
  ```

  - A second full run reproduced all 12 captures byte for byte (same manifest).
  - Delete this tag's outputs before re-capturing.
