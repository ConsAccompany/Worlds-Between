# Female protagonist native idle prototype — M8 review

## Source and identity

Reference: `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png`. The source sheet remains concept art. This pass interprets its high side ponytail, tea-green scarf, weathered brown adventurer coat, community diamond emblem, and teal bedroll/backpack at exploration scale.

## Deliverables

Each PNG below is a separate, transparent RGBA **32×48 native-pixel** idle frame. The foot anchor is `(16,44)` for all four. All visible shapes were authored at that resolution; no high-resolution cutout was reduced to sprite size.

| Facing | Native frame | City scene review |
| --- | --- | --- |
| South | `game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-south_m8-prototype_20261014-135400-3bacea6e.png` | `outputs/rpg-2-star-ocean-the-second_protagonist-female_native-idle-south-city-review-640x360_m8-prototype_20261014-135400-5ebc8bc8.png` |
| West | `game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-west_m8-prototype_20261014-135400-b023f47c.png` | `outputs/rpg-2-star-ocean-the-second_protagonist-female_native-idle-west-city-review-640x360_m8-prototype_20261014-135400-70f7fe0c.png` |
| North | `game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-north_m8-prototype_20261014-135400-daa6122c.png` | `outputs/rpg-2-star-ocean-the-second_protagonist-female_native-idle-north-city-review-640x360_m8-prototype_20261014-135400-02bcd739.png` |
| East | `game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-east_m8-prototype_20261014-135400-39d3f522.png` | `outputs/rpg-2-star-ocean-the-second_protagonist-female_native-idle-east-city-review-640x360_m8-prototype_20261014-135400-eabdaecb.png` |

Reproducible pixel design: `tools/rpg-2-star-ocean-the-second_protagonist-female_native-idle-pixels_m8-prototype_20261014-135437-b4a2e1c7.py`.

## Design decisions and checks

- The ponytail projects outside the head and shoulder silhouette to x=1 south, x=0 north, x=30 west, and x=2 east. The tail reaches roughly y=26–28, with warm highlights and a visible teal tie on the south and north frames. The backpack/bedroll sits away from the tail to preserve both forms.
- Preview method: resize the existing 1672×941 city background to the game's **640×360 logical viewport**, then composite one unscaled 32×48 sprite at `(304,185)` with a separate ground shadow. This is a scene-scale visual check, **not** a Godot runtime capture. Each review file contains one character only.
- Automated checks found all four images to be 32×48 RGBA with transparent corners, a shared foot baseline at y=44, and 20–22 effective colors including transparency (within the suggested 20–32 color budget).
- In the 640×360 city review, the face direction, projecting ponytail, scarf/bedroll, and brown coat remain identifiable without a name label. The north view is darkest; actual Godot nearest-filter and movement checks still need to confirm visibility against other backgrounds.

## Acceptance status

**Four-direction idle prototype only.** It is not a completed runtime sprite. The specification requires four walk frames per facing, Godot in-scene inspection at 640×360 and 1280×720, comparison with the male protagonist and Liang Xu in multiple lighting conditions, and a human visual sign-off. The 52-character registry and Game Bible completion flags must remain unchanged until those gates pass.
