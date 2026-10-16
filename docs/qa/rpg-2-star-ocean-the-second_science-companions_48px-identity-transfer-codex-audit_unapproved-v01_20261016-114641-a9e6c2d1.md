# Science companions: 48 px identity transfer audit

Status: visual audit only. No sprite or character art is accepted by this note.

Source sheets inspected:

- `outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png`
- `outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png`
- `outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png`

Game-size comparisons inspected:

- `outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-character-quality-h48-canvas-items_m8-v02_20261014-153547-1ca1259c.png`
- `outputs/rpg-2-star-ocean-the-second_liang-xu_native-game-preview-south_m8-v03_20261014-180100-f3128e01.png`
- `outputs/rpg-2-star-ocean-the-second_scifi-outskirts_zhao-ling-premium-south-vs-native-h48_m8-concept_20261014-161147-8689ef0f.png`
- `docs/character-visuals/rpg-2-star-ocean-the-second_ji-cheng_native-idle-review-south_m8-prototype_20261014-142206-800c4233.png`

At the approved 48-logical-pixel display height, hair contours need to differ before color is considered. Liang Xu needs the high bun and one broad silver forelock; Zhao Ling needs the asymmetrical chin-length bob, teal tips, round teal earcup and vertical antenna; Ji Cheng needs one shaved temple against the shoulder-length hair with silver tips. These are visual transfer targets, not approved replacements.

Each also needs a distinct second silhouette mass: Liang's two long coat tails with negative space between them; Zhao's crossbody equipment and headset antenna; Ji's broad forest-green split coat and brass magnifier held away from the torso. The Liang city capture retains part of the coat silhouette, but the forelock, bun and tablet do not read at ordinary game size. Zhao's concept comparison reads as dark bob/headset, while teal face-level details and gear merge. Ji's isolated native sprite does not show a readable shaved side or silver tips; no matching 48 px exploration Godot capture was found, so game-size legibility is unresolved.

Next art pilot should compare separate south, north and one side-facing frame on a bright city and dark ruins background at native game scale, without relying on a nameplate. Do not begin motion or increment 0/52 from this audit.
