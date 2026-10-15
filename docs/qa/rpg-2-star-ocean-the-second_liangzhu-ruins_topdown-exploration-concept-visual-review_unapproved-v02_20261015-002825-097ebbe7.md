# Liangzhu outdoor exploration — visual candidate v02

Status: **unapproved, not integrated**. Visual review of the separate [1672×941 PNG](../../outputs/rpg-2-star-ocean-the-second_liangzhu-ruins_topdown-exploration-concept_unapproved-v02_20261015-002825-097ebbe7.png), 2026-10-15. SHA-256 `97D9C9CAACC9771CFD9AFF6C6ED1CB162F819BAFF55D9FF9A4FD5C8DC7734F20`.

This is a new composition following [v01](../../outputs/rpg-2-star-ocean-the-second_liangzhu-ruins_earthen-wetland-exploration-concept_unapproved-v01_20261015-000457-2ebec075.png), not a pixel-preserving revision of it.

## Visible result

- Earthen terraces, excavation, shallow channels, reeds, wooden crossings and a small survey station read as an outdoor archaeological wetland rather than the old stone plaza.
- The walkable dirt paths form a clear left-to-center-to-right route. The center clearing leaves space for a 48-logical-pixel character and a nearby NPC or enemy. The lower-right exit is visually clear.
- Pixel clusters and repeated foliage forms are sharper than v01, although the dense reeds, water edge and stair details may be too busy once 48-pixel sprites and interaction markers are overlaid.
- The isolated islands, water channels and bridges imply collision geometry different from the current prototype. Placing this image behind the old collider and hotspot positions would be misleading.
- At 1280×720, several bridge and upper-path widths may become close to one character wide. They need a native-scale engine check before this can become a traversable scene.

## Required visual and game checks

1. Place the candidate in a temporary 1280×720 Godot exploration preview with the approved female south static frame at the approved 48-logical-pixel display scale. Check silhouette/ground contrast in bright and shaded areas.
2. Rebuild walkable polygons and foreground occlusion from the visible land and water, then test all existing investigation points, companion interaction, enemy avoidance and exits. Do not silently move or remove content.
3. Review Chinese/English hotspot labels on the dense background and compare this candidate with v01 in engine.
4. Ask for creator acceptance of the selected composition. Until then, scene gate remains open; this image is not a literal reconstruction of a specific Liangzhu excavation area.
