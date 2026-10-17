# Female protagonist battle static v10: Codex visual audit

Status: unapproved, nonruntime. This is a visual reading of the actual PNG and Godot captures, independent of the authoring note. The creator approved the 0.65 display proportion only. The static frame, motion and complete sprite remain unaccepted; accepted runtime sprites stay 0/52.

## Viewed evidence

- 21:9 character sheet: `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png`.
- v10 flat sprite: `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v10_20261016-162819-1c891d6d.png`.
- Real Godot v10 party captures: `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins-640_unapproved-v10_20261016-162819-de44e59a.png`, `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-outskirts-640_unapproved-v10_20261016-162819-7829fd0b.png`, and the corresponding 1280 × 720 ruins capture.
- Real Godot v09 comparison: `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins-640_unapproved-v09_20261016-135202-c26ecd6c.png`.

## What is visible

At 640 × 360, the fourth party member remains distinguishable by the dark high ponytail, teal neck cloth and forward sword. Her height remains suitable relative to the party and sentry. Compared with v09, the head, fist and blade sit further toward the opponent and the coat back is clearer. This improvement is subtle at the actual 640 × 360 viewport; it is easier to see in the 1280 × 720 capture.

The character sheet establishes a warm field coat, loose rolled sleeves, teal scarf, high ponytail, compact backpack and teal bedroll. In v10, the scarf and ponytail survive. The backpack roll is mostly a teal block at game scale, and its outline can be confused with the raised rear arm. The sword arm, sleeve and torso are similar dark values, so the ready pose loses its forearm separation. The coat still reads darker and cooler than the sheet's brown field coat, and the lower teal cloth is weak. The simplified finish of the three adjacent party members makes the lineup inconsistent even though it does not change the heroine's approved display proportion.

## Next static-only pass

1. Make the forward forearm readable at 640 × 360 with a small clear gap or value break between arm and torso; keep the fist and blade in their current forward positions.
2. Separate the bedroll from the rear arm and pack with a stronger roll end-cap or strap silhouette. Judge the result at 640 × 360, not only on the isolated sprite.
3. Bring one warm field-coat value and a narrow teal hip-cloth cue closer to the character sheet without enlarging the sprite or making it look like a skirt.
4. Retain the 0.65 node scale and the party spacing. Inspect both bright outskirts and dark ruins captures before asking the creator to review a new static frame.

No motion pass or approval request follows from v10. The existing author QA's deterministic tests support technical consistency, but this audit leaves the visual gate open.
