# Science cast visual identity at 48 logical pixels

Codex visual comparison of the existing 21:9 sheets and Godot captures, 2026-10-16. This is an art production brief, not approval of any sprite. The creator has approved the female protagonist's selout v8 **south idle static frame only** and the 48 logical pixel exploration display scale. All other full sprites and motion remain unapproved.

## Why the present cast converges

At gameplay scale, the old companion prototypes collapse into dark hair, dark coats and small handheld props. Their detailed portrait features disappear before their names are readable. The approved heroine v8 demonstrates that a 48 logical pixel figure can retain a distinct hair/coat outline and a high-contrast teal accent against a busy bright scene. Future static pilots should be judged in the same 640×360 Godot view, with no companion follower displayed persistently outside story moments.

## Silhouette contract by character

| Character | Sheet evidence | Cues to preserve at 48 px | Avoid |
| --- | --- | --- | --- |
| Female protagonist | `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png` | Tall tied-back ponytail with loose side strands; teal scarf; short open field coat; pack and rolled bedroll visible in side/back directions. Keep the approved south idle v8 as the density and contrast benchmark. | A short-bob or bun silhouette; merging the teal scarf with the pack or the weapon arm. |
| Male protagonist | `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_male_20261013-153316-5b7c19e2.png` | Uneven outward-pointing short hair, teal scarf, open field coat, pack/bedroll. The hair silhouette should remain visibly shorter and wider than the heroine's ponytail. | A generic rounded cap of hair; simply recoloring the female frame. |
| Liang Xu | `outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png` | High bun plus broad silver front streak; tall structured collar; long, split dark coat with blue interior; thin tablet or field book. The bun and silver streak must be readable without relying on a face close-up. | A plain black bob, short jacket, or tablet reduced to a single indistinguishable hand pixel. |
| Zhao Ling | `outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png` | Asymmetric chin-length hair, one long fringe with blue tips; one visible cyan earcup/headset and narrow antenna; compact communications kit. Her outline should be wider on the fringe side and narrow at the opposite cheek. | Treating the headset as a second bun; symmetrical hair; using Liang's silver streak as a substitute for Zhao's blue fringe. |
| Ji Cheng | `outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png` | One close-shaved temple exposed beside a longer silver-tipped bob; deep green, uneven long coat; small magnifier or artifact reader. In side view, show shaved scalp as a large clear patch rather than one highlight pixel. | Zhao's headset silhouette; a center-parted bob; a smooth uniform hem. |

## Current candidate observations

- The female v8 city capture `outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png` retains the teal scarf and tied-back hair in the bright scene. This is the only approved static visual baseline of this group.
- The male v02 city capture `outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-v2-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-151710-7a499c3e.png` carries the teal scarf and wider hair, but the art is unapproved and its shading density still needs comparison with female v8.
- Liang Xu's `outputs/rpg-2-star-ocean-the-second_city-bright_liang-xu-south-idle-static-pilot-h48_unapproved-v01_20261016-141751-bd083d0a.png` retains a silver forehead area and a long coat, but at actual gameplay scale the tablet and bun do not separate cleanly from the body. The old runtime NPC remains visibly coarser than the heroine v8.
- Zhao Ling's `outputs/rpg-2-star-ocean-the-second_zhao-ling_scene-scale-idle-south-masonry_m8-v01_20261014-142400-73b1cc9a.png` shows a headset accent but its surroundings are a neutral diagnostic floor; it has not passed the busy science-city readability test.
- Ji Cheng's `outputs/rpg-2-star-ocean-the-second_ji-cheng_scifi-battle-native-idle-phase-01_m8-prototype_20261014-145155-3d14544c.png` reduces the undercut/silver bob to a generic grey cap in a simple combat backdrop; the sheet's hair asymmetry and magnifier identity are not yet visible.

## Next visual gate

Make **one south idle frame each** for the male protagonist, Liang Xu, Zhao Ling and Ji Cheng at the approved 48 logical pixel display height. Test each separately on one bright NYC scene and one dark interior scene, then in a single four-character scale frame. The sheet traits above must remain distinguishable when names are hidden. Record creator feedback on the individual static frames before producing four-direction animation sets. None of this changes the 0/52 accepted runtime sprite counter.
