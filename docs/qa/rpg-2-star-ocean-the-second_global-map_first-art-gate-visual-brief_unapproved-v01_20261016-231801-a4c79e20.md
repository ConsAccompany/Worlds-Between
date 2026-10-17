# Global Earth map: first map-art gate visual brief

Status: **Codex visual judgment, not an accepted map**. M2 remains **10/12 technical gates**, the map-art gate is open, and the weighted MVP estimate remains **35.8%**.

## Native gameplay evidence

- `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_us-northeast-zh-runtime-640x360_test-only-v01_20261016-205301-5a17c3e9.png`
- `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_us-great-lakes-card-chicago-air-en-runtime-640x360_test-only-v01_20261016-205301-5a17c3e9.png`

Both captures show real coastlines, usable place markers, the route card, a date-only display and a functional Chicago inset. At the native 640×360 size, however, the land is a large uniform green field, water a uniform blue field, and gridlines dominate the unoccupied space. The labels and side card feel like a technical planning screen, rather than the same polished pixel-art game as the environment. On the Northeast view, NYC and Yonkers remain crowded. The Chicago side card occupies the map's east side, so the route must remain visible in the inset and not depend on an obscured line beneath the card.

## Bounded art direction

1. Keep the current **real Earth coastlines and true city placement**. Add restrained land relief, coastal depth and a few route-relevant terrain cues in intentional pixel clusters; avoid invented geography, invented national borders or a fantasy parchment map.
2. Give land, inland water and sea three clearly different value families. Lower the grid's contrast so cities and selected routes dominate at game scale.
3. Preserve the side card's readable hierarchy and the simple whole-hour travel rule. Do not add airports, schedules, time-of-day detail or more simulated logistics.
4. Separate NYC and Yonkers labels at 640×360. Keep all place names, route length and date readable in both Chinese and English without hiding other selectable markers.
5. For Chicago, make the small Northeast inset and its flight path unmistakable when the right card is open. Treat the inset as the route proof; do not merely add decorative lines to the main map.
6. Harmonize the map's palette and small teal science cues with the exploration UI. This is an art pass over the verified interaction design; preserve click targets, route preview/confirm/cancel, travel timing and save behavior.

## Reviewable evidence

Submit native 640×360 Godot captures for (a) Northeast with NYC, Yonkers and Washington visible, (b) NYC to Chicago flight card and inset, (c) return flight and (d) a car route card, each in Chinese and English. Include actual mouse interaction and a short map/travel regression check. The creator should see these captures before the map-art M2 gate is marked done. The current functional screenshots and this brief do not satisfy that gate.
