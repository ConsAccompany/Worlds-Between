# Female protagonist south RUN v03: test-only single-direction motion pilot (QA note, m8-w06)

**Status: UNAPPROVED / NONRUNTIME. This is a test-only motion pilot, not a production sprite and not a runtime replacement.**
- Every manifest and receipt flag is `false`: `art_approved`, `human_reviewed`, `runtime_integrated`, `walk_animation_approved`, `run_animation_approved`, `stop_animation_approved` and `counts_toward_art_acceptance`.
- Only Claude reviewed this, as an agent. That is not a human or creator review. **Nothing here is accepted. Exploration sprites stay 0/52.**
- Not touched: the approved v8 static PNG (byte-identical, `ccf9d2a2…68b6fd`), `MOVE_SPEED`, the other directions and characters, maps, Washington art, Game Bible code and data, `docs/progress.md` and the progress meter.
- No staging, commit or push.

**Auth.** Checked first with `claude auth status`: `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. `ANTHROPIC_API_KEY` was unset. No API billing, credits or paid fallback was used.

**Read first:**
- the global `~/.codex/AGENTS.md` naming rule (the repo has no AGENTS.md);
- the approved v8 south idle static evidence (`docs/progress.md` decision, v8 QA note, v8 PNG and its hash);
- the v02 technical QA note (`…south-locomotion-compact-v02_part-compositor-zero-slip-run_qa-note_m8-w05_20261016-200500-4993d9e9.md`);
- `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v02-codex-motion-review_unapproved-v01_20261016-191300-7a02d91c.md`.

## Verdict (agent judgment, for Codex review)

**Run, not walk.** At 140 logical px/s, v03 is a deliberate **run**.
- A zero-slip planted boot can only stay down while the leg absorbs the body's travel: 22 window px here, which is 79 ms.
- So the gait keeps a flight phase: **54 % of the cycle has both boots off the floor** (v02: 58 %), at the same 5.83 steps/s as v02.
- A zero-slip walk with no flight would need a stride of at most 44 window px, about 12.7 steps/s. That is not believable, so the speed was **not** changed.

**Does it look better at 1x?** Modestly better on the specific defects Codex listed, but not solved. I compared same-tick v02/v03 strips and in-engine stills at 1x–4x. I **cannot play the GIF/MP4 files in real time**, so the real-time read still needs Codex's eye.

What is visibly better:
- **The rear leg no longer reads as a raised knee.** v02 crushed only the thigh and kicked a dark "sole" block up under the knee. v03 foreshortens the whole rear leg (thigh, knee guard and shin all lose rows in proportion), so the guard tucks under the coat. The boot shows a heel-up or toe view on the floor.
- **The swing foot stays low:** lift is at most 3 rows (v02: 8), with no kicked-up block.
- **Floor contact is readable.** A small ink contact shadow (opacity 0.38) sits under each boot, also under the v8 idle. Flight now shows as a 1–3-row gap above the shadow instead of a floating boot.
- **The upper body moves with the stride:**
  - shoulders, torso, scarf and arms shift 1 texel toward the planted boot, while the head stays steady;
  - the cape follows about 34 ms late;
  - the arms use five poses (B2…F2) instead of three.
- **The forward boot is smaller and higher:** it overhangs v8's ground row by 6 rows (3 logical px), not 8. Hand-authored compact strike/reach boots replace v02's tread-block forward boot.
- **The stop has a single low weight-shift.** The airborne boot lands, then the off-spot boot takes one shuffle step (lift 1 for an offset of up to 3 rows). The torso leans over the weight-bearing boot, the body dips one row for 34 ms, and then the v8 PNG takes over with 0 changed pixels.

What is not better, or is worse:
- **The cadence is still a quick 5.83 steps/s with 54 % flight.** It reads as a light jog/run, not calm exploration.
- **The motion is busier.** The largest per-tick silhouette change at 60 fps went from 268 to 388 pixels (arms, torso shift and roll views). At 1x this may read as livelier, or as jitter.
- **Stops released mid-flight are slower than v02:**

  | Stop at 60 fps | v02 | v03 |
  |---|---|---|
  | released in flight | 117–133 ms | 200–217 ms |
  | released in stance | 233–267 ms | 233–250 ms |

  About the last 50 ms is hair/cape follow-through with the feet already planted.
- **The forward leg is still long and straight** at contact (hip to sole 48 rows versus 42), made of repeated v8 thigh rows.
- **The steady head means a 1-texel neck shear while the torso is shifted.** Single closed holes there are filled with ink.
- **The shadow is a test-only overlay.** The runtime has no shadow system; adding one is a runtime-owner decision. The v8 approval did not cover a shadow.

## What changed from v02

| | v02 (m8-w05) | v03 (m8-w06) |
|---|---|---|
| State name | "locomotion" (a run in fact) | **run**, by name (manifest `motion_state`) |
| Contact | +8 → −12 rows, 20 px, 71 ms, view v8 only | **+6 → −16 rows, 22 px, 79 ms**; the view rolls strike → v8 → heelup → toe on the same pinned lowest row |
| Flight | 100 ms per step, 58 % of the cycle | 93 ms per step, **54 %** of the cycle |
| Swing | lift up to 8 rows, kicked-up `sole` block | **lift 1–3**, views toe / hang / reach / strike, no `sole` |
| Short (rear) leg | thigh rows dropped, knee guard kept whole | **proportional foreshortening** of thigh, knee band (min 5 rows) and shin |
| Upper body | fixed except bob; arms B1 / N / F1 | **torso / scarf / arms ±1 texel toward the planted boot, head steady; cape lags; arms B2…F2** |
| Ground cue | none | **per-foot contact shadow**, a separate part, drawn under the sprite and the v8 idle |
| Forward boot | v01 rows with tread block, overhang 8 rows | **hand-authored compact strike / reach**, overhang 6 rows |
| Stop | land, then shuffle (lift ≤ 4) | land (lift ≤ 2), then shuffle (lift 1 if offset ≤ 3, else 2), torso weight shift, 1-row settle dip, arms step together |
| Re-press | last-landed boot stays planted | same rule (kept) |

Kept from v02, unchanged in method:
- the part library cut 1:1 from v8 (32 colours, binary alpha, no resampling or generative redraw);
- the body drawn at the logical position;
- the distance-driven phase;
- the test-only GDScript compositor.

Not a frame bank:
- 62 part PNGs plus 12 review keyframes and 12 keyframe shadows;
- stop and re-press are rules, not 187 stop frames.

## Measurements (real Godot 4.7.2, windowed)

**Capture setup:**
- the project's 640×360 canvas rendered in its 1280×720 window (integer `canvas_items` stretch), sprite scale 0.5, `TEXTURE_FILTER_NEAREST`;
- the hero is moved by each scene's own `_process` with `move_down` held, measured at **140.000 logical px/s**;
- scenes: **city-bright** (science city) and **annex-dark** (city survey annex room 2).

**Capture gates (all passed, exit 0):**
- GDScript compositor equals v8 at the neutral state, and equals all 12 builder keyframes and their shadows;
- the steady-state gait equals the manifest's per-px table on 154 ticks;
- exact-RGB fidelity of the drawn character on every captured tick;
- straight-south movement, and the hero stationary without input.

**Planted boot (measured on captured pixels; identical in both scenes):**

| fps | Planted tick pairs (with a roll-view change) | Lowest-row world Δ | Sole x-extent Δ, same view | Boot texels changed, same view | Sole x-extent Δ at a roll change |
|---|---|---|---|---|---|
| 60 | 18 (12) | **0** | **0** | **0** | ≤ 2 px |
| 30 | 7 (6) | **0** | **0** | **0** | ≤ 2 px |
| 144 | 48 (14) | **0** | **0** | **0** | ≤ 2 px |

- **The roll caveat, said plainly:** when the planted boot changes view (strike → v8 → heelup → toe), its lowest row stays pinned, but the sole row's x-extent changes by up to 2 px as the heel or toe outline changes. While the view holds, nothing moves.
- **Airborne ticks while moving:** 28/50 at 60 fps, 14/25 at 30 fps, 68/120 at 144 fps.

**Immediate stops** (60 fps every tick of one stride in both scenes, plus 30 / 144 fps in city-bright; 70 cases):

| fps | Cases | Released in flight → v8 PNG | Released in stance → v8 PNG | Longest time a boot stays raised | Max lift | Switch to v8 |
|---|---|---|---|---|---|---|
| 60 | 42 | 200–217 ms | 233–250 ms | 83 ms | 3 | **0 px** |
| 30 | 11 | 300 ms | 300 ms | **100 ms** (at the gate limit) | 2 | **0 px** |
| 144 | 17 | 146–153 ms | 181–188 ms | 69 ms | 3 | **0 px** |

- **No prolonged raised foot:** after a release, no boot stays off the floor longer than 100 ms. That is a gate in both the capture tool and the check.
- **Planted boots during stops:** pinned as above.
- **Silhouette change per tick:** the stop maximum is below the run maximum at each fps:

  | fps | Stop max | Run max |
  |---|---|---|
  | 60 | 285 | 388 |
  | 30 | 319 | 495 |
  | 144 | 328 | 349 |

**Immediate re-press** (city-bright 6 release phases × gaps 1/2/3/5/8/14/30 ticks; annex-dark 3 × 4; 54 cases):
- In **54/54** cases the next touchdown is the other boot.
- The last-landed boot stood at least 67 ms.
- The next touchdown comes 33–150 ms after the re-press.
- The planted boot stays pinned throughout.

**Display and collision bounds:**
- Frames reach at most cell row 109 (108 seen in the captures). That is 6 rows (**3 logical px**) below v8's ground row; the shadow reaches row 111.
- The standing v8 frame and the 48 px display scale are unchanged.
- Runtime collision is the hero's foot point (`CityNavigation` and the annex clamps). It is unchanged: the pilot is display-only and never feeds back into movement.
- The forward overhang has not been checked against neighbouring props in a playable scene.

**Contact shadow:** at least 52 shadow pixels outside the character are darker than the sprite-free background on every tick, in both scenes. The shadow is subtle on the busy city paving and clearer on the annex floor.

## Import and filtering (isolated copy)

- A copy of `game/` without `.godot` was made under `%LOCALAPPDATA%\Temp\wb-rv03-imp-d2169050`, and the pilot's `.gdignore` was removed there only.
- `Godot --headless --import` exited 0. The validation tool then printed `RUN_V03_IMPORT PASS`:
  - 86 PNGs imported lossless (`compress/mode 0`), with no mipmaps;
  - alpha and every opaque texel are identical to the PNG files. `fix_alpha_border` rewrote the RGB of alpha-0 texels only;
  - the project's default canvas filter is Nearest.
- The copy was deleted afterwards.
- In the shared tree the asset folder keeps an empty `.gdignore`. No `.import` or `.uid` file was created, and the sha256 of `game/scripts`, `game/scenes` and `project.godot` is identical before and after.

## Focused check: 27/27 OK

The check was run with `--pixelorama --receipt <capture receipt> --import-receipt <import receipt>`. It covers:
1. source identity: v8 sha256-bytes plus `git diff --quiet HEAD` on the v8 file;
2. a byte-identical rebuild;
3. manifest LF, flags, run-not-walk and hashes;
4. alpha and palette: character PNGs inside v8's 32 colours with binary alpha; shadow PNGs in a single ink colour with binary alpha;
5. an independent compositor re-implementation that rebuilds v8 and every keyframe and shadow;
6. head and torso identity;
7. nominal foot pinning and the roll order;
8. display/collision bounds, MOVE_SPEED 140 and no runtime reference;
9. `.ora` structure;
10. Pixelorama 1.2.3 headless with an isolated APPDATA:
    - the `.pxo` `--split-layers` export gives 156 layer PNGs (12 frames × 13 layers);
    - the character layers restacked equal the keyframe PNGs, and the shadow layer equals the shadow PNGs;
    - the `.ora` `--split-layers` export equals the 62 part PNGs;
11. receipt gates: pinning, 0-px switch, raised ≤ 100 ms, alternation, bounds, and the GIF/MP4 hashes;
12. the import receipt.

The real `%APPDATA%\pixelorama` only showed another session's open GUI updating its `.running` heartbeat.

## Evidence for Codex visual review

All files are in `outputs/`, stamp `20261017-014517-f2d27661`, and every name ends `…_unapproved-nonruntime_20261017-014517-f2d27661.<ext>`. "Real-time" means actual speed.

**Stills (42 separate PNGs, colour-exact, full 1280×720 window, game canvas 640×360):**
- city-bright: `…city-bright_protagonist-female-south-run-v03-still-v8-idle-shadow-h48_…png`, `…still-key-00px…` through `…still-key-88px…` (12 keyframes);
- annex-dark: the same 13 stills;
- each scene, two stop sequences: `…stop-stance-{1-last-move,2-plus2,3-plus5,4-v8}…` and `…stop-flight-{…}…`.

**Real-time 1x loop:**
- `…city-bright_…-preview-run-1x-h48_…gif` and `…annex-dark_…-preview-run-1x-h48_…gif`: GIF at about 30 fps, 1 window px = 1 px;
- `…-preview-run-2x-60fps-h48_…mp4`: every 60 fps tick at 60 fps, 2x nearest, H.264;
- `…-preview-run-follow-3x-h48_…gif`: camera follows the hero.

**Immediate stop:**
- `…-preview-stop-stance-r030-{1x.gif, quarter-2x.gif, 2x-60fps.mp4}`;
- `…-preview-stop-flight-r036-{…}`.

**Re-press:** `…-preview-repress-r016-g01-{1x.gif, 2x-60fps.mp4}` and `…-r016-g08-{…}`.

**Receipts:**
- `…city-annex_protagonist-female-south-run-v03-capture-receipt-h48_…json` (sha256 `52e5a24969a7996f…`);
- `…preview-receipt-h48_…json` (`01b21ec5eeef0926…`);
- `outputs/rpg-2-star-ocean-the-second_protagonist-female_south-run-v03-import-validation-receipt_unapproved-nonruntime_20261017-014721-a5ff3084.json` (`c3287edd29386043…`).

The capture log printed two `output name too long (151)` warnings. That is the tool's own conservative 150-character warning; both files were written and verified by hash.

## Files (all new; nothing existing was overwritten)

| Path | sha256 (first 16 hex) |
|---|---|
| `game/assets/characters/run-v03-unapproved/` (90 files incl. empty `.gdignore`, 488 KB): 62 `…south-run-v03-part-<role>_unapproved-nonruntime_…png`, 12 `…-keyframe-<NN>px_…png`, 12 `…-keyframe-<NN>px-shadow_…png` | hashes in the manifest |
| `…/…south-run-v03-manifest_unapproved-nonruntime_20261017-012243-3a29a732.json`: LF, rig, gait, stop / re-press rules, per-px table, bounds, flags | `a5a2f7fa9ccdd9fc` |
| `…/…south-run-v03-keyframes-editable_unapproved-nonruntime_20261017-012243-e48dfc91.pxo`: **editable Pixelorama source**, 12 frames × 13 layers (shadow layer at opacity 0.38) | `1eb3f2823ff5efbb` |
| `…/…south-run-v03-part-library-editable_unapproved-nonruntime_20261017-012243-1e2777e9.ora`: 62 layers, one per part; merged image = v8 | `f68a6a5efb2b0722` |
| `tools/…south-locomotion-compact-v03-build_m8-w06_20261017-012243-dd3b5479.py` (started from the v02 builder, not imported) | `9698d4a24f0d2ccd` |
| `tools/…-v03-godot-capture_m8-w06_20261017-012243-8e208784.gd` (`-s` tool, test-only compositor + gait driver + shadow sprite) | `e179f65afda323ee` |
| `tools/…-v03-godot-import-validation_m8-w06_20261017-012243-d2169050.gd` | `a8c86cc37a045606` |
| `tools/…-v03-preview-gif-mp4_m8-w06_20261017-012243-65b9415a.py` | `0dd6a0c0e985a31a` |
| `tests/protagonist-female-south-run-v03/…_focused-check_unapproved-m8-w06_20261017-012243-c68ff8d9.py` | `5d781943af83e58b` |
| `outputs/*south-run-v03*20261017-014517-f2d27661*` (42 PNGs, 16 GIFs, 10 MP4s, 2 receipts; about 73 MB) and the import receipt | see the receipts |

**Path-length note:** an early build used a longer folder and variant name, and one keyframe-shadow path reached 261 characters, over Windows MAX_PATH.
- Those builds were deleted. The final names keep every asset path at or below 245 characters, and the builder now refuses any path over 250.
- Scratch, logs and per-tick crops are in `work/loco-v03-scratch/`, which is gitignored.

## Reproduce

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
GD=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
$PY -I -B tools/…compact-v03-build_…-dd3b5479.py --out-dir <scratch>         # byte-identical rebuild (--write = asset folder)
APPDATA=<scratch appdata> $GD --path game -s <abs …v03-godot-capture_…-8e208784.gd> -- --motion-dir=<abs scratch>   # windowed; writes outputs/
$PY -I -B tools/…v03-preview-gif-mp4_…-65b9415a.py --motion-dir <abs scratch> --receipt outputs/<capture receipt>.json
$PY -I -B tests/protagonist-female-south-run-v03/…-c68ff8d9.py --pixelorama --receipt outputs/<capture receipt>.json --import-receipt outputs/<import receipt>.json
```

**Reversal:** delete the following. Nothing else was changed.
- `game/assets/characters/run-v03-unapproved/`
- `tests/protagonist-female-south-run-v03/`
- the four `tools/…south-locomotion-compact-v03…` files
- this note
- `outputs/*south-run-v03*`

## Open decisions for Codex / the creator

1. Is a 5.83 steps/s light run with about 54 % flight acceptable as the 140 px/s exploration state? Or should the speed change? That is a gameplay decision; with a lower speed, the same rules give longer contacts and less flight.
2. Should the motion layer include a contact-shadow layer? It would be a runtime-owner decision, and would also apply under the static idle.
3. Is the 1-texel torso/scarf shift with a steady head readable as stride, or is it jitter at 1x?
4. Are 200–250 ms settle stops acceptable, or should the hair and cape follow-through be dropped to shorten flight-release stops toward v02's 117–133 ms?

No runtime integration, art acceptance or meter change follows from this note. Exploration sprites remain **0/52**.
