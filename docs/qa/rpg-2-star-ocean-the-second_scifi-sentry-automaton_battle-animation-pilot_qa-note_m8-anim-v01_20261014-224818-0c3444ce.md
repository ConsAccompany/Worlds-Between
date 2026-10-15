# Science region: sentry automaton battle animation pilot QA note

2026-10-14. The creator viewed the real Godot ruins idle and wind-up captures of the static sentry and answered "方向可以，继续完善动作": the visual direction is accepted and animation should continue. This is **not** an art gate. This pass adds a reversible, **unapproved** animation pilot on top of the static 96×62 sentry:
- **Art acceptance stays at 0.** No global art counter changed.
- No Game Bible, progress, readiness, protagonist or walk file was touched.
- The patrol keeps its static pilot.
- Human review of the animation is pending.

## Asset

- **Strip:** [`…battle-animation-strip-left_m8-anim-v01_20261014-223820-f181f893.png`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v01_20261014-223820-f181f893.png), 1632×62 = 17 cells of 96×62, SHA-256 `7b6bc0c4…4e9a`. The `.import` sidecar is the default lossless import.
- **Manifest:** [`…battle-animation-manifest_m8-anim-v01_20261014-223820-f181f893.json`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-manifest_m8-anim-v01_20261014-223820-f181f893.json) records the state table, per-frame report, hashes and previews.
- **Author script:** [`…battle-animation-pilot-author_m8-anim-v01_20261014-223554-0ae02683.py`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot-author_m8-anim-v01_20261014-223554-0ae02683.py).
  - It imports the static author script **unchanged** for its palette, `Part` class and compositor.
  - It redraws the same plates at the static coordinates plus integer joint offsets: body, head, and hip / knee / foot per leg.
  - Polygon vertices are tagged by joint, so a moving knee bends the thigh and shin rather than sliding the whole leg.
  - Lens and status-light states are explicit palette paints. A few explicit 1 px effect pixels give the sparks, dust and smoke.
  - No image is read, traced, resampled or AI-generated.
  - It asserts:
    - the neutral pose reproduces the static PNG pixel for pixel;
    - every frame uses only the 17 static colours and alpha 0 / 255;
    - row 60 is the last opaque row of every frame.

| Frames | State | Motion |
| --- | --- | --- |
| 0–3 | idle (0.22 s loop) | Body sinks 1 px on bent knees with the feet planted, the eye core pulses, a scan glance shifts the pupil 1 px, and the fin twitches. |
| 4–7 | move (0.12 s loop) | Diagonal gait: the near-front and far-rear legs lift 3 px and reach forward, then the near-rear and far-front pair. The head bobs. |
| 8–9 | windup (by remaining time) | The body rears back 2–3 px, the nose lifts, and the near-front claw-foot rises 4 → 7 px. The fin flares, the eye charges white-hot and the rear and strip lights brighten. |
| 10–11 | strike (0.15 s, once) | The head rams 4 px forward and down and the raised foot stamps back onto its static spot. The hind knees push, and the eye flashes with cyan sparks in front and dust at the foot. |
| 12–13 | hit (0.12 s, once) | Jolted 2–3 px away from the party with a dome rattle. A slate shutter drops over the lens, half then quarter closed, and sparks fly off the bezel. |
| 14–16 | defeat (0.16 s, holds the last frame) | The knees splay and the body sinks 3 → 7 → 9 px. The head drops to the floor, the lens dims to dark, the lights go out, and a little smoke rises. |

Review previews (nearest-neighbour enlargements or unscaled crops, never shipped):
- [4× frame sheet](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_4x-frame-sheet_m8-anim-v01_20261014-223820-f181f893.png)
- [3× loop GIF](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_3x-loop-preview_m8-anim-v01_20261014-223820-f181f893.gif)
- **Real Godot render loop:**
  - [GIF](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_godot-render-loop-preview_m8-anim-v01_20261014-224606-86b1d5b9.gif) and [frame sheet](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_godot-render-frame-sheet_m8-anim-v01_20261014-224606-86b1d5b9.png). They are built from 17 unscaled 1280×720 viewport crops, one per frame, at runtime timings. Crop hashes are in the [note](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_godot-render-preview-note_m8-anim-v01_20261014-224606-86b1d5b9.json).
  - The crops sit in the gitignored `work/sentry-animation-godot-crops-20261014-224514/`.
  - Builder: [`…animation-godot-loop-preview-builder_m8-anim-v01_20261014-224544-4f86e754.py`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_animation-godot-loop-preview-builder_m8-anim-v01_20261014-224544-4f86e754.py).

## Runtime (`game/scripts/battle_arena.gd`)

- **New nested switch.** `ENEMY_SPRITE_ANIMATION_ENABLED := true` sits under `ENEMY_SPRITE_PILOT_ENABLED`, with an `ENEMY_SPRITE_ANIMATIONS["sentry"]` entry holding the path, state table and frame times.
- **Loading.** `_load_enemy_animation()` runs only after the static pilot has loaded. It accepts the strip only if its height equals the static cell and its width equals cell × frame count. Otherwise the static pilot stays.
- **Unchanged static path.** `enemy_texture` still holds the static pilot as the fallback cell, and the anchor (48, 60) is unchanged.
- **State selection.** `_advance_enemy_visual(delta, moved)` reads combat state and never writes to it:
  - defeat beats wind-up;
  - wind-up beats strike and hit, so the telegraph pose is never interrupted;
  - strike is triggered by `enemy_attack_count` changing;
  - hit is triggered by `enemy_hp` dropping, and does not restart while a flinch is still playing;
  - move is chosen when `enemy_x` changed this frame, otherwise idle.
- **Where it runs.** It is called from `_process` after `_update_enemy`, and also on the battle-finished path. Pause returns before it, so the animation freezes.
- **Drawing.** `_draw_enemy()` draws the strip cell with `draw_texture_rect_region` at the same origin as the static pilot. The ellipse ring and wind-up tint now also require `enemy_hp > 0`, so a sentry that dies mid-wind-up does not keep a red corpse. That changes nothing for the old paths, which never drew at 0 HP.
- **Defeat visibility.** Only an animated pilot stays drawn at 0 HP, in its defeat hold. The static pilot and block still vanish as before.
- **Mechanics untouched.** Stats, AI, approach, 53 px stop distance, 69 px reach, timers, damage, guard and dodge are unchanged, as are the arena code, contact shadows, HUD and labels.

### Reversal

Any one of these returns the sentry to the static pilot exactly:
- set `ENEMY_SPRITE_ANIMATION_ENABLED := false`;
- delete the `"sentry"` animation entry;
- set the per-instance `enemy_sprite_animation_enabled = false`;
- a missing or wrong-shaped strip.

`ENEMY_SPRITE_PILOT_ENABLED := false` still restores the placeholder block and the r30 ring.

### Static manifest

In the [static pilot manifest](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-pilot-manifest_m8-pilot-v01_20261014-221901-e3ab87f9.json):
- `runtimeIntegrated` is now `true`, which has been the truth since the integration pass;
- `scope` is rewritten, and the original text is kept as `scopeAtCreation`;
- a `runtimeIntegration` block explains the update.

The PNG, its SHA-256, the author script, its SHA-256 and `createdAt` are unchanged and were re-verified. No other file references the manifest by hash.

## Evidence

The [check/capture test](../../game/tests/rpg-2-star-ocean-the-second_sentry-automaton-animation-pilot_battle-check-capture_m8-anim-v01_20261014-224030-38da9a92.gd) exits 0 both headless (`-- --no-capture`) and windowed at 1280×720. It prints `SENTRY_AUTOMATON_ANIMATION PASS frames=17` (windowed: `captures=15 loop_crops=17`).

- **Load:**
  - the real ruins scene change opens in 317 ms;
  - the strip is 1632×62;
  - the static cell stays 96×62 at anchor (48, 60);
  - idle frame 0 equals the static pilot in alpha and opaque colour (the importer's alpha-border fix rewrites only transparent RGB);
  - the state table matches the manifest.
- **Frame audit (all 17):**
  - The last opaque row is 60 and nothing leaves the 96×62 cell.
  - Idle, strike, hit and defeat keep both near soles exactly on their static pixels. Wind-up keeps the rear sole while the front claw is raised, and every gait frame keeps a near foot on row 60.
  - Body centroid drift stays within 4 px: idle ≤ 0.15, wind-up +1.9 / +2.76 (rear-back), strike −2.0 / −1.2 (lunge), hit +1.7 / +0.8, defeat ≤ 0.9.
  - Every frame differs from the previous frame of its state.
- **Combat unchanged:**
  - stats 96 / 18 / 68 / 0.48 / 1.10;
  - approach step 6.8 px per 0.1 s;
  - the wind-up starts at 53 px and lasts 0.48 s;
  - melee 19, dodge −12, guard 60 → 54, unguarded 60 → 42;
  - a fighter at 70 px is untouched, so reach is still 69 px despite the lunge frame.
- **Simulation parity:**
  - 600 steps (10 s) of full-auto combat from the same paused start, with the animation on and off. Enemy HP was raised to 600 in both runs to lengthen the fight.
  - Enemy x, HP, wind-up, cooldown and attack count are identical at every step, and so are each fighter's x, HP and energy (`firstDifferentStep −1`).
  - The animated run passed through every state: move 83, wind-up 116, strike 72, hit 148, idle 34 and defeat 147 steps (4 enemy strikes).
- **State selection:**
  - idle loops 0, 1, 2, 3, 0 and the gait 4, 5, 6, 7, 4; stopping returns to idle;
  - wind-up shows 8, then 9 in its second half, and a hit during the wind-up keeps the wind-up pose;
  - expiry plays strike 10 → 11 while the hit lands for 18, a blow mid-strike does not interrupt it, and it returns to idle after 0.30 s;
  - hit plays 12 → 13 → idle and is not restarted by a second blow;
  - pause freezes the clock;
  - defeat plays 14 → 15 → 16 and holds 16.
- **Fallbacks:**
  - with the animation switch off, a missing strip, or a single-cell strip, the static pilot is used;
  - with the pilot switch off, the block and r30 ring return;
  - the patrol keeps its static pilot;
  - the static fallback still vanishes on defeat.
- **Telegraph:**
  - The ring stays visible around both coiled poses: 3213 / 3212 px against 1248 for the block, with halo above and beyond both sides.
  - The label bottom (y 204) clears the coiled top (y 212–213).
- **Rendering and layering:**
  - In every animated capture the on-screen sentry matches its strip frame at the anchor, including the wind-up tint. The ratio is 1.000, or 0.998 for the hit frames, where a few hero sword pixels reach the compared rear region. Contact poses compare cell x ≥ 40 because the hero covers the front.
  - At contact, every hero pixel overlapping the sentry shows the hero: strike 320/320 and 300/300, hit 409/409 and 493/493.

Each capture is listed with its SHA-256, frame, transition time and match ratio in the [capture manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_capture-manifest_m8-anim-v01_20261014-224514-b633b5de.json):

| Capture | Arena / state / frame / language |
| --- | --- |
| [idle breathe](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-idle-breathe-f0-zh_m8-anim-v01_20261014-224514-9b9c370f.png) | ruins / idle / 0 / zh |
| [idle pulse](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-idle-pulse-f2-en_m8-anim-v01_20261014-224514-104dd6af.png) | ruins / idle / 2 / en |
| [gait A](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-move-gait-f4-zh_m8-anim-v01_20261014-224514-f1157783.png) | ruins / move / 4 / zh |
| [gait B](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-move-gait-f6-zh_m8-anim-v01_20261014-224514-b11d51c9.png) | ruins / move / 6 / zh |
| [wind-up coil](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-windup-coil-f8-en_m8-anim-v01_20261014-224514-11161973.png) | ruins / windup at 53 px / 8 / en |
| [wind-up full](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-windup-full-f9-zh_m8-anim-v01_20261014-224514-a262f6e1.png) | ruins / windup at 53 px / 9 / zh |
| [strike impact](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-strike-impact-f10-en_m8-anim-v01_20261014-224514-f84f46b5.png) | ruins / strike, hero 42/100 / 10 / en |
| [strike recover](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-strike-recover-f11-zh_m8-anim-v01_20261014-224514-ea85201c.png) | ruins / strike / 11 / zh |
| [hit shutter](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-hit-shutter-f12-zh_m8-anim-v01_20261014-224514-e5d0f5b0.png) | ruins / hit from hero melee / 12 / zh |
| [hit recover](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-hit-recover-f13-en_m8-anim-v01_20261014-224514-3cea380e.png) | ruins / hit / 13 / en |
| [defeat sink, overlay hidden](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-defeat-sink-f15-inspect-zh_m8-anim-v01_20261014-224514-d2133ecc.png) | ruins / defeat / 15 / zh (result overlay hidden for inspection) |
| [defeat hold, overlay hidden](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-defeat-hold-f16-inspect-zh_m8-anim-v01_20261014-224514-95ffe7e8.png) | ruins / defeat / 16 / zh (result overlay hidden for inspection) |
| [defeat hold, as played](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-defeat-hold-f16-result-en_m8-anim-v01_20261014-224514-dc34a20b.png) | ruins / defeat / 16 / en (real result overlay) |
| [city wind-up](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_city-terrace-windup-full-f9-zh_m8-anim-v01_20261014-224514-7088e50e.png) | city-terrace / windup / 9 / zh |
| [static fallback wind-up](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-static-fallback-windup-zh_m8-anim-v01_20261014-224514-e14287f4.png) | ruins / animation off / static / zh |

**Regressions:** each of these ran headless, exited 0, printed its OK/PASS marker and had no FAIL lines.
- Milestone smokes: `m2_smoke` through `m7_smoke` and `m6_restart_smoke`.
- The five side-view combat smokes.
- The arena candidate check, the patrol pilot check, and the static sentry pilot check (`--no-capture`).

The static sentry check's windowed capture assertions were **not** re-run. They measure the static mask, and the animation now draws instead; the new test covers those cases.

The headless batch also ran the arena candidate's `runtime-crop-prep` script by mistake (a glob caught it). It re-wrote the four arena band PNGs. All four are byte-identical to their 21:37 import (MD5 matches Godot's import record), so only their modification times changed.

## Visual issues and risks (relative, not acceptance)

1. **Contact overlap hides the face.** At the unchanged 53 px stop distance the hero covers the eye, lens shutter and raised claw during the wind-up, strike and hit. The ram and rear-back body motion and the ellipse still read, but the most expressive parts are hidden. This is inherited from the static pilot; fixing it needs a spacing or layering decision.
2. **The wind-up tint mutes the charge.** The `(1.0, 0.70, 0.66)` modulate turns the white-cyan charging lens a pale beige. The telegraph reads through the ring, label, coil and raised claw rather than the eye colour.
3. **Defeat is mostly hidden.** The result overlay (88 % opacity) appears on the killing blow, so in play the defeat pose shows only dimly; the clear evidence is with the overlay hidden. The shared contact shadow is still dropped at 0 HP (arena code untouched), so the corpse has no shadow.
4. **Gait slide.** The body travels about 8 px per 0.12 s gait frame while planted feet stay fixed in the cell, so feet slide on the floor. It reads as a scuttle, not a locked planted-foot walk.
5. **Frequent flinching.** Under a four-member combo the sentry spends about 25 % of combat in the hit state. It no longer restarts mid-flinch, but it flinches often.
6. **Small effects.** The sparks, dust and smoke are single pixels. They are subtle at 2× and the smoke is barely visible.
7. **Subtle idle.** Idle is 1 px of breathing, an eye pulse, a 1 px glance and a fin twitch. That is calm by design but low-energy.
8. **Unreviewed.** Every frame, timing and state priority is a pilot choice. Creator review of the motion and a human 1280×720 play session are pending.
