# US science sphere: runtime migration QA note (M2 v02)

- Date: 2026-10-15
- Scope: the travel/calendar data, the world map, the save loader and a new Chicago placeholder scene. Task B in a shared checkout.
- M2 status: **not accepted**. The M2 gate count is unchanged (6/12). Nothing here accepts art, scene quality or a human playtest.
- Not touched: `docs/progress.md`, the Game Bible `outputs/`, art files, and other workstreams' dirty files. Nothing was staged, committed or pushed.

## What the creator approved and what is now in the runtime

| Item | Runtime | Status |
|---|---|---|
| New York City is the science hub. City Hall Park, Lower Manhattan is playable. | `earth.us.ny.new-york-city` → scene `scifi.city`. Start location. | Place set approved. The scene reuses the **unaccepted generic science-city plate**; there is no City Hall Park art yet. |
| Yonkers, NY is the outskirts. | `earth.us.ny.yonkers-outskirts` → `scifi.outskirts` | Same scene and art as before (unaccepted). |
| The whole of Washington, D.C. is abandoned ruins, centred on the partly collapsed, overgrown U.S. Capitol grounds, with a survey post and patrol automata. | `earth.us.dc.washington-ruins` → `scifi.ruins` (survey entrance and automaton encounter unchanged). | Coordinates are the real Capitol. The ruin is fiction. The **generic ruins plate is not a recognizable Capitol**. That art is open. |
| The first air route is New York City–Chicago. One Chicago Loop district is playable. | `earth.us.il.chicago` → `scifi.loop` → `res://scenes/chicago_loop_district.tscn` | **Explicit technical placeholder, art not accepted**. It is drawn in code and labelled on screen. |
| The calendar starts 2537-05-25. | `calendar.startDate` = 2537-05-25 (a Saturday, proleptic Gregorian) | 08:00 is an engineering placeholder for the time of day. |
| The science sphere is the US and Canada only. | Region `science.countryCodes = ["US","CA"]`. The registry rejects any other country in that region. | Enforced by the validator. |
| Local walking costs no calendar time. Car and air world travel advances realistic time. | Only `settle_travel` and rest advance the clock. Walking in all four scenes is tested as zero-cost. | Unchanged rule, now tested in the Loop too. |

## Files

New (unique names):
- `game/data/world-travel/…locations-routes_m2-us-science-v02_20261015-175011-c454007b.json`: travel data v02.
- `game/data/world-map/…place-registry_m2-us-science-v02_20261015-175011-eeaa6baa.json`: display registry v02 (regions `us_northeast` and `us_great_lakes`).
- `game/data/world-map/…runtime-geodata_m2-us-science-v02_20261015-175011-944d9635.json`: runtime geodata v02 (global 110m land plus a `us_east` layer).
- `game/tests/…us-science-sphere_runtime-geodata-build_m2-v02_…-0a728533.gd`: geodata builder and reproducibility check.
- `game/tests/…us-science-sphere_runtime-migration-smoke_m2-v02_…-5ffdb1e9.gd`: scene-level migration smoke.
- `game/scenes/chicago_loop_district.tscn` and `game/scripts/chicago_loop_district.gd`: the Loop placeholder. Renamed before sync to `rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn` / `.gd` (see the integration QA note, §7).

Kept unchanged on disk as records: the v01 travel data, the v01 place registry and the v01 geodata (Yangtze Delta). The runtime no longer reads them. No Liangzhu art, design or test artifact was deleted or edited. Liangzhu becomes later Asia work.

Edited:
- `world_route_registry.gd`: new data path, `retiredLocations`, region `countryCodes` check.
- `world_map_data.gd`: v02 paths, `geodata_key`, `region_frame_bbox`, layers may omit roads.
- `scifi_world_map.gd`: one projection and land layer per region; region switching; W/S grid labels; per-region `frame_px` and globe label side; scale bar moved to y 258; the scene path comes from AppState.
- `world_map_text.gd`: US labels and kind `capital_ruins`.
- `app_state.gd`: US scene names in zh and en, Loop strings, `PLACEHOLDER_DESTINATIONS`, `AREA_SCENES`, `area_scene_path()`, `is_area_scene()`, and save validation and loading for `scifi.loop`.
- `save_screen.gd`: area-scene return now covers the Loop.

Tests updated to the US IDs (same file names): the core smoke, the map smoke, the integration regression, the commerce weekly-settlement hookup, the route-card and status-backing readability checks, the map visual capture and the M8 canvas-pointer regression (only its region key and labels changed).

## Old saves

- `retiredLocations` keeps `earth.cn.shanghai` → NYC, `earth.cn.shanghai.songjiang-outskirts` → Yonkers and `earth.cn.liangzhu-ruins` → Washington. Each retired record keeps its former names, coordinates and source. Retired IDs are hidden: they are never listed, never discoverable and have no map marker.
- Loading resolves the retired IDs in `locationId`, `discovered` and the commerce company keys. The first re-save writes only US IDs. The scene IDs (`scifi.city`, `scifi.outskirts`, `scifi.ruins`) did not change, so a save inside a scene reopens the same scene.
- **Saves keep their absolute clock.** A save made under the 2026-04-01 placeholder still shows its 2026 date after loading; nothing is shifted to 2537. This follows the existing rule ("saved games keep their absolute date"). Shifting would also need a whole-week offset to keep the commerce cursors consistent. **Open decision for the creator:** shift old saves into 2537, or leave them.
- If Liangzhu returns as an active Asia location with the same ID, remove its retired record at that time.

## Coordinates and provenance (retrieved 2026-10-15)

| Place | Stored point | Source | Licence status |
|---|---|---|---|
| NYC / City Hall Park | 40.71205, -74.00708 | GeoNames 5112759 (L.PRK) | CC BY 4.0, stated by publisher |
| NYC city reference | 40.71427, -74.00597 | GeoNames 5128581; GNIS 975772 cross-check | CC BY 4.0 / US federal PD (needs verification) |
| Yonkers | 40.9304, -73.89789 | GeoNames 5145215; GNIS 971828 cross-check | as above |
| U.S. Capitol (ruins centre) | 38.88983, -77.00887 | GeoNames 4140827 (S.ADMF); GNIS 531316 Capitol Hill summit cross-check | as above |
| Washington city reference | 38.89511, -77.03637 | GeoNames 4140963 | CC BY 4.0 |
| The Loop | 41.88407, -87.6333 | GeoNames 8436065; GNIS 406045 cross-check | as above |
| Chicago city reference | 41.85003, -87.65005 | GeoNames 4887398 | CC BY 4.0 |
| LGA / ORD | 40.777199, -73.872597 / 41.9786, -87.9048 | OurAirports 3643 / 3754 | Public domain, stated |

GNIS no longer has records for City Hall Park or the Capitol building; GeoNames is the only source for those two points. Place facts are cited in the data: NYC Parks for City Hall Park, the Architect of the Capitol for the Capitol's location, and Wikipedia (CC BY-SA, text cited not copied) for Yonkers bordering the Bronx and for the Loop's boundary streets.

## Travel figures

**All of these are preliminary estimates. None is marked verified.** The game shows them with its "estimated" note.

| Route | Distance | Minutes | Basis |
|---|---|---|---|
| NYC → Yonkers / reverse | 28.2 / 28.3 km road | 35 / 35 | OSRM demo server, car profile, free flow |
| NYC → Washington / reverse | 363.2 / 361.4 km | 289 / 286 | same |
| Yonkers → Washington / reverse | 388.0 / 383.4 km | 306 / 303 | same, direct drive |
| NYC → Chicago (air) | 1177.1 km great circle LGA–ORD | 365 = 24 access + 120 check-in/wait + 166 flight + 55 egress | see below |
| Chicago → NYC (air) | 1177.1 km | 338 = 54 + 120 + 142 + 22 | see below |
| Yonkers ↔ Chicago, Washington ↔ Chicago | — | none (status `pending`, `no-researched-route`) | Not researched. No figure is derived by adding legs. |

Each direction is a separate one-way segment with its own reverse query, so no reverse time is assumed. The air components:
- **Flight minutes:** the median scheduled block time (CRSElapsedTime) of 997 nonstop flights each way, from US DOT BTS On-Time Reporting for July 2026, the latest month available. LGA→ORD p10/p90 is 157/188 min; ORD→LGA is 136/149.
- **Check-in and wait (120 min):** American Airlines' guidance to arrive "at least 2 hours" before a US domestic flight. TSA gives no fixed figure. This is a planning allowance, not a measured wait.
- **Access and egress:** OSRM free-flow drives between City Hall Park or the Loop and the airport reference points, not the terminals. Deplaning, baggage and curb time are not counted.
- **Flight distance:** the great circle between the OurAirports points, not the flown track.

## Geodata

- The 50m land in the repository puts City Hall Park in the water and has no Great Lakes. The v02 `us_east` layer (clip -93, 36, -66, 47.5) therefore uses Natural Earth **10m land** plus **10m lakes** (scalerank ≤ 3) at release **v5.1.2** (public domain). Lakes are stored as hole rings and lake islands are left out. There is no US road layer yet.
- The two 10m source files (about 15 MB) are **not stored in the repository**, because `assets/reference/geography/` was outside this task's scope. Their upstream URLs and SHA-256 hashes are recorded in the geodata's `sources` (`retained_copy: false`). The builder re-downloads them and reproduces the file exactly: `US_GEODATA_REPRODUCED_OK land_rings=74 lake_rings=15`. Recommendation: archive the subset sources under `assets/reference/geography/` in a later, approved sync.
- The 10m coastline is generalised. The Yonkers point (on the Hudson shore) falls just outside the land polygon, so the map smoke allows places within 2 km of land.

## Test results (Godot 4.7.2, headless, 2026-10-15)

| Test | Result |
|---|---|
| core travel/calendar smoke (…a19d5ae7) | `GLOBAL_TRAVEL_CORE_OK` |
| global map smoke (…7b4550d6) | `GLOBAL_EARTH_MAP_SMOKE_OK checks=212` |
| map-travel integration regression (…786a054d) | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=105` |
| commerce weekly settlement hookup (…a9d18fda) | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` |
| US migration smoke (…5ffdb1e9, new) | `US_SCIENCE_MIGRATION_SMOKE_OK checks=29` |
| geodata reproducibility (…0a728533 --check) | `US_GEODATA_REPRODUCED_OK` |
| broader batch (readability, export inclusion, merchant, M1–M8 smokes) | see the task report |

Not run: the map visual capture, the merchant UI visual capture and the M8 canvas-pointer regression. They write into `outputs/` and have no redirect option. Their ID and region keys were updated but are unverified.

## Unresolved research and decisions

1. **OSRM demo-server terms:** "reasonable, non-commercial use". Re-derive all car and airport-drive figures with a self-hosted OSRM on a dated OpenStreetMap extract (ODbL attribution) before release.
2. **The BTS and USGS public-domain statements** were not read from the publishers' terms pages (needs verification).
3. **Check-in allowance:** only American Airlines could be read; United and Delta pages failed. Terms are not established.
4. **LGA–ORD service** is confirmed only through July 2026. In the 2537 fiction, which airports operate is a creator decision.
5. **Terminal-specific airport points** and a door-to-door allowance (deplaning, baggage, curb) are not researched; the allowance is 0.
6. **Yonkers outskirts scene entry** is not registered; the city reference point is used.
7. **Yonkers–Chicago and Washington–Chicago** have no route. Players travel to NYC first.
8. **Art:** City Hall Park, a recognizable collapsed and overgrown Capitol, and the Loop all still need art. The scene backgrounds are the old generic plates or a code-drawn placeholder.
9. **Old-save dates** stay in 2026 (see above). This is a creator decision.
10. **The time of day at the start** (08:00) is a placeholder.
11. The Loop placeholder's own comment says State & Madison is the origin of Chicago's address grid. That claim was not separately sourced in this pass.
