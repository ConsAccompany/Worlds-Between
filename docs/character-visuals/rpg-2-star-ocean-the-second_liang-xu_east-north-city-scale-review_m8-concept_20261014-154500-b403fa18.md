# Liang Xu east and north exploration concepts

**Status:** directional art concepts; visual acceptance pending. No gameplay scene, runtime registry, or character data was changed.

## Separate assets and actual game captures

| Direction | Source | 48px actual Godot city capture |
| --- | --- | --- |
| East | [Transparent PNG](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_east-exploration-premium-pixel_m8-concept_20261014-154119-4cb71aff.png) | [East capture](../../outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-east-character-quality-h48-canvas-items_m8-v02_20261014-154305-90539b0d.png) |
| North | [Transparent PNG](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_north-exploration-premium-pixel_m8-concept_20261014-154238-518189c4.png) | [North capture](../../outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-north-character-quality-h48-canvas-items_m8-v02_20261014-154332-f6c12a84.png) |

The [three-direction manifest](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_exploration-direction-concepts-manifest_m8-v01_20261014-154500-fae9103a.json) also records the [south concept](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_south-exploration-premium-pixel_m8-concept_20261014-153531-4c6e2bcd.png), source hashes, foot anchors, and capture receipts. The approved character sheet was used as the identity reference; the south concept was used as a direction/style reference. Each new image was generated separately with built-in imagegen and `transparent_background=true`.

## Inspection

- **East:** A clear right-facing head profile and silver hair streak survive the 48-pixel city scale. The graphite coat, copper collar trim, and folded tablet remain consistent with south. Torso and two boots are still partly three-quarter rather than a strict side view, so animation turnaround fidelity is unresolved.
- **North:** The dark bun, silver side strand, copper upper-back ring, navy center panel, coat tails, and tablet are consistent with the sheet's rear view. The head turns slightly left, exposing an ear; a stricter rear silhouette may be needed. At 48 pixels the small silver strand is less distinct than in south/east, while the long coat remains the primary identity cue.
- Both files are 1024 × 1536 RGBA with real transparent areas and no alpha≥64 subject pixels on the canvas edge. East alpha≥64 bounds: `(179,55)`–`(819,1491)`; north: `(190,47)`–`(863,1503)`.
- The captures are from the actual sci-fi city at a 640 × 360 logical canvas rendered to 1280 × 720 using `canvas_items`, with the same `(340,253)` logical foot anchor, 48-pixel visible height, nearest figure filtering, and a separate soft shadow. There is no obvious broad dark box in these two city captures. Source files contain 27,297 (east) and 32,822 (north) low-alpha pixels, so edge QA against other backgrounds remains open.

## Next art gate

Creator review should decide whether the east torso and north head angle meet directional continuity. The set lacks west and animation frames; these concepts are not ready for runtime replacement.
