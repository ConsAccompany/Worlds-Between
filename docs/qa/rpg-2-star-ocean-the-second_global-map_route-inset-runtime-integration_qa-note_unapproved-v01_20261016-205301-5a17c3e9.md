# Global map — runtime route inset and label slots (Stream A)

**Status: UNAPPROVED. Code is in the working tree, uncommitted. Since 2026-10-16 ~21:10 ET it has been compiled and run in real Godot 4.7.2 and captured at native 640×360: 657/657 tool checks and 7 of 8 targeted regressions pass, and the one failure predates this change (see "Run results").** The map-art gate stays open. M2 stays at 10/12, the meter at 35.8%, scenes at 0/11. Nothing is committed or pushed, and the progress ledger, Game Bible and v02 skin files were not touched.

Answers: `docs/qa/rpg-2-star-ocean-the-second_global-map-v02_native-640-visual-hierarchy-review_unapproved-v01_20261016-193000-6c4b527e.md`, items 1, 2, 3 and 5. Item 4 (terrain finish) is not addressed.

## Run results (2026-10-16 ~21:10 ET, supervised Claude session)

The environment was verified first. `Godot_v4.7.2-stable_win64_console.exe --version` printed `4.7.2.stable.official.ed1daf0bf`. `claude auth status` reported `authMethod: claude.ai`, `apiProvider: firstParty` and `subscriptionType: max`, and `ANTHROPIC_API_KEY` was absent.

**Isolated copy.** Everything ran in `%TEMP%\sa5a`, so the shared tree's `.godot` cache and `.uid` files were untouched:

- `game/` minus `.godot`, which includes other streams' uncommitted files as they were at 21:05 ET;
- `tools/` holding this tool and the v02 skin script;
- `assets/map-art/` and the Natural Earth 110m source;
- an empty `outputs/`.

A native `--headless --import` of that copy exited 0 with no script errors. The only repo change is the 17 tagged outputs, copied back into `outputs/`. A `git status` diff before and after shows nothing else from this session.

**Tool:** one windowed run gave `ROUTE_INSET_RUNTIME_OK 657 checks, 16 captures` with 0 failures. The "Known risks" items about compiling (inner-class access to outer constants, the generated skin subclass) did not occur. The checks that ran:

- real click on the Chicago marker → card; click on the inset → no state change and no pan; real Cancel → card, preview and inset cleared, no time charged;
- real Depart → arrives in Chicago, charged 360 min (the card's whole-hour option), exactly one `travel_completed`;
- reverse Chicago→NYC card → Northeast view with the inset; reverse previews charged nothing;
- no `LGA/ORD/JFK/airport/机场…` word on any card or inset, and no clock time in any duration or arrival.

**Measured facts** (`…checks_test-only-v01_…5a17c3e9.json`):

| Fact | Value |
|---|---|
| Inset rect (map-local) | Chicago card `230,152 190×94`; reverse card `230,120 190×94`; 4 px left of the card |
| Inset chord | 151.4 px |
| Dashed-line light pixels | 219 (zh) / 225 (en) |
| NYC↔Yonkers label gap | 40 px browsing, 16 px with a card |
| Washington label clearance above the footer | 26 px, every state |
| Skin edge tags (Chicago card) | `纽约 · 不在本图` at `342,118 78×15`, `New York City · off this map` at `283,118 137×15`, pinned to the card's left edge |

**Captures** (`outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_<state>-640x360_test-only-v01_20261016-205301-5a17c3e9.png`, sha256 first 12):

| state | runtime | skin-v02-edge-tag |
|---|---|---|
| us-northeast-zh | 531af7050d58 | 92da75cfa848 |
| us-northeast-en | 9bc3ac4b98ab | ceec414ba404 |
| us-northeast-card-washington-car-zh | b0158c33cfa3 | 6d481babfc33 |
| us-northeast-card-washington-car-en | 321b24a9ee1e | 03e57bfe9225 |
| us-great-lakes-card-chicago-air-zh | f57dbf028b69 | b040c005572f |
| us-great-lakes-card-chicago-air-en | 3a0f2a7e2c62 | 2f9bfcc9d39e |
| us-northeast-card-nyc-from-chicago-air-zh | fba3661c6f7e | b96af1befcd8 |
| us-northeast-card-nyc-from-chicago-air-en | 236f683fedc5 | 6095d379cee0 |

The checks JSON hashes to `f4d0d0403550`. The inputs were `game/scripts/scifi_world_map.gd` at `767573972ff2` and the tool at `e036e9472d4b`.

**Regressions**, run in the same copy:

| Test | Result |
|---|---|
| `global-map-travel_integration-regression_m2-v02` (headless) | `OK checks=105` |
| `global-earth-travel_whole-hour-travel-rule-check_m2-v10` (headless) | `OK checks=246` |
| `global-earth-map_smoke_m2-v01` (headless) | `OK checks=212`. The first run failed only because the copy lacked the hashed 110m source; it passed once the source was copied in |
| `us-science-sphere_runtime-migration-smoke_m2-v02` (headless) | `OK checks=32` |
| `merchant-career-city-commerce_playable-path-smoke_m2-v01` (headless) | `OK checks=110` |
| `global-map-route-card_readability-check_m2-v01` (windowed, captures to temp) | `OK 109 checks` |
| `global-map-status-backing_readability-check_m2-v01` (windowed, captures to temp) | `OK 199 checks` |
| `scifi-world-map_background-visual-check_m8-v01` (windowed) | **FAIL** `button geometry scifi.city`. It fails identically with `git show HEAD:game/scripts/scifi_world_map.gd` swapped in, so it predates this change |

**What I saw in the captures:**

- No label collisions in either language. With a card open, the NYC and Yonkers labels move left of their dots.
- The inset reads clearly. The aircraft wedge points toward the destination in both directions, and the caption matches the card (`飞机 · 航程约 1180 km`, `Air · Flight ~1180 km`).
- The footer, calendar and scale bar are clear. Depart and Cancel are uncovered.
- A 6 px teal-edged sliver right of the card (x 634–640, y ≈93–110) is map water and coast showing between the card and the screen edge. It is identical in the pre-change v02 baseline capture, so it is not from this change.

**Visual questions left open (not defects the checks catch):**

- In the Northeast card states, the NYC selection ring and the Yonkers dot sit within about 2–6 px of the card's left edge, because the region framing doesn't pan for the card. This predates the change, but the dots read as crowded.
- The inset hides most of Pennsylvania while the reverse card is open.
- The inset keeps the flat v01r1 look.
- In the reverse skin view, the v02 skin draws no far stub or edge tag for Chicago (`edge_tags` is empty), so only the inset says where Chicago is.

## Evidence boundary (original session, superseded by "Run results")

The first Claude session (Stream A, 2026-10-16 ~20:53 ET) could not run Godot. Every attempt to start `work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe` asked for a permission approval. A non-interactive session can't grant one, and a subagent got the same refusal. So:

- **No Godot captures exist from this task.** None of the PNG names listed below have been produced.
- **No regression test was run**, not even the ones listed below. Results are unknown, not passing.
- The GDScript has only been reviewed by eye. Compile errors are possible (see Risks). The first run has to be treated as the real test.

The same session also couldn't confirm the Max subscription: `claude auth status` and the environment-variable checks also needed approval. It found nothing pointing to API billing, but this was not verified.

## What changed

Only `game/scripts/scifi_world_map.gd` changed in `game/`. New files: the test-only tool `tools/rpg-2-star-ocean-the-second_global-map_route-inset-runtime-integration_capture-check_test-only-v01_20261016-205301-5a17c3e9.gd` and this note.

1. **Route inset in the live map.** `RouteInset` is an inner `Control` adapted from the v01r1 test-only inset (`adea3798`, audited `b6d76529`).
   - **When it shows:** the route card is `ready` in a regional view, and the trip's origin (the party's place) is outside that view. That means either another geo region, or under/right of the card.
   - **What it draws:**
     - both places at their registry coordinates, on the same `us_east` land data (the globe's 110m land if a place lies outside that clip box);
     - a dashed true great-circle line with a generic aircraft wedge for air;
     - a dotted direction line for car, with no road geometry;
     - the party ring on the origin and the selection ring on the destination;
     - its own scale bar;
     - a caption with the card's own mode and approximate-distance strings (`飞机 · 航程约 1180 km`, `Air · Flight ~1180 km`).
   - **What it leaves out:** no duration, clock time or airport name. Durations and arrival dates stay on the card, which is unchanged.
   - **Placement:** the lowest, then rightmost, 190×94 slot left of the card and above the scale-bar row that covers no marker button, label or fixed control. Degree labels that would fall under it are dropped, as they already are for the card.
   - **Behaviour:** it ignores the mouse, and it hides on Cancel, Esc, region change and the globe. `route_inset_rect()` and `route_inset_wanted()` are public so skins and tests can avoid it.
2. **Label slots.** Labels are placed cities first, then other kinds. Each takes its registry `label_side` if that is clear, else the first clear slot in `right, left, below, above` and four diagonal slots.
   - "Clear" means inside the frame, with a 3 px gap from the fixed controls (status panel, zoom and view buttons, calendar text, the scale-bar area `SCALE_BAR_RECT`, and the open route card), from every other marker's 18 px dot box, and from labels already placed.
   - Marker dots and their coordinates never move, and each button still covers its own dot.
   - With the card open, NYC's and Yonkers' labels move out from under the card instead of being hidden beneath it.
3. **Washington and the footer.** The bottom row of controls and the scale bar are now obstacles for labels. A longer Washington label in either language must therefore take a slot above them, or beside them. It can no longer reach the 313 px footer.
4. **Off-screen stub (skin only).** The far-city tag lives in the v02 skin (`_offscreen_marker`), not in the runtime. The skin file is untouched. The new tool loads it through a generated subclass that only replaces `_offscreen_marker`:
   - a dotted leader runs from the stub tip to the edge of the free map area;
   - a plate is pinned to that edge, with an outward chevron;
   - the text reads `芝加哥 · 不在本图` / `Chicago · off this map`.

   These two strings exist only in the test tool. If the creator accepts this treatment, they belong in `world_map_text.gd`, a file this stream doesn't own.

## How to produce the evidence

Run from the repo root with a display (no `--headless`). The tool writes only files with its own tag:

```
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s C:/Users/hkzha/Documents/Codex/2026-10-12/rpg-2-star-ocean-the-second/tools/rpg-2-star-ocean-the-second_global-map_route-inset-runtime-integration_capture-check_test-only-v01_20261016-205301-5a17c3e9.gd
```

Expected outputs, all native 640×360:

- `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_<state>-<lang>-<presentation>-640x360_test-only-v01_20261016-205301-5a17c3e9.png`
  - `<state>`: `us-northeast`, `us-northeast-card-washington-car`, `us-great-lakes-card-chicago-air`, `us-northeast-card-nyc-from-chicago-air`
  - `<lang>`: `zh`, `en`
  - `<presentation>`: `runtime`, or `skin-v02-edge-tag` when the v02 skin assets are present. Up to 16 PNGs in all.
- `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_checks_test-only-v01_20261016-205301-5a17c3e9.json`

What the tool checks:

- **Inset geometry:** visibility in each card state; endpoints exactly on their coordinates; the line stays ≥6 px inside the inset, spans ≥100 px and points toward the destination; labels stay clear of the line, the aircraft and each other.
- **Inset placement:** clear of markers, labels, fixed UI, degree labels and the Depart button; the caption distance equals the card's.
- **Card text:** whole-hour durations (`total_minutes % 60 == 0`); no clock time in duration or arrival text; no airport or IATA words on the card or inset.
- **Labels:** pairwise separation; no overlap with fixed UI, the card, the footer or other markers; markers stay on their coordinates.
- **Real clicks:** marker → card; a click on the inset changes nothing; Cancel charges nothing.
- **Travel:** a real Depart charges exactly the card's whole-hour option once; the reverse Chicago→NYC card then shows the inset. This travel happens in a test save root, `user://test-saves/m2-route-inset-runtime-test-only-5a17c3e9`.
- **Pixels and skin:** rendered pixels show the inset border and the dashed line; skin tags are edge-pinned and say "off this map".

Regressions to run once Godot can run:

- **Headless:**
  - `global-map-travel_integration-regression_m2-v02`
  - `global-earth-travel_whole-hour-travel-rule-check_m2-v10`
  - `global-earth-map_smoke_m2-v01`
  - `us-science-sphere_runtime-migration-smoke_m2-v02`
  - `merchant-career-city-commerce_playable-path-smoke_m2-v01`
- **Windowed:** `global-map-route-card_readability-check_m2-v01` and `global-map-status-backing_readability-check_m2-v01`. Set `M2_CARD_CAPTURE_DIR` / `M2_STATUS_CAPTURE_DIR` to a temp folder.
- `scifi-world-map_background-visual-check` was already failing before this change, on old marker geometry.
- Don't run the v02 map-art capture tool for this check. It rewrites that candidate's own 40 tagged outputs.

## Known risks

- **Not compiled.** The inner classes use the outer script's constants and preloads (`COLOR_*`, `INSET_SIZE`, `GeoProjection`, `MapData`, `OFF_MAP`). This relies on GDScript resolving outer-class constants. If a run reports otherwise, pass the values in instead.
- **The generated skin subclass** uses `extends "<absolute path>"`. If it fails to compile, the tool records one failed check and still writes the runtime captures.
- **Labels move when the card opens.** With the Washington card open, NYC's label should move left and Yonkers' label above-left. That is clearer than labels hidden under the card, but the cluster is no longer one fixed layout. The creator may prefer fixed slots.
- **Globe badges** now also avoid the fixed controls and each other's dots, so a globe region label may take a different side than before.
- **The inset covers part of the regional map** while the card is open. Where it lands in the reverse Chicago→NYC Northeast view depends on Washington's and NYC's labels and hasn't been seen.
- **Caption width:** the zh caption is estimated at about 93 px. The tool's width check can fail if the font is wider than estimated.
- **Inset style** keeps the flat v01r1 look. It is not finished pixel art.

## Gate

The map-art gate stays **open**. This is not map-art acceptance, not visual approval and not runtime-default approval. Codex and the creator must review real captures first. No meter, ledger or Bible change.
