# Female protagonist native animation review — prototype

Source identity: the existing 32×48 directional female idle art. Her high, left-side ponytail, teal scarf, cream shirt, brown coat and backpack stay recognizable across directions. This batch adds motion drawn at the same 32×48 pixel resolution.

## Deliverables

- 16 separate walk PNGs: south, west, north, east × four phases.
- Two separate south-facing attack PNGs and one south-facing hit PNG as **exploratory motion studies**. They are not finished horizontal combat assets.
- Reproducible authoring script: `tools/rpg-2-star-ocean-the-second_protagonist-female_native-animation-author_m8-v01_20261014-183000-3b7c92d1.py`.
- Runtime-readable manifest: `game/assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-animation-manifest_m8-prototype_20261014-140955-d7d64ca7.json`.

## Pixel checks

All 19 frame files are distinct RGBA images at 32×48 with transparent corners and at least one opaque pixel on the y=44 foot baseline. The authored motions change the leg stride, wrist height and ponytail tip. No frame is made by translating or scaling the full idle sprite. Attack phases coil and extend the right arm; hit opens both arms.

## Acceptance state

These are **prototypes**. The walk loops still need motion timing, game-size review and human approval. Combat requires a separate horizontal asset set covering idle, move, attack, guard, dodge, hit, down and skill. The south attack/hit studies do not satisfy that requirement. This batch should not increase the accepted 52-sprite asset count yet.
