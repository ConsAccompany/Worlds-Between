# Science region: sentry automaton battle sprite runtime integration QA note

2026-10-14. The static sentry pilot (`sentry-automaton-pilot-0b9664e2`) now draws in the real Godot battle in place of the purple placeholder block. Ruins and city encounters both spawn the sentry. This is a **reversible, unapproved runtime candidate**:
- **Art acceptance stays at 0.**
- No Game Bible, progress, readiness, counter or protagonist v8 file was changed.
- The patrol pilot keeps its exact behaviour.
- No human playthrough or creator review has happened.

## What changed

- **`game/scripts/battle_arena.gd`:**
  - `ENEMY_SPRITE_PILOTS` gains a `sentry` entry: the pilot PNG, anchor (48, 60), and an optional telegraph ellipse (`telegraph_center_y` 241, `telegraph_scale` (2.0, 1.2)).
  - New constants `ENEMY_TELEGRAPH_CENTER_Y` (240), `ENEMY_TELEGRAPH_RADIUS` (30) and `ENEMY_TELEGRAPH_COLOR` hold the original ring values. Per-instance `enemy_telegraph_center_y` / `enemy_telegraph_scale` default to them.
  - `_load_enemy_sprite_pilot()` resets the ring to the original before loading. It applies a pilot's ring override only once that pilot's texture has loaded.
  - `_draw_enemy()` draws the original `draw_circle((x, 240), 30)` call whenever the scale is 1, which covers the patrol and the placeholder. Only a scaled pilot uses the transformed ellipse.
  - The header comment now names both pilots.
- **Godot import sidecar:** [`…battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png.import`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png.import) is the default lossless import. The PNG is unchanged, SHA-256 `5ca76fe9…2462`.
- **Unchanged:**
  - sentry and patrol stats, AI, start x 493, approach speed, the 53 px stop distance, the 69 px enemy hit reach and hit ranges;
  - the wind-up tint `(1.0, 0.70, 0.66)`, the telegraph label, the HUD and transitions;
  - the arena candidate and the patrol pilot (PNG SHA-256 `e40e91e0…f31d`, anchor (29, 90), r30 ring).
  - With a sprite pilot active the enemy still draws before the fighters, so fighter frames stay on top.

### Why the sentry ring is wider

The sentry is 96 px wide and 60 px tall, while the original ring is a 60 px circle centred at y 240. Measured in logical pixels by the check script:

| Ring | Visible ring px (not hidden by the enemy) | Halo above the body |
| --- | --- | --- |
| Placeholder block, original r30 | 1248 | — |
| Patrol pilot, original r30 | 579 | — |
| Sentry with the original r30 | 869 | 52 px, almost all between the legs |
| **Sentry ellipse 60×36 at y 241** | **3244** of 6784 | **414**, plus 700 beyond the sides |

With the original ring, the wind-up halo for the sentry would mostly show only between its legs. The ellipse matches its proportions and shows at least as much ring as the old block. In the ruins wind-up capture, it raises red-minus-green by 0.218 over idle on the visible ring pixels.

## Reversal

Any one of these restores the placeholder block **and** the original r30 ring:
- set `ENEMY_SPRITE_PILOT_ENABLED := false`;
- delete the `"sentry"` entry (the patrol is unaffected);
- set the per-instance `enemy_sprite_pilot_enabled = false`;
- let the texture go missing.

All but the constant switch are asserted by the test below.

## Evidence

The [check/capture test](../../game/tests/rpg-2-star-ocean-the-second_sentry-automaton-pilot_battle-check-capture_m8-v01_20261014-222407-5e92645e.gd) ran headless (`-- --no-capture`) and windowed at 1280×720. Both runs exit 0 and print `SENTRY_AUTOMATON_PILOT PASS cases=8` (headless `captures=0`, windowed `captures=8`). It asserts:

- **Load and placement:**
  - the real `change_scene_to_file` path from a ruins run opens the `ruins` band with the pilot;
  - the first windowed transition takes 310 ms (under one second);
  - the texture is native 96×62 and the anchor (48, 60) sits on the last opaque row;
  - the sprite top lands at logical y 213, inside the band.
- **Combat unchanged:**
  - stats 96 / 18 / 68 / 0.48 / 1.10;
  - start x 493 and an approach step of exactly 6.8 px per 0.1 s;
  - the wind-up starts at the 53 px stop distance and lasts 0.48 s;
  - movement, melee 19 (96 → 77), dodge −12 energy, guard 60 → 54, unguarded 60 → 42;
  - the strike case: the wind-up expires, the hit lands for 18, the hero plays the `hit` frame, and a 1.10 s cooldown starts;
  - telegraph label, Tab, auto and pause.
- **Telegraph clarity:**
  - the ellipse shows at least as many pixels as both the patrol ring and the block ring, with halo above the body and beyond both sides;
  - the label's bottom (y 204) clears the sentry top (y 213);
  - the wind-up tint reads redder than idle (mean R−G 0.068 vs −0.014).
- **Attack layering:** at 53 px all 535 hero attack-frame pixels that overlap the sentry show the fighter.
- **Fallbacks and patrol preservation:**
  - the patrol keeps its pilot, anchor and r30 ring;
  - with the switch off, or with a missing texture, the sentry shows the block and r30 ring;
  - the pilot also renders over the legacy geometric backdrop;
  - city encounters use the pilot on the `city-terrace` band.

Each capture is listed with its SHA-256 in the [capture manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_capture-manifest_m8-v01_20261014-222715-33266209.json):

| Capture | Arena / pose / language | Transition | Body vs surround luma Δ |
| --- | --- | --- | --- |
| [ruins idle](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_ruins-idle-zh_m8-v01_20261014-222715-6ee85900.png) | ruins / idle / zh | 20.29 ms | 0.035 |
| [ruins wind-up](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_ruins-telegraph-en_m8-v01_20261014-222715-168f8533.png) | ruins / telegraph / en | 20.53 ms | 0.124 |
| [ruins hero melee](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_ruins-melee-attack-zh_m8-v01_20261014-222715-cbb2e83e.png) | ruins / hero attack at 53 px / zh | 20.36 ms | 0.054 |
| [ruins sentry strike](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_ruins-sentry-strike-en_m8-v01_20261014-222715-3404176d.png) | ruins / hit lands, hero 42/100 / en | 19.14 ms | 0.036 |
| [city wind-up](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_city-terrace-telegraph-zh_m8-v01_20261014-222715-b9b28cb8.png) | city-terrace / telegraph / zh | 18.46 ms | 0.143 |
| [legacy backdrop wind-up](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_legacy-backdrop-telegraph-zh_m8-v01_20261014-222715-aa2ceb7f.png) | geometric (arena off) / telegraph / zh | 7.75 ms | 0.110 |
| [block fallback idle](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_block-fallback-idle-zh_m8-v01_20261014-222715-58c57e17.png) | ruins / pilot off / zh | 17.26 ms | — |
| [block fallback wind-up](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-pilot_block-fallback-telegraph-zh_m8-v01_20261014-222715-528c1df2.png) | ruins / pilot off, original ring / zh | 16.04 ms | — |

**Regressions:** all run headless, exit 0 and print their OK/PASS marker, with no FAIL lines.
- Milestone smokes: `m2_smoke` through `m7_smoke` and `m6_restart_smoke`.
- The five side-view combat smokes (`--no-capture`).
- The [arena candidate check](../../game/tests/rpg-2-star-ocean-the-second_battle-arena-candidate_runtime-check-capture_m8-v01_20261014-213622-14315e18.gd) (`--no-capture`).
- The [patrol pilot check](../../game/tests/rpg-2-star-ocean-the-second_patrol-automaton-pilot_battle-check-capture_m8-v01_20261014-221500-b83e1c57.gd) (`--no-capture`).
  - Its one stale assertion, "sentry keeps the placeholder block", is now intentionally false.
  - It now opens the sentry with its pilot off and asserts the block. Nothing else in that test changed.

## Visual observations (relative, not acceptance)

- In both ruins and city, the sentry reads as a low, wide machine distinct from the upright patrol and the party. The cyan eye and brass joints carry it on stone.
- The red ellipse frames the whole body during the wind-up, and the label sits fully above it. Both read more clearly than the patrol's mostly hidden ring.

## Remaining risks

1. **Low idle mass contrast.** Body-vs-surround luma Δ is 0.035 on ruins stone at idle, even lower than the patrol's 0.052 on outskirts. Readability rests on the outline, brass and cyan.
2. **Melee overlap.** At the 53 px stop distance the hero's attack and hit frames cover roughly half of the sentry's eye and front leg. Spacing was tuned for the 34 px block. Fighters draw on top, as intended, but the enemy's face is hidden during contact.
3. **No authored attack pose.** The wind-up is the tint plus the ellipse, and the "strike" is only the hero's hit frame and HP drop. There is no idle bob, walk, strike, hit or defeat animation, so the enemy slides and vanishes on defeat.
4. **Narrow contact shadow.** The shared contact shadow is still an 18 px radius ellipse at `enemy_x`, which is narrow under a 96 px body with spread feet. It was left unchanged to avoid touching the arena candidate code.
5. **Ellipse size.** The 60×36 ellipse extends to logical y 277, 5 px below the floor line. At alpha 0.28 it is a strong red field. It is a tuning choice for clarity, not a reviewed design.
6. **Right-edge clamp.** At the 612 px clamp, half the 96 px sprite would leave the screen. The enemy starts at 493 and moves toward the party, so this was not observed.
7. **Unreviewed.** The pilot, its concepts and this ring tuning are unapproved. Creator art review and a human 1280×720 play session are pending.
