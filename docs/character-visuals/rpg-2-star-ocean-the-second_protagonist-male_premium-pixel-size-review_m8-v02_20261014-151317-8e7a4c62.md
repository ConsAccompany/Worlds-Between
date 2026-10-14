# Male protagonist premium pixel exploration sample — M8 v02

Status: **concept / visual review only**. This is one south-facing exploration image; no runtime sprite, directional animation, or asset acceptance is implied.

## Files and sources

- Revised transparent source: `game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-male_south-exploration-premium-pixel_m8-v02_20261014-190703-746cf39d.png` (1145 × 1374 RGBA).
- Canonical identity reference: `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_male_20261013-153316-5b7c19e2.png`.
- Pixel-art style reference: `game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png`.
- Current provisional game-scale evidence: `outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-v2-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-151710-7a499c3e.png` with adjacent JSON receipt. Liang is shown at the same ground height for scale comparison.
- Earlier size comparisons: `outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-v2-character-quality-h56-canvas-items_m8-v02_20261014-151227-58d31ac0.png` and `outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-v2-character-quality-h60-canvas-items_m8-v02_20261014-151056-b0c9f698.png`, each with adjacent receipt.

## Generation brief

Create **one** full-body, south-facing, high-detail pixel-painted male adventurer on a transparent canvas. Follow the original male's tousled layered short dark-brown hair, tea-green scarf, brown travel coat, cream shirt, fingerless gloves, boots, bedroll and community diamond emblem. Borrow the female premium sample's crisp colored pixel clusters, lighter midtones and silhouette finish, but preserve the male character's own face, hair and clothing. No ground, vignette, text, UI, other character or collage.

## Game-scale review

The candidate was rendered in Godot 4.7.2 in the actual science city at a 640 × 360 logical canvas and captured at a 1280 × 720 `canvas_items` window. Figure texture uses nearest filtering; the city and a **separate** procedural soft shadow use linear filtering. The source anchor `(575, 1352)` maps to city foot `(340, 253)` in both captures. The alpha content bounds are `(279, 48)` to `(876, 1352)`, with no content touching the source canvas edge and no review-harness warnings.

**Provisional size: 48 logical pixels** for this city composition. A later same-ground comparison with the existing Liang sprite showed that 56 px still looked oversized. At 48 px, the male retains a readable short-hair silhouette, scarf and coat, and sits closer to the existing human scale. The female peer review reached the same provisional 48 px target. The harness flagged 48 px as outside its earlier 52–80 px diagnostic band, but the capture completed at the requested 48 px and otherwise reported no content or anchor warnings. This remains a visual proposal requiring creator approval.

Compared with v01, the face, shirt and coat are brighter, the teal scarf separates from the hair and collar, the short layered hairstyle is distinct, and the earlier dark low-alpha vignette is no longer visible in the city capture. The community emblem and small travel accessories cannot be reliably read at 48 px; they remain useful in dialogue/portrait art. The source has antialiased partial-alpha edge pixels, so every later direction and animation needs its own in-engine halo check.

## Remaining gate

Review the source and 48 px city capture with the creator. If accepted, use the 48 px height and foot convention for directional/animation development. Do not mark runtime character coverage complete from this single concept frame.
