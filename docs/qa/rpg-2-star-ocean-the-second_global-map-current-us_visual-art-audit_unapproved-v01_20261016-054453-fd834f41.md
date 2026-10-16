# Global and US regional map — Codex visual art audit

**Status: functional map art placeholder, unapproved.** I inspected the actual Godot captures `outputs/rpg-2-star-ocean-the-second_global-earth-map_globe-zh-runtime-capture_m2-v02_20261015-184808-49d78162.png` and `outputs/rpg-2-star-ocean-the-second_global-earth-map_us-northeast-zh-runtime-capture_m2-v02_20261015-184808-49d78162.png`. These are current US science-region geography captures, not the superseded 2026/Shanghai map. The global-world/travel art gate remains open.

## What already reads clearly

- The Earth silhouette and US Northeast coastline are recognizable, with real-place markers placed in the intended regions.
- The active science sphere, date and local travel destinations are visible in Chinese. The controls for globe/region level, zoom and site selection can be found.
- The map communicates the technical global-to-region navigation model.

## What keeps the art gate open

- Land and sea are broad flat fills under a strong longitude/latitude grid. At gameplay size the view reads as GIS or debug data rather than the game's high-precision pixel visual language.
- The global view gives only North American marker detail and otherwise vast undifferentiated continents. A player can misread the intentionally limited MVP route scope as a visually unfinished world.
- On the Northeast view, New York and Yonkers markers and dark label boxes crowd one another. The Washington marker and label sit low against the edge and interface overlays.
- The regional map has no road, highway, rail context, or drawn air route to distinguish car travel from airplane travel. Its route card may state the mode, but the map surface does not explain it.
- The header, map labels, date, status bar and lower buttons compete at near-equal visual weight. The large grid and coast line remain more prominent than the player's destination choice.

## Art direction for a later candidate

Preserve the verified geography, coordinates, click targets and bilingual labels. Create a map-specific pixel palette and hierarchy: coastline and relief at low contrast, accessible science destinations/route at high contrast, quieter grid, and visibly distinct road and air connections where the route data actually exists. Move labels away from neighboring markers and screen edges without moving the underlying geographic pins. Treat the five civilization spheres as a future color-language layer; the science MVP should only highlight its available routes. Check a 1280×720 Godot globe and Northeast view plus a destination route card before asking for creator approval.

**Counter impact:** none. This is a visual assessment; it does not satisfy M2 map-art acceptance or change the MVP meter.
