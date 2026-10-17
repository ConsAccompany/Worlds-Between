# Washington Capitol west grounds: visual transfer brief (unapproved)

Status: art direction only. The generated reference is neither a runtime image nor a hand-authored Pixelorama scene. Science environment acceptance remains 0/11.

## Evidence compared

- Actual Godot entry capture: `outputs/wdc-cw-v08_20261016-155827-6cf49486/rpg-2-star-ocean-the-second_wdc-capitol-west_godot-640x360-entry_unapproved-v08_20261016-155827-6cf49486.png`.
- New nonruntime reference: `outputs/rpg-2-star-ocean-the-second_wdc-capitol-west_structural-damage-art-direction-nonruntime-v02_20261016-183256-3865fc0f.png`.
- Gameplay-perspective edit of the actual Godot capture: `outputs/rpg-2-star-ocean-the-second_wdc-capitol-west_gameplay-perspective-ruin-reference-nonruntime-v03_20261016-190544-6fa6af3f.png`. This is a generated visual guide, not a runtime frame or editable pixel layer.

The Godot view already shows a legible Capitol silhouette, central approach, survey apparatus, patrol machine, and ruined paving. Its facade and dome read as largely intact. The new reference shows the missing large-scale cue: one wing has lost a section of its roofline and upper wall, with rubble and plants emerging from that break. Its dome and opposite wing remain recognizable. The reference uses dense continuous-color rendering and a frontal perspective; neither its pixels nor its camera geometry should be transferred directly into the game.

The later v03 edit stays closer to the current Godot camera and object placement. Its left-wing dark opening and broken roofline remain visible at the whole-frame view, so it is the better layout guide. It also changes the player's costume, enlarges detail density, and smooths some shading; those parts must **not** be transferred. The original Godot image remains the source of runtime scale and collision geometry.

## Pixelorama transfer priorities

1. Preserve the approved scene scale, the central traversable route, the readable dome, and the west-grounds composition. Keep the player, survey instruments, and patrol machine distinct at the actual 640 × 360 viewport.
2. Break the **left wing's upper silhouette** with a contiguous missing roof and wall section. Show the torn edge and interior darkness in large pixel clusters that survive gameplay scale. Keep the dome and right wing predominantly intact.
3. Let vines and a small tree root into the broken wing itself. Place part of the fallen masonry below that break, with separated walkable and blocked tiles. Avoid concentrating every ruin cue in the foreground pile.
4. Give the building three material values: lit intact stone, cooler shaded stone, and dark fracture/interior. Reduce repeated identical window and vine patterns.
5. Retain the current entrance path and interaction spaces. Verify collision, draw order, character legibility, and bilingual UI overlap in real Godot captures after each authored pass.

## Acceptance boundary

First check a Pixelorama editable project and exported frame for actual deliberate pixel clusters. Then inspect it in Godot at 640 × 360 against the player scale. Only the creator can accept this as one of the 11 science-region environment scenes. This note and its reference do not change completion meters.
