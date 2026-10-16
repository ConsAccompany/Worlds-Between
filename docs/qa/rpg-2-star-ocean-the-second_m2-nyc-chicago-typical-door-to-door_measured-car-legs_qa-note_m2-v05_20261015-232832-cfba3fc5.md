# M2 NYC–Chicago typical door-to-door: measured car legs (QA note, NONRUNTIME, v05)

- Date: 2026-10-15 23:28 America/New_York.
- Follows the v04 blocked note: `docs/qa/rpg-2-star-ocean-the-second_m2-nyc-chicago-typical-door-to-door_resume-attempt-blocked_qa-note_m2-v04_20261015-224916-c4e1a7b2.md`. It runs that note's pre-registered plans P1, P2 and P3.
- Candidate data: `docs/qa/rpg-2-star-ocean-the-second_global-earth-travel_nyc-chicago-measured-car-legs_m2-us-science-v05-candidate-nonruntime_20261015-232832-cfba3fc5.json`. It sits outside `game/`, so the runtime never loads it.
- **Not changed:** active game data, scripts, the Game Bible, art, `docs/progress.md`, the v03 candidate and Git. This note and the candidate JSON are the only files added. No commit or push.
- Tools: only anonymous public reads, with no account, key, credit or paid fallback. Sources were NYC Open Data and City of Chicago SODA endpoints, the TLC CloudFront lookup, and flychicago.com and laguardiaairport.com. No request carried user identifiers.
- **M2 door-to-door route-figures gate: stays OPEN.** E1 and E2 are resolved. E3 (the arrival side) and E6 (the time-of-day policy) are not.

## 1. Result

All values are in minutes. Each segment is access + check-in/wait + flight + egress + arrival allowance.

| Segment | v03 (free-flow car legs) | **v05 candidate (measured 2025 medians, all hours)** | weekday 07–19 sensitivity |
|---|---|---|---|
| NYC → Chicago | 21 + 120 + 165 + 23 + 0 = 329 | **32 + 120 + 165 + 42 + 0 = 359** (raw 359.1) | 38 + 120 + 165 + 49 = 372 |
| Chicago → NYC | 24 + 120 + 136 + 19 + 0 = 299 | **41 + 120 + 136 + 37 + 0 = 334** (raw 333.8) | 45 + 120 + 136 + 45 = 346 |

- The totals are a **sum of component medians**. They are not the median of a full door-to-door trip.
- The flight times (BTS 12-month medians: 165 westbound, 136 eastbound) and the 120 min check-in/wait come from v03 unchanged.
- **The arrival allowance is still 0 and still unsourced (§4).** Both totals are therefore lower bounds on true door-to-door time.

## 2. Zone IDs, checked against the source data rather than from memory

| Place | Point | Server-side point-in-polygon result |
|---|---|---|
| City Hall Park | (40.71205, −74.00708) | NYC Taxi Zones `8meu-9t5y` → **231 "TriBeCa/Civic Center"**, Manhattan |
| LGA B departures curb (v03) | (40.7724664, −73.8712600) | → **138 "LaGuardia Airport"**, Queens |
| The Loop | (41.881144, −87.6297746) | Chicago Community Areas `igwz-8jzy` → **32 "LOOP"** |
| ORD T1 departures and arrivals curbs (v03) | both points | → **76 "OHARE"** |

The TLC `taxi_zone_lookup.csv` agrees: 231 = Manhattan, TriBeCa/Civic Center, Yellow Zone; 138 = Queens, LaGuardia Airport, Airports. The plan's "(confirm)" values 138, 32 and 76 were right. The City Hall zone is **231**.

## 3. Measured car legs (calendar year 2025, one query per direction)

**Metrics.**
- NYC yellow: `tpep_dropoff − tpep_pickup`.
- NYC HVFHV: `trip_time`, excluding matched shared rides.
- Chicago taxi: `trip_seconds`.
- In every dataset, rows with a duration of ≤ 0 or > 180 min are dropped.

**Row counts.** For every file, the number of rows downloaded equals the server's `count(*)`. The Chicago `trip_id` values are all unique.

| Leg | Dataset | Rows | Dropped | n | Median | p10 | p90 | Weekday 07–19 median | v03 free-flow |
|---|---|---|---|---|---|---|---|---|---|
| 231 → 138 (access) | Yellow `irx2-vgm4` | 4,180 | 28 | 4,152 | 34.98 | 22.68 | 56.72 | 39.48 | |
| | HVFHV `nt46-nv3c` | 68,012 | 150 shared | 67,862 | 31.50 | 22.30 | 52.83 | 37.97 | |
| | **Pooled** | | | **72,014** | **31.68** | 22.31 | 53.07 | 38.07 | 20.70 |
| 138 → 231 (egress) | Yellow | 14,385 | 188 | 14,197 | 36.07 | 23.80 | 54.01 | 43.03 | |
| | HVFHV | 51,351 | 15 shared | 51,336 | 37.63 | 25.65 | 55.55 | 44.98 | |
| | **Pooled** | | | **65,533** | **37.32** | 25.23 | 55.25 | 44.52 | 18.60 |
| 32 → 76 (access) | Chicago Taxi 2025 `b8xg-w8bx` | 49,443 | 119 | **49,324** | **40.53** | 25.28 | 64.00 | 44.98 | 23.82 |
| 76 → 32 (egress) | Chicago Taxi 2025 | 166,188 | 51 | **166,137** | **42.45** | 25.00 | 67.80 | 49.18 | 23.45 |

**Hour-of-day peaks** (full tables are reproducible with the stats script):
- NYC yellow 231→138 rises from about 21 min at 04:00–06:00 to 49.9 min at 16:00.
- Chicago 76→32 rises from about 23 min overnight to 61.5 min at 07:00 and 57.6 min at 17:00.

**Plausibility checks.**
- Every measured median is above its v03 free-flow value. The increase is 11–19 min in each case.
- Reverse directions differ by 1.1 min (Chicago) and 5.6 min (NYC pooled), both well under the 10 min flag.

**Caveats.**
1. These are **zone-to-zone** times, not point-to-point. Zone 231 covers TriBeCa as well as Civic Center. City Hall Park is at its south-east corner, closest to the Brooklyn Bridge and FDR approaches, so the zone median probably runs slightly long rather than short for this start point. Community areas 32 and 76 cover the whole Loop and the whole airport.
2. The times cover only the meter or app trip. They exclude the taxi-stand queue, the app-ride wait and curb dwell.
3. Chicago legs are **taxi only**. The 2025 TNP rideshare query (`6dvr-xwnh`, `count(*)` for 76→32) timed out after 300 s with no bytes received. P2 asked for "Taxi Trips and TNP", so this part of P2 is unmet.
4. NYC yellow rows from LGA cluster in the afternoon and evening. Pooling with HVFHV gives a broader sample by hour.

## 4. Arrival side (E3): still not resolved

| Source | What it gives | Usable as a typical arrival allowance? |
|---|---|---|
| CDA O'Hare "Taxi, Limo, TNP" page (sha256 `843bd5a1…`) | "Depending on airport traffic, it can take between 5 and 20 minutes for the vehicle to get to the designated pickup location." | **No.** This sentence is in the **limousine / pre-arranged ride** section, not the taxi section. The taxi section only says stands are "at the lower level curb front (outside of Baggage Claim)" and gives no time. The figure is also a range, not a typical value. |
| PANYNJ LGA Taxis page (sha256 `880bc8cc…`) | "Terminal B : Curbside in the arrivals area on Level 2." and "join the line at the official taxi stand … a dispatcher will direct you to the next available cab." | **No.** It gives no queue time. |
| TLC HVFHV, PU 138 → DO 231, request → pickup | n = 51,248; median **5.25 min**; p10 1.87; p90 11.60. This is a measured value. | **Partial only.** It covers the app-ride wait at LGA, not deplaning, the walk to the curb or bags. Chicago data has no request timestamps, so there is no ORD equivalent. The value is stored but not added to any total. |
| PANYNJ LGA Departures Guide | "Airline check-in typically opens 3–4 hours before departure and closes 45–60 minutes before takeoff." | This is departure-side context and is consistent with keeping 120 (v04 E4). It does not touch the arrival side. |

- United's check-in-requirements page timed out after 60 s with no bytes received, so no airline rule was retrieved this session.
- The PANYNJ page puts the Terminal B taxi stand on "Level 2" arrivals. The v03 OSM curb way for Terminal B arrivals has `layer 1`. OSM `layer` is a relative stacking value, not a floor number, so the two do not necessarily conflict. The curb point is not used in v05's car legs, so this is noted only.
- **No value was invented.** `doorToDoorAllowanceMinutes` stays 0.

## 5. Exact remaining gate

1. **E3, arrival allowance (blocking).** No public primary source gives a typical deplane → curb → in-car time at LGA B or ORD T1. Options:
   - an ACRP or TRB measured distribution;
   - published PANYNJ or CDA taxi-queue statistics;
   - a creator-approved `design-constant`, which could use the measured LGA app-wait of 5.25 min as one sub-component.
   The creator also has to decide whether the traveller checks bags.
2. **E6, time-of-day policy (creator).** The choice is all-hours (359 / 334) or weekday daytime (372 / 346).
3. **Chicago TNP (optional).** Retry the `6dvr-xwnh` query with server-side aggregation, or add a date filter so it does not time out. Then report taxi-only against pooled.
4. **Promotion.** Runtime promotion is a separate, creator-approved task. It needs an edit to the active travel data and a re-run of the travel tests.

## 6. Reproduction and tests

- Scripts, kept outside the repo and run stdlib-only with `python -I`, are in `%LOCALAPPDATA%\Temp\wb-m2v05-scripts\`:
  - `stats.py`
  - `hvfhv_stats.py`
  - `pooled.py`
  - `check_v05.py`
  - `chi_fetch.js` (unused; it timed out, and curl paging replaced it)
- The raw CSVs, the query-URL logs (`*.urls.txt`) and the page HTML are in `%LOCALAPPDATA%\Temp\wb-m2v05-web\`.
- **`check_v05.py` gave 62/62 PASS.** It checks:
  - every raw-file SHA-256 against the JSON;
  - rows = server count;
  - the Chicago monthly counts sum;
  - every median, p10, p90 and weekday median recomputed from the raw files;
  - median ≥ free-flow for all four legs;
  - yellow n + HVFHV n = pooled n;
  - each segment component = the rounded median;
  - integer and raw totals;
  - all sensitivity totals;
  - reverse-direction difference ≤ 10;
  - the page hashes;
  - zone IDs against the TLC lookup;
  - allowance = 0;
  - gate = OPEN.
