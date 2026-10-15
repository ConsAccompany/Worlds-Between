# Liangzhu pixel-art transition: visual review

2026-10-15. The creator accepted the **earthen terrace, waterways, wetland and survey-station terrain direction** of the [first concept](../../outputs/rpg-2-star-ocean-the-second_liangzhu-ruins_earthen-wetland-exploration-concept_unapproved-v01_20261015-000457-2ebec075.png) and asked to turn it into high-precision pixel art. That reply did not approve the image as production art or settle the scene composition.

Two independent generated candidates were saved after the reply:

| Candidate | Visual finding | Read-only color sample |
| --- | --- | --- |
| [v03, first concept's layout](../../outputs/rpg-2-star-ocean-the-second_liangzhu-ruins_earthen-wetland-pixel-pass_unapproved-v03_20261015-015324-371f9ffc.png) | Retains the central crossroads, tent, terrace and waterways. Contours are somewhat blockier, yet the rendering still reads as a textured illustration rather than deliberate pixel clusters. | 85,567 distinct colors among 98,648 pixels sampled every fourth row and column; v01 sampled the same way has 86,281. This is not a controlled limited-palette conversion. |
| [v04, new low-resolution visual language](../../outputs/rpg-2-star-ocean-the-second_liangzhu-ruins_low-res-pixel-language-concept_unapproved-v04_20261015-015613-81c79fef.png) | Stronger geometry and open traversal path; large earth terraces, bridge and excavation read immediately. The composition differs substantially from v01, so it cannot be treated as a faithful pixel edit of the accepted terrain concept. | 81,233 distinct colors in the same 98,648-pixel sample. The prompt's requested 64-color palette was not achieved. |

The sample counts are an objective indicator of continuous-tone output, not an assessment of beauty or a requirement that a finished HD pixel scene literally contain only 64 colors. Both images are **concept studies**, not editable pixel layers and not integrated Godot backgrounds. Scene acceptance remains 0/11.

## Practical next step

Use the accepted v01 terrain direction as the location brief and v04's clearer route hierarchy as optional layout reference. Determine the actual in-engine pixel grid and character ground pin, then author walkable ground, embankments, water, reeds, survey objects and foreground occlusion as separate editable pixel layers. Review a single local-scene section at native 1280×720 with the approved female south static frame before expanding the entire background. Preserve the existing investigation and recruitment functions when remapping hotspots. The proposed Pixelorama environment workflow awaits the creator's answer; earlier permission covered the female sprite pilot only.

No palette count, image-generation prompt or concept screenshot substitutes for the native-size Godot inspection or creator's visual acceptance.
