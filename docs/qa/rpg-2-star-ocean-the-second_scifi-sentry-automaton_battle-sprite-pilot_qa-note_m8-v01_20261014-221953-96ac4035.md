# Science region: sentry automaton battle sprite pilot QA note

2026-10-14. One hand-authored, native-resolution pixel-art sprite for the **sentry**: the science-region ruins enemy that still draws as a red block. This is an **isolated, unapproved pilot**:
- **Art acceptance stays at 0.**
- **It is not wired into the game.** `battle_arena.gd` belongs to another session and was not touched, so the sentry still draws its placeholder block.
- No Game Bible, progress, readiness, counter, patrol or character file was changed.
- No human playthrough or creator review has happened.

## Files (all new)

- **Asset folder:** [`game/assets/enemies/sentry-automaton-pilot-0b9664e2/`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/)
- **Sprite:** [`…sentry-automaton_battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png), SHA-256 `5ca76fe9…2462`.
- **Manifest:** [`…battle-pilot-manifest_m8-pilot-v01_20261014-221901-e3ab87f9.json`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-pilot-manifest_m8-pilot-v01_20261014-221901-e3ab87f9.json). It records the hash, size, bounding box, anchor, alpha values, palette, method, the author script's hash and the references.
- **Author script:** [`…battle-idle-pilot-author_m8-v01_20261014-221848-0b9664e2.py`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-pilot-author_m8-v01_20261014-221848-0b9664e2.py), SHA-256 `39fbd418…226b`.
  - Amended 2026-10-14 ([hash-lock repair](rpg-2-star-ocean-the-second_m8-battle-visuals_hash-lock-repair_qa-note_m8-v01_20261014-234133-317f4482.md)): `39fbd418…226b` is the raw hash of the CRLF working copy. The manifest now locks the same text as sha256-text-lf-v1 `a8dfa204…d6d0`, which matches LF and CRLF checkouts.
- **Inspection builder:** [`…pilot-4x-inspection-builder_m8-v01_20261014-222200-0b9664e2.py`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_pilot-4x-inspection-builder_m8-v01_20261014-222200-0b9664e2.py), SHA-256 `2d8324b3…a8e`.
- **4× inspection sheet:** [`outputs/…sentry-automaton-pilot_4x-inspection_m8-v01_20261014-221934-29cc34c0.png`](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_4x-inspection_m8-v01_20261014-221934-29cc34c0.png), 1096×1286, SHA-256 `d19fbb5a…f1c5`. It has five parts:
  - A: native view;
  - B: alpha check on a checkerboard;
  - C: shared-baseline lineup with Liang Xu's idle frame and the patrol pilot;
  - D: an **offline mock-up** pasted at 2× onto an existing ruins capture. It is not a Godot render.
  - Palette strip.

## Measurements

- **Canvas:** 96×62 RGBA. The opaque box is x 0–95, y 1–60, with 3704 opaque pixels.
- **Alpha:** only 0 and 255. There are no semi-transparent pixels and the background is fully transparent.
- **Colours:** 17. The palette is identical to the patrol pilot's: a slate ramp of 7 steps including the outline, a brass ramp of 5, one rust tone, and a cyan ramp of 4. 92 pixels are lit cyan.
- **Ground anchor (48, 60):**
  - Row 60 is the last opaque row: the outline under the soles of both near feet, spanning x 1–94.
  - The far feet end 2 px higher, for depth.
  - The intended draw position is `(enemy_x − 48, 272 − 60)`, which puts the contact row on `ARENA_FLOOR_Y` 272. The author script asserts this row and its foot coverage.
- **Scale:** 1 native px = 1 logical px = 2×2 physical px at 1280×720, matching the fighters and the patrol pilot.
  - The sentry is 60 px tall, against 72 px for Liang Xu and 90 px for the patrol.
  - It is 96 px wide, against 34 px for the old block. So it is low and wide, not tall.

## Method and design read

- **Method:** every plate polygon, joint, lens ring, seam, rivet and grime pixel is placed explicitly in code on the final 96×62 canvas.
  - Parts are composited back to front, each with a 1 px seam ring, plus a selective outline on the top/left edges.
  - Neither concept image was opened, sampled, traced or resized. The [character sheet](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton_character-sheet-unapproved_m8-v01_20261014-210321-64fc7295.png) and [single-sprite study](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton_single-sprite-style-concept-unapproved_m8-v02_20261014-211731-d544cc62.png) were visual reference only.
  - It went through five scratch iterations outside the repo. The final PNG is byte-identical to the last scratch render.
- **Silhouette:** a low, wide, four-legged crab stance facing left.
  - One large cyan eye sits in a 21 px brass bezel inside an octagonal housing, with a far-side visor fin above it.
  - Behind the eye is a slotted near cheek plate. The rounded carapace has two raked brass straps, a small top dome with a cyan pip, skirt seams, rear vents and a rear status light.
  - The legs have brass hip and knee joints and toe-capped block feet. The far legs are one ramp darker.
- **Distinct from the patrol:** no mast, no camera head, no pauldron and no upright biped stance. The shared palette keeps the region coherent.

## Remaining risks (relative observations, not acceptance)

1. **Not in game.** No Godot load, draw order, wind-up tint or telegraph has been tested. Panel D is a paste onto an old capture, not a runtime render.
2. **Value contrast.** In the mock-up, mean body luma (0.267) is 0.047 below the surrounding ruins paving (0.314). That is the same low mass contrast seen with the patrol, so readability rests on the outline, brass and cyan.
3. **Width.** The sentry is 96 px wide against the block's 34 px. At the current AI melee stop distances, fighters will overlap its front leg and eye. The hit ranges and draw order were tuned for the block.
4. **Shape.** The carapace still reads somewhat like a cylinder. The concept's faceted wedge shell is simplified. The far legs are plain dark posts.
5. **Single static frame.** There is no idle, walk, wind-up, strike, hit or defeat pose.
6. **Unreviewed.** Creator art review and a 1280×720 human play session are pending.
