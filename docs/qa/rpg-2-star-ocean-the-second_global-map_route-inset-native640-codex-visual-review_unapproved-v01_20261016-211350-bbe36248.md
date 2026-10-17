# Global map route inset: Codex visual review of actual Godot 640×360 captures

**2026-10-16, candidate only.** Claude's isolated Godot run passed 657/657 map checks and 7/8 regressions; the remaining failure is documented as preexisting in the integration note. I inspected the generated native-size images independently. This review does not approve map art or alter M2 10/12, overall 35.8%, or science scene visuals 0/11.

## Actual frames inspected

- Browse, Chinese: `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_us-northeast-zh-runtime-640x360_test-only-v01_20261016-205301-5a17c3e9.png`.
- NYC→Chicago, Chinese and English: `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_us-great-lakes-card-chicago-air-zh-runtime-640x360_test-only-v01_20261016-205301-5a17c3e9.png` and the matching `-en-` frame.
- Chicago→NYC, English: `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_us-northeast-card-nyc-from-chicago-air-en-runtime-640x360_test-only-v01_20261016-205301-5a17c3e9.png`.
- NYC→Washington, Chinese: `outputs/rpg-2-star-ocean-the-second_global-map_route-inset-runtime_us-northeast-card-washington-car-zh-runtime-640x360_test-only-v01_20261016-205301-5a17c3e9.png`.

## Judgment at game size

The two-endpoint inset clearly communicates that Chicago and New York are far apart while preserving the correct marker positions in each regional map. The dashed link and aircraft glyph read at 1×, and the card still displays the simple six-hour flight without airport names. The NYC and Yonkers labels no longer overlap; Washington's label remains above the bottom controls. The English and Chinese cards are legible. These are meaningful improvements over the off-screen chevron presentation.

Three visual issues remain for the map-art gate: (1) with a route card open, the selected marker sits tightly against its left edge, especially in the Northeast; (2) the large inset masks much of Pennsylvania on the return view and is not yet visually distinct enough from the underlying map panel; (3) map land, grid and inset are flat and functional, short of the project's approved environment finish target. A small inset header or an explicit minimap border treatment could help distinguish its scale; this is an art suggestion, not a request to change geography or travel logic. Keep the route preview technically integrated but mark the map image **unapproved** pending owner review.
