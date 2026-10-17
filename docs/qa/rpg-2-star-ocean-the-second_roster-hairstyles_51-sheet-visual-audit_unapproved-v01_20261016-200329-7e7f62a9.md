# Roster hairstyle and silhouette audit — 51 sheets

Visual review, 2026-10-16. I inspected one current 21:9 sheet for each of the 51 character identities, using the `hairstyle-v02` sheet where present, plus the available science-region scene-scale pilots. The protagonist's male and female appearances are two variants of one identity, making 52 visual variants overall. This note records visual evidence only; it does not approve art or change the 0/52 complete-sprite gate.

## Seen in existing small game pilots

There is **no proven pairwise 48-pixel collision** yet: the roster has not been shown together as finished, name-hidden sprites in a busy scene. These are visible losses of identity cues in individual pilots:

| Character | Sheet cue | Pilot observation |
| --- | --- | --- |
| Ji Cheng | A wide shaved temple beside a longer black bob with silver tips; `outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png` | The hair reads as a rounded gray cap in the native combat still `outputs/rpg-2-star-ocean-the-second_ji-cheng_scifi-battle-native-idle-phase-01_m8-prototype_20261014-145155-3d14544c.png`. The shaved patch and asymmetric edge are not legible. This is a combat prototype, not a validated 48-pixel exploration frame. |
| Liang Xu | High bun, broad silver forelock, thin tablet; `outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png` | In the 48-pixel bright-city pilot `outputs/rpg-2-star-ocean-the-second_city-bright_liang-xu-south-idle-static-pilot-h48_unapproved-v01_20261016-141751-bd083d0a.png`, the silver front area and coat read, but the bun does not separate strongly from the head and the tablet is hard to distinguish from her arm. |
| Zhao Ling | One-sided black bob with blue tips, cyan earcup and antenna; `outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png` | `outputs/rpg-2-star-ocean-the-second_zhao-ling_scene-scale-idle-south-masonry_m8-v01_20261014-142400-73b1cc9a.png` shows the cyan head accent on a plain diagnostic floor. It has not demonstrated readable hair asymmetry against the busy science city. |

The female protagonist's approved south idle reference `outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png` retains a recognizable tied-back outline and teal scarf in a bright scene. Approval covers this static frame, not a complete sprite set. Her male variant's short outward hair differs on the sheet; both intentionally share scarf, coat and pack.

## Sheet-level near-collisions to test later

These similarities are visible on full character sheets. They are **risks at game scale**, not demonstrated sprite failures.

| Pair or cluster | Similarity visible on sheets | Distinction to preserve in a small pilot |
| --- | --- | --- |
| Mi Yi / Mu Xiu | Both have a single long brown braid behind an earth-tone cloak: `outputs/rpg-2-star-ocean-the-second_mi-yi_character-sheet_v01_20261013-190819-fe5c8d41.png`, `outputs/rpg-2-star-ocean-the-second_muxiu_character-sheet_v01_20261013-153818-25247999.png` | Differentiate rear-view braid placement and width, top hair mass, bow/quiver versus green hood. |
| Kern / Pei Zhi | Both have rust-brown short spiked hair, shaved sides and dark industrial clothes: `outputs/rpg-2-star-ocean-the-second_kern_character-sheet_v01_20261013-192354-db79abc8.png`, `outputs/rpg-2-star-ocean-the-second_pei-zhi_character-sheet_v01_20261013-193120-0397bc6c.png` | Keep Kern's rough low spikes distinct from Pei Zhi's higher angular swept crest; use the hammer versus equipment silhouette. |
| Gu Lin / Que Zhi | Both have tousled dark layered hair and a thin trailing braid or queue: `outputs/rpg-2-star-ocean-the-second_gu-lin_character-sheet_v01_20261013-193838-16710012.png`, `outputs/rpg-2-star-ocean-the-second_que-zhi_character-sheet_v01_20261013-194543-4ac30749.png` | Differentiate side lock, queue height/length, and garment values in back and three-quarter views. |
| Short dark hair group | Zhao Ling, Ji Cheng, Lin Que, Luo Wen, Lai Rui and Ye Lan all occupy a short dark head silhouette on their sheets. These are not identical hairstyles. | Preserve Zhao's cyan earcup, Ji's exposed shaved temple, Lin Que's goggles, Luo Wen's long side bang and clipped side, Lai Rui's feather clips, and Ye Lan's straight blunt lower edge. |

The nonhuman sheets already show distinct head outlines: Huan-7's orb, Ling Bing's oval screen, Men Ling's tall window, Zhong Du's rectangle, Leng Jing's prism, Sui Ya's leaf crest and Yu Yin's crescent. They do not create a hairstyle issue on the sheets reviewed.

## Next static pilots

1. **Zhao Ling and Ji Cheng:** separate south-facing exploration idle frames at the approved 48-logical-pixel display height. Compare them without name labels in the same bright city and dark interior, then side by side. Require the cyan earcup/antenna versus broad shaved patch/silver tips to remain readable.
2. **Liang Xu:** refine one south idle frame to separate bun, silver front streak and tablet; compare against the approved heroine static frame in the same two environments.
3. **Mi Yi/Mu Xiu:** paired rear-view static study before animating either braid.
4. **Kern/Pei Zhi, then Gu Lin/Que Zhi:** paired front and rear static studies only if their regions enter production.

No art acceptance follows from this audit. A complete runtime sprite still requires the creator's visual approval and the existing animation/scene checks.
