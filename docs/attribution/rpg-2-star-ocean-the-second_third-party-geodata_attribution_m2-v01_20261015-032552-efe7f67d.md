# Third-party geodata attribution (M2)

Recorded 2026-10-15. This lists every external source of coordinates, map vectors and route figures in the M2 world-travel and world-map data. It is a project record for packaging, not legal advice. The machine-readable copy is the [attribution manifest](rpg-2-star-ocean-the-second_third-party-geodata_attribution-manifest_m2-v01_20261015-032552-916697a2.json); the travel data repeats its own sources under `attribution.sources`. The game runtime ignores both.

## Credits to ship with the game

- Contains data from [GeoNames](https://www.geonames.org/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Made with [Natural Earth](https://www.naturalearthdata.com/). Free vector and raster map data @ naturalearthdata.com.

Add a credit line for any source below that is verified rather than replaced.

## Sources

| Source | Used for | Terms | Status |
| --- | --- | --- | --- |
| [GeoNames 1796236](https://www.geonames.org/1796236) (retrieved 2026-10-15) | Shanghai coordinates `31.22222, 121.45806` | CC BY 4.0, credit with a link required ([export terms](https://www.geonames.org/export/), [about](https://www.geonames.org/about.html)) | Stated by publisher; credit line above |
| Natural Earth [110m land](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson), [50m land](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_land.geojson), [10m roads](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_roads.geojson) subset (retrieved 2026-10-15) | Map land and road vectors in the runtime geodata | Public domain ([terms of use](https://www.naturalearthdata.com/about/terms-of-use/)); credit not required | Stated by publisher; credited anyway |
| Natural Earth [10m populated places](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_populated_places_simple.geojson) (retrieved 2026-10-15) | Hangzhou reference point in the map place registry | Public domain, as above | Stated by publisher |
| [Wikipedia: Songjiang District](https://en.wikipedia.org/wiki/Songjiang_District) (retrieved 2026-10-15) | Songjiang Outskirts coordinates `31.00583, 121.23333` | Not established. Wikipedia text is CC BY-SA 4.0 (and GFDL), not CC BY 4.0. It is unclear what applies to one copied coordinate pair, or where Wikipedia got it. | **Replace or verify before packaging** |
| [UNESCO World Heritage Centre 1592, Maps component table](https://whc.unesco.org/en/list/1592/maps/), row 1592-004 "Area of City Site", N30 23 43.97 E119 59 26.97 (retrieved 2026-10-15) | Liangzhu Ruins coordinates `30.39556, 119.99083` (within 2 m of the DMS value) | Not established. UNESCO states no licence for the table. Its [disclaimer](https://whc.unesco.org/en/disclaimer/) (checked 2026-10-15) says "photographs and other elements" of the site "may not be copied or retransmitted by any means without explicit authorisation"; `/en/terms-of-use/` returned 404. No reuse permission is claimed. | **Obtain authorisation, replace, or verify before packaging** |
| [Rome2Rio](https://www.rome2rio.com/) route pages for [Shanghai–Songjiang](https://www.rome2rio.com/s/Shanghai/Songjiang) and [Shanghai–Liangzhu](https://www.rome2rio.com/s/Shanghai/Archaeological-ruins-of-Liangzhu-City) (retrieved 2026-10-15) | Two car segments: 34.8 km / 26 min and 187.9 km / 120 min | Not reviewed. These are route figures, not geodata. | **Verify before release**; already marked preliminary estimates |

The Songjiang district government page (https://english.songjiang.gov.cn/facts/location/) is cited in the travel data only to explain why its coordinates were rejected. No value comes from it.

On 2026-10-15 the Liangzhu citation moved from the Wikipedia copy of the UNESCO table (former source ID `wikipedia-liangzhu-unesco-1592`, kept as `supersedesSourceIds`) to the UNESCO table itself. The coordinate value did not change. See the [source-correction QA note](../qa/rpg-2-star-ocean-the-second_liangzhu-coordinate-source_unesco-citation-correction_qa-note_m2-v01_20261015-040500-c3e1a7d2.md).

## Open items

1. Replace the Songjiang coordinates with a value from a source of known terms (for example a GeoNames record, which would fall under the GeoNames credit above), or verify the current value and its terms. For Liangzhu, the value now cites UNESCO directly, but reuse is still not cleared: obtain UNESCO authorisation, replace the value, or verify the terms. Keep the location IDs unchanged.
2. Review Rome2Rio's terms, or re-source the two route figures, before release.
3. When a new external source is added, add it to the manifest and to `attribution.sources` in the travel data, and give the entry a `sourceId`. The validation test fails otherwise.

Validation: `node tools/rpg-2-star-ocean-the-second_geodata-attribution_validation-test_m2-v01_20261015-032552-678bd5f4.js`.
