# NYC–Chicago air route inset v01r1 — Codex visual audit

**Status: test-only, unapproved, nonruntime. M2 map-art gate stays open; completion remains 35%.** I inspected the actual Godot v01r1 English 1280×720 and Chinese 640×360 captures in `outputs/` (run `adea3798`), alongside the technical QA note.

## Visible result

- The dashed connection makes the New York City origin and Chicago destination understandable while the Great Lakes camera still shows only Chicago. The inset separates the endpoints from the larger route card, and its dark label plates improve readability.
- The air caption and the inset's own 250 km scale bar are visible in both sizes. The card, calendar and primary controls remain unobscured.
- At 640×360, the plane icon is a tiny wedge. It conveys direction only with the dashed line and endpoint labels. Both the inset and the underlying map's 100 km scale bar remain visible close together; their borders distinguish them, but the view is information dense.

## Remaining quality gap

The inset solves this one route-orientation problem. It does not turn the surrounding functional map into the game's finished pixel-art map: land is still broad flat colour, grid lines dominate, and the inset is a small overlay with limited visual depth. Do not mark the M2 map-art gate complete from its automated 108/108 checks.

## Next step

Keep v01r1 as the test-only option. If it is integrated later, verify interaction and legibility in the full map at both languages and both resolutions, then refine the main map's visual language as a separate art task. The current candidate makes no runtime or completion-meter change.
