# M2 door-to-door route figures: independent source audit of the m2-v08 draft (QA supplement, research only, m2-v08a)

- Date: 2026-10-16, about 08:58 EDT (12:58 UTC). Web sources retrieved on 2026-10-16.
- Audited draft: `docs/qa/rpg-2-star-ocean-the-second_m2-door-to-door-route-figures_public-source-evidence-proposed-calculations_qa-note_m2-v08_20261016-112319-834f6532.md` ("the draft"; untracked at audit time).
- Scope: Task D. An independent check of the NYC ↔ Yonkers, NYC ↔ Washington, D.C. (car) and NYC ↔ Chicago (air) research. **Research only.**
  - No runtime travel figure, segment label, script, test, completion meter, Game Bible, `docs/progress.md` or Git history was changed. Nothing was staged or committed.
  - The draft received one pointer line to this supplement. Its body and numbers are unchanged.
- **M2 door-to-door route-figures gate: stays OPEN.** This audit does not implement any figure. Creator choices C1–C6 (draft §6) and creator review are still pending.
- Rules tested:
  - Travel rule 5 in `docs/design/rpg-2-star-ocean-the-second_global-earth-map-real-place-travel_rules-v01_20261014-235354-2b5d4d98.md`: typical door-to-door time; car uses road distance and drive time; air counts the necessary airport transfer and waiting time; static values state how they were estimated.
  - The data contract in the same file: road distance and great-circle distance are kept separate.
- Runtime data audited, read only: `game/data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json` (v02, default).
- Network hygiene:
  - Only public official or operator pages, the FHWA PDFs and the public OSRM source on GitHub were fetched, plus one public web search.
  - No routing API, Socrata query, account, key or paid service was used.
  - No request carried personal data, e-mail addresses, tokens, local paths or project data.

## 1. Evidence classes used in this supplement

| Class | Meaning |
|---|---|
| **Measured** | Observed trips or observed probe speeds (BTS actuals, TLC/Chicago trip records, FHWA NPMRDS indices) |
| **Scheduled** | An operator's published plan (BTS `CRSElapsedTime`, MTA and coach timetables). A plan, not an observation. |
| **Model** | A routing-engine output (OSRM). Neither measured nor scheduled. |
| **Proxy** | A measured or scheduled value taken from a *different* trip and transferred to this one |
| **Guidance / standard** | An airline recommendation or a service guarantee. Neither a measured wait nor a median. |
| **Assumption** | A value chosen without a source (a design constant) |
| **Inference** | A conclusion reasoned from the above |

## 2. What I re-verified independently

| Draft claim | How I checked it | Result | Class |
|---|---|---|---|
| S1 FHWA UCR Jul–Sep 2025, NY 1.32 / 2.04 / 90%; DC 1.31 / 2.22 / 93%; Chicago 1.39 / 2.14 / 96%; Phila 1.23 / 1.77; Balt 1.28 / 1.97 | Re-downloaded https://ops.fhwa.dot.gov/perf_measurement/ucr/reports/fy2025_q4.pdf. The SHA-256 `3fcb12b1…b693f042` is identical to the draft's. Rows read with `pdftotext -raw`. **Warning:** `-layout` output misaligns the rows by one or more lines. | **Confirmed** | Measured (probe), weekday peak only |
| S3 FHWA UCR Oct–Dec 2025, NY 1.34 / 2.19 / 92% (draft: excerpt only) | Downloaded https://ops.fhwa.dot.gov/perf_measurement/ucr/reports/fy2026_q1.pdf (SHA-256 `cd073843ed5eb8a6e63bb4f108db68775992c3ee121c8506a4e460891c8338d9`). Row: `New York, NY 6:39 +0:06 1.34 0 2.19 +1 92%`. Also DC 1.33 / 2.17 / 92%; Chicago 1.30 / 2.08 / 96%. | **Confirmed.** Draft §8 item 1 can be closed. | Measured |
| S2 FHWA UCR Apr–Jun 2026, NY 1.24 / 1.79 / 72% | Re-downloaded https://ops.fhwa.dot.gov/perf_measurement/ucr/reports/fy2026_q3.pdf. The SHA-256 `4a9bee95…a4443a` is identical. | Values **confirmed**. **Correction:** the PDF Info title is correct ("April through June 2026"). Only one stale XMP `dc:title` says "January through March 2022". The draft's "metadata title wrongly says 2022" is half right. | Measured |
| S4 TTI/PTI and free-flow definitions | https://ops.fhwa.dot.gov/perf_measurement/ucr/documentation.htm | **Confirmed.** TTI = "the ratio of the peak-period travel time to the free-flow travel time". Free-flow = "85th percentile of off-peak speeds", off-peak = weekdays 9 am–4 pm and 7–10 pm. Peaks are 6–9 am and 4–7 pm weekdays. Coverage is "the entire National Highway System (NHS)", from NPMRDS. | Definition |
| S5 OSRM car profile | Downloaded https://raw.githubusercontent.com/Project-OSRM/osrm-backend/master/profiles/car.lua (SHA-256 `57778a75…a59fa66`) and `profiles/lib/way_handlers.lua` (`4d503da9…7c6a0`) | **Confirmed.** `speed_reduction = 0.8` is applied as `result.forward_speed = forward * profile.speed_reduction` when a maxspeed tag parses. Defaults: motorway 90, trunk 85, primary 65, residential 25 km/h. Penalties: turn 7.5 s, u-turn 20 s. **Still open:** which profile version the public demo server runs. | Model definition |
| S6 MTA BxM3 weekday run times | Re-extracted the draft's saved PDF (SHA-256 `25fd75ef…0c343f3`, matches the draft) with `pdftotext`. Re-read every full-length weekday trip. https://www.mta.info/schedules/bus/bxm3 returned 403 to a plain request today. | **Confirmed.** To Midtown: 25 trips from Prospect St, min 63 / median 76 / max 99. To Yonkers: 26 trips to New Main St, 60 / 79 / 93. The trips the draft excluded are short-turn trips that do not start at Prospect St; excluding them is correct. Draft §8 item 2 can be closed. **Note:** the PDF's footer says "Traffic conditions and weather can affect running time". The bus runs on Madison/5th Avenue local streets through Manhattan, so it is an *upper bound* for a car, not a proxy. | Scheduled |
| S12 BTS gate and elapsed-time definitions (draft: excerpt only) | The two bts.gov pages returned 403. The official TranStats glossary https://www.transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFD was fetched (HTML SHA-256 `5569cdfd…b62aabe`). | **Confirmed from an official page.** "Gate arrival time is the instance when the pilot sets the aircraft parking brake after arriving at the airport gate or passenger unloading area". "Elapsed Time: The time computed from gate departure time to gate arrival time". "A flight is considered on-time when it arrives less than 15 minutes after its published arrival time". CRS = "Computer Reservation System". Coverage is reporting carriers with at least 0.5% of domestic scheduled passenger revenue, so it is **not every flight**. Draft §8 item 4 is closed on substance; the two bts.gov pages remain unread. | Definition |
| S11 BTS pairs | Wrote my own stdlib script (§6), independent of the draft's `bts_pairs.py`, and ran it on the same 12 zips. All 12 zip SHA-256 values appear in both the v03 JSON and the draft's `wb-m2v08-bts-pairs.json`. | **Reproduced exactly:** LGA→ORD n 11,611, CRS p10/p50/p90 157 / 165 / 176, actual 160; ORD→LGA 128 / 136 / 144, actual 129; LGA↔MDW 150 / 125; EWR and JFK rows match. Draft §8 item 3 is closed. | Scheduled + measured |
| S15 Delta check-in | https://www.delta.com/us/en/check-in-security/check-in-time-requirements/domestic-check-in | **Confirmed.** "we recommend that you arrive at the airport at least 2 hours prior to departure". Bags 45 min, no bags 30 min. The LGA row gives 45 / 45. At the gate "15 minutes before scheduled departure". | Guidance |
| S16 Delta 20-minute bag guarantee | https://www.delta.com/us/en/baggage/additional-baggage-information/baggage-faqs | Wording confirmed: "the time elapsed between the aircraft's arrival at the gate and delivery of the bag to the baggage claim carousel" > 20 min earns 2,500 miles. Measured by Delta's system "where available". Only Delta-marketed **and** operated domestic flights. **Wording fix:** this is a promotional guarantee threshold, not a "service failure" definition. It covers about 20% of LGA–ORD flights (DL 2,306 / 11,611). | Guidance / standard |
| S17 TSA | https://www.tsa.gov/travel/frequently-asked-questions | **Confirmed:** no fixed arrival time; "contact your airline as times may vary". | Guidance |
| S7 Greyhound | https://www.greyhound.com/bus-routes/new-york-ny-washington-dc | "226 miles" and "3 hr 30 mins" confirmed. Departures now read **73** (draft: 72; ordinary page drift). **Omission:** the same page says the trip "typically takes around five and a half to six hours" (330–360 min). The draft did not cite this. | Scheduled / operator statement |
| S9 OurBus | https://www.ourbus.com/routes/nyc-to-dc | **Confirmed:** "3 hours 30 minutes to 5 hours 50 minutes"; "About 203.9 miles". My haversine Port Authority → Union Station is 205.2 mi and City Hall Park → Capitol is 203.1 mi, so 203.9 mi is a straight-line figure, as the draft says. | Scheduled |
| S10 Capitol parking | https://www.visitthecapitol.gov/plan-visit/getting-capitol | **Confirmed:** "very little public parking available near the Capitol"; "The nearest public parking facility is at Union Station, to the north of the Capitol". The page gives **no** walking time. | Official statement |
| S14 CTA airports | https://www.transitchicago.com/airports/ | **Confirmed:** "The normal travel time on the Blue Line from O'Hare to downtown, is 40-45 minutes"; Midway "20-25 minutes". These are rail times, used only as a relative-proximity proxy. | Scheduled proxy |
| Runtime check-in source (American Airlines) | https://www.aa.com/i18n/travel-info/check-in-and-arrival.jsp | **403** to an automated fetch today. United (`united.com/.../check-in-times.html`) timed out after 60 s. | Unverified this session |

## 3. Weak or unsupported claims in the draft

Highest impact first.

1. **§3.2: "The two independent factors agree" (TTI 1.33 vs calibration 1.32) is not valid corroboration.** Downgrade it.
   - The FHWA TTI is a **weekday 6–9 am / 4–7 pm** ratio to the **85th-percentile off-peak speed** on the NHS, metro-wide (S4).
   - The 1.32 is an **all-hours** TLC median divided by an **OSRM model** time for one zone pair. The draft's own §3.1 argues that OSRM is not free-flow.
   - The two ratios have different numerators and different denominators. If the TTI belongs anywhere, it belongs beside the weekday-peak figure (1.59), not the all-hours one. Their numerical closeness is a coincidence.
   - **Status of 46 min:** a *proxy* (City Hall Park → LGA calibration transferred to the Yonkers corridor) plus an *inference*. It is not a calculation from Yonkers data.
2. **§3.2: the calibration factor uses a different data window from §4.4.**
   - `calc.py` divides the v05 **calendar-2025** medians (31.68 all hours, 38.07 weekday) by 24.0.
   - §4.4 uses the v06 **Sep 2025 – Aug 2026** medians (32.27, 38.82).
   - With one consistent window: 32.27 / 24.0 = 1.345, giving 35 × 1.345 = 47.1 → **47**; weekday 38.82 / 24.0 = 1.62, giving 56.6 → **57**. The difference is +1 min, but the method should use one window.
   - The denominator 24.0 *is* the OSRM-demo curb time from v03 §3 (19.3 km / 24.0). The 20.70 that v05 lists as "v03 free-flow" is the **Valhalla** time. Since the Yonkers base (35.4) is also OSRM demo output, 24.0 is the like-for-like denominator, and the draft is right on this point.
3. **§3.3: "Distance is confirmed to within 0.5 km" overstates the match.** Greyhound's 226 mi is Port Authority/Midtown → Union Station. The runtime segment is City Hall Park → Independence Ave SE, roughly 4 km and 1 km away from those stops. The 0.5 km agreement is partly coincidence. Reword to "consistent with operator road distance (S7/S8)". Keeping 363.2 km is still fine.
4. **§3.3: the time bracket omits Greyhound's own "typically ... five and a half to six hours".** That figure is for stopping coaches, so it is not a car proxy either. It shows that the 210–350 bracket mixes nonstop express and stopping services.
   - No official measured NYC ↔ DC car travel time was found. FHWA UCR is metro-only. The I-95 probe data (NPMRDS) is not published as a corridor time.
   - "Keep 289" is therefore an **inference** that the model value falls inside a scheduled-coach bracket. I would rate confidence **low–medium**, not medium.
   - Directional inference: the fastest coach (210 min, about 104 km/h) and OSRM's 80%-of-limit rule (S5) suggest that 289 *overstates* an off-peak car trip and roughly matches a typical daytime one. That is unquantified.
5. **§3.1: "free-flow ... on US freeways is usually above the limit" is an inference with no cited source.** It is plausible given the 85th-percentile definition, but should be labelled an inference. The core correction is sound and verified (S5): the v02 notes "Free-flow routing-model time" are mislabelled.
6. **§4.2: "schedule padding" framing.** The traveller's clock starts from *scheduled* departure (they arrive 2 h before it) and ends at *actual* gate arrival. The relevant measured quantity is `CRSElapsedTime + ArrDelay` over operated flights. My re-computation (§6):
   - LGA→ORD median **163** (mean 185.8, p90 252); ORD→LGA median **134** (mean 155.6, p90 221).
   - Cancellations 5.25% / 5.06%; diversions 0.35% / 0.67%.
   - The typical (median) value is therefore within 2 min of the scheduled 165 / 136, which supports the proposal. The mean is about 20 min longer and the tail is long. Cancelled flights are not represented at all.
   - BTS taxi-in medians are ORD 19 and LGA 6 min. They are already inside block time, so they must not be added again in E3.
7. **§4.5: E3 components.**
   - The "deplane + walk ≈ 10" is an **assumption**.
   - The 5.25 min car wait is **measured, but only for LGA app rides** (v05). Applying it at ORD is a **proxy**: Chicago trip records have no request timestamps.
   - The Delta 20-min figure is a single-carrier **guarantee**, not an upper bound on typical bag times for United or American, which carry most LGA–ORD flights.
   - E3 = 15 / 25 must stay a labelled `design-constant` (C6), as the draft says.
8. **§4.3: check-in 120 is airline guidance worded as a minimum ("at least 2 hours").** It is neither a measured wait nor a typical value. The dominant LGA–ORD carrier is United (UA 4,665 / 11,611 = 40%), and its page could not be read in either session. The runtime's American Airlines citation could not be re-read today (403). Keep it as guidance under C4.
9. **Header timestamp.** The draft says "11:23 America/New_York", but its file mtime is 07:25 EDT. 11:23 matches **UTC**: Git Bash on this machine has no tz database, so `TZ=America/New_York date` prints UTC. The time should read 07:23 EDT (11:23 UTC). The filename stamp is therefore UTC. I did not rename the file.

No arithmetic errors were found. I re-checked every sum and product in draft §3.2 and §4.6.

## 4. Proposed figures with uncertainty (2025–2026 real-world baseline; none implemented)

| Route (one way) | v02 runtime | Audited proposal | Plausible typical range | Basis class | Needs |
|---|---|---|---|---|---|
| NYC City Hall Park → Yonkers | 35 | **46–47** all hours / **56–57** weekday 07–19 | 40–65 | Model × proxy factor (inference) | C1, C5; Yonkers scene entry |
| Yonkers → NYC | 35 | same | 40–65 | same | C1, C5 |
| NYC → Washington Capitol grounds | 289 | **289** (keep; relabel as model) | ≈230–330 | Model, bracketed by scheduled coaches | C2 |
| Washington → NYC | 286 | **286** (keep; relabel) | ≈230–330 | same | C2 |
| Yonkers ↔ Washington | 306 / 303 | **keep**; relabel | ≈245–345 | Model only; no independent check | C2 |
| NYC → Chicago (LGA → ORD) | 365 | **358 + E3** → 373 (E3 15) / 383 (E3 25); weekday 372 + E3 | median-sum ≈ 355–395 for E3 = 15; delays add about +20 on the mean, and the 90th-percentile flight alone adds about +85 | Measured car legs + scheduled block (validated by a measured median of 163) + guidance + assumption | C3, C4, C5, C6 |
| Chicago → NYC (ORD → LGA) | 338 | **336 + E3** → 351 / 361; weekday 348 + E3 | ≈ 335–375 for E3 = 15; same tail | same | C3, C4, C5, C6 |

The ranges are judgement bands built from the component spreads above. They are not statistical intervals; percentiles of components cannot be summed.

## 5. What could be implemented without a creator choice (each still needs a separate, reviewed runtime change)

1. **Relabel the six car segments' basis text.**
   - Current: "Free-flow routing-model time with no traffic".
   - Proposed: "OSRM routing-model time (car profile: 80% of tagged speed limits, fixed defaults elsewhere; no live traffic). Not free-flow, not measured."
   - This changes text, not minutes. It is verified (S5) and choice-independent.
2. **Flight block minutes under the current LGA ↔ ORD pair: 166 → 165 and 142 → 136.**
   - Same basis as v02 (scheduled `CRSElapsedTime`), but a 12-month median instead of July only.
   - Independently reproduced, and supported by the measured scheduled-departure → actual-arrival medians (163 / 134).
   - It does not depend on C3 *as long as the default pair stays LGA ↔ ORD*. If C3 picks MDW, it is superseded.
3. **Flag the ORD access/egress 54 / 55 as a known routing error** (airside service-road routing, v03 §3) in the segment note.
   - The error itself is choice-independent.
   - The replacement *value* is not: 41 (all hours) vs 45 / 48 (weekday) depends on C5, and taxi-only vs pooled is still open.
4. **Source-note hygiene.**
   - Record S3 and S12 as verified (this supplement).
   - Record that the American and United pages were not re-readable today.

Everything else needs a creator decision: the Yonkers change (C1), any DC arrival allowance (C2), the airport pair (C3), check-in (C4), the time-of-day policy and car-start allowance (C5), and E3 (C6). Nothing here declares the M2 door-to-door route-figures gate implemented.

## 6. Reproduction (outside the repository; nothing committed)

- Script: `%LOCALAPPDATA%\Temp\wb-m2v08d-scripts\bts_audit.py` (stdlib only).
  - Run: `python -I bts_audit.py %LOCALAPPDATA%\Temp\wb-m2v03-bts\dl <out.json>`, using the bundled runtime Python.
  - Output: `%LOCALAPPDATA%\Temp\wb-m2v08d-bts-audit.json`, SHA-256 `546109956ec9de620315ba5b2c46d0af8cd6770c433730354292599914b91de2`.
- Downloads in `%LOCALAPPDATA%\Temp\wb-m2v08d-web\`:
  - the three FHWA UCR PDFs and their `-raw` text;
  - OSRM `car.lua` and `way_handlers.lua`;
  - the TranStats glossary HTML;
  - BxM3 text extracted from the draft's saved PDF.
- Hashes are quoted in §2.
- Row reading for UCR: use `pdftotext -raw`. The `-layout` mode shifts metro names against their values; in the Jul–Sep 2025 PDF it printed "New York, NY" beside another metro's figures (3:17 / 1.18 / 1.73).
