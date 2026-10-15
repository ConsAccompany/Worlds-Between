# Cross-city air route candidates from provisional Shanghai: research packet

Status: **research only, unapproved.** Nothing here selects a playable city, a board placement, or game data. Shanghai (上海) is still a provisional anchor until the user decides. Every route below is a candidate for creator review.

- Rule it serves: `docs/design/rpg-2-star-ocean-the-second_global-earth-map-real-place-travel_rules-v01_20261014-235354-2b5d4d98.md`. Air travel uses a typical door-to-door time that includes airport access and waiting. Road distance and great-circle distance stay in separate columns. Unverified routes show as "pending production".
- Retrieval date for every source: **2026-10-15**.
- How the sources were checked: each source was fetched on 2026-10-15. "Raw HTML" means I downloaded the page and searched its text for the quoted strings. "Fetch summary" means the page was read through a web-fetch tool that returns an extracted summary. Those quotes match the tool output but were not compared character by character against the HTML. Pages I could not fetch are listed in §6.

## 1. Labels used in this packet

| Label | Meaning |
|---|---|
| **SOURCE FACT (official)** | Stated by a government body, airport operator, or airline about its own operations. |
| **SOURCE FACT (secondary)** | Stated by a news outlet or a third party that credits an official source. |
| **INDICATIVE (non-official)** | From an aggregator, schedule tracker, or booking site. Not suitable as evidence for production values. |
| **CALCULATED** | Computed by me from stated inputs. Not reported by any source. |
| **DESIGN ESTIMATE** | An assumption chosen for the game example. Not reported by any source. |

The distance terms are never interchangeable:

- **Road distance**: drivable road kilometres. I did not source any road distance in this pass. See the gaps in §5.
- **Air (great-circle) distance**: CALCULATED with the haversine formula (mean Earth radius 6371.0088 km) from airport reference coordinates in the OurAirports dataset (secondary, community-maintained). It is not the filed flight-path length.
- **Flight block time**: scheduled gate-to-gate time from the published departure and arrival times.
- **Airport access / wait / egress**: time from the city to the airport, time at the airport before departure, and time from the arrival gate to the city. These are always listed separately from block time.

## 2. Candidate summary

| # | Route (both name forms) | Pairing proof | Block time evidence | Great-circle distance (CALCULATED) | Road alternative |
|---|---|---|---|---|---|
| A | 上海虹桥 Shanghai Hongqiao (SHA) → 北京首都 Beijing Capital (PEK) | **Strong**: Shanghai and Beijing government pages (2025) | INDICATIVE only (≈2h10–2h30) | 1,075.7 km (581 nmi) | Exists; road km not sourced |
| B | 上海虹桥 Shanghai Hongqiao (SHA) → 广州白云 Guangzhou Baiyun (CAN) | **Strong**: Guangzhou government English portal (2024) | **Official schedule**: MU5309 09:30→11:55 (2h25), 2024 | 1,175.5 km (635 nmi) | Exists; road km not sourced |
| C | 上海虹桥 Shanghai Hongqiao (SHA) → 东京羽田 Tokyo Haneda (HND), international | **Official airline**: ANA schedule release dated 2026-08-28 | INDICATIVE only (≈3h05) | 1,777.4 km (960 nmi) | **None**: the sea crossing rules out a car |

## 3. Candidate detail

### A. Shanghai → Beijing (上海 → 北京), SHA → PEK "express route" (京沪快线)

**Source facts**

- SOURCE FACT (official). The Shanghai Municipal Government's English portal ran "China Eastern upgrades express air service between Shanghai, Beijing" on 2025-08-06. It says the service runs "between Beijing Capital International Airport and Shanghai Hongqiao International Airport" and was "launched in 2007 under the Civil Aviation Administration of China". It is operated by "Air China, China Eastern, China Southern, Hainan Airlines, and Shanghai Airlines". Flights "depart at least every 30 minutes", with "dedicated check-in, security screening, boarding gate, and baggage claim services at both airports". **The page gives no flight duration or check-in times.** (Fetch summary)
- SOURCE FACT (official). The Beijing Municipal Government's English portal posted on 2025-05-16 about the SHA–PEK express route. A voluntary cross-airline rebooking trial between Air China and China Eastern ran from 2025-05-06 to August 2025. **The page gives no duration or frequency.** (Fetch summary)
- SOURCE FACT (official). The China Eastern page "Check-in Counters and Boarding Gate Closing Time" is undated. For SHA T2 domestic it lists check-in closing 30 min and gate closing 20 min before departure. For PEK T2 it lists check-in closing 30 min and gate closing 20 min. (Fetch summary)
- SOURCE FACT (secondary, credited to "上海机场"). A Guangming Online repost dated 2026-06-26 says that from 6/29 the check-in cutoff for all domestic flights at Hongqiao is within 30 min before departure, including passengers with checked bags. Spring Airlines' cutoff is 25 min. China Eastern, Shanghai Airlines and China United Airlines offer "一刻行", which lets passengers without checked bags finish check-in, security and boarding by 15 min before scheduled departure. https://m.gmw.cn/2026-06/26/content_1304511047.htm (Fetch summary)
- SOURCE FACT (official tourism portal, dated 2021-07-29). Visit Beijing says the Capital Airport Express runs from Terminal 2 to Dongzhimen in 21 minutes. A taxi to the city centre takes 45–60 min. (Fetch summary; the page is 5 years old)
- SOURCE FACT (official airline guide, stale). ANA's Hongqiao airport guide, with notes "As of November 20, 2020", gives Metro Line 10 Hongqiao T2 → East Nanjing Road ≈33 min (T1 → East Nanjing Road ≈31 min). A taxi to the Bund takes about 50 min. (Raw HTML)

**Block time**: INDICATIVE (non-official) only. Flightmapper lists MU5101 SHA→PEK at 2:10, changing to 2:15 from 2026-10-25. Other aggregators show about 2h15–2h30. **I found no official airline or government page that states a SHA→PEK scheduled time.**

**Door-to-door example (DESIGN ESTIMATE, not source-reported)**: central Shanghai (near East Nanjing Road) to central Beijing (near Dongzhimen), carry-on only, daytime.

| Segment | Minutes | Basis |
|---|---|---|
| Door → Line 10 station | 10 | DESIGN ESTIMATE |
| Line 10 East Nanjing Rd → Hongqiao T2 | 33 | SOURCE FACT (ANA, 2020) |
| Airport buffer before departure | 60 | DESIGN ESTIMATE. The source cutoff is 30 min and the gate closes at 20 min; the buffer adds security and walking margin. |
| Flight block SHA→PEK | 140 | DESIGN ESTIMATE, midpoint of the INDICATIVE 2h10–2h30 range |
| PEK T2 deplane → Airport Express platform | 20 | DESIGN ESTIMATE |
| Airport Express T2 → Dongzhimen, including headway wait | 31 | 21 SOURCE FACT (Visit Beijing 2021) + 10 DESIGN ESTIMATE wait |
| Dongzhimen → door | 10 | DESIGN ESTIMATE |
| **Total** | **304 (≈5h04)** | CALCULATED |

Sensitivity (CALCULATED): with a 45-min buffer and a 2h10 block, the total is about 4h40. With taxis at both ends in traffic (about 60 min each way, per the source ranges) and a 2h30 block, it is about 6h. A reasonable game value is **≈5h**. It must be labelled as an estimate.

**Missing for production**: an official scheduled SHA→PEK block time from an airline timetable or press release; current Line 10 and Airport Express times from the operators; a sourced road distance if the game also offers a car option (Shanghai to Beijing by road is a long, multi-day-feeling drive and needs its own source); and a decision on whether Beijing is a city the game will have at all.

### B. Shanghai → Guangzhou (上海 → 广州), SHA → CAN (东航"沪广快线")

**Source facts**

- SOURCE FACT (official government portal). The Guangzhou Municipal Government English portal (GDToday content, updated 2024-06-14) published "China's homegrown C919 jetliner to fly on 4th regular route between Guangzhou and Shanghai". From 2024-06-14, China Eastern MU5309 **departs Shanghai Hongqiao 9:30 and lands at Guangzhou Baiyun 11:55**. The return, MU5316, leaves Guangzhou at 13:30 and arrives in Shanghai at 16:00. The route runs "36 round-trip flights daily". (Fetch summary)
- SOURCE FACT (secondary, crediting China Eastern). Beijing Business Today, Yangcheng Evening News and The Paper (2024-06-14) report the same times and describe "沪广快线" as about one flight per hour, every half hour at peak. I could not open these pages directly (403); see §6.
- SOURCE FACT (official). The China Eastern cutoff table lists Guangzhou Baiyun with check-in closing 40 min and gate closing 15 min. The SHA T2 values are as in A. (Fetch summary)
- SOURCE FACT (official airline guide, stale). ANA's Guangzhou airport guide, with notes "As of November 20, 2020", gives Metro Line 3 Airport South (T1) → Tiyu Xilu ≈40 min and Airport North (T2) → Tiyu Xilu ≈42 min, with trains every 5–7 min. A taxi downtown takes 40–50 min. (Raw HTML)

**Block time**: CALCULATED from the official published schedule. 09:30 → 11:55, both China Standard Time, is **145 min**. This is the 2024 launch schedule; I did not confirm the 2026 timetable. That date limit must stay with the value.

**Door-to-door example (DESIGN ESTIMATE)**: central Shanghai (near East Nanjing Road) to central Guangzhou (near Tiyu Xilu), carry-on only.

| Segment | Minutes | Basis |
|---|---|---|
| Door → Line 10 station | 10 | DESIGN ESTIMATE |
| Line 10 East Nanjing Rd → Hongqiao T2 | 33 | SOURCE FACT (ANA, 2020) |
| Airport buffer before departure | 60 | DESIGN ESTIMATE |
| Flight block SHA→CAN | 145 | CALCULATED from the official 2024 schedule |
| CAN deplane → Line 3 platform | 20 | DESIGN ESTIMATE |
| Line 3 → Tiyu Xilu, including headway wait | 47 | 42 SOURCE FACT (ANA 2020, T2 worst case) + 5 DESIGN ESTIMATE wait |
| Tiyu Xilu → door | 10 | DESIGN ESTIMATE |
| **Total** | **325 (≈5h25)** | CALCULATED |

Sensitivity (CALCULATED): with a 45-min buffer and Airport South (T1), about 5h05. With taxis in traffic at both ends, about 6h. A reasonable game value is **≈5h30**, labelled as an estimate.

**Missing for production**: confirmation that the 2026 schedule still shows a similar block time; which Baiyun terminal China Eastern uses now (it changes the 40 vs 42 min metro figure); current Guangzhou Metro times from the operator; a sourced road distance if a car option is offered.

### C. Shanghai → Tokyo (上海 → 東京), SHA → HND, international

**Source facts**

- SOURCE FACT (official airline). ANA HOLDINGS published "El Grupo ANA anuncia la revisión de su programa de vuelos para la segunda mitad del AF2026" (Mexico City, 2026-08-28). For the period "a partir del 25 de octubre de 2026" it lists **Haneda = Shanghái Hongqiao, NH 969/970, 7 round trips per week** in both the current and the revised plan. **It gives no times or duration.** (Raw HTML; Spanish-language edition; the English edition did not load, see §6)
- SOURCE FACT (official). The China Eastern cutoff table lists international check-in closing 40 min and gate closing 20 min at SHA T1. (Fetch summary)
- SOURCE FACT (official airline, 2019). ANA's press release of 2019-08-20 moved the check-in cutoff for ANA international flights from Haneda from 40 to 60 min before departure, effective 2019-10-27. Note that this is the cutoff for departures **from** Haneda, so it applies to the return trip. (Raw HTML)
- SOURCE FACT (official airline guide, stale). ANA's Hongqiao guide gives Line 10 East Nanjing Road ↔ Hongqiao T1 ≈31 min. (Raw HTML)
- SOURCE FACT (secondary). GLTJP, a travel guide that says the operator supervised it, gives the Tokyo Monorail Haneda Express from Terminal 3 to Hamamatsucho as "as little as 13 minutes". I did not reach the operator's own site.

**Block time**: INDICATIVE (non-official) only. Trip.com shows JL082 SHA 12:45 (CST) → HND 16:50 (JST). JST is CST+1h, so the CALCULATED block time is ≈185 min. **I found no official page that states a SHA→HND scheduled time.** The JAL press page that might have one returned 403.

**Door-to-door example (DESIGN ESTIMATE)**: central Shanghai to central Tokyo (Hamamatsucho), carry-on only.

| Segment | Minutes | Basis |
|---|---|---|
| Door → Line 10 station | 10 | DESIGN ESTIMATE |
| Line 10 East Nanjing Rd → Hongqiao T1 | 31 | SOURCE FACT (ANA, 2020) |
| Airport buffer before departure, international, including exit formalities | 120 | DESIGN ESTIMATE. The source cutoff is 40 min; exit immigration time is not sourced. |
| Flight block SHA→HND | 185 | INDICATIVE, CALCULATED with the time-zone correction |
| HND T3 entry immigration + customs + walk | 45 | DESIGN ESTIMATE, not sourced |
| Monorail T3 → Hamamatsucho, including wait | 18 | 13 SOURCE FACT (secondary) + 5 DESIGN ESTIMATE |
| Hamamatsucho → door | 10 | DESIGN ESTIMATE |
| **Total elapsed** | **419 (≈7h)** | CALCULATED |

Elapsed time is about 7h, but local clock time advances about 8h because of the +1h zone change. The game would need to decide whether its single timeline ignores time zones. That decision is not covered by the current rule.

**Missing for production**: an official SHA→HND scheduled time; sourced exit and entry processing times; a time-zone policy; and the fact that this is the only candidate that crosses a border. Passports and visas are a story and design question, not a travel-time question. This candidate does test the rule that a car cannot cross the sea.

## 4. Recommendations (pending creator review; nothing is selected)

- **Test-only fixture: Candidate B, SHA → CAN.** It has the most complete source chain: official proof of the pairing, an **official published schedule** that gives a 145-min block time, an official airline cutoff table, and airline-published metro access times. A fixture can use `block_minutes = 145` with source and date fields, and keep the airport access and buffer values as named DESIGN ESTIMATE fields. That checks the data contract (separate segments, provenance, `verified_on`) without implying that Guangzhou is a playable city. Mark the fixture ID clearly as test-only. The 2024 schedule date stays attached to the value.
- **Possible later playable route: Candidate A, Shanghai → Beijing (SHA → PEK).** It has the strongest official proof that the pairing exists (two municipal governments, five carriers, departures at least every 30 min). It is China's flagship domestic air corridor, and the express-route framing fits a "frequent, reliable flight" travel option. Before it can be playable it needs an official block time, a creator decision on Beijing as a city, and current access times.
- **Not recommended yet: C (Tokyo).** It is interesting for the sea-crossing rule and for Tokyo as an alternative first city in the rules doc. But it has no official block time, needs a time-zone policy, and depends on a border-crossing story decision.

## 5. Gaps and uncertainty

1. **No official block time for A or C.** Only aggregators (Flightmapper, Trip.com, Skyscanner) give values, and they are recorded as INDICATIVE. Next step: an airline timetable page or PDF (China Eastern, Air China, JAL or ANA) that can be fetched and saved.
2. **Road distances are not sourced** for A and B. I did not use an official map provider, and I did not substitute a great-circle distance. Next step: an Amap or Baidu route query, or a provincial transport-department figure, with the retrieval date recorded.
3. **Access times are stale.** The ANA guides are marked "As of November 20, 2020", and Visit Beijing is dated 2021. Operators (Shanghai Metro, Beijing Subway, Guangzhou Metro, Tokyo Monorail) were not reached directly.
4. **The China Eastern cutoff table is undated.** Its SHA domestic value of 30 min matches the 2026-06-29 Hongqiao change. Bridge and remote-stand gate times "may differ", according to the page.
5. **Airport buffer, deplane and immigration times are design assumptions.** No source gives a "typical" passenger arrival time before departure.
6. **The B schedule is from June 2024.** The 2026 timetable was not confirmed.
7. Airport coordinates come from OurAirports, which is community-maintained. That is good enough for great-circle reference; production would cross-check against the AIP or the airport operator.

## 6. Source manifest

| ID | Publisher (type) | Title / content | URL | Pub. date | Retrieved | Check method |
|---|---|---|---|---|---|---|
| S1 | Shanghai Municipal Gov. (official) | China Eastern upgrades express air service between Shanghai, Beijing | https://english.shanghai.gov.cn/en-Latest-WhatsNew/20250806/12f6997fdc464e028541cb3ec15191e9.html | 2025-08-06 | 2026-10-15 | Fetch summary |
| S2 | Beijing Municipal Gov. (official) | Voluntary cross-airline rebooking, SHA–PEK express route | https://english.beijing.gov.cn/latest/news/202505/t20250516_4090416.html | 2025-05-16 | 2026-10-15 | Fetch summary |
| S3 | China Eastern Airlines (official) | Check-in Counters and Boarding Gate Closing Time | https://global.ceair.com/global/en_static/Announcement/TravelTips/CheckinCountersandBoardingGateClosingTime/ | undated | 2026-10-15 | Fetch summary |
| S4 | Guangzhou Municipal Gov. English portal / GDToday (official) | China's homegrown C919 jetliner to fly on 4th regular route between Guangzhou and Shanghai | https://www.gz.gov.cn/guangzhouinternational/home/citynews/content/post_9704309.html | 2024-06-14 | 2026-10-15 | Fetch summary |
| S5 | Guangming Online repost of 新闻晨报 / 上海机场 (secondary) | 6月29日起，虹桥机场所有国内航班截载时间缩短 | https://m.gmw.cn/2026-06/26/content_1304511047.htm | 2026-06-26 | 2026-10-15 | Fetch summary |
| S6 | ANA (official airline guide) | Shanghai Hongqiao International Airport – Airport and City Info | https://www.ana.co.jp/en/eur/travel-information/airport-and-city-info/shanghai-hongqiao/ | notes "As of 2020-11-20" | 2026-10-15 | Raw HTML |
| S7 | ANA (official airline guide) | Guangzhou Baiyun International Airport – Airport and City Info | https://www.ana.co.jp/en/eur/travel-information/airport-and-city-info/guangzhou/ | notes "As of 2020-11-20" | 2026-10-15 | Raw HTML |
| S8 | Visit Beijing (official tourism portal) | Transportation of Beijing Capital International Airport | https://english.visitbeijing.com.cn/article/47OLi94T30q | 2021-07-29 | 2026-10-15 | Fetch summary |
| S9 | ANA HOLDINGS (official) | El Grupo ANA anuncia la revisión de su programa de vuelos para la segunda mitad del AF2026 | https://www.ana.co.jp/es/mx/the-ana-experience/corp_info/pr20260818/ | 2026-08-28 | 2026-10-15 | Raw HTML |
| S10 | ANA (official) | Change in Check-in Cut-off Time for Haneda International Airport… | https://www.ana.co.jp/group/en/pr/201908/20190820.html | 2019-08-20 | 2026-10-15 | Raw HTML |
| S11 | GLTJP (secondary, operator-supervised) | Tokyo Monorail guide | https://www.gltjp.com/en/article/item/21122 | undated | 2026-10-15 | Search-result excerpt only |
| S12 | OurAirports (secondary dataset) | airports.csv: ZSSS, ZBAA, ZGGG, RJTT coordinates | https://davidmegginson.github.io/ourairports-data/airports.csv | rolling | 2026-10-15 | Raw file |
| I1 | Flightmapper (INDICATIVE) | MU5101 SHA→PEK schedule | https://info.flightmapper.net/flight/China_Eastern_MU_5101 | rolling | 2026-10-15 | Search-result excerpt only |
| I2 | Trip.com (INDICATIVE) | JL082 status | https://www.trip.com/flights/status-jl082/ | rolling | 2026-10-15 | Search-result excerpt only |

Coordinates used (S12): SHA 31.198104, 121.33426 · PEK 40.077349, 116.596702 · CAN 23.392401, 113.299004 · HND 35.549678, 139.786958.

**Could not fetch, so not used as evidence:** JAL press release https://press.jal.co.jp/en/release/202608/009673.html (403); the JAL FY2026 international schedule PDF on press.jal.co.jp (403); Beijing Business Today pages https://www.bbtnews.com.cn/2024/0614/518287.shtml and https://www.bbtnews.com.cn/2026/0707/598422.shtml (403); ANA's English check-in page (its static HTML did not show the cutoff table). I did not use Wikipedia for any route claim.

## 7. Decisions for the creator

1. Confirm or replace Shanghai as the science-region anchor. Everything here depends on it.
2. Choose whether the first air-mode verification uses a test-only fixture (B recommended) before any playable destination exists.
3. Choose whether a second Earth city (Beijing, Guangzhou, or another) is wanted. Picking a route also picks a city.
4. Set the time-zone policy before any international route.
5. Approve the default airport buffer (60 min domestic / 120 min international in these examples), or ask for a sourced alternative.
