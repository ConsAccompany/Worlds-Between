# Washington Capitol battle arena: visual direction only

The current 640×360 sentry battle captures use ornate, generic stone ruins for both the `ruins` and `outskirts` arena bands. They read as a fantasy location, while the science MVP now takes place in New York, Yonkers and the abandoned Washington, D.C. Capitol grounds. The underlying battle system and the creator-approved sentry v2 action direction are separate from this background issue. No arena art is accepted by this note; science scene visuals remain 0/11.

## Evidence inspected

- Real Godot ruins battle: `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins-640_unapproved-v10_20261016-162819-de44e59a.png`.
- Real Godot outskirts battle: `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-outskirts-640_unapproved-v10_20261016-162819-7829fd0b.png`.
- Separate generated **nonruntime art-direction reference**: `outputs/rpg-2-star-ocean-the-second_wdc-capitol-west_sideview-battle-arena-art-direction-nonruntime-v01_20261016-193018-f4d8246c.png`. This is continuous-colour image generation, not editable or approved pixel art.

## Visual judgment

The reference conveys a recognizable Capitol dome, two broken west-front sections, vegetation in the masonry and a small science survey post. Its broad paved foreground gives the five-person party and sentry a shared floor. That relationship is useful for the Washington encounter. The image is too detailed and bright to paste behind the current combat UI, and its floor occupies much more than the live arena's playable middle band. The inactive machine shape at far right would also compete with the actual sentry sprite and should be removed from the authored background.

The existing combat HUD fills approximately the top 90 logical pixels and the bottom 55 pixels of the 640×360 view. Author the new arena specifically for the remaining combat band: a readable, near-level foot line around logical y≈270, calmer masonry behind the fighters, and the distinctive damage in the upper middle distance. The background should have no raised terrain or obstacles affecting battle, matching the game's fixed-arena rule. Keep the owner-approved heroine battle display proportion at node scale 0.65 and do not treat this reference as a character or scene approval.

For Yonkers, make a separate science-outskirts variant rather than reusing this Capitol silhouette. Both variants need real Godot captures showing five party slots, the sentry wind-up and hit frame, bilingual HUD, floor contact, and a sub-second battle transition before human art review. Pixelorama layers and exported PNG must be retained as editable source and runtime output respectively. The generated reference cannot stand in for those artifacts.

## Yonkers variant direction

Separate **nonruntime reference**: `outputs/rpg-2-star-ocean-the-second_yonkers-outskirts_sideview-battle-arena-art-direction-nonruntime-v01_20261016-193255-76d9b413.png`. The image suggests a low brick service building, rail embankment, Hudson-facing hills and a small amount of science instrumentation, rather than another ancient stone courtyard. [Yonkers' city overview](https://www.yonkersny.gov/739/About-Yonkers) establishes the Hudson waterfront, rail and road connections; the [city waterfront page](https://www.yonkersny.gov/511/The-Pier) establishes the urban waterfront context. The concept is an invented edge-of-city composition, **not** a precise named Yonkers street or canon landmark.

At the actual battle size, its huge clear sky would mostly be hidden behind the HUD, and the painted floor occupies too much vertical space. Transfer the brick/rail/water/low-hill material hierarchy into a compact authored pixel arena band with a flat fighter baseline, and reduce background detail behind character faces and enemy tells. Do not paste the generated image into runtime art. Both references remain unapproved and leave scene visuals at 0/11.

## Independent game-scale check

An independent Codex visual pass compared both references with the actual four-person 640×360 combat captures. In the Washington reference, the top HUD would cover the dome's upper profile unless the landmark and visible damage are moved into the exposed upper-middle battle band (roughly y=95–190). The floor around y=200–290 needs quieter cracks and fewer bright amber patches so red enemy telegraphs and contact shadows remain legible. In the Yonkers reference, the garage, rail and guardrail should read as distant background, not as climbable or blocking geometry; reduce the bright water and roadway texture behind the five fighter slots. Current test captures show four party members and an empty fifth slot. Acceptance needs a new **native 640×360** capture with all five party members, the machine, red wind-up indicator, full HUD and a consistent flat foot line. This check reinforces the unapproved status of both generated references.
