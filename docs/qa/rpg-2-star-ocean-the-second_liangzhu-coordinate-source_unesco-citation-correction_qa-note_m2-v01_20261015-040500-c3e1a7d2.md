# Liangzhu coordinate source: UNESCO citation correction (M2 QA note)

Recorded 2026-10-15. Status: **source citation corrected; reuse terms still unestablished.** This is a project record, not legal advice.

The change follows recommendation 2 in the [research QA note](../design/rpg-2-star-ocean-the-second_shanghai-songjiang-liangzhu-guangzhou_coordinates-road-air-door-to-door_research-qa-note_unapproved-v01_20261015-033837-7d8308aa.md). It cites the UNESCO component table directly for `earth.cn.liangzhu-ruins`, instead of Wikipedia's copy of it.

**Auth:** `claude auth status` returned `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. No `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, Bedrock or Vertex variable was set.

## What changed

| File | Change |
|---|---|
| `game/data/world-travel/…locations-routes_m2-provisional-v01_…b876e53d.json` | Source `wikipedia-liangzhu-unesco-1592` is replaced by `unesco-whc-1592`, which lists the old ID under `supersedesSourceIds`. The Liangzhu `coordinateSource` now cites the UNESCO table URL, row 1592-004, and the DMS value. |
| `docs/attribution/…attribution-manifest_m2-v01_…916697a2.json` | Same source replacement. The item now records `recordUrl`, `component` and `sourceValue`. |
| `docs/attribution/…attribution_m2-v01_…efe7f67d.md` | The Liangzhu row, a note on the change, and open item 1 are updated. |
| `tools/…geodata-attribution_validation-test_m2-v01_…678bd5f4.js` | Changes are listed under "Test changes" below. |

## What did not change

Coordinates, scene IDs, segment figures, route legs and statuses, `pendingRouteRequests`, the calendar, and `startLocationId` are all unchanged. The proof is a SHA-256 of the travel JSON with `attribution` and every `coordinateSource` removed. It is `ad076e0127b0e55d565f4ccd9faae0ea5d4c091b78d8522368fba0cfbbc8a039` both before and after the edit. The existing test pins also still pass.

- Songjiang keeps its value and source. It is still `wikipedia-songjiang-district`, provisional, and must be replaced or verified.
- Both car segments keep Rome2Rio as the source, with status `preliminary-estimate` (estimate only).
- No user-pending anchor, door, route-time source or traffic decision was touched.

## Source check (2026-10-15)

- **Table:** https://whc.unesco.org/en/list/1592/maps/. WebFetch and curl's default user agent got HTTP 403. curl with a browser user agent got HTTP 200. Row: `1592-004`, "Area of City Site", `N30 23 43.97 E119 59 26.97`, 881.45 ha. That converts to 30.395547, 119.990825. The stored value 30.39556, 119.99083 is about 1.5 m away.
- **Terms:** https://whc.unesco.org/en/disclaimer/ (HTTP 200) says: "All photographs and other elements of the UNESCO World Heritage Centre website are protected by international treaties on intellectual property and other applicable laws. The elements it displays may not be copied or retransmitted by any means without explicit authorisation from the World Heritage Centre or the copyright holders." `/en/terms-of-use/` and `/en/copyright/` returned HTTP 404.
- **Correction to the research note:** the note says the disclaimer "covers images". The site-wide sentence above also covers "other elements". The data therefore records `license: null` and `licenseStatus: needs-replacement-or-verification`, and asserts no reuse permission. Whether that reservation covers one factual coordinate is not established. Before packaging, someone must obtain authorisation, replace the value, or get a reviewed determination.

## Test changes

- The Liangzhu pin now expects `unesco-whc-1592`.
- The Liangzhu `coordinateSource.url` must be the UNESCO 1592 maps URL.
- The stored value must be within 5 m of the 1592-004 DMS value.
- A `whc.unesco.org` source must not assert a licence.
- A superseded source ID must not be listed or referenced anywhere.
- Manifest and travel data must also agree on `termsUrls`, `termsCheckedOn` and `supersedesSourceIds`.

## Verification

| Check | Result |
|---|---|
| `node tools/…geodata-attribution_validation-test_m2-v01_…678bd5f4.js` | `PASS geodata attribution validation: 4 travel sources, 5 manifest sources, 3 map geodata layers` |
| Negative: old source ID restored in memory / CC BY asserted for UNESCO / latitude shifted by 0.001° | Each FAILs with the expected messages (exit 1) |
| Godot 4.7.2 headless, calendar-route core smoke | `GLOBAL_TRAVEL_CORE_OK` |
| Global earth map smoke | `GLOBAL_EARTH_MAP_SMOKE_OK checks=201` |
| Map-travel integration regression v02 | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=103` |
| Export data-inclusion smoke | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |

The Godot runs used an isolated copy of `game/` and `assets/reference/geography/` under `%LOCALAPPDATA%\Temp`. This kept import side effects out of the repo. The map smoke needs `../assets/reference/geography` for its source-hash checks, and fails without it.

No Git stage, commit or push was made. The Game Bible, progress files and art were not edited.
