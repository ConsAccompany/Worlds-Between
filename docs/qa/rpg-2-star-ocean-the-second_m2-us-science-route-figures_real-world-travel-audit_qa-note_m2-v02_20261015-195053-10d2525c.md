# M2 US science sphere: route figures audit against real-world sources (QA note, read-only)

- Date: 2026-10-15. All web sources below were retrieved on 2026-10-15.
- Audited file: `game/data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json`. Its migration note is `docs/qa/rpg-2-star-ocean-the-second_us-science-sphere_runtime-migration_qa-note_m2-v02_20261015-175011-364131c8.md`.
- Rule being tested: travel rules v01, player rule 5 (`docs/design/rpg-2-star-ocean-the-second_global-earth-map-real-place-travel_rules-v01_20261014-235354-2b5d4d98.md`). Travel time follows the real **typical door-to-door** time. Car time uses road distance and drive time. Air time uses the flight plus the necessary airport transfers and waiting. Every static in-game value must state how it was estimated.
- Scope: read-only. I did not change runtime route data, code, the Game Bible, `docs/progress.md`, M2 gate counters, art files or Git. This note is the only file added.
- **M2 door-to-door route-figures gate: stays OPEN.** This audit does not accept any figure.
- Tools: public web sources and the free public OSRM demo server and BTS downloads. No paid service, API credit or fallback was used.

## 1. Verdict and recommendation

| Question | Answer | Confidence |
|---|---|---|
| Do the stored figures reproduce from the cited sources? | **Yes, exactly.** All 10 OSRM queries match the stored distances to 0.1 km and the stored minutes after rounding to the nearest minute. The BTS July 2026 medians and p10/p90 for LGA↔ORD match exactly (n = 997 each way). | High |
| Is the route structure sound? | **Yes.** Each direction is its own one-way segment queried separately. Air time = access + arrive-before-departure allowance + scheduled block time + egress, with nothing counted twice. Pending routes give no figure and are not built by adding legs. The runtime sums exactly the stored fields (`world_route_registry.gd:112-119`). | High |
| Are the car figures typical door-to-door times? | **No. They are free-flow lower bounds**, with no traffic, parking or loading. The data says so honestly, but rule 5 asks for typical times. | High |
| Are the air totals (365 / 338) typical door-to-door times? | **Not yet.** The method is right, but three inputs are unsupported or biased (see §4: airside routing at ORD, a zero arrival allowance, free-flow access drives). The errors push in opposite directions, so I cannot say whether 365 / 338 is too high or too low overall. | Medium-low |
| Plausible as preliminary game estimates? | **Yes.** Every figure is the right order of magnitude, and each direction is consistent with independent official reference times (§3). | Medium-high |

**Recommendation:** keep v02 in the runtime as labelled "preliminary estimates". Do not mark any figure verified and do not close the gate. In the next data revision (a separate task), apply the reproducible policy in §6. Fix the ORD and LGA airport points first: that issue is concrete and its source is known.

## 2. Reproduction of the stored figures

### 2.1 OSRM demo server, car profile (re-queried 2026-10-15)

Query form: `https://router.project-osrm.org/route/v1/driving/<lon,lat;lon,lat>?overview=false`, with the exact coordinates stored in each segment's `source.url`.

| Segment | Stored km / min | Re-query km / min | Snap (origin / destination) |
|---|---|---|---|
| NYC → Yonkers | 28.2 / 35 | 28.2 / 35.4 | Park Row 27 m / South Broadway 11 m |
| Yonkers → NYC | 28.3 / 35 | 28.3 / 35.5 | as above |
| NYC → Washington | 363.2 / 289 | 363.2 / 289.2 | Park Row 27 m / Independence Ave SE 249 m |
| Washington → NYC | 361.4 / 286 | 361.4 / 286.0 | as above |
| Yonkers → Washington | 388.0 / 306 | 388.0 / 306.1 | |
| Washington → Yonkers | 383.4 / 303 | 383.4 / 302.8 | |
| City Hall Park → LGA (access) | 18.3 / 24 | 18.3 / 23.7 | LGA point snapped **461 m** to an unnamed road |
| LGA → City Hall Park (egress) | 16.5 / 22 | 16.5 / 22.1 | |
| ORD → Loop (egress) | 34.4 / 55 | 34.4 / 54.7 | ORD point snapped **342 m** to an unnamed road |
| Loop → ORD (access) | 34.3 / 54 | 34.3 / 54.1 | |

Rounding is to the nearest whole minute, and the data uses it consistently. OSRM's public demo has no fixed data date, so these figures can drift as OpenStreetMap is edited. Today they still match.

### 2.2 BTS on-time data (re-computed from the raw monthly files)

Files: `https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_<M>.zip`. Each was downloaded into an isolated temp directory and parsed with a standalone script (`python -I`), keeping only rows with Origin/Dest LGA/ORD. `CRSElapsedTime` is the scheduled gate-to-gate block time, including taxi.

| Month (2026) | zip SHA-256 (first 12) | LGA→ORD scheduled n / median / p10 / p90 | ORD→LGA scheduled n / median / p10 / p90 | Cancelled LGA→ORD / ORD→LGA | Actual median (non-cancelled) |
|---|---|---|---|---|---|
| January | 9ff58f560519 | 951 / 171 / 167 / 178 | 955 / 137 / 128 / 146 | 77 / 69 | 162 / 125 |
| April | 70e685ffa604 | 963 / 167 / 159 / 175 | 962 / 138 / 131 / 139 | 33 / 29 | 162 / 130 |
| **July (stored)** | 61d657eb17f5 | **997 / 166 / 157 / 188** | **997 / 142 / 136 / 149** | 105 / 102 | 157 / 133 |

- The stored July medians reproduce exactly. Across the three months the scheduled median moves by 5 minutes or less (LGA→ORD 166–171, ORD→LGA 137–142). Using one month is a small bias, not an error.
- The westbound leg is about 25–30 minutes longer than the eastbound one in every month (prevailing westerlies, plus LGA departure taxi). The asymmetry between 365 and 338 is real-world-consistent.
- Scheduled block time exceeds the actual median by 4–12 minutes (schedule padding). Using the scheduled time is the right conservative choice for a "planned trip" figure.
- In July 2026 about 10.5% of LGA–ORD flights were cancelled. This does not affect a static estimate. It is a reminder that "nonstop service exists" was confirmed only for the sampled months.
- BTS's newsroom lists "Airline Service Quality Performance Data — July 2026" (https://www.bts.gov/newsroom/airline-service-quality-performance-data-july-2026), so July 2026 is the latest released month. The page returned HTTP 403 to WebFetch. Its title and the July date were seen in search results only.

## 3. Independent real-world cross-checks (2026 data, official sources where reachable)

These are **2026 real-world references**. They are not 2537 game values (see §5).

| Check | Source (retrieved 2026-10-15) | What it says | Bearing on the stored figure |
|---|---|---|---|
| O'Hare ↔ downtown by rail | CTA airports page, https://www.transitchicago.com/airports/ | "The normal travel time on the Blue Line from O'Hare to downtown, is 40-45 minutes." | The stored 55 / 54-minute free-flow **drive** is 10–15 minutes slower than the scheduled train. A free-flow drive on I-90 should not lose to the train. Points to the routing defect in §4.1. |
| Arrival guidance (Delta) | https://www.delta.com/us/en/check-in-security/check-in-time-requirements/domestic-check-in | "we recommend that you arrive at the airport at least 2 hours prior to departure". The domestic minimum is 30 minutes without bags and 45 with bags; **LGA is 45 / 45 minutes**; be at the gate 15 minutes before departure. ORD is not listed as an exception. | Independently supports the 120-minute `checkInAndWaitMinutes`. It is a recommendation, not a measured wait. |
| Arrival guidance (American) | https://www.aa.com/i18n/travel-info/check-in-and-arrival.jsp | **HTTP 403** to WebFetch and to curl with a browser user agent today. | The stored AA quote could not be re-verified today. Delta now provides an independent second source. |
| Arrival guidance (TSA) | https://www.tsa.gov/travel/frequently-asked-questions | No fixed figure: "You are encouraged to contact your airline as times may vary depending on the airport and date of travel." | Confirms the data note that TSA gives no fixed number. |
| United arrival guidance | https://www.united.com/en/us/fly/travel/airport/check-in-requirements.html | Timed out (WebFetch) / no readable text (curl). | Not established. |
| LGA ↔ Manhattan by transit | MTA, https://www.mta.info/guides/airports/laguardia/lga-to-nyc | Q70 LaGuardia Link to the subway: "The trip takes about 15 minutes in typical traffic." The page gives no Manhattan total. | Gives no total to compare with. A secondary analysis (FiveThirtyEight, https://fivethirtyeight.com/features/planes-trains-and-taxis-when-to-take-public-transit-from-the-airport) estimated about 65 minutes by transit from LGA to City Hall on an average weekday. It is not official, but it suggests the free-flow 24 / 22-minute drive understates a typical trip. |
| NYC ↔ Washington by rail | Amtrak Northeast Regional timetable PDF dated Thursday, October 15, 2026, https://content.amtrak.com/content/timetable/Northeast%20Regional.pdf, pages 2–3 | Northbound Washington Union Station → New York Moynihan Train Hall: train 164 Mo–Fr 9:20a → 1:00p (3h40m); 1164 Mo–Fr 9:15a → 1:01p (3h46m); 86 Mo–Th 8:50a → 12:37p (3h47m); 164 SuSa 9:10a → 1:00p (3h50m). | Station to station, the train takes about 3h40m–3h50m. A car's free-flow 4h49m being slower than the train is consistent. Rail is not a game mode; this is a sanity bound only. Amtrak notes NEC disruptions from 2026-10-09 to 2026-11-15 (Portal North Bridge work), which may affect these times. |
| Yonkers ↔ Grand Central by rail | Official mta.info timetable not reached; only secondary sites (Rome2Rio about 43 min; RentCafe 30–40 min) | about 30–45 min | The 35-minute free-flow drive is in the same range. No official confirmation; not used. |
| Urban congestion | Texas A&M TTI Urban Mobility Report; latest city TTI values not retrieved. The BTS archive table 4-18 (2004–2009 data; https://www.bts.gov/archive/publications/transportation_statistics_annual_report/2010/chapter_02/table_04_18) is too old to use. | — | **No current, citable congestion factor was established.** Any traffic multiplier would currently be invented. |

## 4. Unsupported assumptions and defects

### 4.1 ORD and LGA airport points are airfield reference points, not public curbs (defect)

The OurAirports latitude and longitude are aerodrome reference points (about mid-airfield). With `steps=true` the ORD → Loop route **starts on airside service roads**: `Baggage Road` → `Concourse Service Road` → `Main Service Road`. Only then does it reach the public road network and join the Kennedy Expressway (I-90/I-94). This is why the egress drive is 54.7 minutes for 34.4 km (about 38 km/h free-flow), slower than the CTA's scheduled 40–45-minute train. The LGA access route ends via `Central Terminal Drive` and then unnamed roads, so it is closer to a curb but still not a defined terminal. **Fix (policy §6.3): route to and from a sourced terminal curb point.** I do not give a replacement figure here, because I have no sourced terminal coordinates.

### 4.2 Zero door-to-door allowance (unsupported, contradicts rule 5)

Every segment has `doorToDoorAllowanceMinutes: 0`.
- **Car:** the figures are free-flow, with no traffic, parking or loading. Rule 5 asks for *typical* door-to-door times. No current official congestion factor was retrieved (§3), so I cannot give a sourced number now. Either source one, or have the creator approve a labelled design constant.
- **Air, arrival side:** deplaning, the walk to the curb, baggage claim and waiting for a car are all counted as 0. The stored data says this is not counted. No primary source for a typical figure was found in this pass. Leaving it at 0 makes air totals too short.
- **Air, departure side:** the 120-minute arrive-by figure covers check-in, security and the gate wait up to scheduled departure, and block time starts at scheduled departure. The stored structure is correct here, and **nothing is double-counted**.

### 4.3 Free-flow access and egress drives (unsupported for "typical")

The 24 / 22-minute City Hall Park ↔ LGA figures are free-flow. A secondary weekday transit estimate (about 65 minutes) and taxi guides that cannot be checked suggest a typical trip is longer. This needs the same congestion treatment as §4.2.

### 4.4 Single-airline arrival source; single-month block time (minor)

The AA page could not be read today. Delta's page (§3) independently gives "at least 2 hours", so 120 minutes is now supported by two carriers that serve LGA–ORD. Using a single month changes block time by 5 minutes or less (§2.2). A 12-month median would remove the seasonal choice.

### 4.5 Licensing (unchanged open items)

The OSRM demo server is limited to "reasonable, non-commercial use" (as recorded in the data). Neither the BTS nor the USGS public-domain terms page was read in this pass either. These remain release blockers, not plausibility issues.

### 4.6 What is *not* a defect

- The asymmetric car figures (e.g. 289 / 286) come from separate reverse queries on one-way street networks. Keep them.
- Washington is approached by a real road snap 249 m from the Capitol point (Independence Ave SE). That is acceptable for a ruins-centre point. How the abandoned-city fiction affects the final approach is a creator decision (§5).
- Pending Yonkers↔Chicago and Washington↔Chicago routes with no figure follow rule "未核实的路线显示为待制作" correctly.

## 5. 2026 real-world data versus 2537 in-game planning

- Every figure in v02 and in this note is **2026 real-world reference data**: OSM roads as of the query date, 2026 BTS schedules, 2026 airline policies and the October 2026 Amtrak timetable.
- The game is set in 2537 after a world reset. Rule 5 already says flight timetables need not match today's, but static values must state their basis. No creator decision yet sets **how 2537 differs** (which airports operate, road state around a ruined Washington, aircraft speed, security process).
- Recommended data split for a later revision (not applied): store a `realWorldBaseline` block (sourced, dated, reproducible) and a separate `inGame` value derived from it by named **fiction modifiers** listed in a design doc. Until the creator approves any modifier, every modifier is 1.0 and the in-game minutes equal the baseline. This keeps "researched fact" and "setting choice" auditable apart.

## 6. Reproducible policy for future global routes (proposed, not adopted)

1. **Endpoints.** Use the registered **scene entry point** of each location, not a city centroid. For airports, use a **sourced public terminal curb point** (airport authority terminal map or an OSM node with a recorded ID and version), never the aerodrome reference point. Record each point's source, ID and retrieval date.
2. **Car legs.** Use a **self-hosted OSRM (or equivalent) on a dated OpenStreetMap extract**. Record the extract URL, date and SHA-256, the router version and the profile. Query each direction separately. Store distance to 0.1 km and the raw duration in seconds. Inspect `steps` for every leg: fail the leg if it starts or ends on service/airside roads, or if a snap distance is over 200 m without a written justification.
3. **Typical-time allowance.** Free-flow is the baseline. A typical-time factor or allowance is applied only if it is (a) taken from a cited source with its own dated value, or (b) a creator-approved design constant labelled `design-constant` in the data. Never present one as research.
4. **Air legs.**
   - Flight minutes are the **median scheduled block time over the latest 12 released months**, with p10/p90 and flight counts recorded. For US routes, use BTS On-Time Reporting raw files with the zip SHA-256. For non-US routes BTS does not apply; the source must be named per country, or the route stays `pending`.
   - The departure allowance is the "arrive at least X before departure" guidance from **at least two carriers serving the route**, quoted with URLs.
   - The arrival allowance (deplane, walk to the curb, bags) is sourced or a labelled design constant. It is never silently 0.
   - Access and egress use rule 2 from and to the terminal curb points. Each one is cross-checked against an official transit time where one exists (e.g. CTA 40–45 min). If a free-flow drive is slower than the scheduled transit time, investigate before storing it.
5. **Cross-check gate per route.** At least one independent official reference must be in the same order of magnitude (rail timetable, transit authority time, airline schedule). Record the comparison in the QA note.
6. **Rounding.** Keep raw component values. Round once, when the total is stored, to whole minutes (the calendar is integer minutes). Display may round further to 5 minutes with an "≈" mark. Never show more precision than the weakest component.
7. **Provenance.** For every component, record the URL, the retrieval date, the dataset hash where something was downloaded, and the exact query or script. Keep `verification.status` at `preliminary-estimate` until rules 1–5 pass. Only then use a `researched` status. **Never** mark a route `verified` without a human review.
8. **Composite routes.** Derive no route by adding legs unless a route record lists those legs explicitly and each leg passes rules 1–7. The existing `pending` / `no-researched-route` handling stays.
9. **Baseline versus fiction.** Apply §5: a sourced `realWorldBaseline` plus named, creator-approved 2537 modifiers (default 1.0).
10. **Paid-service guard.** Use only free or public sources. If a source needs payment, credits or a login that is not available, stop and leave the route `pending`. Do not substitute an estimate.

## 7. Open items handed back

1. The creator must decide whether typical-time allowances (car congestion, airport arrival) are researched values or approved design constants.
2. Choose and source terminal curb points for LGA and ORD. Then re-run access and egress.
3. Self-hosted OSRM on a dated OSM extract (already `request.car.self-hosted-osrm`).
4. Use a 12-month BTS block-time median (extends `request.air.release-grade-figures`).
5. Re-read the AA arrival guidance (403 today) or replace that citation with Delta's page; get United's guidance.
6. Record 2537 fiction modifiers (airports operating, the approach to the Washington ruins), or confirm 1.0.
7. Current congestion data (TTI Urban Mobility Report city values) was not retrieved. Get it before any data-based traffic factor is used.

## 8. Local reproduction artifacts (outside the repository)

- Downloads: `C:\Users\hkzha\AppData\Local\Temp\wb-bts-audit-1792108043\dl\` (`ot.zip` = July, `ot_1.zip`, `ot_4.zip`). The full SHA-256 values are July `61d657eb17f5b6f800ed2f05262a2223c5edf66fe7d9cfb3598c6664a34ed0b6`, January `9ff58f560519dbc8fbd1b8b9fd2a172ca46d0a9e80f1df4fd48891efca41e89c` and April `70e685ffa6042e6c851c4f1e821d774dfe7318d3eb212ac5bfc6a53ea23f3cfb`. The January and April files needed a resumed download, so check their hashes before reuse.
- Script: `C:\Users\hkzha\AppData\Local\Temp\wb-bts-audit-scripts\bts_lga_ord.py` (stdlib only; median, linear-interpolated p10/p90, cancellations and actual elapsed time).
- These are temp files. Nothing was added to the repository except this note.
