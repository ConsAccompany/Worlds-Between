# Global map: native art pass r1, sphere colours and relief credit (UNAPPROVED candidate)

Date: 2026-10-17. Status: **unapproved map-art candidate**. This revises [native art pass v01](rpg-2-star-ocean-the-second_global-map_native-art-pass_qa-note_unapproved-v01_20261017-015515-b5790ae8.md) after Codex's globe review. The map-art gate stays open.

No counters changed. Progress state, the Game Bible, room scenes and character art were not touched. The candidate was later synced to GitHub (see "Git sync" at the end); it is still UNAPPROVED.

## What changed

1. **Five sphere colours restored on the globe.**
   - The v01 globe gave all land one sage. The globe now fills each Earth civilization sphere with its own restrained colour. The values are measured on the live 640×360 frame and are the same in zh and en:

     | Sphere | Colour | Luma |
     | --- | --- | --- |
     | Science (US + Canada) | teal-green `#5f8f76` | 0.515 |
     | Magic (South America) | violet `#7e6d96` | 0.453 |
     | Wuxia (Asia) | red-brown `#97695a` | 0.446 |
     | Nature (Oceania) | olive `#86904c` | 0.537 |
     | Culture (Europe + Africa) | sand `#a08b63` | 0.551 |

   - Neutral areas:
     - Mexico, Central America and the Caribbean are a mixed borderland in warm grey `#777267`.
     - Antarctica DLC is a cool grey-blue `#68747d`.
     - Russia, Turkey and Greenland stay unassigned in neutral grey `#6b716c`. This is the v02 candidate's rule; no creator decision exists for them.
   - Every one of these tones stays in the land value family, at luma 0.437–0.551. That is above the lakes (`#2f6476`, 0.35) and the globe sea (0.162). There is no trade-off against the land/lake/sea hierarchy.
   - The closest pair is nature/culture, at RGB distance 0.138. The threshold is 0.10.
   - Coasts, borders, regions, markers, routes and map size are unchanged.
     - The globe still draws one polygon per Natural Earth 110m land ring.
     - 124 single-sphere rings get a flat fill.
     - The 4 rings that several spheres share (Afro-Eurasia, the Americas, New Guinea and Trinidad) clip a baked sphere texture to their own polygon (`clip_children`). No colour crosses a drawn coast.
   - Source: `game/data/world-map/…globe-sphere-tint-layer_m2-map-art-native-v01r1_20261017-022144-f9b0d28b.json`. It is a 1440×720 palette PNG at 0.25°, about 31 KB.
   - It is baked from Natural Earth 50m countries (public domain, sha256-pinned) by `tools/…globe-sphere-tint-bake_…f9b0d28b.py`.
   - The regional views, the relief and the route inset are unchanged. Their measured means match v01: Northeast land 0.474 / sea 0.212, Great Lakes land 0.475 / lake 0.353.
2. **Relief data attribution, in game.**
   - On both regional views (US Northeast and US Great Lakes, the views that draw the Terrarium relief), a small plate sits on the map's bottom row, between the scale bar and the date:
     - zh: "地形数据：Mapzen · USGS · NOAA"
     - en: "Relief data: Mapzen · USGS · NOAA"
     - Map-local rect: en [404, 254, 157×13], zh [402, 254, 151×13]. It is hidden on the globe.
   - Clicking it, or focusing it and pressing Enter, opens a "Map data credits / 地图数据来源" panel. Back or Esc closes it. The panel holds the [Tilezen attribution](https://github.com/tilezen/joerd/blob/master/docs/attribution.md) lines that apply, verbatim:
     - "Mapzen" (the hosted-service line);
     - "Global ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration";
     - "United States 3DEP (formerly NED) and global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological Survey."
   - The panel also gives the source URL and a Natural Earth (public domain) note.
   - The zh panel keeps the required English lines and adds a Chinese gloss.
   - Applicable providers were checked from the live tiles. The `x-amz-meta-x-imagery-sources` headers of all 77 baked z7 tiles list only `srtm`, `gmted` and `etopo1`.
     - No 3DEP/NED or CDEM (Canada) tile went into the bake. The v01 note's "USGS NED/3DEP" source list and the relief JSON's attribution string overstate this.
     - The USGS line is still quoted whole because it is the upstream example wording.
   - The relief JSON was not rewritten, so its hash stays as cited.
   - Strings: `credit_relief`, `credits_title`, `credits_body`, `credits_close` in `world_map_text.gd`. Its header comment now allows this one exception to "no data sources on screen".

## Files (local, unstaged)

| File | State | sha256 (text-LF / bytes), first 16 |
| --- | --- | --- |
| `game/scripts/scifi_world_map.gd` | modified (sphere fill, credit plate, credits panel) | `c3abde79a278d5f7` |
| `game/scripts/world_map_data.gd` | modified (`globe_sphere_tint()`) | `497a4ca81bc00edc` |
| `game/scripts/world_map_text.gd` | modified (+4 bilingual keys) | `e5d52ce2d1e90e58` |
| `game/data/world-map/…globe-sphere-tint-layer_…f9b0d28b.json` | new | `58bc2224480cf693` |
| `tools/…globe-sphere-tint-bake_m2-map-art-native-v01r1_…f9b0d28b.py` | new | `1607f2b986daf7aa` |
| `tools/…native-art-pass_capture-check_test-only-v01r1_…f9b0d28b.gd` | new (fork of the v01 tool, new tag) | `0dc38bc15c98eedf` |

## Evidence: real Godot 4.7.2, native 640×360, windowed

Captures are in `outputs/`, named `rpg-2-star-ocean-the-second_global-map_native-art_<state>-640x360_test-only-v01r1_20261017-022144-f9b0d28b.png`. The v01 captures were not overwritten.

| State | zh | en |
| --- | --- | --- |
| Globe | `globe-zh` (`a30af0ff5deb7c1d`) | `globe-en` (`fb32c2fb6bda6d85`) |
| Northeast browse | `us-northeast-zh` (`1c27355d267534a6`) | `us-northeast-en` (`4e8f56735020dd7e`) |
| Car card, NYC → Washington | `us-northeast-card-washington-car-zh` (`a5ccb5fe1da1552f`) | `…-en` (`7583653aa3ccccfa`) |
| NYC → Chicago flight card and inset | `us-great-lakes-card-chicago-air-zh` (`ba91998b8cbdd856`) | `…-en` (`04f071da5bcd6196`) |
| Chicago → NYC return card and inset | `us-northeast-card-nyc-from-chicago-air-zh` (`e2245f630eaff1fe`) | `…-en` (`01b1cadb6a9e84a3`) |
| Map credits panel | `map-credits-zh` (`5585a23ea8494dd8`) | `map-credits-en` (`ae73661831fc73ba`) |

Checks: `outputs/…native-art_checks_test-only-v01r1_20261017-022144-f9b0d28b.json`, **NATIVE_MAP_ART_OK 1705 checks, 12 captures, 0 failures**. The run includes all v01 checks plus:
- per-sphere colours sampled on the live globe, with one colour per sphere;
- pairwise distance ≥ 0.10 between the five spheres, and ≥ 0.06 from the neutral tones;
- every land tone ≥ 0.15 luma above sea and ≥ 0.08 above lakes;
- 128 polygons, as before, with 4 clipped rings;
- the credit plate clear of the scale bar, date, view buttons, card, inset, markers and degree labels;
- a real click that opens the credits, the required wording present, the body fitting without scrolling, and a real click on Back that changes nothing.

## Regressions (Godot 4.7.2, final tree)

**Headless:** `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`, `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=106`, `GLOBAL_TRAVEL_CORE_OK`, `M2_WHOLE_HOUR_TRAVEL_OK checks=246`, `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`, `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`, `M2_SMOKE_OK`, `M6_SMOKE_OK`, `M6_RESTART_OK`.

**Windowed:** `ROUTE_CARD_READABILITY_OK 117 checks` and `STATUS_BACKING_READABILITY_OK 203 checks`. Captures went to a temp folder.

## Remaining defects and open questions

1. Sphere membership of Russia, Turkey, Greenland and the US Caribbean territories is still a creator question. They stay neutral grey, and the large grey band over northern Eurasia can still read as a sixth area.
2. The globe shows sphere colour only. The v01/v02 skins' sphere names and lock glyphs are not drawn, because this pass was limited to colour.
3. Sphere borders inside a shared ring (for example Mexico/US or Europe/Asia) come from a 0.25° grid with nearest filtering. At the default zoom they are 1 px stair-steps; at 7× zoom the steps are about 2.8 px.
4. Nature (olive) and culture (sand) are the closest pair. They sit on separate continents, so they are not confused at 1×.
5. The credit plate is 9 px text, small but legible at 1×. The credits panel body is 10 px.
6. The v01 defects (Great Lakes plain, relief cell aliasing, tight margins, lake shore line) are unchanged.
7. The relief JSON's attribution string and the v01 note still list NED/3DEP. This r1 note corrects the record without changing those cited files.

## Reproduce

- **Bake:** `python -I tools/…globe-sphere-tint-bake_…f9b0d28b.py --cache-dir <temp dir>`. It downloads the pinned NE 50m countries file once.
- **Capture and check** (about 45 s, needs a display): `work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <abs path to tools/…capture-check_test-only-v01r1_…f9b0d28b.gd>`. Delete this tag's outputs before re-capturing.

## Git sync (2026-10-17, still UNAPPROVED)

The commit that adds this section syncs the candidate to `main`. Map art stays unaccepted, and no counter changed (40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2).

- **Committed:**
  - the three map scripts and the place registry, as in the Files table;
  - the us_east relief layer and its bake tool (v01);
  - the globe sphere tint layer and its bake tool;
  - the r1 capture-check tool;
  - the v01 and r1 QA notes;
  - six representative captures: globe, Chicago flight card with inset, and map credits, each in zh and en.
- **Left local:**
  - the other six r1 captures and the r1 checks JSON (hashes above);
  - the v01 captures, checks and capture tool.
- **Re-verified before the commit (Godot 4.7.2):**
  - The r1 harness gave `NATIVE_MAP_ART_OK 1705 checks, 12 captures`, 0 failures. All 12 captures were byte-identical to the hashes above, in the working tree and in a clean HEAD worktree holding only these files.
  - In the clean worktree: `GLOBAL_EARTH_MAP_SMOKE_OK 212`, `GLOBAL_MAP_TRAVEL_INTEGRATION_OK 105`, `M2_WHOLE_HOUR_TRAVEL_OK 246`, `US_SCIENCE_MIGRATION_SMOKE_OK 32`, `EXPORT_DATA_INCLUSION_SMOKE_OK` and `M2_SMOKE_OK`.
  - In the working tree, the same checks also passed, with integration at 106, plus `GLOBAL_TRAVEL_CORE_OK`, `M6_SMOKE_OK`, `M6_RESTART_OK`, `ROUTE_CARD_READABILITY_OK 117` and `STATUS_BACKING_READABILITY_OK 203`.
