# Female protagonist south RUN v10: authored gait + push-off revision (QA note, m8-w13)

**Status: UNAPPROVED / NONRUNTIME, one candidate for Root review.** Single direction (south), test-only. Not wired into the runtime, not a production sprite.
- Every approval flag in the v10 manifest is `false`. Counters unchanged (sprites 0/52).
- Nothing was committed or pushed. No Game Bible, ledger, progress, default-runtime or memory file was written. No schedule was created.
- Worktree `work/max0840-motion` (branch `codex/female-south-authored-gait-v09-20261018-0925`, base `160b823`). v09 sources and the v09 asset folder are unchanged; the primary checkout and other worktrees were not touched.
- Auth checked first: Max, first-party, claude.ai login. No API key, cloud, purchased usage or fallback; no quota stop.

**Inputs read:** the creator motion standard (`docs/design/…smooth-fluid-well-paced-creator-standard_v01_…702db4c9.md`, primary checkout); the v09 QA note; the partial v10 builder `…v10_authored-gait-pushoff-build_m8-w13_20261018-143213-ed496e32.py`, which this session continued (no new pilot, no sweep); the v06 / v07 / v09 tools.

## What v10 is

v09 changed only the drawing; its cadence stayed v07's (6.67 steps/s, 50 % airborne). v10 changes the **gait itself**, using Root's reference values. The partial tool had stance 42 px; this session moved it to the authorized 44 px.

| | v07 / v09 | v10 |
|---|---|---|
| Stride (source / window px) | 84 | 128 (two 64 px steps) |
| Stance per boot | 21 px | 44 px = 157 ms (lands +12 rows in front, leaves −32 behind, world row fixed) |
| Cadence at MOVE_SPEED 140 | 6.67 steps/s | **4.375 steps/s** (measured in the driver: 4.41 / 4.38 / 4.38 at 30 / 60 / 144 fps) |
| A boot on the floor | 50 % | **68.75 %** (flight 20 px = 71 ms per step) |
| Torso | 1-row bob | compression 0 → 1 → 2 → 1 → 0 rows over the stance, ≤ 1 row per tick |

**Authored motion (v8 palette and identity, 48 logical px):**
- **One leg rule for every state.**
  - Long reaching / landing leg: stretched by whole-row repeats, shin sloping onto the cuff.
  - Medium leg: v06 foreshortening.
  - Folded leg (< 8 rows): holds its shape, and the boot is drawn *behind* it. The rear foot rises behind the knee as the body passes over it, while its world row never moves.
- **Push-off boots.** New `boot-<side>-toe` parts with the heel high and the toe planted. They are the same height as the heel-up boot, so the roll heel-up → push does not move the leg.
- **Swing:** toe-off → heel kick (v09 sole-under-knee boot) → knee-forward tuck, the foot unfolding under the knee → open reach → heel strike.
- **Coat hem** trails both the torso shift and the vertical bob by the hair lag. When the hem sits one row low, it repeats its top row, so no gap opens.
- **Seams:** v09's ink seam fill is kept. A new **island rule** drops leg-only fragments of ≤ 12 texels that are cut off from the body (a tucked thigh peeking past the coat edge). Without it, 21 of 128 phases had 1–8 texel flecks; with it, every phase is one silhouette.

**Control.** Loco10 is v07's driver (v06 event-clock stop, re-press rule, rise lock) with one change: the multi-level bob.

**Stop retune.** One stop duration was changed: `land_ms_max` went from 70 to 60 ms. With 70 ms, three 30 fps releases in early stance took 266.7 ms; with 60 ms the worst is 233.3 ms.

## Results (real Godot 4.7.2, windowed 1280×720 of the 640×360 canvas, scenes' own `_process`, isolated `%TEMP%\v10m` copy + APPDATA)

| Gate | v10 |
|---|---|
| GDScript Comp10 == builder | neutral == v8; 16 keyframes + shadows; **all 128 per-px composites (sha256)** |
| Steady state == per-px table | 72 captured ticks + 484 sim ticks, 0 mismatches |
| Planted boot world slip (every captured tick, walks / stops / re-presses / reversals / reels) | **0 px** |
| Release → v8, captured, every phase | 30 fps 200–233.3 ms (both scenes); 60 fps 150–216.7 ms |
| Release → v8, sim | 14 frame rates; 30 fps ≤ 233.3, 60 fps ≤ 216.7, ≥ 72 fps ≤ 208.3; mixed frame times 150–250 ms |
| Raised boot after release | captured ≤ 100 ms; sim ≤ 100 ms at every constant rate ≥ 30 fps |
| Switch to the v8 PNG | 0 changed px, every stop and reel release |
| Re-press | 140 captured + 6,400 sim cases; 0 alternation failures, 0 frames with both boots rising; re-press → next touchdown 33–200 ms |
| Reversal (north = runtime placeholder) | 10 cases, final stop 166.7 ms |
| Showreel releases | city 30 fps: 200 / 200 ms (v09 233.3); annex 60 fps: 150 / 150 ms (v09 183.3) |
| Steady pose change per frame (cell XOR) 30 / 60 / 144 fps | 481 / 351 / 226 (v09 476 / 364 / 324) |
| Re-press handoff max 30 / 60 fps | 477 / 331 (≤ the steady maximum) |
| Focused check | **9/9 OK** (incl. official Pixelorama 1.2.3 headless `.pxo` 16 × 13 layers and `.ora` split-layer round trip, exact) |

**Showreels** use the same inputs as v07/v09 (`REEL_SEGS`, inherited unchanged): idle → start → sustained run → quick release + re-press → reversal → south → stop → short run → stop.

**Critical frames** are 11 per reel, saved as separate full-window PNGs (byte copies of the lossless captures, no collage): `start-idle`, `start-step`, `strike`, `midstance`, `flight`, `quick-release`, `repress-step`, `repress-land`, `stop-release`, `stop-land`, `stop-v8`. Each name carries its tick, scene, fps and `win1280-of-640` (native 1280×720 window of the 640×360 logical canvas).

No fluidity claim is made from any metric, still or playback. Root judges the MP4s at 1×.

## Limits (plainly)

1. **Long stance, long reach.** Zero slip over 44 px means the landing leg reaches 12 rows in front and the rear boot travels 32 rows up behind the knee.
   - At 48 px the leading leg is a long diagonal for the last part of the swing. The creator's earlier objection was to v04's long forward reach.
   - Whether v10's reach reads as natural or stilted needs Root viewing.
2. **Visible-extent occlusion.**
   - At 144 fps the lagging coat hem covers one sole-edge texel of the planted rear boot for a tick (2 pairs per walk).
   - Every boot texel keeps its world position and RGB, so this is not slip. The v10 planted gate counts such pairs as occlusion-only, strictly, and records them in the receipt.
3. **Sweep starts.** The re-press and reversal sweeps release from 72 px (half a stride + 8; the gait is nominal from 52 px). The city cases start at y 160 instead of 165, because v10's 128 px stride plus the 0.3 s re-press would cross the city navigation limit (305). Walks, stops and reels use the v07/v09 starts.
4. **Mixed frame times: NON-COMPLIANT. 24 fps: informative.**
   - **v10 violates Root's raised-boot criterion (≤ 100 ms after release).** One existing mixed-frame-time stop (seed 6061) holds a boot raised for 105.6 ms.
   - The 9/9 focused check passed only because v10's sim gate did not test boot-down on mixed frame times. That PASS does not cover this criterion.
   - *Correction added 2026-10-18 after Root review:* the earlier wording here ("below the gated ≥ 30 fps constant rates") understated this. The fix is in v10r1 (`…v10r1…qa-note…249dbf66.md`).
   - 24 fps stops take 250–291.7 ms and can hold a boot for 125 ms. This is recorded only; 24 fps is not a gate.
5. **Not newly drawn.** Arms, hair, cape, torso and head are v06 parts, re-timed to the 128 px cycle. The swing tuck uses v09's knee and kick parts.
6. **Reversal** is still a hard cut to the runtime placeholder north walk. No directions were added.
7. **Scene and reels.** "annex-dark" is v07's darkest annex floor (a tan floor), not a night scene. No v07/v09 comparison reel was re-captured; compare against the existing `outputs/*female-south-run-v0[79]-showreel-1x-*` (`20261018-133700`).

## Files (all new and untracked; nothing existing modified)

| File | Hash (first 16) |
|---|---|
| `tools/…v10_authored-gait-pushoff-build_m8-w13_…ed496e32.py` (continued partial; imports v09 builder read-only, pinned) | lf `1516f7f2ca8fa36a` |
| `tools/…v10-godot-capture_m8-w13_…ed496e32.gd` (extends the v09 tool, pinned) | lf `52ff5ffdf35c8572` |
| `tools/…v10-showreel-mp4-and-critical-frames_m8-w13_…ed496e32.py` | lf `09981eff40927d41` |
| `tests/female-south-run-v10/…focused-check_m8-w13_…ed496e32.py` | lf `039ed8b6c1ff0262` |
| `game/assets/characters/run-v10-unapproved/` (38 files: `.gdignore`; 2 push-boot parts; 16 keyframe + 16 shadow PNGs) | — |
| manifest `…gait-pose-manifest_…63dec7d3.json` (in the asset folder) | lf `de1789e376c34340` |
| keyframes `.pxo` (16 frames × 13 layers incl. the shadow) | `0d92f67c26401549` |
| new-parts `.ora` | `c06a1541e7f40c3f` |
| `outputs/…city-bright_female-south-run-v10-showreel-1x-win1280-of-640-30fps-h48_…79fb8f7d.mp4` (94 frames) | `64567697cfe2a1fa` |
| `outputs/…annex-dark_female-south-run-v10-showreel-1x-win1280-of-640-60fps-h48_…ba41a3e9.mp4` (187 frames) | `3d75274067ac6a2f` |
| 22 critical-frame PNGs `outputs/…female-south-run-v10-<label>-t<NNN>-win1280-of-640-<fps>fps-h48_…png` | in the reel receipt |
| `outputs/…v10-sim-timing-receipt_…181043-64346c97.json` | lf `7bbf8e1db17e5e14` |
| `outputs/…v10-capture-receipt-h48_…181120-cbd39978.json` | lf `8a5f6029dd4f8799` |
| `outputs/…v10-showreel-and-critical-frames-receipt_…6bcf95ec.json` | lf `06df6c5d1fe5f422` |

Scratch: `%TEMP%\v10m` (isolated Godot copy, lossless reel frames, earlier superseded sim/capture receipts) and `%TEMP%\v10s` (previews, patch scripts). Nothing in the repository refers to them.

## Reproduce (worktree root)

Godot runs from a short-path copy.

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
$PY -I -B tools/<v10 build>.py --out-dir game/assets/characters/run-v10-unapproved
# copy game/ + the v06, v07, v09, v10 capture tools to %TEMP%\v10m; once: Godot --headless --path <copy>/game --import
APPDATA=<copy>/appdata Godot_console --headless --path <copy>/game -s <copy>/tools/<v10 gd> -- --sim=1 --out-dir=<abs>
APPDATA=<copy>/appdata Godot_console --path <copy>/game -s <copy>/tools/<v10 gd> -- --motion-dir=<abs> --out-dir=<abs>
$PY -I -B tools/<v10 mp4>.py --frames <motion dir> --receipt <capture receipt> --out-dir outputs
$PY -I -B tests/female-south-run-v10/<check>.py --pixelorama --sim-receipt … --receipt … --reel-receipt …
```

**Reversal:** delete `game/assets/characters/run-v10-unapproved/`, the three v10 tools, `tests/female-south-run-v10/`, this note and `outputs/*female-south-run-v10-*`.

## Decision for Root

1. Watch the two v10 1× MP4s next to the v09/v07 1× reels (same inputs).
   - Does the slower, longer-contact stride with torso compression read as smooth, fluid and well-paced?
   - Does the 12-row forward reach or the rear foot rising behind the knee read wrong at 48 px?
2. If the direction is right, the next bounded step would be authored arms/torso for the 128 px cycle (still v06 parts). If the reach is wrong, the lever is the land/lift split of the 44 px stance (+12 / −32), which is one art-and-gait decision, not a sweep.
