# M2 whole-hour travel rule: runtime simplification (m2-v10) — QA note

Date: 2026-10-16 (EDT). Author: Claude Code (Opus 5.5). Status: **implemented, tested and inspected by Codex; committed with the route-data gate change (§13).** §1–§12 record the state before that inspection; their "not committed / awaiting Codex / 35.0%" status lines are superseded by §13. The M2 `route-data` gate is now "Route times (whole-hour rule)", `implemented`; the meter is 35.8%; M2 is **not** accepted.

## 1. Rule implemented

Creator correction, now a game rule: “这不是一款模拟游戏，不用在时间上那么精细，把rules变简单化” ("This is not a simulation game; the time doesn't need to be that precise; simplify the rules").

- The global real-place map stays. Car or plane only between scenes. Travel advances the calendar. Walking happens only inside scenes.
- **Every available car or air leg settles to a fixed whole number of hours:** a plausible real-world city-to-city trip estimate rounded to the nearest hour (half up), never less than one hour. A multi-leg route charges the sum of its legs.
- Science MVP values: New York⇄Yonkers **1 h** by car; New York⇄Washington, D.C. **5 h** by car; Yonkers⇄Washington, D.C. **5 h** by car; New York⇄Chicago **6 h** by air in both directions.
- The charge never depends on the departure clock, the airports, check-in, baggage, waiting, rush hour or timetables.
- Players see only the transport mode, an approximate distance, the whole-hour trip time and the arrival date. **Superseded by §12 (m2-v11):** dates show year/month/day only, with no clock time.
- Earlier creator questions C1–C6 and their answers are superseded and are not modelled. Those answers were the 46-min Yonkers proxy, a direct car stop at the DC scene, generic air service, 60-min preparation, an all-hours average, a zero car start and a 15-min arrival.

## 2. What the interrupted session left, and what happened to it

The interrupted session had begun "choice-independent minute corrections" (m2-v09). I inspected its diff before editing.

| Interrupted edit | Decision | Reason |
|---|---|---|
| v02 travel JSON: 12-month BTS block-time medians 165 / 136 min, replacing the July-only 166 / 142 | **Kept as evidence**, moved into `referenceEvidence.components.flightMinutes` | A truthful source correction. It now feeds only the internal reference figure, never the charge. |
| v02 travel JSON: BTS source renamed to the 12-month ID `bts-ontime-2025-08_2026-07`; AA licence note (HTTP 403 on 2026-10-16, Delta independently says 2 h) | **Kept** | Truthful provenance. |
| v02 travel JSON: ORD car legs flagged "KNOWN ROUTING ERROR … depends on creator decision C5" | **Kept the flag, reworded** | The airside-routing error is real. The "pending C5" framing is gone, because C5 no longer exists. |
| v02 travel JSON: totals 364 / 332 charged through the sum of four components | **Replaced** | The component sum was the runtime rule the creator ruled out. 364 / 332 survive only as `referenceDurationMinutes`, which round to the charged 360 / 360. |
| `game/tests/…door-to-door-route-figures-check_m2-v06_…gd` (tracked) and its m2-v09 additions | **Deleted** (working tree) | Its whole model (component equality, 364 / 332 totals, door-to-door allowance 0) is superseded. Its useful idea, that an old-figure save loads exactly and is not re-priced, moved into the new v10 test (§6). |
| Bible state `routeFigureEvidence` (status `choice-independent-corrections-only`, 165／136, 364／332) and the matching builder canon check | **Rewritten** for the whole-hour rule | The old text described a runtime that no longer exists. It also cited an m2-v09 QA note that was never written; that link is removed. |
| `tools/…m2-chicago-air-route-card_block-time-revision-capture_m2-v09_…gd` (untracked) | **Left untouched and unstaged**; superseded by the v10 capture tool | It asserts 364 / 332 and would now fail. Codex can delete it. |
| `docs/progress.md` diff | **Left untouched** | It contained no travel content: inserted 2026-10-14 environment, paving and enemy-pilot entries from another workstream. A new 2026-10-16 entry is appended at the end, as a separate hunk. |

Other dirty files (`battle_arena.gd`, readiness checklist md/json, Bible `app_v01` js, Bible server v05) belong to other workstreams and were not touched.

## 3. Runtime source of truth (unambiguous)

Data: `game/data/world-travel/…m2-us-science-v02_20261015-175011-c454007b.json`. Place IDs, route IDs, segment IDs and retired aliases are unchanged.

- New top-level `travelTimeRule` (`id` `whole-hour-fixed-v1`). It sets `chargedField: "gameplayDurationMinutes"`, `referenceField: "referenceDurationMinutes"`, `stepMinutes: 60`, `minimumMinutes: 60` and `rounding: "nearest-hour-half-up"`, and records the creator's quote. The registry rejects data whose rule record disagrees with the code.
- Every segment now has `gameplayDurationMinutes`, the **only** charged value, and `referenceDurationMinutes`, the real-world estimate that value is rounded from.
- Air segments no longer carry `airportAccessMinutes`, `checkInAndWaitMinutes`, `flightMinutes`, `airportEgressMinutes`, `doorToDoorAllowanceMinutes`, `departureAirport`, `arrivalAirport` or `components` at the top level. That research now sits in `referenceEvidence` (`runtimeUse: "none"`), with `componentMinutes` that must add up to the reference. Car segments lost the zero `doorToDoorAllowanceMinutes`.
- `WorldRouteRegistry.segment_minutes()` returns `gameplayDurationMinutes` and nothing else. A route's `total_minutes` is the sum over its legs.

Validator (`game/scripts/world_route_registry.gd`) rejects a segment when:

- it is not a whole number of hours (≥ 60 and a multiple of 60);
- it is not `whole_hour_minutes(referenceDurationMinutes)`;
- it lacks a reference;
- it still has any retired top-level timing field;
- its `referenceEvidence` is not `runtimeUse: "none"`, its `componentMinutes` do not add up to the reference, or a documented component disagrees with the figure it explains.

Revising evidence within the same hour is accepted and leaves the charge unchanged. A revision that crosses a half hour is rejected until the hours are changed explicitly. Both are tested.

New static helpers: `whole_hour_minutes(reference)` and `approximate_km(km)`. The second gives whole km under 100 km and the nearest 10 km above that; it is used for display only.

## 4. Values

| Segment | Reference (min) and basis | Charged | Shown distance |
|---|---|---|---|
| seg.car.nyc__yonkers / yonkers__nyc | 35 / 35 (OSRM demo routing model) | **1 h** (min. 1 h) | road ~28 km |
| seg.car.nyc__washington-ruins / washington-ruins__nyc | 289 / 286 (OSRM) | **5 h** | road ~360 km |
| seg.car.yonkers__washington-ruins / washington-ruins__yonkers | 306 / 303 (OSRM) | **5 h** | road ~390 / ~380 km |
| seg.air.nyc-lga__chicago-ord | 364 = 24 + 120 + 165 + 55 (internal research sum) | **6 h** | flight ~1180 km |
| seg.air.chicago-ord__nyc-lga | 332 = 54 + 120 + 136 + 22 (internal research sum) | **6 h** | flight ~1180 km |

Road and flight distances stay in separate fields. New York–Chicago is air only. Yonkers–Chicago and Washington–Chicago stay `pending` with no time, and no figure is derived by adding legs. No car crosses open water.

## 5. Player-facing text

Route card (`scifi_world_map.gd` `route_option_text`, strings in `world_map_text.gd`). The `HH:MM` arrival times below are the m2-v10 state; §12 removed them:

- Before: `汽车 · 公路 28.2 km · 35分钟 / 抵达 … / 里程与旅时为估算`; `Car · Road 28.2 km · 35 min / Arrive … / estimated distance and time`.
- After:
  - `汽车 · 公路约 28 km · 1小时 / 抵达 2537年5月25日 09:00`
  - `Car · Road ~28 km · 1 h / Arrive May 25, 2537 09:00`
  - `飞机 · 航程约 1180 km · 6小时 / 抵达 2537年5月25日 14:00`
  - `Air · Flight ~1180 km · 6 h / Arrive May 25, 2537 14:00`

The estimate note is gone. The core preview lines (`AppState.travel_preview_lines`) now read `公路约 360 公里 · 旅时 5小时 · 抵达：…` and `Road about 360 km · Travel time 5 h · Arrival: …`. The "door-to-door time not yet verified" note is removed. The unavailable line now reads `暂无可用路线 · 不可出发` / `No route available yet · Cannot depart`.

The v10 test scans every string literal in `game/scripts/*.gd` and `game/scenes/*.tscn`, skipping comment lines and the registry's own validation messages. The scan finds no airport names or IATA codes (LGA, ORD, JFK, EWR, MDW, DCA, IAD), no check-in, baggage, boarding, timetable, rush-hour, layover or door-to-door wording, and no Chinese equivalents (机场／值机／行李／候机／登机／时刻表／高峰／航站楼／门到门). Airport names exist only in the travel JSON's `referenceEvidence` and attribution, which the UI never reads.

## 6. Save compatibility

The calendar core is still integer minutes (`TravelCalendar` is unchanged). Saves store absolute minutes and the `lastTravel` history; loading never re-prices a trip.

Tested:

- A save from the old 35-min Yonkers drive (clock 08:35, `lastTravel.minutes` 35) loads exactly, emits no events, and the next drive charges 60 (08:35 → 09:35).
- A save from the old 365-min flight (14:05) loads exactly, and the return then charges 6 h (→ 20:05).
- Re-saving and reloading keeps the clock.
- The existing Shanghai-era (v01) and pre-travel migrations still pass in the core smoke.

## 7. Tests run (Godot 4.7.2, this working tree)

Headless:

| Test | Result |
|---|---|
| **New** `game/tests/…whole-hour-travel-rule-check_m2-v10_20261016-145448-8353eeac.gd` | `M2_WHOLE_HOUR_TRAVEL_OK checks=211`, 0 script errors |
| `…calendar-route-core-smoke_m2-v01…` (updated) | `GLOBAL_TRAVEL_CORE_OK` |
| `…global-earth-map_smoke_m2-v01…` (updated fixture expectation) | `GLOBAL_EARTH_MAP_SMOKE_OK checks=212` |
| `…global-map-travel_integration-regression_m2-v02…` (updated) | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=105` |
| `…us-science-sphere_runtime-migration-smoke_m2-v02…` (updated) | `US_SCIENCE_MIGRATION_SMOKE_OK checks=32` |
| `…commerce-weekly-settlement_calendar-hookup-smoke…` | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` |
| `…merchant-career-city-commerce_playable-path-smoke…` | `MERCHANT_CITY_COMMERCE_PATH_OK checks=109` |
| `…merchant-fair-quote_rank-settlement-ui-smoke…` | `MERCHANT_FAIR_QUOTE_OK checks=92` |
| `…export-data-inclusion-smoke…` (source mode) | `EXPORT_DATA_INCLUSION_SMOKE_OK checks=24` |
| `…progression-ten-node_rules-save-ui-smoke…` | `PROGRESSION_TEN_NODE_OK checks=494` |
| `m2_smoke.gd` | `M2_SMOKE_OK` |

Windowed:

- `…global-map-route-card_readability-check…`: `ROUTE_CARD_READABILITY_OK 109 checks`
- `…global-map-status-backing_readability-check…`: `STATUS_BACKING_READABILITY_OK 199 checks`
- `…global-earth-map_visual-capture…`: `GLOBAL_MAP_CAPTURE_OK 22`. Its 22 regression PNGs were deleted afterwards, because the v10 captures below are the evidence set. The readability checks wrote to a temp dir.

The new v10 test covers:

- the exact hours of all 8 legs and routes;
- the rounding and distance helpers;
- 16 validator rejections, plus the same-hour accept and half-hour-crossing reject;
- a two-leg route charging 1 h + 6 h = 7 h, with road and flight km kept apart;
- identical previews at 7 departure clocks for all 8 trips;
- cancel costing 0 with no events;
- six 1 h hops (08:00 → 14:00) and a 23 h chain (→ 2537-05-26 07:00);
- crossing midnight (22:30 + 5 h → 03:30);
- crossing New Year (2537-12-31 20:00 + 6 h → 2538-01-01 02:00);
- a Sunday 22:00 drive crossing the week exactly once;
- old-minute saves (§6);
- zh/en card and preview text for all 8 trips (32 texts, with a count guard against silent aborts);
- the string-table scan.

The weekly commerce suites passed unchanged: they read leg minutes from the registry, and a 5 h Sunday-night drive still crosses Monday.

Node:

- `node tools/…game-bible-builder_v01… --check`: content equal, canon checks pass (§9).
- `node tests/game-bible-m2-global-travel/…gates_check…` (updated): passes.
- `node tests/game-bible-builder/…canon-reconciliation_check…`: passes.
- `node tools/…mvp-completion-meter…cli… check`: `CHECK OK 35.0%`, unchanged.
- `node tools/…geodata-attribution_validation-test…`: PASS. It reads the archived v01 Shanghai file and is unaffected.

Not re-run: the exported-pack mode of the export-inclusion smoke, and the full non-M2 sweep.

## 8. Captures (UI changed)

Tool: `tools/…m2-whole-hour-route-cards_capture_m2-v10_20261016-145448-7bbe9283.gd`, run windowed at 1280×720 over the 640×360 canvas. Result: `M2_V10_WHOLE_HOUR_CARD_CAPTURE_OK captures=8`.

Manifest: `outputs/rpg-2-star-ocean-the-second_m2-whole-hour-cards_manifest_m2-v10_20261016-150414-493ffce9.json`. It records the card text, minutes, the calendar before and after (May 25, 2537 08:00 → 14:00, charged 360) and the sha256 of each PNG.

PNGs `outputs/rpg-2-star-ocean-the-second_m2-whole-hour-card_<label>_m2-v10_20261016-150414-493ffce9.png`:

| Label | sha256 (first 12) |
|---|---|
| nyc-to-yonkers-zh | 4a19d3acb982 |
| nyc-to-yonkers-en | 1b68ae9fc86c |
| nyc-to-washington-zh | 358367876b82 |
| nyc-to-washington-en | 08d1b7203275 |
| nyc-to-chicago-zh | 342a1bd1fc2a |
| nyc-to-chicago-en | eb0a10105954 |
| chicago-to-nyc-zh | d04c45273447 |
| chicago-to-nyc-en | e79e0230043d |

I viewed the zh Yonkers and en Chicago cards: the text fits in two lines and `~` renders. These are unapproved runtime evidence, not visual acceptance.

## 9. Documentation and tracking text (no status or meter change)

- Rules doc `docs/design/…real-place-travel_rules-v01_20261014-235354-2b5d4d98.md`: a new 2026-10-16 rule block at the top. Rules 4–6 and the route data contract are rewritten; the superseded door-to-door wording is marked.
- Bible state `outputs/…game-bible_state_v01…json`:
  - the chapter travel paragraph and the time rule now state the whole-hour rule;
  - the remaining-work line now says to recheck reference figures under compatible terms;
  - `routeFigureEvidence` now has status `whole-hour-rule` and a `wholeHourRule.legHours` field that the builder checks against the travel data.
- Builder `tools/…game-bible-builder_v01…js`: the route canon check is replaced. It now asserts 1 / 5 / 5 / 6 h equal to `gameplayDurationMinutes`, no top-level components, and evidence links that exist.
- Progress state `outputs/…mvp-progress_state_v01…json`: only the M2 gate *detail* text changed:
  - route-preview, calendar, route-data and air-route describe the whole-hour rule;
  - route-data cites this note.
  - All gate statuses, the gate labels and `completionMeter` are byte-for-byte unchanged. I reverted a label rename of `route-data` because the meter stores gate labels in its `nextGate` text.
- `docs/progress.md`: new 2026-10-16 entry appended.

## 10. Proposed gate assessment (for Codex; applied in §13)

| Gate | Current | Proposal |
|---|---|---|
| route-preview, calendar, save-migration, acceptance-test, air-route | implemented | Stay implemented. Detail text already updated. |
| **route-data** (label still "门到门路线数值 / Door-to-door route figures") | estimate_only | **Recommend: rename to "路线旅时（整点规则）/ Route times (whole-hour rule)" and set `implemented`.** The charged values are now creator-decided whole hours enforced by the validator and tests, not unverified door-to-door estimates. Per the meter's own sample, this would move M2 9/12 → 10/12 and the meter about 35.0% → 35.8%. Remaining open item, which could be a separate pending request: the reference distances and minutes still come from the OSRM demo server (non-commercial terms). The conservative alternative is to keep `estimate_only` until those are replaced. Codex decides. |
| map-art | not_started | Unchanged. |
| visual-review | human_pending | Unchanged. |

Counters, all unchanged: runtime sprites **0/52**, science scene visuals **0/11**, human timed playtests **0/2**, 51 identities / 52 variants, meter **35.0%**. M2 stays in progress at 9/12.

## 11. Known limits

1. **Eastbound air rounding margin.** Chicago→New York's reference is 332 min, only 2 min above the 330-min (5.5 h) boundary. Correcting the known ORD airside-routing error downward by more than 2 min would round it to 5 h. The validator would then reject the creator's 6 h until someone changes the hours deliberately, or replaces the reference with a different representative city-to-city estimate. That is intended: the source of truth stays unambiguous.
2. The ORD car-leg routing error itself is not corrected. It is evidence only and is never charged.
3. Car reference distances and minutes are OSRM demo-server outputs. Their reuse terms are open (`request.car.self-hosted-osrm`). Displayed distances come from the same figures.
4. ~~The arrival shows date and clock time.~~ Resolved in §12: the card, the map calendar, the core preview lines and the Company panel show the date only.
5. Old saves keep off-hour clocks (e.g. 08:35), so their later arrivals stay off the hour. New runs start 08:00 and stay on the hour.
6. Route options still carry the internal `estimate` / `verified` flags (all legs `preliminary-estimate`). They are no longer displayed.
7. The exported-pack mode of the export-inclusion smoke was not re-run; source mode confirms the JSON is packed. The non-M2 full sweep was not run.
8. No human reviewed the cards. Captures are unapproved evidence.

## 12. Addendum m2-v11 (2026-10-16): the player calendar shows the date only

Creator correction, relayed by Codex after inspecting the real 1280×720 cards: this is an RPG, not a travel simulator. The cards' 1 h / 6 h values were right, but the card arrival (`抵达 2537年5月25日 14:00`) and the bottom-right map calendar (`2537年5月25日 08:00`) still showed `HH:MM`. Player-visible calendar text is now **year/month/day only**. The change is display-only. It does not touch travel values, data, art or other runtime systems.

### Changed (display only)

| File | Change |
|---|---|
| `game/scripts/world_map_route_adapter.gd` | `calendar_text()` returns `calendar_date_text_at(now)` only. Option `arrival_text` is the arrival preview's `text` (date) only; its `time_text` is ignored. `REQUIRED_METHODS` is unchanged, so `calendar_time_text_at` stays in the provider contract and departure is never disabled. Header comment states the date-only rule. |
| `game/scripts/app_state.gd` | `travel_preview_lines` arrival line is `抵达：<date>` / `Arrival: <date>`. `calendar_time_text_at` is kept and commented as the internal clock text (saves, tests, debugging). `travel_arrival_preview` still returns `time_text` for internal use. |
| `game/scripts/scifi_world_map.gd` | The Company panel's line is `日期：<date>` / `Date: <date>`. The `route_option_text` comment says "arrival date". |
| `docs/design/…real-place-travel_rules-v01…md` | 2026-10-16 rule block: "抵达日期（附时刻）" became date only, with the creator correction. The internal minute clock and its purposes are named, and time-of-day variation is added to the never-shown list. |

**Unchanged:**

- `TravelCalendar` and the integer-minute clock: accumulation, midnight, New Year and Monday week transitions, and commerce settlement.
- Save format and old-save loading. A save at 08:35 still loads at 08:35 internally and is not re-priced.
- `travel_duration_text` and all fixed hours.
- The travel JSON, the Bible state and builder (the Bible already said "抵达日期"), and the progress-state gates and meter.
- The HUD `play_time_text` ("本次探索 %02d:%02d" / "Run time"). It is elapsed real play time, not the in-game calendar, so it was left alone.

No established rule needed the clock in the UI. The only text that asked for it was this session's own §1 wording and limit 4, both now superseded.

### After

- `汽车 · 公路约 28 km · 1小时 / 抵达 2537年5月25日`
- `Car · Road ~28 km · 1 h / Arrive May 25, 2537`
- `飞机 · 航程约 1180 km · 6小时 / 抵达 2537年5月25日`
- `Air · Flight ~1180 km · 6 h / Arrive May 25, 2537`
- Map calendar: `2537年5月25日` / `May 25, 2537`.
- Core lines: `旅时 6小时 · 抵达：2537年5月25日` / `Travel time 6 h · Arrival: May 25, 2537`.

### Tests (Godot 4.7.2, this working tree)

Test edits:

- **v10 test:** new `CLOCK_TEXT` (`\d{1,2}:\d{2}`) check on all 32 card and core texts. A map calendar check runs in zh and en with the internal clock set to an old-save 08:35: the label is the date alone while `iso_text` still reads `2537-05-25 08:35`. A count guard covers it. Total: 211 → **246** checks.
- **Earth-map smoke:** the fixture's `time_text` ("+250") must not appear on the card.
- **Integration regression:** after loading a save, the map label equals the date and contains no `:`.
- **Merchant city path smoke:** after resting a week, the Company panel has the exact line `日期：<date>`, with no clock. 109 → **110** checks.

Headless, all exit 0 with 0 `SCRIPT ERROR`:

- `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
- `GLOBAL_TRAVEL_CORE_OK`
- `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
- `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=105`
- `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
- `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149`
- `MERCHANT_CITY_COMMERCE_PATH_OK checks=110`
- `MERCHANT_FAIR_QUOTE_OK checks=92`
- `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`
- `PROGRESSION_TEN_NODE_OK checks=494`
- `M2_SMOKE_OK`

Windowed:

- `ROUTE_CARD_READABILITY_OK 109 checks`
- `STATUS_BACKING_READABILITY_OK 199 checks`

Their PNGs went to a temp dir, not `outputs/`.

### Captures (before / after)

- **Before:** the m2-v10 set listed in §8. The `…nyc-to-chicago-zh/en…` and `…chicago-to-nyc-zh/en…` cards show `抵达 2537年5月25日 14:00` and the HUD `2537年5月25日 08:00`.
- **After:** run the tool `tools/rpg-2-star-ocean-the-second_m2-date-only-route-cards_capture_m2-v11_20261016-151244-02e0f2f0.gd` windowed. It printed `M2_V11_DATE_ONLY_CAPTURE_OK captures=9`. It uses the same flow as v10, adds a card-plus-HUD no-clock assertion, and captures the map after arriving in Chicago. The manifest (`outputs/rpg-2-star-ocean-the-second_m2-date-only-cards_manifest_m2-v11_20261016-151511-c1ed4ab2.json`) records:
  - each card's text and calendar label;
  - `dateOnly: true` for all 8 cards;
  - internal clock 08:00 → 14:00, with 360 minutes charged;
  - the HUD after arrival, `May 25, 2537`.

PNGs `outputs/rpg-2-star-ocean-the-second_m2-date-only-card_<label>_m2-v11_20261016-151511-c1ed4ab2.png`:

| Label | sha256 (first 12) |
|---|---|
| nyc-to-yonkers-zh | bdf84df54cc4 |
| nyc-to-yonkers-en | 19face254057 |
| nyc-to-washington-zh | 944be4a7d0cb |
| nyc-to-washington-en | 754f5ce175c0 |
| nyc-to-chicago-zh | 7f4e34762c90 |
| nyc-to-chicago-en | f528422dabc3 |
| arrived-chicago-en | 0673d1467017 |
| chicago-to-nyc-zh | 62591ae120e9 |
| chicago-to-nyc-en | 802907a86874 |

I viewed the zh Yonkers card, the zh and en NYC→Chicago cards, the en Chicago→NYC card and the post-arrival map. Each card fits in two lines, and the date-only HUD label sits right-aligned in its backing.

Pre-existing and unchanged: the Yonkers map label is partly covered by the open route card in the Northeast view.

The captures are unapproved runtime evidence.

### Status

~~Not committed. The route-data gate stays `estimate_only` and the meter stays at **35.0%** until Codex validates.~~ Superseded by §13.

## 13. Route-data gate implemented (2026-10-16, after Codex inspection)

Codex independently reviewed the route registry and travel data and the Godot 1280×720 m2-v11 date-only captures. The NYC→Chicago zh card and the NYC→Yonkers en card show the mode, an approximate distance, 6 h / 1 h and the arrival **date only**. The map calendar shows the date only. Codex reran `M2_WHOLE_HOUR_TRAVEL_OK checks=246`, `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=105` and `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`. This is technical evidence, not M2, art or playtest acceptance.

### Gate and wording changes

- **Progress state, M2 `route-data`.** The label "门到门路线数值 / Door-to-door route figures" became "路线旅时（整点规则）/ Route times (whole-hour rule)". The status `estimate_only` became **`implemented`**. The detail states the rule, the 1 / 5 / 5 / 6 h values with their reference figures, the date-only card, and the limit: the reference figures are still preliminary and this is not map-art or human acceptance. The evidence is this note and the m2-v11 manifest. Game test files are not cited, because the Bible's evidence route serves only `docs/qa/` and `outputs/`.
- **Calendar gate label.** "整数分钟日历 / Integer-minute calendar" became "日历（整点旅时，只显示日期）/ Calendar (whole-hour trips, date-only display)".
- **Other current-rule text fixed.**
  - M2 step summary, blocker, details and `remaining[0]`. These still named an "integer-minute calendar", "08:00 placeholder time of day", "BTS July medians plus a 120-minute check-in allowance" and "route figures are preliminary".
  - `m2Expansion.researchPacketNote`, which named the July BTS medians.
  - Bible state `routeFigureEvidence` (now 10/12, date only, M2 not accepted), the new-game date question and the world chapter's date-only arrival.
  - Bible app (`outputs/…game-bible_app_v01…js`) M2 summary line, which had said "分钟日历" and "真实门到门旅时 … 仍未完成".
  - The Production rule card, which had said "旅时参考真实地理距离", "出发按路线分钟推进日历" and "路线仍是初步估算".
  - Rules doc: the 2026-10-15 block is labelled history, and a 2026-10-16 status line was added.
- **Unchanged.** `map-art` (`not_started`), `visual-review` (`human_pending`), runtime sprites **0/52**, science scene visuals **0/11**, human playtests **0/2**, and 51 identities / 52 variants. Travel data, scripts and the internal minute save format are unchanged.

### Checks updated

- **Builder canon checks: 32 → 33.** The route-times check now requires 10/12, date-only and not-accepted wording. A new check requires the implemented route-data label and the date-only calendar label, rejects any door-to-door or integer-minute gate label, and confirms that map art and review remain open.
- **M2 gate check.** It now expects 10 implemented and 2 open gates, the new labels, no "仅初步估算" badge or door-to-door label, and a rule card stating fixed whole hours and a date-only calendar.
- **Canon reconciliation check.** It now expects 10/12, with route-data as the whole-hour gate.
- **Meter self-test.** It now expects the real state at 35.8% (10/12). The "count change" fixture moved from route-data to map-art in a temp copy: 36.7%, 39.2% with pacing, 31.8% after reopening M4, and +0.48 → 36.3% for one backed sprite.

### Meter

Recorded through the meter CLI as `closeout-20261016-192517-a21f7e7f`, claiming `global-world-travel/route-data`. The six compartments:

| Compartment | Count | Percent |
|---|---|---|
| Core gameplay | 5/5 | 100% |
| Global world and travel | 10/12 | 83.3% |
| Science playable content | 3/4 | 75% |
| Character art | 0/52 | 0% |
| Science environment art | 0/11 | 0% |
| Final integrated validation | 0/2 | 0% |

The weighted estimate moved from **35.0% to 35.8%** (+0.83 points). `CHECK OK 35.8%`.

### Committed proof captures

- `outputs/rpg-2-star-ocean-the-second_m2-date-only-cards_manifest_m2-v11_20261016-151511-c1ed4ab2.json` (unchanged; it lists all nine captures with sha256)
- `…m2-date-only-card_nyc-to-chicago-zh_m2-v11…png` (sha256 7f4e34762c90…)
- `…m2-date-only-card_nyc-to-yonkers-en_m2-v11…png` (sha256 19face254057…)
- The m2-v11 capture tool.

The other seven m2-v11 PNGs and the m2-v10 set stay local and uncommitted. The superseded m2-v09 capture tool is still untracked.
