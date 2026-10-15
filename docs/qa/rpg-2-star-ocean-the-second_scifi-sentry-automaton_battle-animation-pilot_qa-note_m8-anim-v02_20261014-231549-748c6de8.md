# Science region: sentry automaton battle animation pilot v2 QA note

2026-10-14. The creator watched the real Godot v1 loop GIF and replied "方向可以，继续修正遮挡与滑步" (direction works; keep fixing the occlusion and the foot sliding). This is **not** animation acceptance.

v2 is a focused refinement of the [v1 pilot](rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot_qa-note_m8-anim-v01_20261014-224818-0c3444ce.md) that fixes those two problems.
- **Art acceptance stays at 0** and no counter changed.
- Human review of v2 is pending.
- Every v1 file is unchanged. The v1 strip still hashes to `7b6bc0c4…4e9a`.
- No Game Bible, progress, readiness, protagonist, walk or hash-portability file was touched. The patrol keeps its static pilot.

## Diagnosis

1. **Occlusion.** The 96 px sentry was drawn centred on `enemy_x` (anchor x 48), so its eye (cell x 10–30) sat 18–38 px in front of its logical position. At the AI melee spacing, the hero's body and sword sit exactly there:
   - the sentry stops 53 px from its target;
   - the hero (range 61) closes to 53 px;
   - Liang Xu (range 65) closes to 57 px.
2. **Foot slide.** v1 played four gait frames on a 0.12 s timer while the body travelled about 8 px per frame. Its planted feet were fixed in the cell, so they slid along the floor with the body.

## Fix (visual only; no combat rule changed)

### Asset

- **Strip:** [`…battle-animation-strip-left_m8-anim-v02_20261014-230329-ffefdc6f.png`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v02_20261014-230329-ffefdc6f.png), 2352×62 = 21 cells of **112×62**, SHA-256 `26d1fb1c…e52e`. The default lossless import applies.
- **Per-frame files:** each frame is also its own PNG in [`frames_m8-anim-v02_ffefdc6f/`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/frames_m8-anim-v02_ffefdc6f/).
  - A `.gdignore` keeps Godot from importing them; the runtime reads only the strip.
  - Names are shortened to stay under the 260-character Windows path limit.
  - The author asserts that each frame file is byte-identical to its strip cell.
- **Manifest:** [`…battle-animation-manifest_m8-anim-v02_20261014-230329-ffefdc6f.json`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-manifest_m8-anim-v02_20261014-230329-ffefdc6f.json).
- **Author script:** [`…battle-animation-pilot-author_m8-anim-v02_20261014-225908-7e2215bc.py`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot-author_m8-anim-v02_20261014-225908-7e2215bc.py). It imports the static author script unchanged and only widens its canvas globals to 112 px.
- **Cell layout:** the unchanged 96×62 plates sit 16 px from the left edge, which leaves room for the strike to lunge.
- **Author assertions:**
  - same 17 colours, alpha only 0 or 255;
  - row 60 is the last opaque row of every frame;
  - frame 0 equals the static pilot pixel for pixel;
  - **the idle, wind-up, hit and defeat frames are the v1 cells exactly**.

| Frames | State | v2 change |
| --- | --- | --- |
| 0–3 | idle (0.22 s loop) | none (v1 poses) |
| 4–11 | move | **New 8-frame diagonal gait driven by distance, not time.** One frame per 4 px step, one 32 px cycle. That is about 2.1 cycles/s at 68 px/s, roughly v1's cadence. A foot in stance moves exactly +4 px backward in the cell per step. The near-front foot lands on its static spot and pushes 12 px back; the near-rear foot lands 12 px forward and pushes back to its static spot; the far feet stroke 6 px either side of their static spots. Knees follow halfway, and the body dips 1 px as each pair lands. |
| 12–13 | wind-up | none (v1 poses) |
| 14–15 | strike | **Larger lunge.** Impact: body 7 px and head 11 px forward and down, and the raised claw stamps 13 px ahead of its static spot, with sparks and dust. Recoil: the claw lifts back to −6 px and the body draws back. The rear soles never move. |
| 16–17 | hit | none (v1 poses) |
| 18–20 | defeat | none (v1 poses) |

Review previews (nearest-neighbour enlargements, never shipped):
- [4× sheet](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_4x-frame-sheet_m8-anim-v02_20261014-230329-ffefdc6f.png), which marks the anchor row and the runtime anchor;
- [3× GIF](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_3x-loop-preview_m8-anim-v02_20261014-230329-ffefdc6f.gif), where the gait walks 4 px per step over a ticked floor.

### Runtime (`game/scripts/battle_arena.gd`, sentry animation entry only)

The `ENEMY_SPRITE_ANIMATIONS["sentry"]` entry gains optional keys. The v1 code paths remain the default when a key is absent:
- **`cell` (112, 62) and `anchor` (46, 60).** The loader checks strip width against `cell.x × frames` (the static size by default). Anchor x 46 is static x 30, so the animated sprite draws **18 px further from the party**. The static fallback keeps anchor 48.
- **`body_center_x` 64.** The wind-up ring and the sentry's contact shadow centre on the drawn body (`enemy_x + 18`). They are unchanged for the static pilot and the block.
- **`gait_step_px` 4.** The gait frame is `round((gait origin − enemy_x) / 4) mod 8`.
  - The cell is drawn at the step position, at most 2 px from `enemy_x`, so stance feet hold one floor pixel.
  - Backing away plays the gait in reverse.
  - **`move_grace` 0.08 s** keeps the gait pose through a one-frame stop, so the sentry does not flicker to idle.
- **`front_states` ["strike"].** During its own strike the sentry draws over the fighters. Everywhere else (idle, move, wind-up, hit, defeat) the fighters stay on top, as before.
- **What stays the same:** `_advance_enemy_visual` still only reads combat state. Stats, AI, the 53 px stop distance, the 69 px strike reach, hero melee ranges (still measured from `enemy_x`), timers, damage, guard and dodge are unchanged.

**Gameplay change: none.** The sentry's logical position, every distance check and all timing are untouched (simulation parity below). The visible change, quantified:

| What changed on screen | Amount |
| --- | --- |
| Sprite drawn further back | 18 px (static x 30 now sits on `enemy_x` instead of x 48) |
| Ring and contact shadow | moved +18 px |
| Gait draw position | quantized to 4 px steps, at most ±2 px from `enemy_x` |
| Snap when the walk ends | at most 2 px (0 in the measured approach) |
| Draw order | sentry over the fighters for 0.30 s per strike |

**Reversal:**
- `ENEMY_SPRITE_ANIMATION_ENABLED := false` (or the per-instance flag), deleting the entry, or a missing or wrong-shaped strip each return the static pilot exactly.
- Pointing the entry back at the v1 strip and dropping the v2 keys (`cell`, `anchor`, `body_center_x`, `gait_step_px`, `move_grace`, `front_states`) restores v1 behaviour. The v2 test replays v1 this way for its comparisons.

## Evidence

The [v2 check/capture test](../../game/tests/rpg-2-star-ocean-the-second_sentry-automaton-animation-pilot_battle-check-capture_m8-anim-v02_20261014-230639-ad3f9d97.gd) exits 0 headless (`-- --no-capture`). It also exits 0 windowed at 1280×720 with `--fixed-fps 60`, printing `SENTRY_AUTOMATON_ANIMATION_V2 PASS frames=21 captures=15 crops=57` (366 PASS lines). The full report is the [capture manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_capture-manifest_m8-anim-v02_20261014-231314-e205c276.json).

### Foot slide

The sentry walks in to its 53 px stop in real enemy code at 60 fps and winds up. Planted-foot world positions come from the strip's anchor-row pixels at every rendered frame.

| | v1 replay (same runtime, v1 entry) | **v2** |
| --- | --- | --- |
| Distance walked | 140.5 px (124 frames) | 140.5 px (124 frames) |
| Planted-foot slip | **187 px** over 172 grounded frame pairs | **0.0 px** over 115 grounded frame pairs |
| Near foot on the floor | every frame | every frame |
| Drawn x minus `enemy_x` | ≤ 0.5 px | ≤ 2 px |

Strip audit: in every gait step pair where a near foot stays grounded (6 per cycle), its sole run moves back exactly 4 px in the cell. The author asserts the same for all four feet from the pose data.

### Occlusion

Eye bezel and claw boxes, measured as the share of the sentry's own pixels that are visible on screen. Rows marked "real" are measured on the real 1280×720 renders: wind-up and strike have the hero at 53 px, and the flinch has the hero mid-attack.

| Pose (real 1280×720) | v1 replay eye / claw | **v2 eye / claw** |
| --- | --- | --- |
| Wind-up coil, hero idle | 0.941 / 0.583 | **1.000 / 0.869** |
| Wind-up full, hero idle | 0.973 / 0.615 | **1.000 / 0.815** |
| Strike impact, hero hit | 0.692 / 0.692 | **1.000 / 1.000** |
| Strike recoil, hero hit | 0.739 / 0.689 | **1.000 / 1.000** |
| Flinch 1, hero attack phase 1 | 1.000 / 0.376 | **1.000 / 0.995** |
| Flinch 2, hero sword thrust | 0.576 / 0.371 | **0.866 / 0.995** |

The [offline analysis](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_contact-occlusion-analysis_m8-anim-v02_20261014-231542-e6167637.json) covers every native hero, female hero and Liang frame at their real AI spacing ([script](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_contact-occlusion-analysis_m8-anim-v02_20261014-230600-3c1f9a47.py)). Mean / max share of the region covered:

| | v1 | v2 |
| --- | --- | --- |
| Wind-up claw (hero idle) | 0.37 / 0.42 | 0.11 / 0.19 |
| Strike eye (hero hit) | 0.22 / 0.31 | 0 |
| Strike claw (hero hit) | 0.27 / 0.31 | 0 |
| Flinch eye (hero attack) | 0.17 / 0.43 | 0.03 / 0.13 |
| Flinch claw (hero attack) | 0.50 / 0.62 | 0.04 / 0.18 |
| Flinch eye (hero skill) | 0.36 / 0.64 | 0.01 / 0.08 |

The 18 px spacing does most of the work: without the strike draw-order rule, the v2 strike eye is at most 9.5 % covered and the claw at most 33.5 %.

### Draw order (real renders)

- **Strike:** the sentry shows on every overlapping pixel, 127/127 at impact and 26/26 at recoil. It hides 127 of the hero's 2045 opaque pixels at impact.
- **Flinch:** the hero stays on top, 5/5 and 79/79.

### Combat unchanged

- **Rules and numbers:**
  - stats 96 / 18 / 68 / 0.48 / 1.10;
  - approach step 6.8 px per 0.1 s;
  - the wind-up starts at 53 px and lasts 0.48 s;
  - melee 19, dodge −12, guard 60 → 54, unguarded 60 → 42;
  - a fighter at 70 px is untouched (69 px reach);
  - the hero hits at 61 px and misses at 62 px from `enemy_x`.
- **Simulation parity:** 600 steps of full-auto combat with the animation on and off give identical enemy x, HP, wind-up, cooldown and attack count, and identical fighter x, HP and energy (`firstDifferentStep −1`). The animated run passed through move 83, wind-up 116, strike 72, hit 148, idle 34 and defeat 147 steps.

### State selection

- idle loops 0–3;
- walking gives frames 4–11, then 4, by distance; backing away gives 4, 11, 10, 9;
- a 0.05 s stop holds the gait frame, and a real stop returns to idle at `enemy_x`;
- wind-up shows 12 then 13 behind the fighters, and a hit during the wind-up keeps the pose;
- expiry plays strike 14 in front while the hit lands for 18, the strike continues to 15 through a blow, and it returns to idle behind the fighters after 0.30 s;
- a flinch plays 16, 17 behind the attacker, then idle, unrestarted by a second blow;
- pause freezes the clock;
- defeat plays 18–20 and holds 20.

### Telegraph

- The ring stays visible around both coiled poses: 3213 / 3212 px against 1248 for the block, with halo above and beyond both sides.
- The label bottom clears the coiled top.

### Fallbacks (all pass)

- each of these keeps the static pilot at anchor 48 with no offset: the animation switch off, a missing strip, a single-cell strip, or the v1 strip under the v2 entry (wrong cell width);
- with the pilot switch off, the block and r30 ring return;
- the patrol keeps its static pilot;
- the static fallback still vanishes on defeat.

### Captures

Real captures (1280×720, listed with hashes in the capture manifest):
- idle;
- gait 4 and 8;
- wind-up coil and full (ruins and city terrace);
- strike lunge and recoil;
- flinch shutter, and flinch under the sword thrust;
- defeat with the overlay hidden and as played;
- static-fallback wind-up;
- two v1-replay comparisons.

### Godot loop previews

Built from unscaled real crops by the [builder](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_animation-godot-loop-preview-builder_m8-anim-v02_20261014-231500-5b0e8c21.py); crop hashes are in the [note](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_godot-render-preview-note_m8-anim-v02_20261014-231330-2852d3e8.json).
- **[Solo loop](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_godot-render-loop-preview_m8-anim-v02_20261014-231330-2852d3e8.gif).** Its walk section is 16 real consecutive gait steps in a fixed window, so the floor stays put.
- **[Contact loop, v2](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_godot-render-contact-loop_m8-anim-v02_20261014-231330-2852d3e8.gif).** The hero stands at 53 px through the wind-up, the strike, the hero's blow, the flinch and back to idle.
- **[Contact loop, v1 replay](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_godot-render-contact-loop-v1-replay_m8-anim-v02_20261014-231330-2852d3e8.gif)** is the same sequence, for comparison.
- **Where the crops are:** the 57 crops (21 solo, 16 walk, 10 + 10 contact) are separate files in the gitignored `work/sentry-animation-v2-godot-crops-20261014-231314/`.

### Regressions

Each of these ran headless, exited 0, printed its OK/PASS marker and had no FAIL lines:
- `m1_smoke` through `m7_smoke` and `m6_restart_smoke`;
- the three `m8_city_*` smokes;
- the five side-view combat smokes;
- the arena candidate check, the patrol pilot check and the static sentry pilot check (`--no-capture`);
- the v2 test.

The **v1 animation test passes**. It first asserts that the runtime default is the v2 strip, then uses a test-only [helper](../../game/tests/rpg-2-star-ocean-the-second_sentry-automaton-animation-pilot_v1-runtime-entry-helper_m8-anim-v01_20261014-232137-297784ce.gd) to point each sentry battle at v1 without changing `battle_arena.gd`. It exits 0 headless (`-- --no-capture`). It also exits 0 windowed at 1280×720 with `--fixed-fps 60`, printing `SENTRY_AUTOMATON_ANIMATION PASS frames=17 captures=15 loop_crops=17` (238 PASS lines, no FAIL). Every v1 still matches its strip frame at 0.998 or better, and the hero draws over the sentry on all four strike/hit frames. The 15 capture SHA-256 hashes in the [v1 replay manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_capture-manifest_m8-anim-v01_20261014-232537-40220ad3.json) match the files. The v2 test supersedes it as the runtime default.

### Side effect

The headless `--import` pass that imported the v2 strip also gave three test scripts the `.uid` sidecars Godot generates for scripts that lack one:
- the v1 animation test;
- `…south-walk-pilot-capture_m8-w01…`;
- `…paving…selout-v8-ab…`.

They are inert metadata. They were left in place, not deleted.

## Remaining overlap and slide (relative, not acceptance)

1. **Sword over the shutter.** On the flinch frame that coincides with the hero's sword thrust (0.13 s), the blade tip crosses the bezel: 0.866 of the eye is visible. Skill phase 3 covers up to 8 %.
2. **Low sword over the raised claw.** During the wind-up, the hero's low-held idle sword covers up to 18.5 % of the raised claw (0.815–0.869 visible).
3. **The strike hides the hero's front.** That is intended, but it is a visible draw-order switch for 0.30 s.
4. **Gaps beyond 53 px.**
   - The lunge face reaches about `enemy_x − 33`, and the stamped claw `enemy_x − 42`. That makes visual contact with a target at ≤ 53 px (idle pose) or ≤ 62 px (hit pose).
   - A target struck at 54–69 px is still hit by the unchanged 69 px reach, but the lunge falls short by up to about 16 px.
   - AI targets are normally at ≤ 53 px.
5. **A player-steered hero can still walk into the sentry.** There is no collision, so the overlap cannot be prevented at any spacing.
6. **Pose pops at the gait edges.** Starting or stopping the walk pops between gait pose and idle pose, as in v1, with at most a 2 px position snap. The far feet are locked by construction (author assertion) but are pixel-verified only via the near feet, since they never touch row 60.
7. **Wider sprite footprint.** The sprite now reaches 18 px further right (last opaque pixel at `enemy_x + 64`). That is still on screen at the start position (557 px); a sentry pushed to the 612 px clamp would clip, as v1 already did beyond 640.
8. **Unchanged v1 risks.**
   - the wind-up tint mutes the charging lens;
   - the result overlay dims the defeat pose;
   - the corpse has no shadow;
   - the sparks and smoke are single pixels;
   - the flinch is frequent.
9. **Unreviewed.** The gait, the lunge, the 18 px offset and the strike draw order are pilot choices. Creator review of the v2 loops and a human 1280×720 play session are pending.
