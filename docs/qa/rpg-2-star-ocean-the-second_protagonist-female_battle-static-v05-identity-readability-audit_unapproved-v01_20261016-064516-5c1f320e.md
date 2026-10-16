# Female protagonist battle static v05 — identity and readability audit

**Status:** Visual assessment of an unapproved static candidate. The creator approved the battle display **proportion** at node scale 0.65, not this frame or any animation. Accepted complete character sprites remain **0/52**.

## Evidence inspected

- Character identity sheet: `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png`.
- Candidate source frame: `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v05_20261016-054620-8e5e4656.png`.
- Actual 1280 × 720 four-person Godot renders: `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v05_20261016-054620-845c716a.png` and `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-outskirts_unapproved-v05_20261016-054620-cfa9cdf9.png`.

## Visible assessment

- The high dark ponytail and teal scarf survive at gameplay size. The shorter blade, one backpack shape and gap from the adjacent companion also keep the four-person row readable.
- The sheet's rolled teal bedroll, diamond pack emblem, raised field-coat collar and pale rolled cuff do **not** resolve as separate cues in either Godot render. The pack reads as a plain brown vertical block; the coat reads as one narrow dark mass. A viewer without the sheet would have little to distinguish her as the specific traveler from a generic swordswoman.
- The small flesh-tone face patch carries no readable expression at this size. The ponytail is a single compact arc rather than the sheet's loose high-tied strands. Her boots and lower coat overlap in value, so the stance remains rather straight and static.
- On the ruins floor, coat and paving are close in value and the silhouette depends on its dark outline. The outskirts floor gives slightly clearer separation, but both arenas contain richer material and lighting variation than the heroine. The existing 0.65 proportion works in the party row; changing size is not the next fix.

## Next refinement priority

At the **same 0.65 display scale and foot baseline**, first allocate a few deliberate pixel clusters to the identity cues: a distinct teal roll atop the pack, a simplified bright pack emblem, one clear coat-collar/cuff break and a more asymmetric high ponytail. Then separate the coat's light and dark planes from the floor while retaining the approved exploration palette. Test those changes in both original 1280 × 720 Godot arenas and in the four-person row before attempting motion. Avoid solving legibility only by enlarging the source frame or adding tiny details visible solely when zoomed.

This is Codex visual judgment of the cited pixels, not creator acceptance or a production sprite approval.
