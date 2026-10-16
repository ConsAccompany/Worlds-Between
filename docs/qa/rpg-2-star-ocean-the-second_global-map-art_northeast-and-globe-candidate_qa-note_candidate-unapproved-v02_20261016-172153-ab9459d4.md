# Global Earth + US regional map-art candidate v02 — QA note

- **Status:** **UNAPPROVED / NONRUNTIME** map-art candidate for Codex visual review. Not creator-accepted.
  - v02 is a **separate, test-only** candidate. v01 (`candidate-unapproved-v01_20261016-164615-f9e453b0`) also stays UNAPPROVED / NONRUNTIME, and its bytes are unchanged (checked against v01's own manifests).
  - The M2 `map-art` gate stays **open**. Science scene quality stays **0/11** and the MVP meter is unchanged at **35.8%**.
  - No runtime default changed. No file under `game/` was edited, and no Game Bible file or Git state was touched (nothing was staged or committed).
- **Tag:** `candidate-unapproved-v02_20261016-172153-ab9459d4` (2026-10-16, local time).
- **Worker:** Claude Code CLI 2.1.300, Opus 5.5, signed in through Claude Max (`claude auth status`: `authMethod claude.ai`, `apiProvider firstParty`, `subscriptionType max`).
  - `ANTHROPIC_API_KEY` was checked and is **absent**.
  - No API billing, usage credits, paid fallback or image-generation service was used.
  - Every pixel is computed from Natural Earth public-domain geodata and the game's own runtime geodata. The captures are real Godot 4.7.2 renders (Compatibility renderer, windowed, not `--headless`).
- **Answers:** the Codex visual review of v01 found two problems in the US Northeast view:
  - a heavy near-black diagonal NYC–Washington route;
  - congested NYC / Yonkers labels at 640×360.

  It also confirmed that the globe makes the five spheres distinguishable. v02 corrects only what needs no creator decision.

## Files

| Part | File | Role |
|---|---|---|
| Layer builder | `tools/…global-map-art_pixel-layer-builder_candidate-unapproved-v02_…ab9459d4.py` | `extract` (pinned Natural Earth → v02's own subset), `build`, `check` (byte-identical rebuild) |
| Runtime skin (test-only) | `tools/…global-map-art_godot-runtime-skin_candidate-unapproved-v02_…ab9459d4.gd` | Swaps the map's two draw callbacks and recolours label plates. `apply()` / `remove()` |
| Capture + checks | `tools/…global-map-art_godot-capture-check_candidate-unapproved-v02_…ab9459d4.gd` | `-s` tool: real map scene, baseline and candidate frames, hitbox / route / text / pixel / click checks, plus the v02 route-weight checks |
| Deterministic checks | `tools/…global-map-art_deterministic-checks_candidate-unapproved-v02_…ab9459d4.py` | 103 offline checks, including read-only v01 vs v02 metrics; `--write-index` writes the capture manifest |
| Assets (19 files, 6.7 MB) | `assets/map-art/global-map-art-candidate-v02-ab9459d4/` | 13 flat level PNGs, 3 editable `.ora`, v02 NE subset, runtime meta, manifest |
| Editable layered sources | `…globe-lv0-layered-source….ora` (10 layers, new `lakes-flat`), `…us-northeast-default-layered-source….ora` (13), `…us-great-lakes-default-layered-source….ora` (13) | OpenRaster (Krita / GIMP). Binary alpha; layer composite == merged == runtime PNG (checked) |
| Captures (40) + reports | `outputs/rpg-2-star-ocean-the-second_global-map-art_<state>-<zh\|en>-<1280x720\|640x360>-<baseline\|candidate>_candidate-unapproved-v02_…ab9459d4.png`, `…godot-checks_…ab9459d4.json`, `…capture-manifest_…ab9459d4.json` | One image per file, no contact sheets. The capture manifest also carries the v01 vs v02 metrics |

**Isolation.**
- None of v02's builder, skin or capture tool reads a v01 file or folder (checked).
- v02 re-extracted its own subset from the same six pinned Natural Earth v5.1.2 files (SHA-256 verified). The sources are in `%TEMP%\wb-mapart-ne-src-20261016` and are not stored in the repo.
- The subset adds two Natural Earth attributes, used only for zoom filtering: road `scalerank` and urban `area_sqkm`.
- Only the deterministic checker reads v01 files, and only to compare against them.

## What changed from v01 (and why it needs no creator decision)

### 1. Car connector subordinate to markers and card selection; route hierarchy kept

| | v01 | v02 |
|---|---|---|
| Card-selected route | 2 px bright gold core + near-black casing (4 px total) | 1 px core in the route card's own kind-text cream `#e9d9a8`, plus a 1 px soft drop shadow in dark land teal `#1f3b35` (luma 0.21, not black) |
| Routes from the party's place | 1 px gold, cased | 1 px muted cream `#b9aa7c`, no casing (air: dashed `#a9c7c4`) |
| Other available routes | dim gold dots (1 on, 2 off) | sparse dots close to the land tone (1 on, 3 off; air 2 on, 4 off) |
| Marker ends | line runs into the icon and the here-ring | every connector stops 7 px short of a marker (square distance, so the icon plus a 1 px margin stays clean) and 9 px short at the party's place (clears the here-ring) |
| Selection brackets | white | the route card's border teal `#79cfc0`, so the selected marker visibly belongs to the open card |

- The hierarchy is kept and checked in all 20 frames: per mode, the luma order selected > party > other holds in every frame, and the shadow appears only on the selected route.
- On the globe, the link between the two region badges (NYC–Chicago air) is cut back to the badges' edges, so its dash shows between them instead of under them.
- **Measured** in the real NYC–Washington card captures (same camera and window pixels for v01 and v02; band ±2.5 logical px around the route; plates, card, buttons and marker boxes excluded):

| Capture | v01 near-black share | v02 near-black share |
|---|---|---|
| zh 640×360 | 41.8% | **0.0%** |
| en 640×360 | 41.8% | **0.0%** |
| zh 1280×720 | 41.6% | **0.0%** |
| en 1280×720 | 41.5% | **0.0%** |

### 2. Default-zoom road and urban noise reduced (filtering by Natural Earth's own ranks; nothing invented)

At the min and default regional levels v02 draws:
- only the **backbone expressways** (Natural Earth `scalerank` ≤ 3), in a quiet sage `#5a806c` instead of amber;
- only the **urban areas of at least 150 km²**, as one flat tone with no edge line and no 2×2 checker.

At higher zoom:
- From 2× the default: all expressways (muted amber), the other major highways, and urban areas ≥ 40 km².
- From 4×: secondary highways and all urban areas, with a sparse texture.

| Default level | v01 | v02 |
|---|---|---|
| US Northeast road pixels | 9,598 | **3,708** |
| US Great Lakes road pixels | 8,084 | **2,543** |
| Mean road-to-land luma contrast | 0.235 | **0.109** |
| Urban checker texels (both regions) | > 0 | **0** |
| Road + urban edge density, US Northeast | 0.085 | **0.025** |
| Road + urban edge density, US Great Lakes | 0.046 | **0.012** |
| Whole-land edge density (incl. unchanged land dither), US Northeast | 0.231 | 0.175 |
| Whole-land edge density, US Great Lakes | 0.195 | 0.160 |

### 3. Globe island / lake speckle generalised at the two smallest levels (lv0 ×1, lv1 ×2)

- Enclosed water specks smaller than 10 px (lv0) or 8 px (lv1) become land of the surrounding sphere: 220 / 261 specks.
- Lakes that remain are one flat tone, with no shelf bands, wave ticks or graticule.
- Islands under 4 px are one flat light dot (100 / 135 islands), **kept, not deleted**.
- The relief rim follows sea coasts only. It skips one-pixel spurs, and one de-speckle pass reverts rim pixels that would sit isolated.
- lv2 and lv3 (zoomed in) are **not** generalised.

| Globe | v01 isolated px on coast band | v02 | Land-area change from generalisation |
|---|---|---|---|
| lv0 | 1,924 | **290** | +1.22% |
| lv1 | 3,900 | **524** | +0.39% |

- **Honest cost:** at lv0 / lv1 small enclosed lakes and one-pixel inlets are filled. This is cartographic generalisation at 1.5–3 px per degree; the large lakes (Great Lakes, Hudson Bay, Caspian, Victoria …) remain.

### 4. Map-only palette unified with the header / card (their rectangles, text and logic unchanged)

- Water `#0f1e2a` now sits between the header `#0d1723` and the card fill `#12212b`: RGB distance to the nearest chrome tone fell from 10.2 (v01) to 4.4. The shelf tones moved toward the status-panel border `#25404b` (19.5 → 11.7), and the globe equator uses that border colour exactly (22.3 → 0).
- Region land is slightly deeper, so the cream / teal UI stays on top.
- Label plates, the off-screen tag and the scale bar use the live map's own `COLOR_LABEL_BG`, `COLOR_TEXT` and `COLOR_SUBTEXT`. These are read from the map script at run time, not copied. v01 had used its own warm white and a different plate fill.
- The only plate change against the live map is that the **outskirts** plate's primary line uses `COLOR_SUBTEXT`, so New York City leads the NYC / Yonkers pair. Plate geometry and text are unchanged.
- The chrome reference colours in the builder are re-read from `game/scripts/scifi_world_map.gd` by the checker and must match.

### Not changed (by instruction)

- **Click geometry.** No place, route, marker or label click geometry changed. Every marker and region button, the card, Depart, Cancel, the status panel and the calendar keep identical rects with the skin on, in all 20 frames.
- **Places and routes.** No place or route was added. There are still exactly three car links and one air link, from `WorldRouteRegistry.routes_between`.
- **No invented data.** No airport name, airport, road geometry or new string.
- **Spheres.** Russia, Turkey, Greenland and Bermuda / St. Pierre and Miquelon stay **unassigned**. Puerto Rico and the US Virgin Islands stay in the Caribbean borderland exactly as in v01; that is still an open question (below).
- **Sphere names.** All five sphere names are drawn on the default globe in zh and en at both resolutions (checked; none hidden).

### Schematic nature (explicit)

- The car lines are **schematic connectors** between two places. The travel data has no road geometry, and v02 adds none.
- The quieter, thinner cream line no longer looks like a painted highway. It still runs straight across the land, though, and a player can still read it as "a road". The route card's "Car · Road ~360 km" text is the live map's own.

## Checks

- **Godot** (`MAP_ART_CANDIDATE_OK 499 checks, 40 captures`, exit 0; report `outputs/…godot-checks_…ab9459d4.json`):
  - all v01 checks: scales and levels 1:1, identical hitboxes / UI rects, route state, camera, preview / calendar / card text, frame redraw with header and bottom strip unchanged, palette samples, the text audit, `remove()` restores the callbacks, and the real mouse clicks (US Northeast badge, NYC / Yonkers / Washington cards and Cancel, Chicago ready card, no time charged);
  - v02 additions, per frame:
    - plates use the live label / text colours (20 frames);
    - all connectors are 1 px cores, none darker than luma 0.3, with the shadow only on the selected route (20);
    - the per-mode hierarchy holds (40);
    - exactly the expected route is drawn as selected: NYC–Washington car in the Washington card, NYC–Chicago air in the Chicago card, none without a card;
    - every connector end stops its square gap short of its marker (12 region frames: 7.0–9.0 px);
    - no selected or party route pixel lies inside any marker's 11×11 box in the real capture (12 region frames, 0 hits);
    - the globe NYC–Chicago dash is visible between the badges (8 globe frames: 4 px at ×1, 15 px at ×2).
  - The calendar stayed at 2537-05-25 08:00, the party stayed in New York, no `calendar_advanced` or `travel_completed` signal fired, and Depart was never pressed.
- **Python** (`MAP_ART_DETERMINISTIC_OK 103 checks`):
  - a byte-identical rebuild, manifest hashes and status (UNAPPROVED / NONRUNTIME, gate open, 0/11, 35.8%);
  - the v02 subset comes from the six pinned files;
  - `.ora` structure, exact composite and binary alpha;
  - palette discipline for all 13 levels;
  - place registration;
  - the sphere rule (17 reference countries; science = USA + CAN only; Russia / Turkey / Greenland unassigned);
  - camera scales re-derived;
  - text sources; isolation (no `game/` reference to either tag, no `.uid` / `.import`, no candidate path in `git status -- game`, no v01 path in the v02 tools);
  - **v01 bytes untouched** (17 v01 asset outputs, 40 v01 captures and the v01 tools match v01's manifests);
  - capture inventory and sizes;
  - every v02 Godot check family;
  - the metric tables above, each with a pass threshold. The corridor needs v02 ≤ 1% and v01 ≥ 15%, so v01 itself is the positive control that the metric detects the old casing.
- **Footprint:** comparing `git status` before and after shows only the four v02 tools, the 40 PNGs and the checks JSON in `outputs/`, plus the v02 asset folder inside the already-untracked `assets/map-art/`. Nothing in `game/` changed and no `.uid` was written.
  - Other sessions meanwhile changed `game/scripts/growth_rules.gd` and `growth_screen.gd`, and added the NYC chp v04 candidate and the science-career stage-1 files. They also committed `3841241`, which tracks the v01 QA note. None of these belong to this stream.

## Captures inspected at gameplay scale

I opened every one of these at its native size and enlarged crops of the 640×360 frames, side by side with the matching v01 capture:
- the 640×360 candidates of `globe` (en), `globe-zoom2x` (zh), `us-northeast` (en, and zh crop), `us-northeast-card-washington-car` (en, zh) and `us-great-lakes-card-chicago-air` (en);
- the 1280×720 candidates of `globe` (zh) and `us-northeast-card-washington-car` (zh).

**Compared with v01:**
- **US Northeast, Washington card.**
  - The diagonal is now a thin cream line with a soft shadow. It is still the brightest line on the map, but it no longer competes with the Washington ruins icon, the teal selection brackets or the card.
  - The parallel Yonkers–Washington "other" route is a faint dotted trace, not a second dark band.
  - The roads read as background context, and the Philadelphia / NYC urban fabric is soft flat patches.
- **US Northeast default (no card).** The party routes (NYC–Washington, NYC–Yonkers) are visible but muted. The Chicago air stub and its tag are unchanged in role.
- **Globe.**
  - The Canadian lakes and Arctic islands read as clean shapes instead of rim speckle.
  - The ocean, header and status panel now share one navy family.
  - The five sphere tints, names and lock glyphs are as in v01.
- **Great Lakes, Chicago air card.** The default level is quieter; otherwise unchanged (see defect 2).

## Unresolved defects

1. **NYC / Yonkers crowding at 640×360.** It is reduced only in emphasis (outskirts primary line dimmed, the connector gap and ring no longer pile up on the icons), not in layout. The two plates still stack, and with a card open the card still covers the right part of Yonkers' plate and the 73°W / 41°N labels. Fixing this needs the label sides, and therefore the hitboxes, to move: a creator decision.
2. **Great Lakes air stub** still runs mostly under Chicago's own plate, between that plate and the card (unchanged from v01).
3. **Land dither.** The low-density land dither, state lines and coast rim are v01's technique. Whole-land edge density fell only 18–24% because of them.
4. **Unassigned grey.** Russia, Turkey and Greenland stay grey because canon does not place them. The large grey band can still read as a sixth faction.
5. **Generalisation trade-off.** At lv0 / lv1 small lakes and inlets are filled (land area +1.22% / +0.39%). Some readers may miss a specific small lake at the smallest zoom.
6. **In-between zoom** still stretches the nearest lower level (uneven texels; unchanged from v01).
7. **Chicago on the shoreline** at the Great Lakes default level (within 2 px of land; unchanged).
8. **Chrome style.** The chrome itself (header, buttons, card, gold hover outline) is untouched by instruction. The map moved toward it in colour, but the chrome keeps its flat functional look.
9. **Thin selected route at 640×360.** The 1 px selected route is quiet. It is clearly the brightest line, but a reviewer may want it one step stronger. That would be a tuning choice within the hierarchy, not a structural change.
10. **Schematic car lines** (see above). They are straight connectors, not roads.

## Open decisions (for Codex / creator; not decided here)

- **Sphere membership** of transcontinental Russia and Turkey, of Greenland, and of US Caribbean territories (currently borderland).
- Whether locked spheres stay **named** on the globe (v02 keeps all five names, as instructed).
- Whether **label sides (hitboxes) may move** to fix NYC / Yonkers crowding.
- Whether car routes should follow **real highway geometry**, which needs sourced route-geometry data.
- Whether the **chrome** (buttons, card, header) should get a matching pixel restyle. v02 only moved the map toward the chrome.

## How to reproduce

From the repo root, with the real Python (`C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`):

```
python tools/…pixel-layer-builder_…ab9459d4.py build        # or: check   (~2 min)
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to …godot-capture-check_…ab9459d4.gd>
python tools/…deterministic-checks_…ab9459d4.py --write-index   # ~4 min; reads v01 files for comparison only
```

- `extract --source-dir DIR` re-derives the v02 subset from the six pinned Natural Earth GeoJSON files.
- The Godot capture needs a window (not `--headless`). Delete this tag's own captures before re-capturing.

## Integration path (only after Codex visual review and creator approval; not done)

Same as v01:
1. Move the skin's draw functions into the map script (or a sibling) behind a setting.
2. Ship the level PNGs as nearest-filtered textures.
3. Extend the global-map smoke, route-card and status-backing checks with this note's hitbox, route-weight, marker-gap and text assertions.
4. Re-run the M2 regressions.

No gate, counter or Bible status may move from this note.

## Zero-change closeout (2026-10-16, ledger only)

- Recorded as a **zero-change** meter closeout: 35.8% → 35.8%, no gate, counter or category change. M2 stays 10/12 and the `map-art` gate stays **open**. Scenes 0/11.
- Re-run for the closeout: deterministic checks **103/103** (`MAP_ART_DETERMINISTIC_OK`, read-only mode, no `--write-index`). The Godot result is the recorded run: **499/499**, 0 failures, 40 captures. It was not re-captured.
- Codex viewed the globe and the NYC / Washington 640×360 captures. It judged the route **thinner** and the texture **better** than v01, but the **labels still crowd**. That issue and the defect list above remain **open**. This closeout is not a visual acceptance.
- No runtime integration. Only this note is tracked. The tools, assets and captures stay local and are hash-pinned in `outputs/rpg-2-star-ocean-the-second_mvp-completion-ledger_map-art-v02-nyc-v04-career-s1b-closeout-evidence-index_v01_20261016-220533-2f06d687.json`.
