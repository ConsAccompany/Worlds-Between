# M2 NYC–Chicago air route: airport curb endpoints, v03 candidate (QA note, NONRUNTIME)

- Date: 2026-10-15 (America/New_York). Late queries fell on 2026-10-16 UTC.
- Responds to §4.1 and §7 items 2 and 4 of `docs/qa/rpg-2-star-ocean-the-second_m2-us-science-route-figures_real-world-travel-audit_qa-note_m2-v02_20261015-195053-10d2525c.md`.
- Candidate data: `docs/qa/rpg-2-star-ocean-the-second_global-earth-travel_nyc-chicago-airport-curbs_m2-us-science-v03-candidate-nonruntime_20261015-200518-7c3e19a4.json`. It sits outside `game/`, so the runtime never loads it.
- **Not changed:** the active v02 data, scripts, the Game Bible, `docs/progress.md`, art and Git. This note and the candidate JSON are the only files added.
- Tools: only free public services. These were Overpass API, the Valhalla and OSRM public instances, and BTS/CDA/PANYNJ/MTA/CTA pages. No paid route, credit or fallback was used.
- **M2 door-to-door route-figures gate: stays OPEN.**

## 1. Result

| Segment | v02 (OurAirports reference points, July block time) | v03 candidate (terminal curbs, 12-month block time) |
|---|---|---|
| NYC → Chicago | 24 + 120 + 166 + 55 = **365** | 21 + 120 + 165 + 23 = **329** (raw 329.1) |
| Chicago → NYC | 54 + 120 + 142 + 22 = **338** | 24 + 120 + 136 + 19 = **299** (raw 298.4) |

Fields are access + check-in/wait + flight + egress. `doorToDoorAllowanceMinutes` is still 0.

Nearly all of the change comes from ORD. The v02 drive started and ended on airside service roads (`Baggage Road` → `Concourse Service Road`) and took 54–55 min. The candidate drive uses the public terminal roadway and takes 23–24 min for 30 km. The 12-month block time is 1 min shorter westbound and 6 min shorter eastbound than July alone.

Sensitivity (same method; these are not proposed values):

| Variant | NYC→CHI | CHI→NYC |
|---|---|---|
| American: LGA B ↔ ORD T3 | 329 | 299 |
| Delta: LGA C ↔ ORD T5 | 328 | 300 |
| United, OSRM for the LGA legs + Valhalla for ORD | 332 | 302 |
| United, July-only block time | 330 | 305 |

Changing the carrier terminal moves the totals by 1 min or less. Changing the router moves them by about 3 min.

## 2. Curb points (sources and exact rule)

**Terminal assignment.** These sources say which terminal each airline uses. They do not give coordinates.
- LGA: https://www.laguardiaairport.com/explore-lga/terminals. It says: "Terminal B serves Air Canada, American Airlines, Frontier Airlines, JetBlue, Porter, Southwest, and United Airlines." and "Terminal C is operated by Delta Airlines."
- ORD: the Chicago Department of Aviation directory map, https://www.flychicago.com/SiteCollectionDocuments/O'Hare/ArchivedPDFs/Map/FullTerminal.pdf. It is marked "EFFECTIVE 11.15.2025" and the server's Last-Modified date is 17 Nov 2025. It lists T1 "United (domestic; international departures only)", T3 "American (domestic; …)" and T5 "Delta". It also says "Rideshare Pickup (at Terminal 2, Departure Level)".
  - The file sits under an `ArchivedPDFs` path. The live airlines page builds its list by script and could not be read.

**Primary carrier pair.** I chose United because it is the largest reporting carrier on LGA→ORD from Aug 2025 to Jul 2026, with 4,665 of 11,611 rows (AA 2,961; DL 2,306; YX 1,288; NK 299; OO 92). YX and OO fly regional service for mainline airlines, and the BTS file does not say which airline brand they fly for.

**Coordinates.** No airport authority page I found publishes curb coordinates. Each curb point is therefore the midpoint, by length, of one named OpenStreetMap roadway way. The data came from an Overpass snapshot dated `2026-10-15T23:56:45Z`; the response SHA-256 is `606da1cf…354b5c`.

| Curb | OSM way (version) | Name / level | Point (lat, lon) |
|---|---|---|---|
| LGA B departures | 818527303 (v5) | Terminal B Departures, layer 2 | 40.7724664, −73.8712600 |
| LGA B arrivals | 818527302 (v5) | Terminal B Arrivals, layer 1 | 40.7725048, −73.8712715 |
| ORD T1 departures | 28257344 (v35) | Departures Terminal 1, layer 1 | 41.9785810, −87.9060245 |
| ORD T1 arrivals | 474544200 (v12) | O'Hare Arrivals Terminal 1 | 41.9789941, −87.9057288 |

The T3, T5 and LGA C points are listed in the JSON. A Node check confirmed that every point is within 0.01 m of its way's line. The Valhalla `/locate` service matched each of the four primary points to that same way ID at 0.0 m. This matters at LGA, where the departures and arrivals roadways are stacked about 4 m apart in plan.

## 3. Re-queries, snap distances and street names

Each direction was queried separately, with the same scene points as v02 (City Hall Park; the Loop).

| Leg | Valhalla (FOSSGIS) km / min | snap (scene / curb) | first / last named roads | OSRM demo km / min, curb snap |
|---|---|---|---|---|
| City Hall Park → LGA B dep | 19.3 / 20.7 | 27 m / 0 m | Park Row … LaGuardia Road → Terminal B Departures | 19.3 / 24.0, 0.1 m ✔ |
| LGA B arr → City Hall Park | 18.2 / 18.6 | 0 m / 27 m | Terminal B Arrivals → GCP … Brooklyn Bridge Blvd, Park Row | 16.6 / 21.8, 0 m ✔ |
| Loop → ORD T1 dep | 30.3 / 23.8 | 33 m / 0 m | S Dearborn St … I-190 W / Kennedy Expy → O'Hare Departures | 34.3 / 54.1, **327 m to an unnamed road ✘** |
| ORD T1 arr → Loop | 30.5 / 23.5 | 0 m / 33 m | O'Hare Arrivals Terminal 1 → O'Hare Arrivals → Kennedy Expy … Eisenhower Expy, S Dearborn St | 34.4 / 54.6, **282 m ✘** (starts `Baggage Road`) |

- Valhalla URLs and response hashes are stored per leg in the JSON. The Valhalla instance is version 3.9.1, with tiles dated 2026-10-15 15:24 UTC.
- **OSRM cannot reach the ORD T1 or T3 curbs.** The public demo and the FOSSGIS OSRM instance return identical results. Both snap 282–643 m to an unnamed airside road and route via `Baggage Road`/`Concourse Service Road`, as v02 did.
  - The OSM tags on the curb roads look routable for cars (`highway=unclassified`, `oneway=yes`, no access restriction).
  - The cause is not identified. It is probably the way OSRM decides the terminal loop is a disconnected "tiny component".
  - OSRM does reach the LGA curbs and the ORD T5 roadways (0 m).
- **Candidate values therefore use Valhalla for all four legs**, so that one router is used throughout. OSRM is kept as a cross-check: on the LGA legs it runs about 3 min slower than Valhalla, which is a difference between the routers' speed models.

## 4. Comparison with official travel guidance

- **CTA** (https://www.transitchicago.com/airports/): "The normal travel time on the Blue Line from O'Hare to downtown, is 40-45 minutes."
  - The candidate free-flow drive (23–24 min) is now faster than the scheduled train, as a free-flow drive should be. v02's 54–55 min was slower, which was the defect.
- **MTA** (https://www.mta.info/guides/airports/laguardia/lga-to-nyc): Q70 "The trip takes about 15 minutes in typical traffic." This is to Jackson Heights only. The page gives no Manhattan total, so it is not comparable.
- **Port Authority NY&NJ**, *Options for Mass Transit Solutions to LGA Airport* (2023-03-13), PDF page 43, §1.0: https://www.panynj.gov/content/dam/port-authority/press-room/press-kits/lga-mass-transit/2023-03-13-Full-Report+Executive-Summary.pdf. For trips from Times Square to LGA it says "The annual average travel time increased from approximately 31 to 35 minutes" (2014→2019), and the average daily maximum rose from 47 to 57 min.
  - The candidate free-flow time from City Hall Park, a longer trip than from Times Square, is 19–21 min. **Typical vehicle time is clearly well above free-flow.**
  - I did **not** turn this into a factor. The origin is different, the data is from 2019, and there is no City Hall figure.

## 5. Block time: 12-month median (reproduced)

- Window: all 12 BTS PREZIP monthly files from Aug 2025 to Jul 2026, `https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_<YYYY>_<M>.zip`. The Aug 2026 file returned HTTP 404 today.
- Every zip passed a CRC test. Every row matched its file's month. The zip SHA-256s are in the JSON.
- Row definition: same as v02 (every scheduled row with `CRSElapsedTime`, cancelled flights included).

| Direction | n | median | p10 | p90 | monthly medians |
|---|---|---|---|---|---|
| LGA→ORD | 11,611 | **165** | 157 | 176 | 157–171 |
| ORD→LGA | 11,611 | **136** | 128 | 144 | 131–142 |

## 6. Exact assumptions (also listed in the JSON `assumptions`)

1. **Curb model.** The traveller is dropped off at the departures curb and picked up at the arrivals curb by private car or taxi. ORD rideshare pickup (T2 departure level) and the LGA app-ride lots are not modelled.
2. **Car times are free-flow model times.** No traffic or time-of-day factor is applied, and no parking, loading or curb dwell is added.
3. **Check-in and wait stays 120 min**, unchanged from v02.
4. **`doorToDoorAllowanceMinutes` stays 0.** Deplaning, the walk to the curb, baggage and waiting for a car remain **uncounted and unsourced**. No figure was invented.
5. **No 2537 fiction modifier** is applied.
6. **Rounding.** Components are rounded to whole minutes and then summed, matching how the runtime sums them (`AIR_MINUTE_FIELDS`). The unrounded totals are also stored.

## 7. Gate status and what is still open

**The door-to-door gate remains OPEN.** The endpoint defect is fixed in this candidate only. Still open:
- the car legs are free-flow, against the "typical" time rule 5 asks for;
- the arrival-side allowance is still 0;
- Valhalla's public instance has unverified terms (the FOSSGIS terms page was blocked by bot protection) and an unpinned OSM snapshot, so a self-hosted router on a dated extract is still needed;
- the creator has not decided the typical-time policy or the 2537 modifiers;
- the BTS, USGS and OSRM licence checks from the audit are still open.

Promoting this candidate to runtime is a separate, creator-approved task. It needs an edit to v02/v03 and a re-run of the travel tests.

## 8. Reproduction (outside the repository)

These scripts are stdlib-only, run with `python -I` and Node:
- `C:\Users\hkzha\AppData\Local\Temp\wb-m2v03-scripts\curb_osrm.py`
- `curb_valhalla.py`
- `bts_12m.py`
- `build_v03_candidate.py`
- `check_v03_candidate.js`

The raw responses are in `…\Temp\wb-m2v03-{osm,osrm,valhalla,bts,web}\`.

**Test result:** `node check_v03_candidate.js` gave **ALL PASS** (41 checks). It covers:
- JSON parse;
- segment total = sum of fields;
- access and egress = round(seconds/60);
- the raw totals;
- snaps ≤ 200 m and curb-end snaps < 1 m;
- flight minutes = the pooled medians, and the monthly n values sum to the pooled n;
- each curb point lies on its OSM way, with the matching version;
- every stored response hash matches the saved raw file;
- the gate is OPEN and the allowance is 0.
