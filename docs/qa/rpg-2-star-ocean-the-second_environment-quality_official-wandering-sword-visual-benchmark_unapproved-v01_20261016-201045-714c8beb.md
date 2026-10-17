# Environment quality benchmark: what to carry into the approved top-down game

Codex visual comparison, 2026-10-16. Reference: the [official *Wandering Sword* Steam screenshot](https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1876890/ss_71c4de4c59b83429711f6e0ee2eb94b02df1be60.1920x1080.jpg?t=1766110443), viewed in the browser. The creator requested comparable environment finish, while this project retains its own top-down 2D camera, science-city setting and approved 48-logical-pixel heroine display scale. Do not copy the reference image, its architecture, or exact composition into project assets.

## Direct visual observations

- Architecture has a readable foreground/middle/background separation. The near roof and banners frame a brighter walkable centre; distant structures are softer.
- The floor is not a single repeating grid: masonry blocks vary in value and wear, yet the principal walking plane stays legible under the characters.
- Warm practical lights, dark eaves and diffuse daylight produce a controlled value hierarchy. Small props cluster where people would use them, instead of appearing uniformly scattered.
- Individual characters remain distinguishable at game view despite a busy scene. Their contact shadows and nearby table or doorway relationships anchor them.

## Transfer to Worlds Between candidates

1. **Keep the top-down camera.** Match the *finish* by layering facade depth, contact shadows, localized light, authored material variation and atmospheric recession. A 3D camera, heavy bloom or copied roofline is not required.
2. **Reserve a clean walk zone.** Add detail at structural edges and story fixtures, then inspect at native 640×360 with the 48-pixel heroine and actual UI. Detail that hides a route or interaction cue fails.
3. **Make each science place identifiable.** NYC City Hall Park should retain its ordered civic park and active technology; Washington Capitol west should show visible asymmetric collapse and survey/patrol activity; Yonkers should use edge-of-city service, rail or waterfront cues rather than another generic garden.
4. **Use scene lighting to separate identical hues.** NYC and Washington currently share cream facades and green tree masses. Texture count alone will not communicate inhabited hub versus abandoned ruin.
5. **Verify in the engine.** Pixelorama-layer/source quality and palette counts are necessary production checks but cannot replace a real Godot screenshot and creator art review.

This is an external visual benchmark and internal art-direction note. It accepts no runtime scene or character asset; meter stays 35.8%, sprites 0/52, scene art 0/11 pending Chicago denominator reconciliation.
