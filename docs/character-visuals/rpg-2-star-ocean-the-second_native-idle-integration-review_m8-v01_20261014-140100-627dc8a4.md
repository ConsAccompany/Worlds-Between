# Native directional idle integration review · M8 v0.1

The male protagonist, female protagonist and Liang Xu now each have **four separate 32×48 transparent PNG idle frames**: south, west, north and east. They use the 21:9 character sheets as identity references. No portrait cutout was scaled into a sprite. The playable science city now displays the protagonist at native scale and selects a facing from movement; Liang Xu uses the native south idle frame until recruited.

## What was checked

- Godot 4.7.2 imported all 12 images and rendered the 640×360 city. The [capture manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-city_native-idle-in-engine_m8-v02_20261014-135900-c51f78ab/rpg-2-star-ocean-the-second_scifi-city_native-idle-capture-manifest_m8-v01_20261014-175723-9797aa74.json) lists separate playable-city screenshots for every protagonist facing and both appearances, plus recruitment states.
- The city integration check verifies each texture is 32×48, unscaled, nearest filtered, foot anchored at (16,44), and selected by the expected direction. Navigation, city return/recruitment, saving and the M7 automated routes still pass.
- In the actual game view, the female ponytail projects beyond the head and shoulder, the male hair stays short and uneven, and Liang Xu has a raised bun, pale side lock and longer charcoal coat. They are distinguishable as **idle prototypes** in the city sample.

## Open gates

- Only **4 of the required 20 frames per character** exist. Four-frame walk loops for each direction are still needed. Static direction switching while the character moves is functional but visibly lacks gait animation.
- The three identities have not yet been reviewed together during moving play, across bright paving, tree cover and darker scenes. City lighting, architecture and asset style have not been approved by the user. The protagonist source portraits and Liang Xu source portrait remain concept status.
- None of the 52 runtime sprite inventory items is checked. The current 12 idle frames count as production prototypes; they do not satisfy a complete four-direction exploration sprite.

Next: make walk cycles for these three identities, check foot stability and silhouette during movement in Godot, then obtain art direction approval before expanding to the remaining 49 visual versions.
