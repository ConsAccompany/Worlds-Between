# Global map v03r1: Codex visual judgment at native size

**Decision: keep unapproved.** The v03r1 zoom-label correction is technically ready for selective integration (503/503 targeted checks, 1873/1873 inherited map checks, bilingual real Godot captures). This note is about the separate **map-art acceptance gate**. It does not advance M2, the 40.8% meter, or any scene/sprite count.

I inspected these actual 640×360 Godot captures at 1×: US Northeast browse in Chinese and English, 1.5× Washington route card in both languages, and the Chicago flight card in both languages. Paths and before/after evidence are listed in `docs/qa/rpg-2-star-ocean-the-second_global-map_zoom-label-clamp_qa-note_unapproved-v03r1_20261017-184737-5ef3676e.md`.

## Visible result

- The v03 label collision is fixed in the zoomed Washington state: New York City and Washington, D.C. names are fully visible; Globe/region controls remain clear. My earlier spoken impression that labels still obstructed controls was mistaken and was corrected to the creator.
- The real northeast coastline and Great Lakes geography are recognizable. The cards keep the simplified car/flight time and arrival date readable in both languages; no airport details intrude.
- The map still reads closer to a geospatial utility view than a finished RPG travel screen. The olive land relief is low contrast and irregularly noisy at 1×; the Great Lakes view has a broad undifferentiated land area around one city marker. Route cards rely on large plain dark rectangles and stock-looking buttons. This is a visual assessment, not a test failure.
- In the 1.5× Washington card, New York City is named at the card edge while its dot is hidden beneath the card. The leader stub technically preserves a click target, but the relationship is hard to read at a glance. Washington's selected ring meets the lower map controls. The card omits some location lines at this zoom as its current overflow rule allows.

## Next visual pass before creator acceptance

Keep the validated geography, locations, route data, dates and click behavior. Improve the land/water value hierarchy and map texture so the route and city markers stand out at 1×; give the Great Lakes card a clearer visual focal path; align the travel card and buttons with the game's established teal/brass science UI. Resolve the boxed-in selected marker and edge-plate reading without covering fixed controls. Return bilingual native Godot captures of globe, browse and the two route-card states. Ask the creator to review the **whole map** only after Codex inspects those captures.

The above is a bounded visual target, not permission to rewrite travel rules or count map art as accepted.
