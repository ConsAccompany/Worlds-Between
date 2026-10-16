# Global Earth + US regional map-art candidate v01 — QA note

- **Status:** **UNAPPROVED / NONRUNTIME** map-art candidate for Codex visual review. Not creator-accepted.
  - The M2 `map-art` gate stays **open** (`not_started`).
  - Science scene quality stays **0/11** and the MVP meter is unchanged (**35.8%**).
  - No runtime default changed. No file under `game/` was edited, and no Game Bible file or Git state was touched (nothing was staged or committed).
- **Tag:** `candidate-unapproved-v01_20261016-164615-f9e453b0` (2026-10-16, local time).
- **Worker:** Claude Code CLI 2.1.300, Opus 5.5, signed in through Claude Max (`claude auth status`: `authMethod claude.ai`, `apiProvider firstParty`, `subscriptionType max`).
  - `ANTHROPIC_API_KEY` was checked and is **absent**.
  - No API billing, credits, auto-reload, paid fallback or image-generation service was used.
  - Every pixel is computed from Natural Earth public-domain geodata and the game's own runtime geodata. The captures are real Godot 4.7.2 renders (Compatibility renderer, windowed, not `--headless`).
- **Answers:**
  - [Current US map visual audit](rpg-2-star-ocean-the-second_global-map-current-us_visual-art-audit_unapproved-v01_20261016-054453-fd834f41.md): flat GIS look, grid louder than destinations, no road/air distinction, a globe that reads as unfinished.
  - [NYC–Chicago air-corridor audit](rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-corridor_visual-audit-unapproved-v01_20261016-064519-bb294d29.md) and the [inset v01r1 audit](rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-inset-v01r1-codex-visual-audit_unapproved-v01_20261016-070201-b6d76529.md): the main map's visual language still had to be solved.

## What the candidate is

The candidate is one visual language for the live global map's existing geometry: the 640×268 map frame, the globe camera and the two science-sphere regional cameras. It is applied at run time by a test-only skin, captured, and then removed again.

| Part | File | Role |
|---|---|---|
| Layer builder | `tools/…global-map-art_pixel-layer-builder_candidate-unapproved-v01_…f9e453b0.py` | `extract` (Natural Earth → small derived subset), `build` (pixel rasters, `.ora` sources, runtime meta, manifest), `check` (byte-identical rebuild) |
| Runtime skin | `tools/…global-map-art_godot-runtime-skin_candidate-unapproved-v01_…f9e453b0.gd` | Swaps the map's two draw callbacks and recolours label plates. `apply()` / `remove()` |
| Capture + checks | `tools/…global-map-art_godot-capture-check_candidate-unapproved-v01_…f9e453b0.gd` | `-s` tool: real map scene, baseline and candidate frames, hitbox/route/text/pixel/click checks |
| Deterministic checks | `tools/…global-map-art_deterministic-checks_candidate-unapproved-v01_…f9e453b0.py` | 67 offline checks; `--write-index` writes the capture manifest |
| Assets (18 files, 6.9 MB) | `assets/map-art/global-map-art-candidate-v01-f9e453b0/` | 13 flat level PNGs, 3 editable `.ora`, NE subset, runtime meta, manifest |
| Editable layered sources | `…globe-lv0-layered-source….ora` (10 layers), `…us-northeast-default-layered-source….ora` (13), `…us-great-lakes-default-layered-source….ora` (13) | OpenRaster (Krita / GIMP / MyPaint). Binary alpha; layer composite == merged == runtime PNG (checked) |
| Asset manifest | `…/rpg-2-star-ocean-the-second_global-map-art_manifest_candidate-unapproved-v01_…f9e453b0.json` | Inputs and outputs with `sha256-text-lf-v1` / `sha256-bytes` |
| Captures (40) + reports | `outputs/rpg-2-star-ocean-the-second_global-map-art_<state>-<zh\|en>-<1280x720\|640x360>-<baseline\|candidate>_…f9e453b0.png`, `…godot-checks_….json`, `…capture-manifest_….json` | One image per file; no contact sheets |

The files sit outside `game/`, so the Godot export cannot pick them up, and nothing in `game/` references them (checked).

### How to reproduce

From the repo root, with the real Python (`C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`):

```
python tools/…pixel-layer-builder_…f9e453b0.py build        # or: check
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to …godot-capture-check_…f9e453b0.gd>
python tools/…deterministic-checks_…f9e453b0.py --write-index
```

`extract --source-dir DIR` is only needed to re-derive the subset. It needs six Natural Earth v5.1.2 GeoJSON files, whose URLs and SHA-256 are pinned in the builder and recorded in the subset: `ne_50m_admin_0_countries`, `ne_50m_lakes`, `ne_10m_roads`, `ne_10m_urban_areas`, `ne_10m_admin_1_states_provinces_lines` and `ne_10m_admin_0_boundary_lines_land`. The sources were downloaded to `%TEMP%\wb-mapart-ne-src-20261016` and are not stored in the repo (about 105 MB). The derived subset (2.4 MB, coordinates rounded) is stored.

## Visual language

- **Pixel treatment.** Each camera level is rasterized natively at the live camera's own scale, so one texel equals one logical 640×360 pixel at that level, and it is drawn with the project's nearest filter. The engine's own math is used:
  - globe min scale 1.48889 px/° (×1, ×2, ×4, ×7);
  - US Northeast min 83.546 / default 89.797 / ×2 / ×4 / max 501.276;
  - US Great Lakes default = min 86.120 / ×2 / ×4 / max 516.723.
- **Palette.** Each flat level has 40 colours (globe) or 16–18 colours (regions), all opaque and all from one declared palette (checked).
- **What the texture adds.** Coasts get a one-pixel light rim on the north- and west-facing edges and a shadow rim on the south- and east-facing ones. The sea gets two shore-shelf bands, sparse wave ticks and a dotted graticule that lives only in open water. Land gets a low-density ordered dither. Island halos come from a mask opened by one pixel, so one-pixel islands do not sprout shelf boxes.
- **Overlay icons.** Route lines, marker icons, the here-ring and the selection brackets are drawn as Bresenham / midpoint pixels on the same logical grid.
- **Sphere colours (globe).**
  - Science (US + Canada), the only open sphere, is the most luminous and saturated (teal-green), with a teal shore glow.
  - Magic (South America, violet), wuxia (Asia, muted red-brown), nature (Oceania, moss) and culture (Europe + Africa, sand) are muted locked tints.
  - Mexico, Central America and the Caribbean are neutral borderlands. The Antarctica DLC is a dim hatched ice tone.
  - The registry board names (`科技板块`, `魔法板块`, … / `Science sphere`, …) sit on each continent. Locked spheres are dimmer and carry a 5 px lock glyph. A name is skipped wherever it would touch a marker plate or the status panel.
  - The portal planet is separate and is not drawn on Earth.
- **Region views (US Northeast, US Great Lakes).**
  - Science land, the same 10m land and lakes rings the live map uses, and Natural Earth urban areas (NYC, Philadelphia, Baltimore, Washington, Chicago, Milwaukee…) as lighter city fabric.
  - Dotted state and province lines, and the US–Canada border (dashed on land, dotted across lakes).
  - Road hierarchy by zoom:
    - expressways (Natural Earth `expressway=1` major highways and beltways) at the default level;
    - other major highways from 2× the default level;
    - secondary highways from 4× it.
- **Route hierarchy** (from `WorldRouteRegistry.routes_between`, read-only):
  1. **Card-selected route:** 2 px, bright, cased.
  2. **Routes from the party's place:** 1 px, cased. Car is solid gold; air is a dashed, pale great circle.
  3. **Other available routes:** dim and uncased, with car routes dotted.
  - Exactly three car links and one air link exist, and the candidate draws exactly those. There is no Yonkers–Chicago or Washington–Chicago line (both are pending in the data; checked).
  - When a route's far end is off-frame in a region view, a 56 px stub runs from the visible place, ending in a chevron and the far place's own map label. The label goes in the first slot that touches no UI: status panel, markers, view buttons, calendar, degree labels, scale bar or card (checked).
  - Car lines are **schematic connectors** between the two places. The travel data has no road geometry, so they do not follow a highway.
- **Markers.** City: a 9×9 teal plate. Outskirts: a 7×7 diamond. Capital ruins: a 9×9 cracked rust plate. Region badge on the globe: 7×7. Label plates are re-coloured (dark plate, warm-white primary, muted secondary, a 2 px accent bar by kind). **Their size, position, text and fonts are the live map's own.**

### Nothing invented

- Places, names, coordinates, kinds, routes, modes, distances, durations and arrival dates all come from the live map, the travel data and the route core.
- The skin passes no literal string to `draw_string`. It draws only:
  - registry board names;
  - place `map_label`s;
  - `map.annotation_label_rects()` degree text;
  - the live map's own `%d km` scale rule.
- There are no airport names anywhere. The Godot audit scanned every visible Label, Button and RichTextLabel plus every skin-drawn string in all 20 frames (checked).
- There are no city labels beyond the four active places. Urban areas are unlabeled geography.
- NYC City Hall Park, Yonkers, Washington, D.C. Capitol ruins, the Chicago Loop, their geography, the route durations and all test contracts are unchanged.

## Checks

- **Godot** (`MAP_ART_CANDIDATE_OK 347 checks, 40 captures`, exit 0; report `outputs/…global-map-art_godot-checks_…f9e453b0.json`):
  - The live default scales equal the builder levels, and the default views draw 1:1.
  - **In all 20 state × language × resolution frames:**
    - every marker, region and view button, the route card, Depart, Cancel, the status panel and the calendar keep **identical rects** with the skin on;
    - route status, options, selection, card text, travel preview, calendar minutes and camera are identical;
    - the skin redraws the map frame while the header and bottom strip pixels stay unchanged;
    - pixel samples land on the expected palette (ocean, science, magic, culture, wuxia, nature on the globe; sea and land in the regions);
    - the text audit is clean;
    - `remove()` restores the map's own draw callbacks.
  - **With the skin on,** real mouse events at 1280×720:
    - the US Northeast badge opens the region;
    - New York, Yonkers and Washington each open their card, and Cancel closes it with no preview left;
    - Chicago opens a ready card.
  - The calendar stayed at 2537-05-25 08:00, the party stayed in New York, no `calendar_advanced` or `travel_completed` signal fired, and Depart was never pressed.
- **Python** (`MAP_ART_DETERMINISTIC_OK 67 checks`):
  - a byte-identical rebuild and manifest hashes;
  - `.ora` structure, an exact layer composite and binary alpha;
  - palette limits and size/unit-rect consistency for all 13 levels;
  - place registration (each place is on land or within 2 px of it at its default level);
  - the sphere rule, with 17 reference countries and science = {USA, CAN} only;
  - all globe tints present;
  - camera scales re-derived from the registry;
  - text sources;
  - isolation (no `game/` reference, no `.uid` / `.import`, no candidate path in `git status -- game`);
  - capture inventory and sizes.
- **Footprint:** comparing `git status` before and after the Godot runs shows only the 40 PNGs and the checks JSON added in `outputs/`. Nothing in `game/` changed and no `.uid` was written. Other sessions committed `f1489aa` and `7fc20ed` meanwhile and added one `tmp/` file; those are not this stream's.

## Captures (`outputs/`, inspected at gameplay scale)

States: `globe`, `globe-zoom2x` (exactly 2× the min scale over New York, so level 1 at 1:1), `us-northeast`, `us-northeast-card-washington-car` and `us-great-lakes-card-chicago-air`. Each was captured in zh and en, at 1280×720 and 640×360, as baseline and candidate. All 40 are listed with SHA-256 in `…global-map-art_capture-manifest_…f9e453b0.json`. I opened the zh/en 1280 and 640 candidates of every state and compared several against their baselines.

### What improved

- **Globe.** It now reads as a game world map rather than GIS data. The five spheres are visible as a colour language, science clearly leads, and the four locked spheres are named and marked locked. The graticule recedes, and the NYC→Chicago dashed arc and both region badges are legible.
- **US Northeast.** It has a road and city context the old view lacked. The selected NYC→Washington car ribbon is the strongest line on the map. The air route to Chicago is visibly a different stroke and points off-frame to a named Chicago tag. The ruins icon distinguishes Washington from the cities.

### Defects (honest, not fixed in v01)

1. **NYC / Yonkers crowding.** The two plates still stack tightly, because label sides are part of the click hitbox, which was kept unchanged by design. With a card open, the card still covers the right part of Yonkers' plate and the 73°W / 41°N labels (existing layout).
2. **Great Lakes air card.** Most of the 56 px air stub runs under Chicago's own label plate. Only the chevron and the `纽约` / `New York City` tag show, squeezed between that plate and the card. At 640×360 the en tag drops onto the Lake Michigan shore.
3. **Busy roads at small size.** At the default regional level the expressway network is still a dense amber web. At 640×360 it, together with the 2×2 urban dot texture, competes with the route ribbons. At 1280 the urban checker reads more as dotted noise than as city fabric.
4. **Unassigned grey.** Russia, Turkey and Greenland are neutral "unassigned" because canon does not place them. The large grey band over northern Eurasia can read as a sixth faction. The Antarctica DLC band is dimmer than in the first pass but still a wide light strip.
5. **Globe speckle.** At level 0, coast rims make the Canadian Arctic archipelago and the larger lakes look speckled.
6. **In-between zoom.** Textures exist only at the listed levels. In-between zoom (wheel ×1.25, pinch) stretches the nearest lower level up to about 1.9×, so texel widths are uneven and those frames are not pixel-exact.
7. **Chicago on the shoreline.** The Loop point falls one texel into Lake Michigan at the Great Lakes default level, so the marker sits on the shoreline (within 2 px of land; checked).
8. **Chrome unchanged.** The header, status panel, view buttons, route card, bottom strip and the gold hover/focus outline are untouched. They keep the old functional look, so the map and the chrome now differ in style.
9. **Small text at 640×360.** Sphere names are 9 px and the lock glyph is 5 px, small but readable at 640×360. In `globe-zoom2x` the science name falls off-frame and is skipped by design.
10. **Schematic car lines.** Car links are straight schematic connectors, not road-following lines (the data has no route geometry). A player may still read the gold line as a specific road.

## Open questions (for Codex / creator, not decided here)

- **Sphere membership** for transcontinental Russia and Turkey, for Greenland, and for US Caribbean territories. The candidate puts Puerto Rico and the US Virgin Islands in the borderlands under the Caribbean rule.
- Whether locked spheres should be **named** on the globe at all, or shown by colour only.
- Whether label sides (and therefore hitboxes) may move to fix NYC / Yonkers crowding.
- Whether car routes should follow real highway geometry, which would need route-geometry data with a source.

## Integration path (only after Codex visual review and creator approval; not done)

1. Move the skin's draw functions into `scifi_world_map.gd` (or a sibling script) behind a setting.
2. Ship the level PNGs as imported textures with nearest filtering.
3. Extend the global-map smoke, route-card and status-backing readability checks with this note's hitbox, route and text assertions.
4. Re-run the M2 smoke and integration regressions.

No gate, counter or Bible status may move from this note.

## Zero-change closeout (2026-10-16, ledger only)

- Recorded as a **zero-change** meter closeout: 35.8% → 35.8%, no gate, counter or category change. M2 stays 10/12 and the `map-art` gate stays **open**. Scenes 0/11.
- Re-run for the closeout: deterministic checks **67/67** (`MAP_ART_DETERMINISTIC_OK`). The Godot result is the recorded run: **347/347**, 0 failures, 40 captures. It was not re-captured.
- Codex visually inspected only the 640×360 globe and the US Northeast captures. It noted a **heavy route line** and **crowded NYC / Yonkers labels**. These issues and the defect list above remain **open**. This closeout is not a visual acceptance.
- No runtime integration. Only this note is tracked. The tools, assets and captures stay local and are hash-pinned in `outputs/rpg-2-star-ocean-the-second_mvp-completion-ledger_map-art-v01-locomotion-v02-closeout-evidence-index_v01_20261016-213224-7e11c4c6.json`.
