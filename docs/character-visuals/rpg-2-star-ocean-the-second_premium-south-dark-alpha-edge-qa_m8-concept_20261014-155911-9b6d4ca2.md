# Premium south concepts — dark alpha-edge QA

Status: **technical inspection only**. These images remain unapproved concepts and were not edited or integrated into runtime.

## Test scene

The existing underground [`prototype_room.tscn`](../../game/scenes/prototype_room.tscn) was rendered in Godot 4.7.2. Its play area is a genuinely dark teal floor (`#28434a`) with a subtle `#33545c` grid. Each character was placed separately at logical foot `(320,270)`, scaled to 48 logical pixels of visible height, with nearest character filtering and an independent soft shadow. The logical canvas is 640 × 360 and each actual `canvas_items` screenshot is 1280 × 720. The [reproducible review harness](../../game/tests/rpg-2-star-ocean-the-second_prototype-room_dark-alpha-edge-review_m8-concept_20261014-155030-cfb311a9.gd) changes no game scene or asset.

| Character | Separate actual Godot screenshot | Visible edge result |
| --- | --- | --- |
| Male protagonist | [Dark-room capture](../../outputs/rpg-2-star-ocean-the-second_prototype-room_protagonist-male-south-dark-alpha-edge-h48_m8-concept_20261014-155247-c73346bd.png) | No discernible black box, dark halo, bright rim, or stray dot around the hair, scarf, backpack or boots. |
| Female protagonist | [Dark-room capture](../../outputs/rpg-2-star-ocean-the-second_prototype-room_protagonist-female-south-dark-alpha-edge-h48_m8-concept_20261014-155331-3143c722.png) | No discernible halo or floating bright pixels around ponytail, scarf, pack or boots. |
| Liang Xu | [Dark-room capture](../../outputs/rpg-2-star-ocean-the-second_prototype-room_liang-xu-south-dark-alpha-edge-h48_m8-concept_20261014-155402-9a6e3c8a.png) | No discernible halo or detached pixels around silver hair, coat tails, tablet or boots; her dark coat merges somewhat with the room's tone, which is a contrast issue rather than an alpha fringe. |

The [capture manifest](../../outputs/rpg-2-star-ocean-the-second_prototype-room_dark-alpha-edge-review-manifest_m8-concept_20261014-155911-22dd193f.json) records source paths, receipts, and analysis counts.

## Source alpha check

All three files have genuine transparency. Pixels with alpha 1–63 number 28,417 (male), 34,395 (female), and 30,325 (Liang). Most are around the silhouette and may be intentional antialiasing. A 16-source-pixel dilation around each alpha≥64 subject leaves only 342, 724, and 184 nonzero-alpha pixels outside it, respectively; **all of those distant pixels have alpha exactly 1**. No distant pixel reaches alpha 16. The distant specks are therefore source-file hygiene issues, not visible artifacts in these 48-pixel captures.

## Cleanup decision and limits

No visible halo repair is required on this tested dark background at static 48-pixel scale. Before production export, a targeted clean-alpha pass can remove the isolated alpha=1 specks, then compare the result visually; do not strip all low-alpha edge pixels without checking hair and coat contours. This is not a production acceptance decision: moving frames, different filtering, true-black backgrounds, and additional light/dark game scenes remain untested.
