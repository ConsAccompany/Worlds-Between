# Global map v02 — native 640×360 visual hierarchy

**Codex visual review, 2026-10-16; unapproved.** Evidence: `outputs/rpg-2-star-ocean-the-second_global-map-art_us-northeast-zh-640x360-candidate_candidate-unapproved-v02_20261016-172153-ab9459d4.png` and `outputs/rpg-2-star-ocean-the-second_global-map-art_us-great-lakes-card-chicago-air-zh-640x360-candidate_candidate-unapproved-v02_20261016-172153-ab9459d4.png`. These are game-size candidates, not creator-accepted map art. M2 map-art gate remains open; meter unchanged.

## What is legible

The map displays a recognizable US Northeast/Great Lakes geography, region title, location names in Chinese and English, transport mode, whole-hour trip duration and arrival date. The coastline and borders do not overpower the markers.

## Specific composition defects

1. **New York/Yonkers labels crowd the same northeast cluster.** Their dark name boxes nearly meet, and the connector strokes overlap the Hudson/coast detail. Set stable label slots or collision avoidance so the two labels have visible separation at this zoom. Keep their marker locations geographically fixed; move the labels, not the city coordinates.
2. **Washington label sits near the bottom overlay.** A longer localized place name risks disappearing under the footer; reserve a map-safe margin around fixed UI before positioning callouts.
3. **Chicago travel preview centers the destination while the origin is outside the view.** The card consumes roughly a third of the map width, so the selected route is not understandable from the map itself. On route preview, fit both endpoints into the remaining geographic viewport left of the card, or put a clearly labeled two-endpoint route inset *inside* the card. One of these must be visibly present in the 640×360 screenshot. Keep route confirmation, cancellation and duration behaviour unchanged.
4. **Surface hierarchy is functional rather than finished pixel art.** The land has broad low-contrast fills and thin route/border lines, while location boxes and panels use crisp UI pixels. Introduce a restrained authored terrain/road layer at the same pixel-grid discipline as the UI, without inventing coastlines, borders or cities. Geographic accuracy and point selection take priority over texture density.
5. **The off-screen route tags can be mistaken for nearby city markers.** In the US Northeast view, “Chicago” appears visually between the NYC/Yonkers cluster; in the Great Lakes preview, “New York City” sits near Chicago. The candidate-skin source intentionally draws a short route stub, chevron and far-city label near the visible endpoint (`_offscreen_marker` in the v02 test-only skin). The registry coordinates remain correct. At native size the tiny chevron does not clearly convey that the named city lies outside this regional frame. Move this information to a clearly marked map-edge direction cue or the two-endpoint route inset, and do not show a far-city label as an apparently local marker. Check both languages and preserve actual marker hitboxes.

## Review gate

Make paired 640×360 Chinese and English captures for the Northeast cluster and NYC→Chicago preview. At both languages, all location names and dates must remain readable, the current city and destination must be distinguishable, and the route must be visible without hiding the map's geographic context. Human visual review is still needed before the map-art gate can be considered implemented/accepted.

The off-screen tag is intentional, but its meaning must be legible to a player who has not read the source code. A route cue should not visually imply that Chicago and New York occupy the same regional map. Demonstrate the revised treatment in native-size screenshots and keep the separate place-marker projection tests passing.

**Existing test-only solution to reuse:** `outputs/rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-inset_v01r1-zh-640x360_test-only-v01_20261016-065443-adea3798.png` and its English counterpart already show a legible two-endpoint inset. The earlier [v01r1 audit](rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-inset-v01r1-codex-visual-audit_unapproved-v01_20261016-070201-b6d76529.md) covers it. Those captures predate the simplified whole-hour/date-only travel rule and use the older flat map rendering. Adapt the inset concept to v02 instead of rebuilding the idea; recheck that the card says only whole hours and date. It is not runtime integrated or art accepted.
