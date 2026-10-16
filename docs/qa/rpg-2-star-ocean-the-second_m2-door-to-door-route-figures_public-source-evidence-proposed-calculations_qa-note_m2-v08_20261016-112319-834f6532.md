# M2 door-to-door route figures: public-source evidence and proposed calculations (QA note, research only, m2-v08)

> **Independent audit (2026-10-16):** see `rpg-2-star-ocean-the-second_m2-door-to-door-route-figures_independent-source-audit_qa-supplement_m2-v08a_20261016-085803-b91a5a30.md`. It confirms S1–S3, S5, S6, S11 and S12, and corrects §3.2's "factors agree" claim, the §3.2 data window, the §3.3 wording and confidence, the S2 metadata remark and this header's time zone (11:23 is UTC, i.e. 07:23 EDT). The body below is unchanged. The gate stays open.

- Date: 2026-10-16 11:23 America/New_York. Web sources were retrieved on 2026-10-16 unless marked otherwise.
- Scope: **research only.** I did not change runtime data, scripts, tests, the meter, the Game Bible, `docs/progress.md` or art. Nothing was staged, committed or pushed. This note is the only file added to the repository.
- Numbering: this note is `m2-v08` because the `wb-m2v07-*` label was already used by the v06 session's temp scripts. No `m2-v07` note exists.
- Canon tested (creator-approved place set in v02 data):
  - start: New York City Hall Park;
  - road destinations: Yonkers outskirts and the abandoned Washington, D.C. Capitol grounds;
  - first air destination: the Chicago Loop.
  - Travel advances the calendar, uses car and plane only, and uses realistic present-day (2025–2026) examples.
- Rule tested: rule 5 in `docs/design/rpg-2-star-ocean-the-second_global-earth-map-real-place-travel_rules-v01_20261014-235354-2b5d4d98.md` (typical door-to-door time; static values must state how they were estimated).
- Runtime data audited: `game/data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json` (v02, still the default).
- Previous notes, in order:
  - v02 audit `…_m2-us-science-route-figures_real-world-travel-audit_qa-note_m2-v02_20261015-195053-10d2525c.md`
  - v03 curbs `…_m2-nyc-chicago-airport-curb-endpoints_v03-candidate_qa-note_m2-v03_20261015-200518-7c3e19a4.md`
  - v04 blocked `…_m2-nyc-chicago-typical-door-to-door_resume-attempt-blocked_qa-note_m2-v04_20261015-224916-c4e1a7b2.md`
  - v05 measured car legs `…_m2-nyc-chicago-typical-door-to-door_measured-car-legs_qa-note_m2-v05_20261015-232832-cfba3fc5.md`
  - v06 offline resume `…_m2-door-to-door-route-figures_offline-resume-runtime-held-v02_qa-note_m2-v06_20261016-003651-90b56d7c.md`
  - v06a traceability `…_m2-door-to-door-route-figures_evidence-traceability-followup_qa-note_m2-v06a_20261016-004249-63176cbd.md`
- **Network use this session:**
  - Ordinary public web search, plus page fetches of official or operator sites (FHWA, BTS, MTA, CTA, Architect of the Capitol / visitthecapitol.gov, Delta, Southwest, Greyhound, FlixBus, OurBus, TSA) and the public OSRM source file on GitHub.
  - No routing API (OSRM or Valhalla), Socrata/SODA query or other third-party API was called. No account, key, credit or paid service was used. No request carried the user's e-mail, tokens, local paths or project data.
  - The BTS airport-pair figures in §4.1 were recomputed **offline** from the 12 monthly BTS zips already on disk from the v03 session.
- **M2 door-to-door route-figures gate: stays OPEN.** Every proposal below is unverified until someone independent re-checks it (§8), and several need creator decisions (§6).

## 1. Summary: current runtime value, proposal, and whether it should change

All values are in minutes. "Typical" follows the creator's time-of-day policy (E6), which is still undecided. Proposals are shown as **all-hours** with the **weekday-daytime** value after a slash where it differs.

| Route (one way) | Current v02 | Proposed | Change? | Confidence | Blocking creator input |
|---|---|---|---|---|---|
| NYC City Hall Park → Yonkers | 35 (28.2 km) | **≈46** / ≈56 (§3.2) | **Likely yes, upward.** Hold until C1 and C5 are approved. | Low–medium. The factor is borrowed from a nearby corridor; this pair was not measured. | C1, C5 |
| Yonkers → NYC City Hall Park | 35 (28.3 km) | **≈46** / ≈56 | Likely yes, upward (same basis) | Low–medium | C1, C5 |
| NYC → Washington Capitol grounds | 289 (363.2 km) | **289, keep**; relabel the basis (§3.1, §3.3) | **Minutes: no. Label: yes.** It is not "free-flow". | Medium. Distance is confirmed to within 0.5 km; time sits within the published bus-schedule range. | C2 (arrival end at the Capitol) |
| Washington → NYC | 286 (361.4 km) | **286, keep**; relabel | Minutes no, label yes | Medium | C2 |
| Yonkers → Washington | 306 (388.0 km) | **306, keep**; relabel | Minutes no, label yes | Medium-low (no independent check for Yonkers specifically) | C2 |
| Washington → Yonkers | 303 (383.4 km) | **303, keep**; relabel | Minutes no, label yes | Medium-low | C2 |
| NYC → Chicago (air, LGA → ORD) | 24 + 120 + 166 + 55 + 0 = **365** | 32 + 120 + 165 + 41 + E3 = **358 + E3** → **373** (E3 = 15, carry-on) or **383** (E3 = 25, checked bag); weekday daytime 372 + E3 | **Yes.** Every component except check-in changes. The total moves only +8 to +18 because the errors partly cancel. | Medium. Components are measured or official; E3 is a design constant. | C3, C4, C5, C6 |
| Chicago → NYC (air, ORD → LGA) | 54 + 120 + 142 + 22 + 0 = **338** | 41 + 120 + 136 + 39 + E3 = **336 + E3** → **351** / **361**; weekday daytime 348 + E3 | **Yes** | Medium | C3, C4, C5, C6 |

The pending routes (Yonkers ↔ Chicago, Washington ↔ Chicago) stay pending. No figure is proposed for them.

## 2. Sources used this session (retrieved 2026-10-16)

| ID | Source (URL) | What it gives | Used for |
|---|---|---|---|
| S1 | FHWA Urban Congestion Report (UCR), Jul–Sep 2025 — https://ops.fhwa.dot.gov/perf_measurement/ucr/reports/fy2025_q4.pdf (sha256 `3fcb12b1…93f042`) | Weekday peak Travel Time Index (TTI) / Planning Time Index (PTI) / data completeness: **New York 1.32 / 2.04 / 90%**, Washington 1.31 / 2.22 / 93%, Chicago 1.39 / 2.14 / 96%, Philadelphia 1.23 / 1.77, Baltimore 1.28 / 1.97 | Congestion cross-check for car legs |
| S2 | FHWA UCR, Apr–Jun 2026 — https://ops.fhwa.dot.gov/perf_measurement/ucr/reports/fy2026_q3.pdf (sha256 `4a9bee95…a4443a`; the PDF's embedded metadata title wrongly says 2022, but every page header says "April through June 2026") | New York 1.24 / 1.79 / **72% complete**; Washington 1.34 / 1.98 / 93%; Chicago 1.30 / 1.91 / 96%; national average 1.23 | Not used for New York, because of the 72% data completeness. Shows the quarter-to-quarter swing. |
| S3 | FHWA UCR Oct–Dec 2025, New York row (1.34 / 2.19 / 92%). Seen only in a **search-result excerpt** of https://ops.fhwa.dot.gov/perf_measurement/ucr/reports/fy2026_q1.pdf; the PDF was not opened. | — | Second NYC TTI value. Needs re-reading before use (§8). |
| S4 | FHWA UCR documentation — https://ops.fhwa.dot.gov/perf_measurement/ucr/documentation.htm | TTI = "the ratio of the peak-period travel time to the free-flow travel time", weekday 6–9 am and 4–7 pm. Free-flow speed = "85th percentile of off-peak speeds". Data: National Highway System, NPMRDS probe data. | Defines what a TTI may and may not be multiplied by (§3.1) |
| S5 | OSRM car profile, current `master` branch — https://raw.githubusercontent.com/Project-OSRM/osrm-backend/master/profiles/car.lua and `profiles/lib/way_handlers.lua` | `speed_reduction = 0.8`; `result.forward_speed = forward * profile.speed_reduction` when a `maxspeed` tag exists. Default motorway speed 90 km/h. | Shows the stored "free-flow" car times are **not free-flow** (§3.1). I did not confirm which profile version the public demo server runs. |
| S6 | MTA BxM3 timetable "Yonkers – Midtown", effective April 12, 2026 — https://www.mta.info/schedules/bus/bxm3 (served PDF, sha256 `25fd75ef…0c343f3`) | Weekday scheduled times, S Broadway/Prospect St (Getty Sq, Yonkers) ↔ Midtown (§3.2) | Official scheduled road-vehicle time on the Yonkers corridor (sanity bound) |
| S7 | Greyhound route page — https://www.greyhound.com/bus-routes/new-york-ny-washington-dc | "Min. distance 226 miles"; "Min. trip duration 3 hr 30 mins"; "72" daily departures; DC stop "Washington DC (Union Station)" | Distance and time cross-check (§3.3) |
| S8 | FlixBus route page — https://www.flixbus.com/bus-routes/bus-new-york-ny-washington-dc | "227 miles" (226 minimum); "3 hr 30 mins" minimum | Same as S7 (it shares the Greyhound network) |
| S9 | OurBus route page — https://www.ourbus.com/routes/nyc-to-dc and blog https://www.ourbus.com/blog/dc-day-trip-from-nyc-by-bus/ (dated 2026-08-08) | "3 hours 30 minutes to 5 hours 50 minutes"; "a swing of 2 hrs 20 min that can reflect traffic and schedule differences"; "Plan against the slow end". Its "About 203.9 miles" equals the straight-line NYC–DC distance, not a road distance. | Upper/lower time bound (§3.3) |
| S10 | U.S. Capitol visitor page — https://www.visitthecapitol.gov/plan-visit/getting-capitol | "very little public parking available near the Capitol"; "The nearest public parking facility is at Union Station" | Arrival end of the DC car trip (C2) |
| S11 | BTS On-Time Reporting monthly zips Aug 2025 – Jul 2026 (`https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_<Y>_<M>.zip`), recomputed offline; the zip SHA-256 values are in `wb-m2v08-bts-pairs.json` and the earlier v03 JSON | `CRSElapsedTime` by airport pair (§4.1) | Block time and airport choice |
| S12 | BTS Technical Directive No. 40 (On-Time 2026) — https://www.bts.gov/explore-topics-and-geography/modes/aviation/number-40-technical-directive-reporting-time ; TranStats glossary https://transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFD ; gate definitions https://www.bts.gov/topics/airlines-and-airports/number-15-gate-departure-time | Scheduled elapsed time = CRS arrival − CRS departure. Gate arrival = "when the pilot sets the aircraft parking brake after arriving at the airport gate". Elapsed time is gate-departure to gate-arrival. (Quoted from search-result excerpts of these official pages; the pages themselves were not fetched.) | Shows block time ends at the gate, so the arrival side must be counted separately (§4.5) |
| S13 | Southwest route page — https://www.southwest.com/routes/flights-from-new-york-to-chicago-midway | "156 weekly flights"; "7 times per day from Monday through Friday"; "Average flight time: 2 hours 25 minutes"; "725 miles" | Cross-checks the LGA–MDW option |
| S14 | CTA airports — https://www.transitchicago.com/airports/ | Blue Line O'Hare → downtown "40-45 minutes"; Orange Line Midway → downtown "20-25 minutes" | Relative airport proximity (C3) |
| S15 | Delta domestic check-in — https://www.delta.com/us/en/check-in-security/check-in-time-requirements/domestic-check-in | "arrive at the airport at least 2 hours prior to departure"; LGA exception 45 min with or without bags; "at the gate and ready to board 15 minutes before scheduled departure" | Check-in/wait 120 (C4) |
| S16 | Delta baggage FAQs — https://www.delta.com/us/en/baggage/additional-baggage-information/baggage-faqs | A bonus is paid if a bag takes more than 20 min, measured as "the time elapsed between the aircraft's arrival at the gate and delivery of the bag"; applies to Delta-operated domestic flights | Upper reference for the checked-bag arrival time (§4.5) |
| S17 | TSA FAQ — https://www.tsa.gov/travel/frequently-asked-questions | No fixed arrival time: "contact your airline as times may vary" | Confirms TSA gives no number |
| — | Not reachable: United check-in requirements (60 s timeout, as in v02/v05); Southwest airport check-in help page (404). | — | Open (§8) |

Secondary sources seen in search results but **not used as evidence**: Rome2Rio and Wanderu bus durations, Fox affiliate UMR articles, third-party "check-in time" guides and the GAO-18-236 TSA wait-time finding (2015–2017 data, too old).

## 3. Car routes

### 3.1 Correction: the stored car times are a routing model, not "free-flow"

Every v02 car segment says "Free-flow routing-model time with no traffic". Per S5, the OSRM car profile sets road speed to **80% of the tagged speed limit** wherever a `maxspeed` tag exists, and uses fixed defaults (motorway 90 km/h) elsewhere. FHWA defines free-flow as the 85th percentile of observed off-peak speed (S4), which on US freeways is usually *above* the limit. So:

- On intercity freeways, OSRM time is **slower than true free-flow** and partly resembles a typical time. Example: NYC → DC is 363.2 km in 289 min, an average of 75 km/h. The fastest scheduled bus (S7) implies about 104 km/h.
- In dense city streets, OSRM does not model signals and congestion well, so it is **faster than typical** (v05 measured City Hall Park → LGA at 31.7 min, all hours, against an OSRM curb time of 24.0; §3.2).
- **Proposed label for every car segment:** "OSRM routing-model time (car profile: 80% of tagged speed limits; no live traffic). Not free-flow and not measured." Applying an FHWA TTI directly to this base is therefore a heuristic, not a calculation. The TTI's denominator is real free-flow.

### 3.2 NYC City Hall Park ↔ Yonkers (current 35 / 35 min, 28.2 / 28.3 km)

**Evidence.**

| Evidence | Value | Bearing |
|---|---|---|
| OSRM model (v02, re-queried in v02 audit) | 35.4 / 35.5 min | Base |
| FHWA UCR New York TTI, weekday peak (S1, S3) | 1.32 (Jul–Sep 2025), 1.34 (Oct–Dec 2025); mean **1.33** | Peak typical ≈ 1.33 × true free-flow |
| Same-origin calibration from measured NYC data (v05 TLC 2025 medians ÷ v03 OSRM curb times, City Hall Park zone 231 → LGA zone 138) | all hours 31.68 / 24.0 = **1.32**; weekday 07–19 38.07 / 24.0 = **1.59** | Converts this router's urban/expressway output from City Hall Park into a measured typical time |
| MTA BxM3 express bus, weekday (S6): Prospect St, Yonkers → 5 Av/W 27 St (25 trips) | min **63**, median **76**, max **99** | Scheduled road time for a stopping bus (about 30 stops), ending about 4 km short of City Hall. A private car must be well below this. |
| BxM3 Madison Av/E 29 St → S Broadway/New Main St, Yonkers (26 trips) | min **60**, median **79**, max **93** | Same |

**Proposed calculation (transparent; needs creator approval C1):**
- All-hours typical = 35.4 × 1.32 = 46.7. With UCR TTI 1.33: 35 × 1.33 = 46.6. The two independent factors agree. Proposed **46** (round from 35 × 1.32 = 46.2 on the stored integer).
- Weekday daytime typical = 35 × 1.59 = 55.7 → **56**.
- Reverse direction: the same factor gives 46 / 56. I did **not** use the LGA→City Hall egress ratio (1.71), because it includes airport-roadway exit delay that does not apply to Yonkers.
- Sanity check: 46–56 min by car against a 60–99 min stopping bus that starts about 4 km closer is consistent.

**Should it change?** Likely yes, upward from 35 to about 46 (all hours). It is not ready, because:
- (a) the factor is **borrowed** from the City Hall Park → LGA corridor, not measured on Yonkers;
- (b) Yonkers is outside NYC, so TLC trip data cannot isolate it (it is lumped into "Outside of NYC");
- (c) the scene entry point in Yonkers is not registered yet (v02 uses the GeoNames city point), and the outskirts scene may sit further north than South Broadway.

Uncertainty: about 40–60 min for a typical car trip.

### 3.3 NYC ↔ Washington Capitol grounds (current 289 / 286 min, 363.2 / 361.4 km) and Yonkers ↔ Washington (306 / 303, 388.0 / 383.4 km)

**Distance.** Greyhound's "Min. distance 226 miles" (Midtown → Union Station) = **363.7 km** (S7). FlixBus states 226–227 mi (S8). The stored 363.2 km agrees to within 0.5 km. **Keep it.** OurBus's "203.9 miles" is the straight-line distance (≈ 328 km) and must not be used as road distance. This matches the design rule's split between road distance and great-circle distance.

**Time.**

| Evidence | Value |
|---|---|
| Fastest scheduled bus Midtown → Union Station (S7, S8) | 210 min |
| OurBus scheduled range (S9) | 210–350 min ("plan against the slow end") |
| OSRM model (v02) | 289 / 286 |
| FHWA UCR TTI along the corridor, Jul–Sep 2025 (S1) | New York 1.32, Philadelphia 1.23, Baltimore 1.28, Washington 1.31. Congestion is concentrated at the two urban ends. |

The stored 289 sits inside the scheduled-bus range, 79 min above the fastest coach and 61 min below the slowest. Coaches are a reasonable proxy for a car on this route (mostly nonstop on I-95 / NJ Turnpike), though they lose some minutes at terminals.
- No public primary source gives a measured typical car time for this pair. Applying a metro TTI to the whole 363 km would overstate it, because most of the distance is outside the congested metro cores.
- **Proposal: keep 289 / 286 and 306 / 303 minutes, and fix the basis label (§3.1).** Uncertainty: about ±60 min. Yonkers ↔ DC has no independent cross-check; it inherits the same method.

**Arrival at the Capitol grounds (C2).** In the real 2026 city there is "very little public parking available near the Capitol" (S10); the nearest public garage is Union Station, about 1 km north. A real door-to-door trip would add parking plus a walk of about 10–15 min, but that walk time is **my estimate, not sourced**. In the game fiction Washington is abandoned, so a car may stop at the grounds. **Creator input C2:** whether to add a car-end allowance at all (0 if the party's vehicle stops at the scene entry), and whether "abandoned" changes the final approach.

### 3.4 Car departure end (C5)

The v02 car segments have `doorToDoorAllowanceMinutes = 0` at both ends (loading the car, leaving a parking spot). Rule 5 says "door-to-door". There is no public primary source for a "walk to car" time. If the creator wants one, it must be a labelled `design-constant` (v02 audit §6.3). My suggestion is 0 for a party vehicle waiting at the scene entry. **Creator input C5.**

## 4. Air route NYC ↔ Chicago

### 4.1 Likely airports (recomputed offline from S11, Aug 2025 – Jul 2026, scheduled `CRSElapsedTime`)

| Pair (direction) | Flights n | Scheduled median (p10 / p90) | Actual median, flown | Carriers (reporting) |
|---|---|---|---|---|
| **LGA → ORD** | **11,611** (≈32/day) | **165** (157 / 176) | 160 | UA 4,665; AA 2,961; DL 2,306; YX 1,288; NK 299; OO 92 |
| **ORD → LGA** | 11,611 | **136** (128 / 144) | 129 | same |
| EWR → ORD | 6,066 (≈17/day) | 164 (158 / 172) | 159 | UA 4,389; AA 831; MQ 595; NK 149; YX 102 |
| ORD → EWR | 6,071 | 139 (130 / 147) | 129 | same |
| JFK → ORD | 2,074 | 176 (165 / 185) | 168 | YX 820; B6 603; AA 521; F9 116; DL 14 |
| ORD → JFK | 2,073 | 143 (134 / 154) | 135 | same |
| LGA → MDW | 2,385 (≈6.5/day) | **150** (140 / 160) | 138 | WN 2,385 |
| MDW → LGA | 2,385 | **125** (120 / 130) | 118 | WN |
| EWR ↔ MDW | 71 / 71 | 150 / 124 | — | F9 only; too sparse to use |

- The LGA↔ORD rows reproduce the v03/v06 values exactly (n 11,611; 165 / 136), which cross-checks the offline script.
- Southwest's own page (S13) gives "7 times per day" Monday–Friday and an "Average flight time" of 145 min. That is close to the BTS 150 / 125 median pair.

**Choice (creator input C3):**
- **LGA → ORD** (current): the most frequent pair by far. Its measured car legs are already available (v05/v06).
- **LGA → MDW**: block time is 15 min shorter westbound and 11 min shorter eastbound. Midway is much closer to the Loop: the CTA quotes 20–25 min for MDW → downtown and 40–45 for ORD (S14). It is served by one airline at about 7 flights a day.
  - Its door-to-door time is probably about 30 min shorter, but that is **not computed**: no measured MDW ↔ Loop car leg exists in the evidence chain.
- **EWR** may be competitive from Lower Manhattan via the Holland Tunnel, but no measured City Hall Park ↔ EWR leg exists either.
- **Recommendation:** keep LGA → ORD as the default "typical" pair, because it is the dominant service. Record MDW as an alternative to measure later.

### 4.2 Flight block time

**Proposal: 165 westbound, 136 eastbound** (12-month median; this replaces the July-only 166 / 142).
- Per S12, this is scheduled gate-departure to gate-arrival time, so taxi-out and taxi-in are included.
- Scheduled block time exceeds the actual flown median by 5–7 min (schedule padding). Using the scheduled figure is the conservative "planned trip" choice that v02 already made.
- **Change: yes.**

### 4.3 Departure side: check-in and wait (current 120)

- Delta: "at least 2 hours prior to departure"; LGA minimum check-in 45 min; at the gate 15 min before departure (S15).
- TSA: no fixed figure (S17). United was not readable this session.
- The 120 min clock starts when the traveller reaches the airport curb, so curb dwell is inside it (v04 E4). Nothing is double-counted with the access drive.
- **Keep 120.** It is airline guidance, not a measured wait, and a creator may prefer a leaner "experienced traveller" value of 60–90 for carry-on only. **Creator input C4.**

### 4.4 Access and egress car legs (measured; from v05/v06, not re-queried this session)

| Leg | v02 runtime | Measured median (all hours) | Weekday 07–19 | Source |
|---|---|---|---|---|
| City Hall Park → LGA (zone 231 → 138) | 24 | **32** (32.27; n 67,932) | 39 (38.82) | NYC TLC Yellow + HVFHV, Sep 2025 – Aug 2026 (v06 §3) |
| LGA → City Hall Park | 22 | **39** (39.32; n 61,255) | 47 (46.95) | same |
| Loop → ORD (area 32 → 76) | 54 | **41** (40.63, taxi; pooled taxi + TNP 39.02) | 45 | Chicago Taxi `ajtu-isnz` / TNP `6dvr-xwnh` (v06 §3) |
| ORD → Loop | 55 | **41** (40.65, taxi only; TNP **missing**) | 48 (47.5) | Chicago Taxi (v06 §3) |

- **Change: yes.**
  - The v02 ORD legs (54 / 55) were routed from the airfield reference point over airside service roads (v02 audit §4.1).
  - The v02 LGA legs (24 / 22) are routing-model times that the measured data shows are 8–17 min too short.
- **Caveat:** the Chicago legs are taxi-only on both sides, chosen for a consistent basis, because the TNP egress pull never completed.

### 4.5 Arrival side, E3 (current 0; still unsourced as a measured typical value)

Block time ends at gate arrival (S12). The traveller still has to deplane, walk to the curb, possibly collect bags, and wait for a car. Evidence:
- **Checked bag:** Delta treats more than 20 min from gate arrival to bag delivery as a service failure (S16). That is a service standard, so it is an *upper reference* for a typical bag wait, not a measured median.
- **Car wait at LGA:** the measured TLC HVFHV request-to-pickup median at LGA → zone 231 is **5.25 min** (p10 1.87, p90 11.60; v05 §4). It covers only the app-ride wait.
- **Deplane and walk to curb:** no public primary measurement found. ACRP Report 40 and its 2024 second edition model curb dwell for vehicles, not passenger walk time.

**Proposed `design-constant` (needs creator approval C6), labelled as such and not as research:**
- **Carry-on only: 15 min** = deplane and walk to curb about 10 (my estimate, unsourced) + car wait 5 (rounded LGA measurement).
- **Checked bag: 25 min** = bag at carousel ≤ 20 (Delta standard, from gate arrival, which overlaps the deplane/walk) + car wait 5.
- Either is better than 0, which is known to be too short. The same value is used at ORD and LGA, since there is no ORD-specific wait data (Chicago trip records carry no request timestamps).

### 4.6 Proposed totals (sum of component medians; not the median of a full trip)

| Direction | Access | Check-in | Flight | Egress | E3 | **All hours** | Weekday 07–19 |
|---|---|---|---|---|---|---|---|
| NYC → Chicago | 32 | 120 | 165 | 41 | 0 / 15 / 25 | 358 / **373** / 383 | 39 + 120 + 165 + 48 = 372 / 387 / 397 |
| Chicago → NYC | 41 | 120 | 136 | 39 | 0 / 15 / 25 | 336 / **351** / 361 | 45 + 120 + 136 + 47 = 348 / 363 / 373 |
| v02 runtime (for reference) | 24 / 54 | 120 | 166 / 142 | 55 / 22 | 0 | 365 / 338 | — |

The westbound total changes from 365 to 373 (+8) with a carry-on E3, and the eastbound total from 338 to 351 (+13). The westbound total changes little because the egress fix (−14) offsets the access, flight and E3 changes (+8 −1 +15).

## 5. 2026 baseline vs 2537 game

Every figure here is a **2025–2026 real-world baseline**. As v02 audit §5 recommends, any 2537 fiction modifier must be a separate, named, creator-approved value. Examples: which airports operate, whether there is security screening, the state of roads into an abandoned Washington. Until approved, every modifier is 1.0. This note proposes none.

## 6. Decisions that need the creator (none are made here)

| ID | Decision | Options and effect |
|---|---|---|
| C1 | Accept a **borrowed calibration factor** for short NYC-area car trips (§3.2)? | (a) Yes: 35 → 46 (all hours) / 56 (weekday daytime). (b) No: keep 35 labelled as a routing-model value until a corridor-specific measurement exists. (c) Commission a measurement (no public trip dataset isolates Yonkers; see §8). |
| C2 | Car arrival end at the Washington Capitol grounds | 0 (vehicle stops at the scene) vs a parking-and-walk allowance (real 2026: Union Station garage, about 1 km; time unsourced). Fiction: "abandoned". |
| C3 | Chicago airport for the "typical" air route | LGA → ORD (most frequent; measured legs) vs LGA → MDW (shorter, one airline, legs unmeasured) |
| C4 | Departure-side allowance | 120 (two-hour airline guidance) vs a lean 60–90 |
| C5 | Time-of-day policy (E6) and car-start allowance | All hours vs weekday 07–19; departure allowance 0 vs a design constant |
| C6 | Arrival-side constant (E3) | 15 (carry-on) vs 25 (checked bag) vs another labelled value |

## 7. Uncertainty summary

| Item | Main uncertainty | Rough range |
|---|---|---|
| NYC ↔ Yonkers | Borrowed factor; scene point unregistered; the time-of-day policy | 40–60 min |
| NYC / Yonkers ↔ DC | No measured car distribution; bus-schedule bracket only; demo-server OSRM version not pinned | ±60 min |
| Air components | Zone-to-zone (not point-to-point) car legs; Chicago taxi-only; E3 is a design constant; check-in is guidance | Total about ±30 min around the proposal |
| FHWA TTI | Weekday peak only; NYC Apr–Jun 2026 only 72% complete; quarter-to-quarter swing 1.24–1.34 | — |
| Router labels | Which OSRM profile version the public demo runs was not confirmed | — |

## 8. What an independent verifier must check before the gate can close

1. Re-open S3 (FHWA UCR Oct–Dec 2025 PDF) and confirm the New York row (1.34 / 2.19 / 92%), which I saw only in a search excerpt.
2. Re-derive the BxM3 run times from the MTA PDF (§3.2). The trip lists are in `wb-m2v08-scripts\calc.py`.
3. Re-run `bts_pairs.py` (below) on the 12 cached zips. Confirm that the zip SHA-256 values match the v03 JSON and that LGA↔ORD gives 11,611 / 165 / 136.
4. Fetch S12 pages directly and quote the gate-arrival definition from the page, not from a search excerpt.
5. Re-try United's check-in page and a Southwest page that quotes a recommended arrival time.
6. Complete the Chicago TNP ORD → Loop pull (v06 §4.1), or approve taxi-only.
7. If C3 picks MDW, measure Loop ↔ MDW (community areas 32 ↔ 56) and City Hall Park ↔ LGA again for consistency.
8. Only after creator decisions C1–C6: write a new candidate data file, run the existing travel tests, and do a separate, reviewed runtime promotion. **Do not edit the v02 runtime file from this note.**

## 9. Reproduction (outside the repository)

- `%LOCALAPPDATA%\Temp\wb-m2v08-scripts\bts_pairs.py`: stdlib only. Run as `python -I bts_pairs.py <zip dir> <out json>`. It reads `%LOCALAPPDATA%\Temp\wb-m2v03-bts\dl\*.zip` and writes `%LOCALAPPDATA%\Temp\wb-m2v08-bts-pairs.json` (sha256 `0a9ce5d8…7f2f`).
- `%LOCALAPPDATA%\Temp\wb-m2v08-scripts\calc.py`: BxM3 run times, the calibration ratios, the totals and the source PDF hashes.
- Saved PDFs in `%LOCALAPPDATA%\Temp\wb-m2v08-web\` (not committed):
  - `fhwa-ucr-2025-jul-sep.pdf`, sha256 `3fcb12b1d09519db21b2b6f53c8dca5dfd352138b3182ec3ddfee8a8b693f042`
  - `fhwa-ucr-2026-apr-jun.pdf`, sha256 `4a9bee957ec962c1ff66c2a27cdeeec17559c160b677efd6bb157055bda4443a`
  - `mta-bxm3-2026-04-12.pdf`, sha256 `25fd75ef0fcf5bd551dfa5d295f41089b9ef266a21a86c634c3bc50630c343f3`
- The Python used is the bundled runtime Python (the `python` on PATH is a Store stub).
