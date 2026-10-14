# 纪澄 / Ji Cheng — native exploration prototype review

## Identity and scope

- Source: `outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png`; character bible describes a 28-year-old relic restorer with a shaved side, silver-black shoulder-length hair, forest-green jacket, and folding magnifier.
- The four separate 32×48 idle frames and sixteen separate 32×48 walk frames are drawn directly at game pixel resolution by `tools/rpg-2-star-ocean-the-second_ji-cheng_native-exploration-author_m8-prototype_20261014-142029-6b9d413e.py`.
- Manifest: `game/assets/characters/native-animation/rpg-2-star-ocean-the-second_ji-cheng_native-exploration-manifest_m8-prototype_20261014-142157-a4836b01.json`.
- Review images, each showing exactly one idle direction at nearest-neighbor 8× scale: [south](rpg-2-star-ocean-the-second_ji-cheng_native-idle-review-south_m8-prototype_20261014-142206-800c4233.png), [west](rpg-2-star-ocean-the-second_ji-cheng_native-idle-review-west_m8-prototype_20261014-142206-d5d47164.png), [north](rpg-2-star-ocean-the-second_ji-cheng_native-idle-review-north_m8-prototype_20261014-142206-a21b233d.png), [east](rpg-2-star-ocean-the-second_ji-cheng_native-idle-review-east_m8-prototype_20261014-142206-41e31b08.png).

## Distinctive design

The long charcoal curtain falls on one side, with silver ends at shoulder height. The opposite side is visibly shaved in south/east/rear views; west reveals more of the long hair. The forest-green split coat, diagonal satchel strap, and warm ring of the folded magnifier reinforce her silhouette. East and west are drawn independently, rather than mirrored. The belt tool stays with the same side of the body across directions.

## Automated checks

- Manifest has 20 frames: one idle and four walking phases for each direction. All 20 PNGs are unique, RGBA, 32×48, with transparent corners.
- All frames use anchor `(16,44)`, have opaque boot pixels on row 44, and keep an unchanged visible bounding box within each direction: south/north `[4,4,28,45]`, west/east `[6,4,27,45]`. This bounds visible animation jitter.
- Each frame has no more than 32 opaque colors. Against its direction's idle image, walking phases change 18–133 pixels; the smaller numbers are intentional passing poses.

## Status and remaining review

**Prototype; not accepted as final runtime art.** The enlarged inspection confirms the intended head shape and color blocks, but the frames still need a five-character, nameplate-free comparison at actual 640×360 game scale, including light and dark ruin backgrounds. The animation needs human motion review after runtime hookup. Side-view combat actions are separate assets and are not covered here. No game scripts, registry, or tracking states were edited by this task.
