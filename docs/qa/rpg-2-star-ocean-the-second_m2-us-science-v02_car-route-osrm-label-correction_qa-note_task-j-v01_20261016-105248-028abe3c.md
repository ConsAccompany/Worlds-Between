# M2 US-science v02: car route OSRM label correction (Task J) — QA note

- Date: 2026-10-16. Worker: Claude Code (signed-in Claude Max, firstParty only; no API billing, credits or paid fallback).
- Scope: a text-only, choice-independent correction. No route minutes, distances, IDs, endpoints, calendar behaviour or source references changed.
- **M2 door-to-door route-figures gate: stays OPEN.** Every choice-dependent minute value (NYC ↔ Yonkers ≈46/≈56, flight block changes, airport components) is left untouched pending creator decisions.
- Not changed: Git state (nothing staged or committed), completion state, `docs/progress.md`, the Game Bible, runtime minute values, unrelated files.

## 1. Basis

- m2-v08 §3.1 (`docs/qa/rpg-2-star-ocean-the-second_m2-door-to-door-route-figures_public-source-evidence-proposed-calculations_qa-note_m2-v08_20261016-112319-834f6532.md`) says the v02 car times are a routing model, not free-flow.
- m2-v08a item 1 (`docs/qa/rpg-2-star-ocean-the-second_m2-door-to-door-route-figures_independent-source-audit_qa-supplement_m2-v08a_20261016-085803-b91a5a30.md`) confirms this from the OSRM source. It classes the relabel as "verified (S5) and choice-independent", changing text but not minutes.
- Both notes say it is **still unconfirmed which profile version the public demo server (router.project-osrm.org) runs**. Both proposed labels quote "car profile: 80% of tagged speed limits", which comes from the GitHub `master` source. The new wording therefore leaves out any profile, version or speed-reduction claim. The existing `source.name` strings ("OSRM demo server, car profile (OpenStreetMap data)") are source references and were kept exactly as they were.
- No network request was made for this task.

## 2. Change

File: `game/data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json`

The leading sentence of `segments[0..5].verification.note` changed. The rest of each note (rounding sentence and the per-route tail) is unchanged.

- Before: `Free-flow routing-model time with no traffic, parking or loading. Rounded to the whole minute; not a measured or scheduled time. …`
- After: `Routing-model estimate from the public OSRM demo server, with no live traffic, parking or loading; not measured free-flow. Rounded to the whole minute; not a measured or scheduled time. …`

| Segment ID | From → To | km | min | Note tail (unchanged) |
|---|---|---|---|---|
| seg.car.nyc__yonkers | earth.us.ny.new-york-city → earth.us.ny.yonkers-outskirts | 28.2 | 35 | City Hall Park (snapped to Park Row) to Yonkers (snapped to South Broadway). |
| seg.car.yonkers__nyc | yonkers-outskirts → new-york-city | 28.3 | 35 | Separate reverse query. |
| seg.car.nyc__washington-ruins | new-york-city → earth.us.dc.washington-ruins | 363.2 | 289 | City Hall Park to the Capitol (snapped to Independence Avenue SE, 249 m from the input point). |
| seg.car.washington-ruins__nyc | washington-ruins → new-york-city | 361.4 | 286 | Separate reverse query. |
| seg.car.yonkers__washington-ruins | yonkers-outskirts → washington-ruins | 388 | 306 | Direct drive, not via Manhattan. |
| seg.car.washington-ruins__yonkers | washington-ruins → yonkers-outskirts | 383.4 | 303 | Separate reverse query. |

Integrity evidence:

- `git diff --stat` shows 6 insertions and 6 deletions, all on the six `note` lines. The file keeps LF line endings with tab indentation (0 CR bytes before and after).
- A JSON deep comparison of before and after (Node) finds exactly 6 differing leaf paths, `/segments/0..5/verification/note`. Every other value is identical: IDs, distances, minutes, endpoints, `bidirectional`, status, allowances, sources, URLs, calendar and air data.
- Raw-bytes SHA-256: before `4b1677264451ed1ab24f95af8c4340eb55ee76fbe8b8cf1f2356dba563b4bb4b`, after `73ff34adf0af66383c4726bc4ddcfe2935ef6b8c935ae413d5123840b6d91464`. Because the file is LF-only, these are also the `sha256-text-lf-v1` values. No test, tool or doc pins this file's hash. Searches of `game/`, `tools/` and `docs/` for the old hash prefix found nothing.

## 3. Test change

File: `game/tests/rpg-2-star-ocean-the-second_global-earth-travel_door-to-door-route-figures-check_m2-v06_20261016-002146-6dc4d1f1.gd`

- Added `_test_car_labels`, a single `_check`.
- It asserts that there are exactly 6 `mode == "car"` segments, and that each note contains "no live traffic".
- It also asserts that, once the negation "not measured free-flow" is removed, no note contains "free-flow" in any letter case.
- No fixture or expected value changed.
- Negative control: the same logic was run from a temporary `-s` script under `%LOCALAPPDATA%\Temp\wb-taskj-neg\` against a copy of the pre-edit data. Result: `NEG valid=true cars=6 failing=6`, so the new assertion fails on all six old labels.

## 4. Checks run (Godot 4.7.2 console, `--headless --path game`)

| Test | Result |
|---|---|
| `…door-to-door-route-figures-check_m2-v06_…-6dc4d1f1.gd` | `M2_ROUTE_FIGURES_V06_OK checks=13` (12 before + 1 new), exit 0 |
| `…global-earth-travel_calendar-route-core-smoke_m2-v01_…-a19d5ae7.gd` | `GLOBAL_TRAVEL_CORE_OK`, exit 0 |
| `…global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_…-6e5c07b5.gd` | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`, exit 0 |

The `git status --untracked-files=all game` output was identical before and after the runs, so no import side-effect files were created.

## 5. Remaining items (not done here, out of Task J scope)

1. **Airport car-leg `basis` strings in the same file still say "Free-flow drive …".** There are four, in the air segments' `airportAccessMinutes` / `airportEgressMinutes` components (City Hall Park → LGA, ORD → Loop, Loop → ORD, LGA → City Hall Park). They come from the same OSRM demo and are mislabelled the same way. The task limited the change to the six car-route notes, so they were left alone. A follow-up can relabel them the same way, still without changing minutes.
2. The public demo server's OSRM profile and version are still unverified (v08 §7, v08a S5).
3. Every choice-dependent minute change (v08 §3.2 NYC ↔ Yonkers, §4 air components, v08a §6 flight blocks) still waits on creator decisions C1–C5 and independent verification. **M2 door-to-door figures stay OPEN.**
