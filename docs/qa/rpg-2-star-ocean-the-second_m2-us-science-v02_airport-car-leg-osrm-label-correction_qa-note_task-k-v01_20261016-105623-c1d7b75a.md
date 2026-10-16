# M2 US-science v02: airport car-leg OSRM label correction — QA note

- Date: 2026-10-16. Worker: Claude Code (signed-in Claude Max, firstParty only; no API billing, credits or paid fallback).
- Follow-up to Task J (`docs/qa/rpg-2-star-ocean-the-second_m2-us-science-v02_car-route-osrm-label-correction_qa-note_task-j-v01_20261016-105248-028abe3c.md`, §5 item 1).
- Scope: a text-only, choice-independent provenance correction. No minutes, distances, IDs, endpoints, topology, source references or unrelated prose changed.
- **This is not M2 gate acceptance. The M2 door-to-door route-figures gate stays OPEN.**
- Not changed: Git state (nothing staged or committed), completion state/meter, `docs/progress.md`, the Game Bible, art, runtime minute values, unrelated files. No network request was made.

## 1. Change

File: `game/data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json`

The four OSRM airport car-leg `basis` strings in the two air segments said "Free-flow drive …". OSRM demo output is a routing-model estimate, not measured free-flow (m2-v08 §3.1, m2-v08a item 1). The leading words were replaced with the same wording Task J used. The route description and km in parentheses are unchanged. As in Task J, the wording makes no claim about the demo server's profile or version.

- Before: `Free-flow drive <A> -> <B> (<km> km).`
- After: `Routing-model estimate from the public OSRM demo server, with no live traffic, parking or loading; not measured free-flow. Drive <A> -> <B> (<km> km).`

| JSON path | Segment | Leg | km | min (unchanged) |
|---|---|---|---|---|
| `/segments/6/components/airportAccessMinutes/basis` | seg.air.nyc-lga__chicago-ord | City Hall Park -> LGA reference point | 18.3 | 24 |
| `/segments/6/components/airportEgressMinutes/basis` | seg.air.nyc-lga__chicago-ord | ORD reference point -> the Loop | 34.4 | 55 |
| `/segments/7/components/airportAccessMinutes/basis` | seg.air.chicago-ord__nyc-lga | the Loop -> ORD reference point | 34.3 | 54 |
| `/segments/7/components/airportEgressMinutes/basis` | seg.air.chicago-ord__nyc-lga | LGA reference point -> City Hall Park | 16.5 | 22 |

The `source.name` strings ("OSRM demo server, car profile") and URLs are source references and were kept as they were. After the edit, `Free-flow` does not appear anywhere in the file except inside the negation "not measured free-flow".

Integrity evidence:

- A JSON deep comparison of a pre-edit copy and the edited file (Node) finds exactly 4 differing leaf paths: the four listed above.
- Line endings are still LF (0 CR bytes before and after), with tab indentation.
- Raw-bytes SHA-256 (the file is LF-only, so these are also the `sha256-text-lf-v1` values): before `73ff34adf0af66383c4726bc4ddcfe2935ef6b8c935ae413d5123840b6d91464` (the Task J "after"), after `65d5e3429e876e0317b1125939444db2454b5acabb0febd690d694b0eeb7d1d7`. A search of `game/`, `tools/` and `docs/` for either hash prefix found only the Task J QA note, which is a historical record. No test or tool pins this file's hash.
- The whole file's diff against HEAD now holds 10 changed lines: Task J's 6 `note` lines and these 4 `basis` lines.

## 2. Test change

File: `game/tests/rpg-2-star-ocean-the-second_global-earth-travel_door-to-door-route-figures-check_m2-v06_20261016-002146-6dc4d1f1.gd`

- `_test_car_labels` gained a second `_check`. For the two air segments, it checks the `airportAccessMinutes` and `airportEgressMinutes` components whose `source.sourceId == "osrm-demo-osm"`.
- It asserts that there are exactly 4 such legs, that each `basis` contains "no live traffic", and that once "not measured free-flow" is removed, no `basis` contains "free-flow" in any letter case.
- No fixture or expected value changed.
- Negative control: the same logic ran from a temporary `-s` script under `%LOCALAPPDATA%\Temp\wb-taskk-airport\`. Against the pre-edit copy it printed `NEG valid=true legs=4 failing=4`. Against the edited runtime file it printed `POS valid=true legs=4 failing=0`. So the new assertion fails on all four old labels.
- Test file SHA-256 after the edit: `2b40d8d555456783015500ab022572acb786e6f635d66fa174cd2da7a6ac5673` (LF-only).

## 3. Checks run (Godot 4.7.2 console, `--headless --path game`)

| Test | Result |
|---|---|
| `…door-to-door-route-figures-check_m2-v06_…-6dc4d1f1.gd` | `M2_ROUTE_FIGURES_V06_OK checks=14` (13 before + 1 new), exit 0 |
| `…global-earth-travel_calendar-route-core-smoke_m2-v01_…-a19d5ae7.gd` | `GLOBAL_TRAVEL_CORE_OK`, exit 0 |
| `…global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_…-6e5c07b5.gd` | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`, exit 0 |

The `git status --porcelain --untracked-files=all game` output was identical before and after all runs, so no import side-effect files were created.

## 4. Remaining items (not done here)

1. **M2 door-to-door route-figures gate: still OPEN and unverified.** No total is accepted or verified. All 8 segments stay `preliminary-estimate` with a 0 door-to-door allowance. The airport legs still treat OurAirports reference points as terminals, and they leave out curb, deplaning and baggage time, typical traffic, and time of day.
2. The public demo server's OSRM profile and version are still unverified (v08 §7, v08a S5). The demo-server terms for commercial use are still unresolved: before release, re-derive the figures on a self-hosted OSRM run on a dated OSM extract.
3. Every choice-dependent minute change still waits on creator decisions C1–C5 and independent verification. That covers v08 §3.2 NYC ↔ Yonkers, the §4 air components, and the v08a §6 flight blocks.
