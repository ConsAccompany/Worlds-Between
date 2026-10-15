# Science region: sentry automaton battle animation candidate v3 QA note

2026-10-15. v3 is an **isolated technical-art candidate**. It targets the three visual issues the [v2 QA note](rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot_qa-note_m8-anim-v02_20261014-231549-748c6de8.md) left open. It does not change any battle mechanic.

- **Art acceptance stays at 0.** No counter changed. v2 remains unapproved and awaits human review; v3 needs Codex/human review too.
- **Not wired in.** `battle_arena.gd` still loads v2 as `ENEMY_SPRITE_ANIMATIONS["sentry"]` and was not edited. A test-only [helper](../../game/tests/rpg-2-star-ocean-the-second_sentry-automaton-animation-pilot_v3-runtime-entry-helper_m8-anim-v03_20261015-041413-ef2ea159.gd) points single battle instances at v3.
- **Nothing else touched.** No v2 file changed; the v2 strip still hashes to `26d1fb1c…e52e`. The Game Bible, progress, other art and Git were not touched (nothing staged or committed).

## Issues and what v3 does

| v2 issue | Cause | v3 fix (art only) | Fully solved? |
| --- | --- | --- | --- |
| A target struck at 54–69 px is hit, but the lunge ends about 16 px short | Strike frames are chosen by state and clock only. The art cannot know the target distance; v2's lunge leads at `enemy_x − 45`. | Frame 14 keeps the v2 lunge pose and adds a cyan **claw-arc** leading at `enemy_x − 62`. Frame 15 shows its broken remnant (lead `enemy_x − 63`). | **Visually yes; physically no.** The arc reaches the target's torso band at 53, 62 and 69 px. The metal claw still stops where v2's does. A lunge that travels to the real target needs runtime code (a distance-aware draw offset or frame choice in `battle_arena.gd`), which was out of scope. |
| The charging tint obscures the eye | `ENEMY_WINDUP_MODULATE` (1.0, 0.70, 0.66) multiplies the whole sprite, so the cyan lens became a dull beige/teal disc | Frames 12–13 repaint **only the lens interior** and a four-point flare inside the bezel. Coil: a 9 px white-hot core in a dark rim. Full charge: a white ring, a cyan ring, a white core and the flare. | **Partly.** Brightness, contrast and structure recover. **No palette colour keeps its cyan hue through that multiply**, so the charging lens still reads warm. Keeping it cyan needs a runtime change (exempt the lens from the tint, or use a lighter tint) or a new non-palette colour. |
| The downed body has no grounding shadow | The runtime contact shadow is drawn only while `enemy_hp > 0` | Frames 18–20 bake an ordered-dither shadow in palette `o` (#101217), centred on the body centre and the floor line. It widens as the body settles: half-width 30 / 40 / 46 px. | **Yes, with a style caveat.** Alpha must be 0 or 255, so the shadow is a dither pattern, not the soft 42 % ellipse the live fighters use. |

### What review should look at

1. **The arc is a new design element.** It is a cyan energy crescent, not a physical claw. It ties into the eye's charge → flash, but it was not in the approved direction.
2. **The arc trades contact for occlusion.** At the AI spacing (53 px) it crosses the hero's torso during the 0.15 s impact frame, because the strike already draws in front. v3 hides 177 hero body pixels there; v2 hid 86.
3. **Variants rejected for the full-charge lens.** A fully white disc measured brighter (luma 0.632) but read as a blank plate. A crosshair version read as a sniper scope.

## Asset

- **Strip:** [`…battle-animation-strip-left_m8-anim-v03_20261015-041706-53479e75.png`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v03_20261015-041706-53479e75.png)
  - 2772×66, which is 21 cells of **132×66**;
  - SHA-256 `47db0317f1beadd44ca3463a080c9cc81240497e4a4fd1c8790baba9d30369b2`;
  - imported with the default lossless settings.
- **Per-frame PNGs:** in [`frames_m8-anim-v03_53479e75/`](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/frames_m8-anim-v03_53479e75/), with a `.gdignore`. Each is byte-checked against its strip cell.
- **[Manifest](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-manifest_m8-anim-v03_20261015-041706-53479e75.json)** and **[author tool](../../game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot-author_m8-anim-v03_20261015-041413-21ec8744.py)**. The tool imports the v2 author unchanged. It swaps only the two wind-up lens paints, then fills transparent pixels with the arc and shadow. No image is traced, resampled or AI-generated.
- **Previews:** no contact sheet, collage or GIF. Review uses the separate Godot captures below.

### Layout

- **Cell:** the v2 cell sits 20 px from the left (room for the arc) on a canvas 4 px taller (room for the shadow).
- **Runtime entry** (`cell` 132×66, `anchor` (66, 60), `body_center_x` 84): these keys already exist in the runtime. They move with the margin, so **the sprite, wind-up ring and contact shadow draw exactly where v2 draws them**.
- **Unchanged from v2:** `states`, `frame_time`, `gait_step_px`, `move_grace` and `front_states` are copied from the runtime's own v2 entry.

### What changed, per frame (asserted by the author tool and re-checked in Godot)

| Frames | State | Change from v2 |
| --- | --- | --- |
| 0–11 | idle, distance-keyed gait | none (pixel-identical) |
| 12, 13 | wind-up | 88 and 78 lens/flare pixels inside the bezel. Silhouette, outline and every other pixel unchanged. |
| 14 | strike impact | +111 arc pixels on transparent pixels only |
| 15 | strike recoil | +28 arc-remnant pixels on transparent pixels only |
| 16, 17 | hit | none (pixel-identical) |
| 18, 19, 20 | defeat | +107 / +191 / +203 shadow pixels on transparent pixels only, up to 4 rows below the floor row |

- **Palette:** the same 17 colours; alpha is only 0 or 255.
- **Rows:** row 60 is the last body row of every frame. Only the defeat shadow uses rows 61–64.

## Evidence

The [v3 check/capture test](../../game/tests/rpg-2-star-ocean-the-second_sentry-automaton-animation-pilot_battle-check-capture_m8-anim-v03_20261015-041413-fb7f4e25.gd):
- **Headless** (`-- --no-capture`): exits 0 with 149 PASS lines and no FAIL.
- **Windowed** at 1280×720 with `--fixed-fps 60`: exits 0 with 198 PASS lines. It prints `SENTRY_AUTOMATON_ANIMATION_V3 PASS frames=21 captures=18`.
- **Report:** the [capture manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_capture-manifest_m8-anim-v03_20261015-042119-ae4ce2a0.json).

### Combat unchanged (parity)

- **Rules with v3 applied:**
  - stats 96 / 18 / 68 / 0.48 / 1.10;
  - approach step 6.8 px;
  - the wind-up starts at 53 px and lasts 0.48 s;
  - melee 19, dodge −12, guard 60 → 54, unguarded 60 → 42;
  - a fighter at **69 px is hit** and one at 70 px is untouched;
  - the hero hits at 61 px and misses at 62 px.
- **Simulation:** 600 steps of full-auto combat with **v3, the v2 default and the animation off** give identical traces: enemy x, HP, wind-up, cooldown, attack count, and every fighter's x, HP and energy (`firstDifferentStep −1` for both comparisons).
- **Visual states:** v3 and v2 pass through identical visual-state counts (move 83, wind-up 116, strike 72, hit 148, idle 34, defeat 147).
- **State selection:**
  - idle 0–3;
  - gait 4–11, then 4, by distance;
  - wind-up 12 then 13, behind the fighters;
  - a target backed off to 69 px is hit for 18 while frame 14 draws in front;
  - strike 15, then idle after 0.30 s;
  - hit 16, 17, then idle;
  - defeat 18–20, holding 20.
- **Fallback:** the v3 strip under the v2 cell keys fails the runtime's shape gate, so the static pilot stays.

### Gait and zero slip (preserved)

| Real approach, 60 fps | v2 | v3 |
| --- | --- | --- |
| Distance walked | 140.53 px | 140.53 px |
| Frames with a near foot grounded | 124 / 124 | 124 / 124 |
| Planted-foot slip | 0.0 px over 115 pairs | **0.0 px** over 115 pairs |

The grounded feet land on the same world pixels in v2 and v3 on every walking frame.

### Strike reach (real renders; the target takes the hit for 18 in every case)

The wind-up starts at the 53 px AI stop. A player-steered hero can then back off during the 0.48 s wind-up (168 px/s), and anything up to 69 px is still hit.
- **Lead** is where the strike's leftmost pixel sits, relative to `enemy_x`.
- **Body contact** counts target pixels covered by the sentry or arc, excluding the bottom 6 rows (feet and ground sparks). Every contact pixel shows the sentry on top.

| Target at | v2 lead / body contact | **v3 lead / body contact** |
| --- | --- | --- |
| 53 px | −45 / 86 px | **−62 / 177 px** |
| 62 px | not captured | **−62 / 69 px** |
| 69 px | −45 / **0 px** (24 px short of the target centre) | **−62 / 14 px** (7 px short of the target centre, inside its torso band) |

All 111 arc pixels show on screen in every impact capture.

### Charging lens under the unchanged wind-up tint (real renders)

Metrics are the mean Rec.709 luma of the on-screen lens disc (137 px), and its contrast against the dark eye housing.

| Capture | Lens luma | Lens − housing | Bright share (≥ 0.6) |
| --- | --- | --- | --- |
| Idle, untinted (reference) | 0.456 | 0.266 | 0.343 |
| v2 coil, f12 | 0.456 | 0.313 | 0.175 |
| **v3 coil, f12** | **0.489** | **0.346** | **0.431** |
| v2 full charge, f13 | 0.492 | 0.348 | 0.358 |
| **v3 full charge, f13** (ruins and city terrace) | **0.564** | **0.420** | **0.591** |

The coil improvement is modest. The full charge is clearly brighter than v2, and brighter than the untinted idle lens.

The ring stays visible around both coiled poses: 3213 and 3212 px, against 1248 for the block. The label bottom clears the coiled top.

### Defeat shadow (real renders, result overlay hidden for inspection)

- All 107 (f18) and 203 (f20) shadow pixels show on screen in the shadow colour.
- At the 91 shadow positions below the floor row, the v2 capture shows bare floor (mean luma 0.373). In v3 those positions are shadow.
- With the result overlay shown, as played, the overlay dims the shadow along with the corpse.

### Captures

These are separate 1280×720 PNGs in `outputs/`, named `…sentry-automaton-animation-pilot_<case>_m8-anim-v03_20261015-042119-*.png`. Their hashes are in the capture manifest.

**v3:**
- idle f0;
- gait f4;
- wind-up coil f12;
- wind-up full f13 (ruins and city terrace);
- impact f14 with the target at 53, 62 and 69 px;
- recoil f15 at 69 px;
- flinch f17 under the sword thrust;
- defeat f18 and f20 (overlay hidden);
- defeat f20 as played.

**v2 comparisons** at the same positions:
- coil f12 and full charge f13;
- impact at 53 and 69 px;
- defeat f20.

### Regressions and side effects

- **v2 test:** still exits 0 headless (`SENTRY_AUTOMATON_ANIMATION_V2 PASS`).
- **Import side effects:** the headless `--import` that imported the v3 strip also created `.uid` sidecars for 7 scripts belonging to other workstreams. Those 7 were removed, verified by a before/after `git status` diff. Kept:
  - the v3 strip's `.import`;
  - the `.uid` files of the two v3 scripts.

## Still open (not acceptance)

1. The charging lens cannot stay cyan under the current tint without a runtime change.
2. The physical claw still stops at `enemy_x − 42`; the arc supplies the contact. A target-aware lunge needs runtime code.
3. The arc covers the hero's torso for 0.15 s at 53 px.
4. The shadow is dithered, not soft. It does not exist under the legacy no-arena backdrop while alive, as in v2.
5. All v2 caveats not listed here carry over unchanged:
   - the 18 px offset;
   - the strike draw-order switch;
   - pose pops at the gait edges;
   - the flinch frequency;
   - player-steered overlap.
6. To trial v3 in play, add the four visual keys from the helper to the runtime entry. That is a `battle_arena.gd` change, left for review.
