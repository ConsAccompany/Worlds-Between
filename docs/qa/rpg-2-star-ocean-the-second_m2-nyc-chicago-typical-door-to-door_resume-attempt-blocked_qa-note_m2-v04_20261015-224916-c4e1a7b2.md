# M2 NYC–Chicago typical door-to-door route figures: resume attempt (QA note, NONRUNTIME, BLOCKED)

- Date: 2026-10-15 22:49 America/New_York.
- Dispatch: Workstream C of `docs/coordination/rpg-2-star-ocean-the-second_post-quota_three-workstream-dispatch-prep_unapproved-v01_20261015-223416-8b4cd70e.md`.
- Builds on:
  - `docs/qa/rpg-2-star-ocean-the-second_m2-us-science-route-figures_real-world-travel-audit_qa-note_m2-v02_20261015-195053-10d2525c.md` (v02 audit, policy §6)
  - `docs/qa/rpg-2-star-ocean-the-second_m2-nyc-chicago-airport-curb-endpoints_v03-candidate_qa-note_m2-v03_20261015-200518-7c3e19a4.md` and its candidate JSON `…_nyc-chicago-airport-curbs_m2-us-science-v03-candidate-nonruntime_20261015-200518-7c3e19a4.json`
- `AGENTS.md` was requested but **does not exist** in the repository (Read and Glob both found nothing).
- **Not changed:** active game travel data, scripts, the builder, the Game Bible, Washington and battle files, `docs/progress.md`, the v03 candidate, Git. This note is the only file added. No commit or push.
- **M2 door-to-door route-figures gate: stays OPEN.**

## 1. Outcome

No new real-world evidence could be retrieved in this session. Every external request path was auto-denied by the session's permission layer, which has no approval surface:

| Attempt | Purpose | Result |
|---|---|---|
| `WebFetch` City of Chicago open-data SODA query (O'Hare → Loop taxi trips) | typical ORD ↔ Loop car time | denied before any request was sent |
| `WebSearch` | locate datasets and arrival-side sources | denied before any request was sent |
| `node -e "fetch(...)"` | same SODA query, raw JSON | denied before any request was sent |
| local Python (`python -I`) and `node -e` computation | offline checks | denied; `node --version` and `date` only |

No request left the machine, so no personal identifier was sent anywhere. No paid service, API credit or fallback was used or attempted.

Because nothing new was sourced, **no new candidate JSON was written.** A v04 file would only copy v03's figures and would suggest progress that did not happen. The v03 candidate stays the latest proposal. v02 stays active in the runtime.

## 2. Offline validation of the v03 candidate (hand-computed from its stored raw values)

Scripted tests could not run, so I re-derived the figures by hand from the stored `timeSeconds` and BTS values. No network was needed.

### 2.1 Totals

| Segment | access (s → min) | check-in | flight | egress (s → min) | rounded sum | raw sum | stored |
|---|---|---|---|---|---|---|---|
| NYC → CHI (UA, LGA B → ORD T1) | 1241.868 → 20.698 → **21** | 120 | 165 | 1407.008 → 23.450 → **23** | **329** | 329.148 | 329 / 329.1 ✔ |
| CHI → NYC (UA, ORD T1 → LGA B) | 1429.420 → 23.824 → **24** | 120 | 136 | 1115.726 → 18.595 → **19** | **299** | 298.419 | 299 / 298.4 ✔ |

### 2.2 Reverse-route validation

- Each direction uses its own one-way query. The access leg ends on the **departures** way and the egress leg starts on the **arrivals** way. The candidate's `departureCurb`/`arrivalCurb` fields match the leg `to`/`from` fields in both segments ✔.
- The reverse legs are not mirrors, and should not be. LGA is 19.3 km out and 18.2 km back; ORD is 30.3 km out and 30.5 km back. These are different stacked roadways and one-way loops.
- The flight median is direction-specific: LGA→ORD 165, ORD→LGA 136. Westbound is 29 min longer, which matches the 25–30 min westerly asymmetry in every month of the v02 audit ✔.
- The monthly `n` values sum to the pooled n in both directions. LGA→ORD: 973+972+1025+976+910+951+883+996+963+997+968+997 = **11,611**. ORD→LGA: 973+972+1025+977+906+955+884+996+962+996+968+997 = **11,611** ✔.
- The carrier rows sum to the pooled n: 4665+2961+2306+1288+299+92 = 11,611 ✔.

### 2.3 Sensitivity rows

| Variant | NYC→CHI | CHI→NYC | stored |
|---|---|---|---|
| AA (LGA B, ORD T3: 24.45→24, 22.63→23) | 21+120+165+23 = 329 | 24+120+136+19 = 299 | ✔ |
| DL (LGA C 21.01→21 / 19.10→19, ORD T5 24.77→25 / 22.17→22) | 21+120+165+22 = 328 | 25+120+136+19 = 300 | ✔ |

**Validation result: all v03 arithmetic reproduces.** This confirms only internal consistency. It does not make free-flow car time "typical".

## 3. What still blocks the gate (exact missing evidence)

| # | Component | Current v03 basis | Why it fails rule 5 ("typical door-to-door") | Evidence needed |
|---|---|---|---|---|
| E1 | City Hall Park ↔ LGA B car legs (21 / 19) | Valhalla free-flow | No traffic. PANYNJ 2023 report: Times Square → LGA annual average 31 → 35 min (2014→2019). That trip is shorter than City Hall Park → LGA, so typical time is clearly above 21. | A measured median trip time for this zone pair from a primary dataset (§4 P1). |
| E2 | Loop ↔ ORD T1 car legs (24 / 23) | Valhalla free-flow | No traffic. CTA rail is 40–45 min; typical driving time is unmeasured. | Measured median for O'Hare ↔ Loop (§4 P2). |
| E3 | Arrival side: deplane, walk to curb, optional bags, car or taxi wait | `doorToDoorAllowanceMinutes = 0`, flagged unsourced | 0 is known to be too short. | A primary source for a typical value, or a creator-approved `design-constant` (§4 P3). |
| E4 | Departure-side curb dwell and walk to check-in | inside the 120 min "arrive 2 h before" guidance | Acceptable: the guidance clock starts on arrival at the airport. | None. Keep it, and do not double-count. |
| E5 | Router provenance | Valhalla public instance; terms unverified; OSM not pinned | Release blocker, not a plausibility issue. | Self-hosted router on a dated extract (open item from v02). |
| E6 | Time-of-day policy | none | "Typical" is undefined until the creator picks all-hours, weekday daytime or per-hour. | Creator decision. |

Applying any multiplier now, such as scaling Valhalla by the PANYNJ 31→35 ratio, **would be an arbitrary constant**. It has a different origin, 2019 data and no City Hall figure, so it was not done.

## 4. Pre-registered retrieval plan for the next session (free, primary, no login)

The plan is fixed now so the next session cannot pick a favourable filter after seeing the data. Dataset IDs and zone or area numbers marked *(confirm)* are from memory and must be checked against the source on retrieval.

**P1. NYC TLC Trip Record Data** (NYC Taxi & Limousine Commission; free monthly Parquet; https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- Use Yellow and High-Volume FHV, the latest 12 released months.
- Zones: LaGuardia = LocationID 138 *(confirm in `taxi_zone_lookup.csv`)*. For the City Hall Park side, use the zone that contains (40.71205, −74.00708). Find it by point-in-polygon on the TLC/NYC Open Data taxi-zone geometry; do not guess.
- Use both directions separately: PU 138 → DO zone (egress) and PU zone → DO 138 (access).
- Metric: `dropoff_datetime − pickup_datetime`. Drop rows with ≤ 0 or > 180 min, and record how many. Report n, median, p10/p90 and an hour-of-day table. Record the Parquet SHA-256 values.
- Caveat to record: meter-on to meter-off. It excludes the LGA taxi-stand queue and zone-centroid offsets.
- Parquet needs pyarrow or DuckDB. If neither is available offline, stop and do not substitute.

**P2. City of Chicago Taxi Trips and Transportation Network Providers – Trips** (data.cityofchicago.org; anonymous SODA reads are free)
- Areas: `pickup_community_area` 76 = O'Hare, `dropoff_community_area` 32 = Loop *(confirm)*, plus the reverse.
- Use `trip_seconds`, the latest 12 months, n, median, p10/p90 and hour-of-day. Record the dataset ID, query URL and response hash.
- Caveat to record: start times are rounded to 15 min, which does not affect `trip_seconds`. ORD rideshare pickup is at the T2 departure level (CDA directory), which differs from the T1 taxi curb.

**P3. Arrival-side allowance** (in order; stop at the first that gives a typical, dated value)
1. TRB/ACRP free reports on terminal or curbside processing times with measured deplane-to-curb distributions. Quote the table and page.
2. PANYNJ or CDA published taxi or ground-transport wait statistics for LGA B or ORD T1.
3. If neither gives a typical value, a creator-approved value labelled `design-constant` in the data. It must never be presented as research. The creator must also decide whether the traveller has checked bags.

**Combination rule.** Total = car-leg median + 120 + BTS 12-month block median + egress median + arrival allowance. Label it **"sum of component medians"**: it is not the median of a door-to-door total. Keep v03 Valhalla free-flow values beside it as the lower bound. Each P1/P2 median must be ≥ the free-flow value for the same direction; investigate any violation before storing it.

**Reverse-route checks for the next candidate.** Treat access and egress as separate datasets. Explain any direction difference over 10 min. Check monthly n sums and the 12-month window as in v03.

## 5. Gate status

**OPEN.** E1, E2 and E3 lack defensible typical evidence. E5 and E6 are unresolved, and nothing was promoted. Runtime promotion is still a separate, creator-approved task.

## 6. Tests run

- Hand re-derivation of the v03 totals, raw sums, sensitivity rows, n sums and carrier sums (§2): **all match**.
- The scripted `check_v03_candidate.js` (41 checks, v03) was **not re-run**. Running a local interpreter needed approval, and this session could not grant it.
