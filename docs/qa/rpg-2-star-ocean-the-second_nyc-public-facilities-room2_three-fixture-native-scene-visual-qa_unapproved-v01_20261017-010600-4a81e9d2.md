# NYC public facilities room 2 — native scene visual review

**Scope:** one Lower Manhattan / City Hall Park investigation room. The creator approved the **static environment art baseline** after seeing a real 640×360 Godot capture with the three new fixtures, then explicitly approved this scene as the first accepted science scene-quality gate. See `docs/qa/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_scene-visual-acceptance_v01_20261017-010900-8f4a2c6e.md`. Character animation and timed playtests remain unapproved.

## What is in the runtime candidate

- Three separately authored 64×64 transparent fixtures sit at the room's existing clue x-coordinates 163, 320 and 477: open repair-manual bench, closed duty-log lectern and round analog load meter. They are visible without relying only on the labels.
- Each fixture has a three-layer editable OpenRaster source (`contact-shadow`, `structure`, `identity-detail`) and a merged PNG in `outputs/room2-fixtures-pilot/`. Runtime PNG copies live in `game/assets/props/nyc-public-facilities-room2/`; `game/scripts/survey_annex.gd` draws them before the original clue indicators. No clue ID or site coordinate was changed.
- The long English room title uses 14 px in this room so that “Lower Manhattan · City Hall Park · Public Works Level” ends before the Save button. Chinese stays at 18 px.
- The capture harness temporarily shows the creator-approved female selout v8 **south static frame** at 48 logical pixels. It does not replace the runtime's incomplete four-direction hero sprite.

## Real Godot evidence

- Godot 4.7.2 editor imported the three PNG assets and the scene parsed successfully.
- The native 640×360 Chinese and English renders, a right-side approach, and an opened repair-manual overlay were captured in `outputs/room2-fixtures-pilot/` with run tag `20261017-010418-6b3138d8`.
- The capture harness exercised the actual `interact` input from a clear right-side approach to each of the three clue locations. All three keys (`scifi.city:3`, `:4`, `:5`) appeared in `AppState.survey_clues`; output: `ROOM2_FIXTURE_INTERACTIONS_OK 3` and `ROOM2_FIXTURE_CAPTURE_OK 4`.
- The left, middle and right fixtures remain separated; the lower walk lane and analysis console are visible. The renderer output is actual Godot imagery, not a composited concept.

## Open limits

- The creator formally accepted this scene's environment quality as **1/12**. This does not accept its character motion or either timed human playtest.
- Room 2 still uses its earlier whole-scene background plate. The prop ORA sources are editable, but the plate's source layers are not part of this pilot.
- Furniture has no new collision body; the recorded approach is from a clear side position. The project’s existing movement system and other room interactions were not altered.
- The capture harness logged a resource-cleanup warning after producing its four images and checking all three interactions; the Godot process exited with code 0. This should be resolved before using the harness as a long-running automated test.
