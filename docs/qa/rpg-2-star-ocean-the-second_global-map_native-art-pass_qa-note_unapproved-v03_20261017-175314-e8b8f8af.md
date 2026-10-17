# Global map: native legibility pass v03, Chicago route strip on the card, value hierarchy and label size (UNAPPROVED candidate)

Date: 2026-10-17. Status: **unapproved map-art candidate**. This is the one bounded pass the [v03 route-legibility dispatch](../coordination/rpg-2-star-ocean-the-second_global-map-v03-route-legibility-dispatch_v01_20261017-175000-88f7ab9e.md) asks for after Codex's 640x360 review of [v02](rpg-2-star-ocean-the-second_global-map_native-art-pass_qa-note_unapproved-v02_20261017-165006-dacc5102.md). Codex found that:
- in the Great Lakes view, the large right card hid the east end of the NYC-Chicago dashed route;
- the card and route hierarchy was cramped;
- lake and coast values were low-contrast;
- labels were tiny.

The M2 map-art gate stays open. M2 stays 10/12 and the MVP meter is unchanged. Codex makes the visual judgment before creator review, and no v04 micro-iteration was made.

Scope:
- Not touched: Game Bible, progress state, City Hall, the Chicago scene, Washington, character motion, the Git index.
- Nothing was staged, committed or pushed.
- Route data and the travel logic are unchanged. The source check proves the route core and travel data equal git HEAD.

This pass ran in Claude Code (Opus 5.5) signed in through claude.ai with a Max subscription (first-party). `ANTHROPIC_API_KEY` was not set, and no quota, auth or paid-fallback path was used.

## What changed (one pass)

1. **The Chicago route is on the card, both ends visible.**
   - v02 drew a 196×108 inset on the map, left of the card. Its New York end sat against the card's edge, as if the card covered it.
   - v03 moves the route into a compact **route strip inside the card**: 194×60, between "From …" and the trip option.
   - The strip shows, at their own coordinates:
     - New York City with the party's gold ring;
     - Chicago with the white selection ring and gold ticks;
     - the dashed great circle with the aircraft pointing at the destination;
     - both names, as plates offset diagonally toward the other end, so they clear the badges and the line;
     - its own scale bar, in the first free corner;
     - its own relief, re-baked at one cell per strip pixel.
   - Both endpoints sit 20.4 px inside the strip edge. The endpoints are 150.5 px apart; v02's inset gave 156.3 px.
   - The strip repeats no mode, distance or time. v02's "Flight path" header and "Air · Flight ~1180 km" caption are gone. The card's unchanged option line ("飞机 · 航程约 1180 km · 6小时 / 抵达 2537年5月25日") is the only trip text.
   - Nothing of the off-view trip is drawn on the map any more: 0 route-gold pixels outside the card in all four flight-card captures.
   - The same applies to the Chicago → New York card on the Northeast view, so v02's inset no longer covers Pennsylvania there.
   - The New York → Washington car card is unchanged: both ends are on the view, so there is no strip, and the dotted connector stays.
2. **Card made room without growing.**
   - The card stays at `CARD_RECT` (210×238), opaque, with its pixels identical with the map hidden.
   - Kind and coordinates now share one row when both fit. A long kind wraps and the coordinates flow under it.
   - The separator line is drawn instead of being a 4 px node. Spacing is 2 px and the vertical margins are 7 px.
   - **Overflow fallback:** if a layout pass still finds the card too tall while the strip is shown, the coordinates line is dropped first, then the "From" line. The strip's gold-ringed origin already names that place. This happens only in the zoomed-in Washington card (see defect 4). Every capture in this note keeps both lines, which is checked.
3. **Value hierarchy (relief re-baked, same data).**
   - Every land band is lifted by about 0.045 luma: flat land goes from `#627856` to `#6d855c`.
   - Lakes are darker and bluer: `#2c6375` → `#225873`.
   - The sea and lake shore rims are brighter and bluer: `#255868` → `#286479` and `#35717f` → `#2f7290`.
   - The coast and lake shore line is brighter sand: `#c4c194` → `#dcd3a0`.
   - Shelf-depth steps, hypsometric bands, hillshade and the deep sea `#0f2b38` are unchanged.
   - Measured on the same lattice and frames as v02:

     | View | v02 land / water | v03 land / water | Step v02 → v03 |
     | --- | --- | --- | --- |
     | Great Lakes card, land − lake | 0.474 / 0.347 | 0.520 / 0.308 | **0.127 → 0.212** |
     | Northeast browse, land − sea | 0.479 / 0.194 | 0.522 / 0.194 | 0.285 → 0.328 |
     | Northeast reverse card, land − sea | 0.486 / 0.228 | 0.522 / 0.229 | 0.258 → 0.293 |

   - The globe's five sphere colours, the sea and the grid weight are identical to v02:
     - spheres: science `#5f8f76`, magic `#7e6d96`, wuxia `#97695a`, nature `#86904c`, culture `#a08b63`;
     - dotted grid excess step 0.0197.
4. **Label size.**
   - Map label plates (places and the globe's region badges) use 12 / 10 px text; v02 used 10 / 9 px.
   - The two lines overlap by their empty leading, so a plate is 27 px tall (v02 25). That keeps Yonkers above-right of its dot inside the frame.
   - Card text is 11 px (v02 10). The subtitle stays at 10 px and the coordinates go from 9 to 10 px. Strip names are 11 px (v02 inset 10).
   - New York City and Yonkers plates stay 37 px apart in both languages. All label, click-target, card and fixed-UI clearances still pass.
5. **Relief bake v03** (offline, deterministic).
   - Same 77 Terrarium z7 tiles. Each tile's sha256 must equal the v02 record (and the v01 pin). The observed source families come from v02's per-tile `x-amz-meta-x-imagery-sources` records: SRTM, GMTED2010 and ETOPO1 only.
   - No network request is made. Two bakes and a rebake inside the source check were byte-identical.
   - The regional layers keep v02's exact grids: Northeast 706×635 and Great Lakes 647×698, one texel per screen pixel.
   - The route-strip layer is 297×168, fitted to the strip's 192×58 map area with margins of 1.5° lon and 1.4° lat.

Preserved and re-checked:
- real coastlines (the same Natural Earth rings);
- marker coordinates, equal to the route core;
- the five-sphere globe;
- credits panel attribution (no 3DEP/NED/CDEM);
- whole-hour travel (NYC→Chicago air 360 min, NYC→Washington car 300 min, Chicago→NYC air 360 min);
- date-only arrival ("2537年5月25日" / "May 25, 2537");
- the generic modes;
- preview, Cancel and Depart by real clicks (Depart charged once);
- Save.

No airport names, schedules, times of day, invented roads or invented terrain were added.

## Candid comparison with v02

**Better:**
- Codex's main defect is fixed. Both ends of the Chicago route are visible together, on the card, at real coordinates. Nothing sits half under the card, and the strip is clearly part of the card (gold frame, inside the card's content box).
- The map to the left of the card is no longer covered by a 196×108 inset, in both the Great Lakes view and the reverse Northeast view.
- Lake Michigan and the Atlantic now separate from land at 1×: the land-lake step went from 0.127 to 0.212. The brighter sand line makes every shore read.
- Place names, CJK especially, are legible at 1× (12 px instead of 10 px).

**Worse or traded off:**
- The strip is smaller than v02's inset: a 192×58 map area against 194×79.
- The strip has no word that names the trip mode. Only the aircraft glyph and the dashed line say "flight"; the card's option line says the rest.
- The card is denser than v02, with 2 px spacing, and only 4 px is left free at the bottom of the Chicago card.
- Bigger plates cover more map:
  - the New York City plate covers more of New Jersey;
  - on the en globe, the US Northeast badge now reaches about 15°E over Western Europe. One globe sample point moved from (10°E, 49°N) to (18°E, 50°N) because of it.
- The Great Lakes view below Chicago is now empty, flat land. That is truthful (Illinois and Indiana), but plain.
- The land-sea step widened less than the land-lake step, because the brighter sea shore rim lifts near-coast sea pixels.
  - My first target (+0.04 over v02) missed by 0.006 on the reverse card.
  - The tool now asks +0.06 for lakes and +0.03 for sea, and says so in its comment.

## Evidence: real Godot 4.7.2, native 640×360, windowed

**Capture tool:** `tools/rpg-2-star-ocean-the-second_global-map_native-art-pass_capture-check_test-only-v03_20261017-175314-e8b8f8af.gd`
- **NATIVE_MAP_ART_OK 1873 checks, 12 captures, 0 failures.**
- Two consecutive full runs produced byte-identical captures (identical manifest).

Captures are in `outputs/`, named `rpg-2-star-ocean-the-second_global-map_native-art_<state>-640x360_test-only-v03_20261017-175314-e8b8f8af.png`. The capture manifest is `outputs/…native-art_capture-manifest_test-only-v03_20261017-175314-e8b8f8af.json` and the checks are in `outputs/…native-art_checks_test-only-v03_20261017-175314-e8b8f8af.json`.

| State | zh (sha256, first 16) | en |
| --- | --- | --- |
| Globe | `globe-zh` `f48d9c90ab846468` | `globe-en` `b750eb43af0be531` |
| Northeast browse | `us-northeast-zh` `418b24c3ef3a9baf` | `us-northeast-en` `249ae409a57de439` |
| Great Lakes flight card (strip) | `us-great-lakes-card-chicago-air-zh` `a1a5b1678c74c2dd` | `…-en` `4c6c705e71489585` |
| Washington car card | `us-northeast-card-washington-car-zh` `b438cb3751bb75ef` | `…-en` `36d047b1171b5054` |
| Chicago → NYC reverse card (strip) | `us-northeast-card-nyc-from-chicago-air-zh` `58198ac44cf1ceb8` | `…-en` `391e65f3a33b3e7d` |
| Map credits panel | `map-credits-zh` `fabc8aec8b21a7c4` | `map-credits-en` `55cbff7ed121e9c1` |

The v03 tool keeps every v02 check, adapted, and adds:
- **The strip belongs to the card.**
  - It is a child of the card, never of the map frame, and no `RouteInset` node exists under the map frame.
  - It sits inside the card's content box, between "From" and the options, clear of Depart and Cancel.
- **Endpoints are correct and clear.**
  - The line starts and ends at both places' coordinates.
  - Each badge is at least 18 px inside the strip edge (measured 20.4 px).
  - The chord is at least 120 px, the line is dashed, and the aircraft points at the destination.
- **Names are correct and clear.**
  - Both names are the travel data's names and contain no digits. The only text nodes are the two names.
  - They stay inside the strip, clear of the line's 5 px casing, the aircraft and the badges as drawn.
  - They are at least 11 px.
- **Scale bar:** clear of the names, badges and line, and it matches the strip's projection.
- **Relief:** the strip's relief is one texel per pixel.
- **Rendered pixels:**
  - 348–349 gold path pixels in the strip;
  - a gold frame along the strip's top edge;
  - the origin's gold ring at 12–16 of 16 samples and the destination's white ring at 11–16 of 16.
- **No route on the map:** 0 route-gold pixels on the map outside the card, the selected marker and the fixed controls.
- **Card:**
  - It stays at `CARD_RECT` with text at the sizes listed above.
  - Kind and coordinates share a row when they fit, and a long kind wraps with the coordinates under it.
  - The coordinates and "From" lines are kept in every captured state.
  - Its pixels are identical with the map frame hidden, in the Washington card and in the Chicago card with its strip.
- **Trips:**
  - The trip minutes and arrival dates are pinned to v02's values.
  - The option line equals `route_option_text()`, unchanged.
- **Palette continuity with v02:** the same 37 palette roles in the same order; land bands and both shore rims re-valued; the regional grids identical.

**Deterministic source check:** `tools/rpg-2-star-ocean-the-second_global-map_native-art-pass_source-check_test-only-v03_20261017-175314-e8b8f8af.py --cache-dir <tile cache>`
- **SOURCE_CHECK_OK 40 checks.** The report is `outputs/…native-art_source-check_test-only-v03_20261017-175314-e8b8f8af.json`.
- **Relief JSON:**
  - schema, supersedes v02, and palette roles as v02 (only land bands and shore rims changed);
  - flat colours equal the `COLOR_LAND` / `COLOR_LAKE` / `COLOR_OCEAN` values parsed from the map script;
  - every layer PNG decodes to its recorded sha256, size and palette.
- **Grids:**
  - the regional grids equal v02's;
  - the bake's `INSET_AREA` and `INSET_MARGIN_DEG` equal the map script's `INSET_SIZE − 2` and `RouteInset.MARGIN_DEG`.
- **Sources:** 77 tiles pinned; families ⊆ {SRTM, GMTED2010, ETOPO1}; no 3DEP/NED/CDEM claim.
- **Rebake** is byte-identical.
- **Source facts:**
  - the strip is built into the card, with no map slot, caption or header;
  - `MapData` reads the v03 JSON;
  - the map text names no airport, terminal or trip component;
  - `game/data/world-travel`, `app_state.gd`, `travel_calendar.gd`, `world_route_registry.gd` and `world_map_route_adapter.gd` equal git HEAD.
- **Hashes:** every v03 file and capture.

## Regressions (Godot 4.7.2, final tree)

**Headless**, no `SCRIPT ERROR` in any log:
- `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
- `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=111`. v02 recorded 108. The difference is that test's static guard, which runs one check per script in `game/scripts/`; other workstreams have added scripts to the shared tree since.
- `GLOBAL_TRAVEL_CORE_OK`
- `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
- `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`
- `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
- `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149`
- `M2_SMOKE_OK`, `M6_SMOKE_OK`, `M6_RESTART_OK`

**Windowed**, captures sent to a temp folder:
- `ROUTE_CARD_READABILITY_OK 117 checks`
- `STATUS_BACKING_READABILITY_OK 203 checks`

The first v03 build failed the route-card check 2/117: the zoomed Washington card was 245 / 268 px. That led to the overflow fallback in item 2. The final tree passes 117/117.

**Pre-existing failure:** `scifi-world-map_background-visual-check` fails with `button geometry scifi.city`. It fails identically with HEAD's three map scripts swapped into a temp copy of the current `game/` tree. Do not report this as all-pass.

## Files (local, unstaged)

| File | State | sha256-text-lf-v1 (first 16) |
| --- | --- | --- |
| `game/scripts/scifi_world_map.gd` | modified (hunks below; v02's own uncommitted edits preserved) | `ad451eb52008a0e4` |
| `game/scripts/world_map_data.gd` | modified (`RELIEF_PATH` → v03, two comment lines) | `c1fe920f07f9613e` |
| `game/scripts/world_map_text.gd` | **unchanged** from v02 | `68400bef1ac32496` |
| `game/data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v03_20261017-175314-e8b8f8af.json` | new | `69e26698c3568210` |
| `tools/rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-v03_20261017-175314-e8b8f8af.py` | new (offline bake) | `38877125148036e8` |
| `tools/rpg-2-star-ocean-the-second_global-map_native-art-pass_capture-check_test-only-v03_20261017-175314-e8b8f8af.gd` | new (fork of the v02 tool) | `84ad6ddf0cf10753` |
| `tools/rpg-2-star-ocean-the-second_global-map_native-art-pass_source-check_test-only-v03_20261017-175314-e8b8f8af.py` | new | see the source-check report |
| 12 captures, the capture manifest, the checks JSON and the source-check JSON in `outputs/` | new | see the table above and the manifest |

The v02 relief JSON, the v02 bake, the v02 tool and v02 captures are untouched. v02's `world_map_text.gd` strings `inset_title_air` / `inset_title_car` are now unused; I left them in place so that file has no v03 hunk.

### Exact hunks, v02 working copy → v03

Both shared files already carried the uncommitted v02 pass against HEAD; those hunks are kept as they were. Only these v03 hunks were added (line numbers are v03's):

**`game/scripts/world_map_data.gd`:**
- l. 13–18: the relief comment and `RELIEF_PATH` now point at the v03 JSON and bake.
- l. 132: the `region_relief()` doc names the route strip.

**`game/scripts/scifi_world_map.gd`:**
- **Constants (l. 34–84):**
  - `INSET_SIZE` is now 194×60, the size of the strip on the card.
  - New `PLATE_FONT` = 12 and `PLATE_SUB_FONT` = 10.
  - `COLOR_LAKE`, `COLOR_LAND` and `COLOR_COAST` are re-valued, with comments.
  - The unused `COLOR_INSET_RULE`, `COLOR_INSET_HEADER` and `COLOR_INSET_SHADOW` are removed.
- **`_build_map_frame`:** no longer adds a `RouteInset` to the map frame.
- **`_build_route_card` (l. 439–495):**
  - content margins of 7 px at top and bottom, VBox separation 2;
  - `sort_children` now goes to `_on_card_sorted`;
  - the subtitle has −3 line spacing;
  - a new `HFlowContainer` row holds `card_kind` and `card_coords`;
  - the `HSeparator` is removed;
  - `route_inset` is created inside the card's VBox after `card_from`;
  - 11 px for kind, from and route.
- **`_draw_route_card`:** the band bottom offset is 2, and a 1 px trip rule is drawn above `card_from`.
- **`_marker_button`:** plate fonts come from the new constants.
- **`_place_marker_button`:** the plate is `p + s − 4` tall and the secondary line offset is `p − 5`.
- **`_refresh_route_card`:** calls `_fit_card_facts()`; option buttons are 11 px with −3 line spacing.
- **New functions:** `_fit_card_facts`, `_fit_card_height` and `_on_card_sorted`.
- **`route_inset_rect` / `_sync_route_inset`:**
  - the rect is now the strip's card position in map-local pixels;
  - the sync has no slot search, no caption and no title, and calls `_fit_card_height`;
  - `_route_inset_slot` is removed.
- **`RouteInset` class:**
  - doc comment;
  - constants: `MARGIN_DEG` (1.5, 1.4), `LABEL_DX` 9 and `LABEL_DY` 3; `CAPTION_HEIGHT`, `HEADER_HEIGHT`, `GLYPH_WIDTH` and the glyph tables are removed;
  - the `caption` and `header` vars are removed, and `scale_at` is new;
  - `_init`: minimum size, and the map area is the full strip inside a 1 px frame;
  - `_plate_label`: 11 px, −2 line spacing, no vertical plate margins;
  - `show_route`: the signature loses the caption and title, with diagonal label placement and scale-corner choice;
  - `_build`: the margins come from `MARGIN_DEG`, with a 36 px scale-bar cap;
  - `_label_pos`: diagonal;
  - new `scale_rect`, `_scale_size` and `_scale_corner`;
  - `_draw`: panel and gold frame only;
  - new `_draw_scale`;
  - `_draw_glyph` is removed;
  - `_draw_lines`: draws the scale plate before the line and a dark inner frame line last.

## Remaining defects and open questions (candid)

1. **Still partly a planning UI.** The card body (stacked lines, an option box, Depart/Cancel), the degree labels, the scale bar, the credit plate and the stock-theme buttons are unchanged from v02. Whether this is close enough to the accepted science scenes is Codex's call.
2. **The strip is small.** It is 192×58 px of map, and the Chicago name plate covers part of southern Lake Michigan and lower Michigan inside it. It has no mode word; the flight reads from the aircraft glyph and the dashed line only.
3. **The card is tight.** The Chicago card has 4 px spare. Any longer place text would trigger the overflow fallback (item 2 above), which is checked only by the route-card readability test's zoomed state.
4. **Zoomed-in (1.5×) Washington card**, from the readability test's state:
   - New York leaves the free part of the view, so the card shows the strip for a car trip (a short dotted line).
   - The fallback then drops the coordinates line (zh), or the coordinates and "From" lines (en).
   - The strip's relief there is the NYC↔Chicago-baked layer drawn at a non-1:1 scale. This is the v02 inset limitation, unchanged.
   - Two label fallbacks are older than v03 and were confirmed with the v02 scripts in a temp copy. With New York's marker under the card, its plate pokes out at the card's edge. Washington's plate overlaps the Globe / region view buttons. The 12 px plates make the overlap slightly larger: zh now also touches the Globe button.
5. **Bigger plates cover more map:** New Jersey on the Northeast view, and Western Europe under the en globe's US Northeast badge.
6. **The sea step widened less than the lake step** (see the comparison).
7. **Unchanged from v02:**
   - the straight car connector across the Delaware valley;
   - relief at 1:1 only at default zoom;
   - the one-cell coast band showing a thin dark ring;
   - procedural dither and hillshade;
   - New York City 7.8 px from the card on the reverse card;
   - the globe's neutral areas and stair-stepped sphere borders inside shared rings.
8. **Superseded tools.** The v01, v01r1 and v02 capture-check tools no longer pass against this tree: the inset moved into the card, and the colours and fonts changed. They are records of their candidates, not regressions. Use the v03 tool.

## Reproducibility

- **Bake (offline):** run it with the pinned z7 tiles, for example the local cache `%TEMP%\wb-terrarium-7bf04753`. Output: `RELIEF_BAKE_OK layers=3 families=['etopo1', 'gmted', 'srtm']`.

  ```
  python -I tools/rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-v03_20261017-175314-e8b8f8af.py --cache-dir <dir with the 77 pinned z7 tiles>
  ```

- **Capture and check:** needs a display and takes about 15 s. Delete this tag's outputs before re-capturing; a rerun reproduces all 12 captures byte for byte.

  ```
  work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to the v03 capture-check tool>
  ```

- **Source check:**

  ```
  python -I tools/rpg-2-star-ocean-the-second_global-map_native-art-pass_source-check_test-only-v03_20261017-175314-e8b8f8af.py --cache-dir <tile dir>
  ```

  Run it after the captures; it hashes the manifest's files.

## Selective Git sync addendum (2026-10-17)

This addendum records the sync asked for by the [v03 selective review-sync dispatch](../coordination/rpg-2-star-ocean-the-second_global-map-v03-selective-review-sync-dispatch_unapproved-v01_20261017-182800-7d31b5ae.md). It is not an approval. Map art stays **unapproved**; M2 10/12, meter 40.8%, scenes 3/12, sprites 0/52 and playtests 0/2 are unchanged.

- **Synced:** the three map scripts; the v01, v02 and v03 relief JSONs (v01 with its in-place attribution correction, v02 because the v03 bake, source check and capture tool read it); the v01, v02 and v03 bake tools; the v03 capture-check and source-check tools; the v01, v01r1, v02 and v03 QA notes and the first-art-gate brief; the two v03 dispatches; the v03 capture manifest, checks JSON and source-check report; and five of the twelve captures (globe zh, Northeast en, Chicago flight card zh and en, Washington car card zh).
- **Left local, hash-pinned in the capture manifest:** the other seven captures. The v02 capture tool and v02 captures stay local; they are superseded records.
- **Source-check fix:** the rebake comparison used raw bytes, so it failed (39/40) in an `autocrlf=true` checkout, where the relief JSON is CRLF. It now compares under sha256-text-lf-v1, like the other text hashes in this repo. No data or check target changed. The source-check report was regenerated: 40/40.
- **Clean-index reproducibility:** HEAD 4b06aef plus exactly the synced files, exported to a temp copy with `autocrlf=true`:
  - the capture tool printed `NATIVE_MAP_ART_OK 1873 checks, 12 captures`, and all 12 captures were byte-identical to the local captures; the manifest and checks JSON matched after CRLF→LF;
  - the source check printed `SOURCE_CHECK_OK 40 checks`;
  - headless: earth smoke 212, integration regression 107 (the static guard counts the scripts in `game/scripts/`; the dirty shared tree has 111), travel core OK, whole-hour 246, export data 24, US migration 32, commerce 149, M2, M6 and M6 restart OK, with no `SCRIPT ERROR`;
  - windowed: route card 117/117 and status backing 203/203.
- **Still failing, inherited:** `scifi-world-map_background-visual-check` fails `button geometry scifi.city`. It fails identically in the same export with HEAD's three map scripts. This sync is therefore **not all-pass**.
