# Shanghai / Songjiang / Liangzhu coordinates, road times, door-to-door method, and one Shanghai → Guangzhou air route: research QA note

Status: **research only, unapproved.** This pass changed no game code or data, no Game Bible, no progress file and no Git state. It checks the provisional values in `game/data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-provisional-v01_20261015-024215-b876e53d.json` (the "game data" below) against primary or reproducible sources. It is not legal advice.

- **Auth check:** `claude auth status` on 2026-10-15 returned `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. `ANTHROPIC_API_KEY` is unset. No paid service was used.
- **Tools:** WebSearch and WebFetch were available. Where WebFetch got HTTP 403 (UNESCO), I downloaded the page with `curl` and searched the HTML. I used the free public OSRM demo router for road routes, at under 1 request per second. I did **not** use Amap or Baidu Maps, because both need a developer account and key.
- **Access date** for every URL below: **2026-10-15**.
- **Labels:** **PRIMARY** means an official publisher stating its own data. **REPRODUCIBLE** means an open-data computation anyone can re-run. **INDICATIVE** means an aggregator or tracker. **CALCULATED** means my arithmetic from the stated inputs. **DESIGN ESTIMATE** means no source reports the value.

## 1. Coordinates

| Location (game ID) | Game value | Checked against | Result |
|---|---|---|---|
| `earth.cn.shanghai` | 31.22222, 121.45806 | PRIMARY dataset: GeoNames 1796236 "Shanghai", PPLA, 31.22222, 121.45806 (31°13′19.99″N 121°27′29.02″E). https://www.geonames.org/1796236 | **Exact match.** It is a city reference point, not a door. OSRM snaps it to 长乐路169弄, 48 m away. |
| `earth.cn.shanghai.songjiang-outskirts` | 31.00583, 121.23333 (source: Wikipedia) | GeoNames 1794035 "Songjiang", seat of a third-order division, **31.034427, 121.223256**. GeoNames 1794034 "Songjiang Qu" (ADM3), N31°1′15″ E121°12′40″. https://www.geonames.org/search.html?q=Songjiang&country=CN | **Does not match a source of known terms.** The game point is 3.3 km (CALCULATED, haversine) south of GeoNames 1794035. The district government page gives "121°45' East Longitude and 31° North Latitude" (https://english.songjiang.gov.cn/facts/location/). That longitude falls east of central Shanghai, so it is still unusable. |
| `earth.cn.liangzhu-ruins` | 30.39556, 119.99083 | PRIMARY: UNESCO WHC 1592 component table, "1592-004 Area of City Site N30 23 43.97 E119 59 26.97", 881.45 ha. https://whc.unesco.org/en/list/1592/maps/ (downloaded with curl, HTTP 200). | **Matches** 30.395547, 119.990825 to within 2 m. The other components are Yaoshan N30 25 33.99 E120 0 42.99, High-dam N30 25 13 E119 54 12.98, and Low-dam N30 24 12.89 E119 56 58.38. |

**Liangzhu visitor access is a different point from the UNESCO centroid.** Hangzhou.com.cn (Hangzhou's news portal, reposting 钱江晚报, 2019-07-05) gives the park's opening arrangements: "在南大门入园", sightseeing shuttles inside the park, and bus 1222M from Liangzhu metro station. https://hznews.hangzhou.com.cn/chengshi/content/2019-07/05/content_7222190_0.htm. A search result also places the park "凤都路与104国道交叉口西北". I did not find an official current visitor-centre coordinate, and the 2019 arrangements may be outdated.

**Reuse terms.** GeoNames is CC BY 4.0, as already recorded. I found no reuse terms covering UNESCO coordinates: https://whc.unesco.org/en/disclaimer/ covers images, and `/en/terms-of-use/` returned 404. Keep `licenseStatus` flagged, but cite UNESCO directly instead of Wikipedia.

## 2. Road distances and times (point-to-point, free-flow)

OSRM demo (https://router.project-osrm.org, `route/v1/driving`, queried 2026-10-15) is REPRODUCIBLE. It routes over OpenStreetMap data and models no live traffic. Its usage policy (https://github.com/Project-OSRM/osrm-backend/wiki/Demo-server) says: "restricted to reasonable, non-commercial use-cases" and "no guarantees wrt. … data updates". A shipped game would need its own OSRM run on OSM data, with ODbL attribution. I did not re-check the OSM licence page in this pass.

| Segment | Game value (Rome2Rio) | OSRM forward | OSRM reverse | Great-circle (CALCULATED) |
|---|---|---|---|---|
| Shanghai (GeoNames) → Songjiang (GeoNames 1794035) | 34.8 km / 26 min | 34.75 km / **30.8 min** | 35.52 km / 30.9 min | 30.6 km |
| Shanghai → Songjiang (current game point) | same | 36.32 km / 32.3 min | not run | 32.2 km |
| Shanghai → Liangzhu City Site (UNESCO) | 187.9 km / 120 min | 187.89 km / **134.6 min** | 189.17 km / 135.0 min | 167.6 km |
| Songjiang (GeoNames) → Liangzhu, **direct** | none (status `unverified`) | 155.95 km / **108.6 min** | not run | not computed |

Findings:

1. The game's distances agree with OSRM to 0.1 km. My inference is that Rome2Rio and OSRM both route over OSM data, so this is **not independent corroboration**. Rome2Rio's times are 5–15 min shorter than OSRM's. Both are free-flow, point-to-point values.
2. The current "via Shanghai" Songjiang → Liangzhu itinerary is 222.7 km and 146 min on game values. OSRM's direct road is about 156 km and 109 min. The detour is real, but the direct road now has a reproducible source if the user accepts OSRM.
3. **No traffic-aware source was found.** I found no published Shanghai congestion index (Amap reports): the search turned up only other cities. TomTom's Shanghai page returned 404. Amap and Baidu routing needs a key. Any peak-hour multiplier is therefore a DESIGN ESTIMATE until a source is chosen.
4. Reverse legs differ by under 1.3 km and 0.5 min. Keeping `assumed-symmetric` is defensible, labelled "OSRM reverse within 1 %".

## 3. Door-to-door method

Use the phase chain from the EU H2020 DATASET2050 project (grant 640353, 2014-12-01 to 2017-11-30, https://cordis.europa.eu/project/id/640353). D4.1 "Current Supply Profile" (Hullah, Kirby, Ureta, Cook, Tanner, Graham, Rothfeld and Paul, 2016) defines "Door" to "Kerb" as running "from leaving the place of origin … to the point of arrival at the airport". "Kerb" to "Gate" runs to "the boarding card scanned immediately prior to embarkation". It notes that "in principle, symmetric processes" such as Door-to-Kerb and Kerb-to-Door are asymmetric (https://westminsterresearch.westminster.ac.uk/item/q2w3v/dataset2050-d4-1-current-supply-profile). The D5.3 deliverable restates the Flightpath 2050 target: "90% of European passengers to complete their door-to-door journey within four hours" (https://www.bauhaus-luftfahrt.net/fileadmin/user_upload/Publikationen/2017_Paul_Kluge_Assessing_Passenger_Requirements_O.pdf, dated 11/12/2017).

Proposed rule, which keeps the existing data fields:

- **Car:** D2D = origin access (scene exit to car) + `referenceDurationMinutes` (point-to-point route) × traffic factor + egress (parking to the scene entrance, for example Liangzhu's south gate and the in-park shuttle). Only the route term is sourced today. Access, egress and traffic factor go into `doorToDoorAllowanceMinutes` with a DESIGN ESTIMATE label until they are sourced.
- **Air:** D2D = Door→Kerb (`airportAccessMinutes`) + Kerb→Gate (`checkInAndWaitMinutes`) + Gate→Gate (`flightMinutes`, published block time) + Gate→Kerb + Kerb→Door (`airportEgressMinutes`). Record each phase in each direction, because the phases are asymmetric.
- Every term carries a source, a date and one of the labels above. A point-to-point figure must never be shown as door-to-door.

## 4. One plausible air route: Shanghai Hongqiao (SHA) → Guangzhou Baiyun (CAN)

| Item | Value | Basis |
|---|---|---|
| Pairing and frequency, **historical** | MU5309 "take off from Shanghai Hongqiao … at 9:30", "land at Guangzhou Baiyun … at 11:55"; "36 flights (round trip)" daily | PRIMARY, Guangzhou government English portal, updated 2024-06-14. https://www.gz.gov.cn/guangzhouinternational/home/citynews/content/post_9704309.html |
| Schedule, **live 2026** | MU5309 10:00 → 12:25 CST, listed for 13, 15 and 16 Oct 2026 | INDICATIVE, Planemapper. https://www.planemapper.com/flights/MU5309. Not airline-confirmed. A search excerpt from Airpaz (https://www.airpaz.com/en/flight/code/MU-5309) shows the same times for Aug 2026. |
| Block time | **145 min** in both cases | CALCULATED. The 2024 official schedule and the 2026 indicative schedule agree. |
| Season | The summer-autumn schedule started 2026-03-29. I did not find the 2026/27 winter-spring start date or an MU5309 timetable for it. | Secondary repost (pedaily, 2026-03-25). https://news.pedaily.cn/20260325/126238.shtml |
| Hongqiao cutoff | "6月29日起 … 所有国内航班 … 截载时间缩短至起飞前30分钟内" | Secondary repost credited to 上海机场 (Guangming, 2026-06-26). https://m.gmw.cn/2026-06/26/content_1304511047.htm |
| China Eastern cutoffs | SHA T2: check-in 30 / gate 20 min. CAN: 40 / 15 min. | PRIMARY, but undated. https://global.ceair.com/global/en_static/Announcement/TravelTips/CheckinCountersandBoardingGateClosingTime/ |
| City → SHA | Line 10 East Nanjing Rd ↔ Hongqiao T2 "Approx. 33 minutes" (T1: 31) | Official airline guide, "As of November 20, 2020", re-fetched. https://www.ana.co.jp/en/eur/travel-information/airport-and-city-info/shanghai-hongqiao/ |
| CAN → city | **The earlier packet's Line 3 Airport South/North → Tiyu Xilu times (40/42 min) are out of date.** T3 opened 2025-10-30 (https://cn.chinadaily.com.cn/a/202510/30/WS6902d7e8a310c4deea5ef07f.html). From 2026-05-07 all 11 domestic carriers at T1 moved to T3. The Airport South metro station is "暂时无法通行". Metro access to T3 is Line 3/9 to 高增站 exit B, then the 空港2线支线 feeder bus, "大约15分钟" (about 12 min on the return). | PRIMARY, Guangzhou government, 2026-05-04. https://www.gz.gov.cn/zwfw/zxfw/jtfw/content/post_10798042.html. A search excerpt (ycwb) says China Eastern domestic flights moved to T3 on 2025-10-31; I could not open that page. The Gaozeng → city-centre metro time is **not sourced**. |
| Great-circle | 1,175.5 km | CALCULATED from the OurAirports coordinates in the earlier air packet. |

Door-to-door example, central Shanghai → central Guangzhou, carry-on only. This is a DESIGN ESTIMATE, not a source value:

| Phase | Minutes | Basis |
|---|---|---|
| Door → station | 10 | DESIGN ESTIMATE |
| Line 10 → SHA T2 | 33 | 2020 airline guide |
| Kerb → Gate buffer | 60 | DESIGN ESTIMATE (the sourced cutoff is 30 min) |
| Gate → Gate | 145 | Official 2024 schedule, matched by the 2026 indicative schedule |
| Deplane → T3 feeder-bus stop | 20 | DESIGN ESTIMATE |
| Feeder bus T3 → Gaozeng | 15 | Official, 2026 |
| Transfer wait | 10 | DESIGN ESTIMATE |
| Gaozeng → destination | **unsourced** | Gap |
| **Subtotal before the last leg** | **293** | CALCULATED |

I am not giving a door-to-door total until the Gaozeng → city-centre leg has a source.

## 5. Recommendations

**Can stay provisional:**

- The Shanghai coordinate. It matches GeoNames exactly, under CC BY 4.0.
- The Liangzhu coordinate **value**. It matches UNESCO 1592-004.
- `roadDistanceKm` 34.8 and 187.9. OSRM reproduces both, with the shared-OSM caveat in §2.
- `reverseBasis` symmetric, as long as it is relabelled with the OSRM reverse check.

**Must change before release (the data edits are for the owning workstream; I made none):**

1. Songjiang `coordinateSource`. The Wikipedia licence is a blocker. Switch to GeoNames 1794035 (31.034427, 121.223256), which moves the point about 3.3 km. Alternatively, keep the current point with a different source of known terms.
2. Liangzhu `coordinateSource`. Cite the UNESCO component table directly (https://whc.unesco.org/en/list/1592/maps/) instead of Wikipedia. Its reuse terms are still unestablished.
3. `referenceDurationMinutes` 26 and 120. They are free-flow and come from a source whose terms were not reviewed. If the user accepts OSRM, replace them with OSRM values (31 and 135) under that source. In either case, the game must not present 26/120 + 0 allowance as the "typical door-to-door" time that rule 5 requires. `doorToDoorAllowanceMinutes` must become a labelled, non-zero estimate.
4. Air fixture inputs. Do not use the ANA 2020 Baiyun metro times. Use T3 egress, sourced as in §4.

**Decisions only the user can make:**

1. Confirm Shanghai as the anchor. Then choose the three "doors": the Shanghai departure point, the Songjiang scene entry, and the Liangzhu entry (the UNESCO City Site centroid or the park's south gate).
2. Choose the route-time source. Options: OSRM/OSM (free and reproducible; needs self-hosting and ODbL attribution to ship), Rome2Rio (terms unreviewed), or an Amap/Baidu developer key (account required; not used here).
3. Choose a traffic policy: free-flow, or a fixed peak multiplier. No sourced multiplier exists yet.
4. Approve the allowance estimates: car access/egress, and the 60-min domestic air buffer.
5. Decide whether Guangzhou is a test-only air fixture or a playable city.
6. Decide whether to offer the Songjiang → Liangzhu direct road from OSRM (about 156 km / 109 min) alongside the via-Shanghai detour.
