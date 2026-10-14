# Native walking integration review · M8 v0.1

The male protagonist, female protagonist and Liang Xu each now have 16 separate native 32×48 RGBA walk frames: four phases for south, west, north and east. Combined with their existing idle frames, each has the specified 20 exploration frames. The nine south-facing attack/hit images are **motion studies**, not the separate horizontal combat art required by the visual specification.

## Playable integration

- Male and female protagonists use the native walk loop in all three playable science areas. The loop changes with the movement direction and returns to the matching idle frame when movement stops, the character meets a boundary, or dialogue opens.
- Every frame uses nearest filtering, unit scale and the shared `(16,44)` foot anchor. The scene continues to use the existing navigation and interaction geometry.
- Liang Xu remains a stationary recruitable city NPC. His walk frames are available by character ID and were posed in the same Godot city at 640×360 for scale review, but there is no genuine companion-follow movement yet.

## Evidence and limits

- Godot 4.7.2 imported all 57 new PNGs. M2, M7, M8 city integration, city navigation and city reentry checks pass. The city integration check covers direction selection, active walk frame, return to idle, and the existing recruitment/save route.
- [The capture manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-city_native-motion-in-engine_m8-v01_20261014-141222-62e97563/rpg-2-star-ocean-the-second_scifi-city_native-motion-capture-manifest_m8-v01_20261014-181226-6f8d6327.json) points to **twelve separate rendered 640×360 images**: one walk phase for each facing and character. These prove in-engine scale and layering for selected poses, not real-time animation quality.
- At scene size, the high side ponytail, short uneven hair, and Liang Xu's bun with pale lock still read as different head shapes in the selected captures. The figures remain small against dense city detail. Timing, all-phase transitions, walking through foliage, and three-character movement together require manual review.
- None of the 52 runtime sprite checklist entries is accepted yet. Source portrait approval and the eleven scene visual gates also remain separate.

Next gate: inspect a live moving play session for foot jitter and silhouette at 1× and 2×, then add actual companion-follow behavior before requesting exploration sprite art approval. The combat art still needs its distinct side-view animation set.
