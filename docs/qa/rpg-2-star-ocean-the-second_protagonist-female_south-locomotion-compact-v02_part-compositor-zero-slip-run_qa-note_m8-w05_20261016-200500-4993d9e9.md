# Female protagonist south compact locomotion v02: part library + test-only compositor, zero-slip planted boot (QA note, m8-w05)

**Status: UNAPPROVED / NONRUNTIME pilot.** Every manifest and receipt flag is `false`: `art_approved`, `human_reviewed`, `runtime_integrated`, `walk_animation_approved`, `stop_animation_approved` and `counts_toward_art_acceptance`.

- Claude checked numbers, stills and per-tick strips as an agent. That is **not** a human or creator review, and nothing here claims acceptance.
- The only approved items are unchanged: the selout v8 SOUTH IDLE static frame and the 48 logical px exploration display scale.
- Exploration sprites stay **0/52**. The meter, the Game Bible, `docs/progress.md` and the progress state were not touched.
- No Git staging, commit or push.

- **Auth.** Checked before any work with `claude auth status`: `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. `ANTHROPIC_API_KEY` was absent and no `ANTHROPIC_*` variable was set. No API billing, credits, auto-reload or paid fallback was used, and quota was not exhausted.
- **Read first:**
  - the global `~/.codex/AGENTS.md` naming rule (the repo has no AGENTS.md);
  - the `docs/progress.md` approval scopes (v8 static only, 48 px, 0/52, the open "female south locomotion" decision);
  - the approved v8 PNG (sha256-bytes `ccf9d2a2…68b6fd`, re-verified by every tool);
  - the v01 QA note, including its independent re-verification and corrections section;
  - the v01 builder, capture tool and check.
- **Not touched:**
  - v8 (byte-identical), every v01 / v3r* file, runtime scripts and scenes, MOVE_SPEED, the stop policy, M2 travel;
  - Washington / City Hall / every environment file. Another session committed part of v01 in `d69871e` during this run; that was not this work.

## Verdict

v02 **materially fixes the world-space planted boot**.
- Every boot in contact keeps its window row, its sole-row x extent and every boot texel while the body passes over it. This was measured on captured pixels at MOVE_SPEED 140 at 30, 60 and 144 fps, in three scenes.
- World displacement is **0 px per tick and 0 px per ground contact**. v01 was 4.64 px per 60 fps tick and up to 121 px per contact.
- All 91 immediate stops (from every tick of a stride) end on the v8 PNG itself with **0 changed pixels at the switch**.
- In all 66 re-press cases the next touchdown is the other boot. No boot steps twice in a row, so the v01 re-lift defect is gone.

**What it costs, said plainly:**
1. **The motion is a light run, not a walk.** At 140 logical px/s = 280 window px/s, a zero-slip contact can last only as long as the leg can absorb the travel. Here that is 20 window px, about **71 ms**. So the cycle is 343 ms (5.8 steps/s), with 100 ms of flight per step (58 % airborne). See "Why a run" below.
2. **Stops from a planted phase take two small steps:** the airborne boot lands, then the planted boot shuffles to its v8 spot. That is 233–267 ms at 60 fps, against v01's 83–150 ms. Stops from flight take 117–133 ms.
3. **It is no longer a frame bank.** The art unit is a part library plus gait keys, and a test-only compositor stacks the parts every tick. The real game runtime is unchanged and does not contain that compositor.

## What changed from v01 (design)

| | v01 (m8-w04) | v02 (m8-w05) |
|---|---|---|
| Art unit | 8 loop + 3 stop whole frames | **43 part PNGs** (one layered `.ora`) + 12 review keyframes (`.pxo`) + gait / stop / re-press keys in the manifest |
| Body | logical position | logical position (no root lock, no body hop) |
| Planted boot | in-cell fixed → slides in world with the body | **window row fixed on landing**. The leg is re-stacked each tick from v8's own leg rows (whole-row repeat / drop, as v01) between the hip and that boot |
| Phase | time (75 ms frames) | **distance** (travelled window px mod 96), so 30 / 60 / 144 fps share one gait |
| Stop | `stop_table[frame]` (≤ 2 frames) → v8 | airborne boots fly to their v8 spots and land. Then off-spot planted boots shuffle (lift ≤ 4 rows), at most one boot view change per tick. Arms step to N on ticks with no boot change. Then the v8 PNG, one tick after the composite already equals v8 |
| Re-press | runtime timer reset → re-lifts the leg just landed | the boot that **landed last stays planted** at its window row. The other boot is re-planned from where it is to the next scheduled landing (stride sync kept). Arms ease one step per tick |
| Cell | 80×112 | 80×120: v8's cell plus 8 rows below for the forward boot, same pin (40, 104) |

Each part is cut from v8 with v01's partition code, copied verbatim and never imported:
- cape and hair-lock lag variants (−1 / 0 / +1);
- hips, coat skirt, upper body;
- arm poses B1 / N / F1 per side (front / back / seam);
- v8's leg rows per side;
- boot views per side: `v8`, `toe`, `heelup`, `sole`, `hang`, `reach`, `strike`. These are v8's own boot plus the v3r4 / v01 shaft-and-foot rows in v8 leather colours.

Texels are 1:1 in v8's 32-colour palette with binary alpha: no resampling, filtering, flips, mirrors or generative redraw. Identity is preserved: v8 rows 8–57 outside the declared arm and hair-lock zones equal v8 shifted by the bob, in every keyframe. That is 0 mismatches and covers hair, face, scarf, coat and skin. The neutral composition rebuilds v8 exactly.

## Why a run: zero slip vs cadence at MOVE_SPEED 140

A stance boot is pinned while the body travels over it, so the in-cell excursion must equal the stance travel. v8's legs are about 43 rows from hip to sole. v02 lets a planted boot travel from +8 rows (toward the camera, landing) to −12 rows (behind, lift-off), so E = 20 window px of travel per contact.

| Stride (window px per cycle) | Cycle | Steps/s | Contact (zero slip) | Flight per step | Airborne share |
|---|---|---|---|---|---|
| 80 | 286 ms | 7.0 | 71 ms | 71 ms | 50 % |
| **96 (chosen)** | **343 ms** | **5.83** | **71 ms** | **100 ms** | **58 %** |
| 112 | 400 ms | 5.0 | 71 ms | 129 ms | 64 % |
| v01 (no pin), 168 | 600 ms | 3.33 | — (slides 4.6 px/tick) | 0 | 0 % |

A zero-slip **walk** (no flight, contact ≥ half the cycle) would need a stride ≤ 40 px, which is about 7 cycles or 14 steps per second. That is not plausible. At 140 px/s the honest choice is between v01's sliding walk and v02's pinned run, unless the speed or the leg range changes. MOVE_SPEED was not changed. The creator's open decision "run at 140 px/s vs planted walk at about 16 px/s" is untouched.

## Measurements (real Godot 4.7.2 windowed, 1280×720 window, 640×360 canvas, scale 0.5, nearest)

The hero is moved by each scene's own `_process` with `move_down` held; the speed measured 140.000 logical px/s. The scenes are city-bright, outskirts-bright and annex-dark. The capture gates all passed (exit 0):
- GDScript compositor == builder keyframes (12/12) and == v8 at the neutral state;
- steady-state gait == the manifest per-px table on 231 ticks;
- exact-RGB fidelity of the drawn image on **every** captured tick;
- straight-south movement, and the hero stationary without input.

### Planted-boot world displacement (captured pixels; identical in all three scenes)

| fps | Planted tick pairs | Lowest-row Δ per tick (max / mean) | Sole x-extent Δ max | Boot texels changed in world | Ticks per contact | Slide per contact | v01 per tick / per contact |
|---|---|---|---|---|---|---|---|
| 60 | 15 | **0 / 0** | **0** | **0 / 1869** | 4–5 (2 at the first landing) | **0 px** | 4.64 / 5 px; ≤ 121 px |
| 30 | 5 | **0 / 0** | **0** | **0 / 623** | 2 (1 at the first landing) | **0 px** | 9.32 / 10 px |
| 144 | 42 | **0 / 0** | **0** | **0 / 5202** | 10–11 (5 at the first landing) | **0 px** | 1.94 / 2 px |

- Per-tick example: city-bright, 60 fps, ticks 19–23. vr is in contact, and its sole stays on window row 427 on all five ticks while the pin moves 4–5 px per tick.
- The swinging boot moves up to 9 window px per tick at 60 fps, 16 at 30 fps and 4 at 144 fps. That is about twice the body speed, as a swing foot must be.
- Visible boot texels per contact were 1861 of 1869 at 60 fps. The difference is coat overlap, not boot motion.

### Immediate stops (every tick of one stride; 63 at 60 fps across the 3 scenes, plus 11 at 30 fps and 17 at 144 fps in city-bright)

| fps | Release in | Cases | Time until v8 PNG | Silhouette XOR max per tick (stop) | Walk max per tick (same fps) | Crown step max | Planted boot during stop |
|---|---|---|---|---|---|---|---|
| 60 | flight | 36 | 117–133 ms | **247** | 268 | 0 | — |
| 60 | stance | 27 | 233–267 ms | **208** | 268 | 1 | 0 px / 0 texels |
| 30 | flight | 7 | 167–200 ms | 278 | 340 | 0 | — |
| 30 | stance | 4 | 300 ms | 184 | 340 | 1 | 0 / 0 |
| 144 | flight | 10 | 83–104 ms | 233 | 245 | 0 | — |
| 144 | stance | 7 | 188–208 ms | **246** | 245 | 1 | 0 / 0 |

- **Switch to v8:** 0 changed pixels in all 91 stops.
- **v01 for comparison:** stop XOR 291–315 against a loop maximum of 231.
- **v02 result:** the stop maximum is below the walk maximum at 30 and 60 fps, and 1 pixel over it at 144 fps from stance (246 vs 245).
- **How XOR is measured:** silhouette XOR is computed on the drawn images in the body frame (alpha masks), the same kind of number as v01's.
  - It is recomputed from the logged states by the deterministic check's independent compositor. The capture proved the drawn image equals the screen on every tick.
  - The screen-mask XOR in city-bright reads higher (361 at 60 fps) because animated background pixels in that scene leak into a background-diff mask. It is kept in the receipt but not used for comparison.

### Immediate re-press (city-bright: 6 release phases × gaps of 1, 2, 3, 5, 8, 14 and 30 ticks; the other scenes: 3 × 4)

- **Alternation:** in 66/66 cases the next touchdown after the re-press is the **other** boot.
- **Last-landed boot:** it stood ≥ 50 ms (touchdown to lift-off, across the stop) in every case; a steady-run contact is 71 ms. It is never lifted on the re-press tick unless it has already stood 83–117 ms, i.e. it was at the end of its stance.
  - The shortest case: a boot that touched down on its v8 spot just before the re-press. From its spot it can only stay planted for 12 px of travel before the −12 rear limit, so it lifts 33 ms after the re-press, having stood 50 ms in total.
  - This is a short contact, not a re-lift: the other boot still lands next.
- **Next touchdown:** 33–150 ms after the re-press.
- **Planted boot:** 0 px world displacement through every re-press.
- **Silhouette XOR max** in the 200 ms after the re-press: **267** (60 fps walk maximum 268).

### Extents and identity

- **Crown:** rows 8–9 only (bob 0 / +1).
- **Lowest row:** up to 111 when the forward boot reaches toward the camera, so a frame is up to **104 texels (52 logical px) tall**. The standing figure and v8 stay 96 texels (48 px). See limitation 2.
- **Keyframe vs v8 silhouette XOR:** 239–490, against v01's 113–203. The contact keyframes (phase 0 and 48 px: 398 and 490) no longer resemble the idle.

## Godot import, filtering, runtime

- **Shared working tree:** the asset folder keeps an empty `.gdignore`, so Godot imports nothing there. No `.import` or `.uid` file was created by any run (checked with find). `git status` was compared before and after; every other difference belongs to other sessions.
- **Isolated import validation:** a copy of `game/` without `.godot` was made under `%LOCALAPPDATA%\Temp\wb-loco-v02-import-3ecb5f9a`, with the `.gdignore` removed. There `Godot --headless --import` exited 0, and the validation tool printed `LOCO_V02_IMPORT PASS`:
  - all 55 pilot PNGs import with `compress/mode=0` (lossless) and `mipmaps/generate=false`;
  - the imported textures have no mipmaps;
  - alpha is identical everywhere and RGB is identical on every opaque texel. Godot's default `fix_alpha_border` rewrote the RGB of 27,760 alpha-0 texels only, which are invisible;
  - the project's default canvas filter is Nearest (0).

  The copy was deleted afterwards.
- **No pixel filtering:** the capture sprite uses `TEXTURE_FILTER_NEAREST` at scale 0.5. Every captured tick is exact-RGB against the drawn image.
- **Runtime unchanged:** sha256 of every file in `game/scripts`, `game/scenes` and `game/project.godot` is identical at start and end. `battle_arena.gd` was already modified by another session before this run and was not touched. The check (09) finds no runtime reference to the pilot.
- **Tool isolation:** every Godot run used a scratch `APPDATA`, and every Pixelorama run an isolated temp `APPDATA`.
  - The real `%APPDATA%\pixelorama` shows only an open GUI's `.running` heartbeat and an untitled autosave from a 2026-10-15 session. Neither came from these runs.
  - The real Godot user data received no test saves.

## Screen-visible limitations (honest)

1. **It reads as a quick, bouncy run** (5.8 steps/s, 58 % airborne, 71 ms contacts). Whether that suits exploration at 140 px/s is a creator decision. Nobody has watched it in real time.
2. **The forward reach goes below the standing pin** by up to 8 texels (4 logical px). Mid-stride the figure spans up to 52 logical px vertically, although the display scale and the standing frame are exactly the approved 48 px.
3. **No contact shadow.** The rear planted boot, up to 12 rows above its v8 spot, and the flight phases can read as floating. Depth reads only from leg length. A shadow layer would be a separate decision.
4. **The kicked-back `sole` boot view** (v3r4 / v01 authored rows) reads as a small dark knob under the knee at 1×.
5. **Leg re-stacking stretches the thigh** on the forward reach (repeated whole rows) and squeezes it at the rear. One rare reachable state squeezes the vl knee band by row drop: `toe` at o −12, lift 5, bob 1. It is listed in the manifest.
6. **Stops from a planted phase are longer** (233–267 ms at 60 fps; 300 ms at 30 fps), because the planted boot must step to its v8 spot instead of popping.
7. **At 30 fps** one tick moves the swing boot up to 16 px, and the walk silhouette changes by up to 340 px per tick.
8. **The compositor is test-only GDScript** that builds an 80×120 image per tick. Its cost was not benchmarked. A runtime version (per-part `Sprite2D`s or a shader) is a runtime-owner decision and was not done.
9. **Arms are v3r4's B1 / N / F1 poses.** The right-arm peak is offset 6 px from the left so both never change on one 60 fps tick, but at 30 fps they can.
10. **Agent review only.** I viewed the keyframes at 4×, the Godot stills and per-tick follow strips at 2–3×. The 114 GIFs were generated and hash-pinned but not watched as motion.

## Files (all new; nothing existing was overwritten)

| Path | sha256 (first 16 hex) / size |
|---|---|
| `tools/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v02-build_m8-w05_20261016-200500-78e18209.py`: source-locked part library + reference compositor + keyframes / `.pxo` / `.ora` / manifest | `1077ac265078c17d`, 58,354 B |
| `tools/…-v02-godot-capture_m8-w05_20261016-200500-a29fc892.gd`: `-s` tool with the test-only `PartCompositor` + `Loco` gait driver; captures and gates | `e3bc304d88d4a110` |
| `tools/…-v02-godot-import-validation_m8-w05_20261016-200500-3ecb5f9a.gd`: run in an isolated imported copy | `9612405b22b4ff9a` |
| `tools/…-v02-preview-gif_m8-w05_20261016-200500-630375df.py` | `3e19a602298bcb71` |
| `tools/…-v02-receipt-metrics_m8-w05_20261016-200500-ff2b3258.py` | `042c2bc1597bb166` |
| `tests/protagonist-female-south-locomotion-compact-v02/…_deterministic-check_m8-w05_20261016-200500-6d8d7fe7.py`: **23/23 OK** with `--pixelorama --receipt` | `27502c5bb94d9192` |
| `game/assets/characters/locomotion-pilots-compact-v02/` (59 files incl. empty `.gdignore`): 43 `…-part-<role>_…png`, 12 `…-keyframe-phase-<NN>px_…png` (all PNGs 154 KB together; hashes in the manifest) | — |
| `…/…-manifest_m8-w05_20261016-200500-a5615443.json`: LF only; rig, gait keys, stop and re-press rules, per-px table, flags | `875f0373b170f845` |
| `…/…-keyframes-editable_…-e241cb44.pxo`: 12 frames × 11 layers, Pixelorama 1.2.3 export == keyframe PNGs | `91015a7016404add` |
| `…/…-part-library-editable_…-7fde2faf.ora`: 43 layers (one per part), split-layer export == part PNGs; merged image == v8 | `f4b24834eb52f7f5` |
| `outputs/…south-locomotion-compact-v02-…-h48_m8-w05_20261016-211456-07c96521.*`: 47 separate 1280×720 PNGs and 114 separate GIFs (listed below) | PNG hashes in the capture receipt, GIF hashes in the GIF receipt |
| `outputs/…city-outskirts-annex_…-v02-capture-receipt-h48_…-07c96521.json` | `46349828662a24c5` |
| `outputs/…-v02-preview-gif-receipt-h48_…-07c96521.json` | `ba9d7c8a9b452bad` |
| `outputs/…-v02-metrics-summary-h48_…-07c96521.json` | `09c377bbf9f7092b` |

**The 47 PNGs:**
- **city-bright:** v8 and all 12 keyframe stills at one pin;
- **outskirts-bright and annex-dark:** v8 and keyframes at phase 0, 24, 48 and 72 px;
- **every scene:** two stop sequences (from stance vl and from flight) at the last moving tick, +2 ticks, +5 ticks and v8.

**The 114 GIFs** (per scene; GIF palettes are lossy, the PNGs are colour-exact):
- walk at 60 fps: realtime 1×, quarter speed 2×, follow camera 3×;
- every 60 fps stop at realtime 1×, plus quarter speed 2× for the two still cases;
- re-press cases at realtime 1×.

Scratch files are in `work/walk-v02-scratch/` (gitignored): logs, review strips, patch scripts. The ~640 MB per-tick motion crops were deleted after the GIFs were written.

## Reproduce

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
GD=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
$PY -I -B tools/…compact-v02-build_…-78e18209.py --out-dir <scratch>                       # byte-identical rebuild (--write = asset folder)
APPDATA=<scratch appdata> $GD --path game -s <abs …godot-capture_…-a29fc892.gd> -- --motion-dir=<abs scratch>   # windowed; writes outputs/
$PY -I -B tools/…preview-gif_…-630375df.py --motion-dir <abs scratch> --receipt outputs/<capture receipt>.json
$PY -I -B tools/…receipt-metrics_…-ff2b3258.py --receipt outputs/<capture receipt>.json
$PY -I -B tests/protagonist-female-south-locomotion-compact-v02/…-6d8d7fe7.py --pixelorama --receipt outputs/<capture receipt>.json   # 23/23
# import validation: copy game/ (no .godot) to %LOCALAPPDATA%\Temp, delete the pilot .gdignore there,
# $GD --headless --path <copy> --import ; $GD --headless --path <copy> -s <abs …import-validation_…-3ecb5f9a.gd>
```

**Reversal:** delete the following. Nothing else was changed.
- `game/assets/characters/locomotion-pilots-compact-v02/`
- `tests/protagonist-female-south-locomotion-compact-v02/`
- the five `tools/…south-locomotion-compact-v02…` files
- this note
- `outputs/*south-locomotion-compact-v02*20261016-211456-07c96521*`

## Next candidate (if the creator wants it)

These are options, not decisions:
- **Contact shadow:** keep v02's zero-slip contact rule and add a small contact-shadow part (one more layer).
- **Smaller forward reach:** limit the reach to +4 / −16 to stay inside 48 px, at the cost of a deeper rear squeeze.
- **Lower speed:** the same part library and rules work at any MOVE_SPEED with new gait keys only. At about 70 px/s the same 20 px contact lasts 143 ms instead of 71 ms, so the cadence can drop and the flight shrink. A true zero-slip walk with no flight still needs a stride ≤ 40 px. That speed would be a gameplay decision.

## Zero-change closeout (2026-10-16, ledger only)

- Recorded as a **zero-change** meter closeout: 35.8% → 35.8%, no gate, counter or category change. Exploration sprites stay **0/52**. Runtime scripts, scenes and MOVE_SPEED are unchanged.
- Re-run for the closeout: deterministic check **23/23 OK** (`--pixelorama --receipt` on the 20261016-211456-07c96521 capture receipt). Measured planted slip is 0 px, with 91 stops and 66 re-press cases.
- Codex inspected **one still frame only** and cannot confirm motion acceptance. At 140 logical px/s the gait currently reads as a **run** and may look floaty. The **run-versus-walk decision** (and any speed change) remains **open** for the creator.
- Only this note is tracked. The part library, sources, tools, check script and the GIF/PNG capture bank (about 98 MB of GIFs) stay local and are hash-pinned in `outputs/rpg-2-star-ocean-the-second_mvp-completion-ledger_map-art-v01-locomotion-v02-closeout-evidence-index_v01_20261016-213224-7e11c4c6.json`.
