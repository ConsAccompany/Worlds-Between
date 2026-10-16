# M2 NYC–Chicago door-to-door route figures: offline resume, runtime held at v02 (QA note, m2-v06)

- Date: 2026-10-16 00:36 America/New_York.
- Resumes the interrupted v06 attempt. That attempt stopped because repeated wide BTS/Chicago monthly downloads returned HTTP 500/503.
- **No network calls this session.** Everything below uses data already on disk under `%LOCALAPPDATA%\Temp\wb-m2v06-*`, collected by the earlier attempt. No paid service or API credit was used.
- Previous notes:
  - v02 audit: `docs/qa/rpg-2-star-ocean-the-second_m2-us-science-route-figures_real-world-travel-audit_qa-note_m2-v02_20261015-195053-10d2525c.md`
  - v03 curbs: `…_m2-nyc-chicago-airport-curb-endpoints_v03-candidate_qa-note_m2-v03_20261015-200518-7c3e19a4.md`
  - v04 blocked: `…_m2-nyc-chicago-typical-door-to-door_resume-attempt-blocked_qa-note_m2-v04_20261015-224916-c4e1a7b2.md`
  - v05 measured car legs: `…_m2-nyc-chicago-typical-door-to-door_measured-car-legs_qa-note_m2-v05_20261015-232832-cfba3fc5.md`
- **M2 door-to-door route-figures gate: stays OPEN.** The meter is unchanged: `global-world-travel` 9/12, overall 35.0% (zero-change closeout `closeout-20261016-043726-b404b4aa`).

## 1. Decision: no runtime promotion

The interrupted attempt had pointed `WorldRouteRegistry.DEFAULT_DATA_PATH` and the Game Bible gates test at a v03 runtime file (`…_m2-us-science-v03_20261016-002146-b65dc35e.json`). **That file was never written**, so as left the runtime would not have loaded.

I chose to simplify rather than finish the promotion:

- The default path is back on **v02**. The Game Bible gates test edit is reverted to HEAD.
- Reasons:
  - The Chicago rideshare sample is incomplete (§3).
  - The arrival allowance (E3) and the time-of-day policy (E6) are still undecided by the creator.
  - The dispatch note says "no runtime promotion without review".
  - Promoting would also mean editing the Game Bible gate text, which other sessions currently have dirty.
- **Kept:** the new registry guard `_check_components` in `game/scripts/world_route_registry.gd`. Any documented `components.<field>.value` must equal the field the runtime charges. A `rawMedianMinutes`, if present, must round half up to that field. v02 already satisfies this.
- **Simplified:** the new Godot test now checks v02 instead of the unwritten v03 file. It has no placeholder values.

## 2. Observed test output (this session)

| Test | Output |
|---|---|
| `game/tests/…_global-earth-travel_door-to-door-route-figures-check_m2-v06_20261016-002146-6dc4d1f1.gd` (new) | `M2_ROUTE_FIGURES_V06_OK checks=12`, exit 0 |
| `game/tests/…_global-earth-travel_calendar-route-core-smoke_m2-v01_20261015-024215-a19d5ae7.gd` | `GLOBAL_TRAVEL_CORE_OK`, exit 0 |
| `game/tests/…_global-map-travel_integration-regression_m2-v02_20261015-031232-786a054d.gd` | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=105`, exit 0 |
| `tests/game-bible-m2-global-travel/…_gates_check_m2-v01_20261015-064400-06efaa9b.js` (unchanged, HEAD) | `RESULT PASS (5 checks)`; route figures match v02 |
| Meter `check` (before the closeout) | `CHECK OK 35.0%` |

The new test checks four things:
- The v02 path is loaded and valid.
- The air components equal the charged fields: 24+120+166+55 = 365 westbound and 54+120+142+22 = 338 eastbound.
- All 8 segments are `preliminary-estimate` with a door-to-door allowance of 0.
- The guard behaves as intended: drift is rejected, a raw 22.5 against a charged 22 is rejected, 22.49 is accepted, and non-object `components` are rejected. NYC↔Chicago still offers one unverified estimate route each way.

## 3. Local evidence available (not promoted; recomputed offline)

These were recomputed by `%LOCALAPPDATA%\Temp\wb-m2v07-scripts\offline_summary.py`, which runs stdlib only under `python -I` and reads files only. The output is in `%LOCALAPPDATA%\Temp\wb-m2v07-offline-summary.json`. All times are medians in minutes. The window is 2025-09-01 to 2026-08-31 for NYC and Chicago, and Aug 2025–Jul 2026 for BTS.

| Component | Source (local) | n | Median | p10 / p90 | Weekday 07–19 |
|---|---|---|---|---|---|
| NYC access, zone 231 → 138 | TLC Yellow + HVFHV, pooled (`wb-m2v06-nyc-legs.json`) | 67,932 | 32.267 | 22.8 / 53.45 | 38.817 |
| NYC egress, 138 → 231 | same | 61,255 | 39.317 | 25.783 / 57.7 | 46.95 |
| Chicago access, area 32 → 76 | Taxi `ajtu-isnz` | 44,294 | 40.633 | 25.0 / 60.717 | 45.0 |
| | TNP `6dvr-xwnh` | 565,110 | 38.9 | 24.95 / 59.683 | 44.7 |
| | Taxi + TNP pooled | 609,404 | 39.017 | 24.967 / 59.75 | — |
| Chicago egress, 76 → 32 | Taxi `ajtu-isnz` | 151,711 | 40.65 | 25.267 / 70.917 | 47.5 |
| | **TNP `6dvr-xwnh`** | — | **MISSING** | — | — |
| Flight LGA → ORD | BTS `CRSElapsedTime`, 12 monthly zips (`wb-m2v06-bts.json`) | 11,611 | 165 | 157 / 176 | — |
| Flight ORD → LGA | same | 11,611 | 136 | 128 / 144 | — |

**Indicative totals (not a candidate for runtime):** taxi-only on the Chicago side, check-in/wait 120, arrival allowance 0.
- Westbound: 32 + 120 + 165 + 41 = **358**.
- Eastbound: 41 + 120 + 136 + 39 = **336**.
- For comparison, v02 runtime is 365 / 338 and v05 (calendar-year 2025) was 359 / 334.

## 4. Source limits (why the gate stays open)

1. **Chicago TNP egress (ORD → Loop) is missing.** The server reports 496,351 rows for that pair in the window. Neither the full query nor the per-month retry finished: `wb-m2v06-chi-monthly` holds only a URL log for 2025-09 and 2025-10 and no result files. So pooled taxi + TNP exists for access only, and the two Chicago legs would mix bases. Under the no-network rule this cannot be fixed this session.
2. **NYC HVFHV raw files:** only 8 of the 12 monthly Parquet files are still on disk (2025-11, 2026-02, 2026-05 and 2026-08 are absent). The NYC leg statistics were computed earlier from all 12 files, and their SHA-256 values are recorded in `wb-m2v06-nyc-legs.json`. I could not re-run them from raw data this session. I only re-read the stored summary.
3. **E3, arrival allowance:** still 0 and unsourced. Every total is a lower bound.
4. **E6, time-of-day policy:** still a creator decision (all-hours vs weekday daytime).
5. **No new BTS month:** Aug 2026 was not available in the earlier attempt and was not retried.
6. **Router provenance (E5):** the free-flow lower bounds still come from a public Valhalla instance. This is unchanged.

## 5. Files

- Changed:
  - `game/scripts/world_route_registry.gd`: adds the `_check_components` guard; the default stays v02.
  - New `game/tests/…door-to-door-route-figures-check_m2-v06_20261016-002146-6dc4d1f1.gd`.
  - This note.
  - A meter zero-change closeout in `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`.
- Not changed: travel data, the Game Bible, the builder, `docs/progress.md`, art, and other sessions' dirty files.
