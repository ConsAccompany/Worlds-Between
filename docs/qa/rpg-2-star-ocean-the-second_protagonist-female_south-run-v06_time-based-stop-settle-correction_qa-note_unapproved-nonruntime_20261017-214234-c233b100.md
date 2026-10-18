# Female protagonist south RUN v06: time-based stop settle (one bounded correction to v05) — QA note, m8-w09

**Status: UNAPPROVED / NONRUNTIME.** This is a single-direction, test-only motion candidate. It is not a production sprite, it is not wired into the runtime, and it is not accepted.
- Every approval flag in the manifest and receipts is `false`.
- Only Claude has reviewed it, as an agent. Codex and the creator judge the normal-speed visuals.
- Counters are unchanged:
  - full sprites **0/52**;
  - accepted scenes **3/12**;
  - M2 **10/12**;
  - overall **40.8%**;
  - human playtests **0/2**.
- Not touched: shared runtime scripts and scenes, the Game Bible, `docs/progress.md` and the git index. Nothing was staged, committed or pushed.
- Byte-for-byte preservation is verified by check 13 against listings pinned before any v06 file existed:
  - v03: 168 files, `f253e9a7…`;
  - v04: 170 files, `9953444c…`;
  - v05: 201 files, `7dab5b20…`, pinned 2026-10-17 21:15 UTC;
  - the approved selout v8 PNG: `ccf9d2a2…68b6fd`, also unchanged against git HEAD.

**Auth.** Checked with `claude auth status` before any work:
- `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`;
- `ANTHROPIC_API_KEY` is absent.

No API key, credits or paid fallback was used, and there was no quota or auth failure.

**Inputs read:**
- the dispatch (`docs/coordination/…female-south-run-v06-30fps-stop-correction-dispatch_v01_20261017-170900-b4f08d16.md`);
- the creator standard "smooth, fluid and well-paced" (`docs/design/…character-motion_smooth-fluid-well-paced-creator-standard_v01_20261016-233420-702db4c9.md`);
- the v05 QA note and the v05 capture receipt (normal-speed stop timings per fps);
- the v04 QA note;
- the approved selout v8 south idle (identity and stop destination);
- `~/.codex/AGENTS.md` (naming rules). The repository has no project-level AGENTS.md.

## The defect and the fix

**Cause.** The 30 fps regression came from v05's settle counting frames, not time:
- Every body change after the last touchdown took its own frame: hair catch-up, torso re-centre, arm step, dip release, hair follow. Then one more frame passed before the v8 PNG.
- The one-boot-change-per-frame hold also cost a whole frame.
- So the same sequence took 83 ms at 60 fps but 167–200 ms at 30 fps.

**Fix.** v06 runs the stop on an **event clock in ms**. The manifest's `stop` block holds the rule and its constants: `settle_clock`, `settle_gap_ms` = 16.667, `hold_shift_ms` = 16.667 and `no_pose_skip`.
1. **Settle changes keep v05's order** and get scheduled times:
   - the hair catches up at the dip + `stop_hair_lag_ms`;
   - each torso step, arm step and the dip release comes at least one 60 fps frame after the previous change (arm steps also stay 25 ms apart, and the dip release comes at least 25 ms after the touchdown);
   - the hair follows the dip release by 16 ms, counted from the release's scheduled time.

   Each frame draws the state at its own time:
   - **60 and 144 fps:** still at most one change per frame (60 fps is identical to v05);
   - **30 fps:** two changes can share a frame. Because the 16 ms hair lag is shorter than one 33 ms frame, the hair moves with the body there.
2. **Touchdown first.** Nothing except the dip changes on the frame that shows the last touchdown. The boot visibly lands before the body settles at every frame rate. This is gated.
3. **Hold cost capped.** A boot held by the one-boot-change rule loses at most 16.7 ms of its clock (v05: a whole frame).
4. **No pose skip.** At low frame rates a moving boot never jumps from its start pose straight to touchdown; it shows its mid key for one frame first. Without this rule, the cheaper hold would have let a landing boot teleport about 10 rows.
5. **Arm steps at 30 fps.** A 30 fps frame may carry an arm step next to one boot or torso change. v05 allowed arm steps only on frames with no other change, and at 30 fps such frames barely exist before touchdown, so two arm steps were left for the settle.

**What did not change:**
- The art is unchanged. All 62 parts, 12 keyframes and 12 keyframe shadows are pixel-identical to v05 by role and key (check 19).
- The gait is unchanged:
  - stride 84 px, so 6.67 steps/s at MOVE_SPEED 140;
  - land +2 rows;
  - swing lift ≤ 2;
  - floor gap max 5, mean 1.64;
  - flight 75 ms per step.
- The compositor, zero-slip planted boot, stance roll, re-press rule, land and shuffle keys and durations are v05's.

No frames were added, and contact is not hidden.

## Results (real Godot 4.7.2, windowed, 640×360 canvas in 1280×720, scenes' own `_process`, measured 140.000 px/s)

Capture stamp `20261017-213159-3a390f7c`, exit 0. Stops are released at every frame of one stride (all entry phases).

| Measure | v05 | **v06** |
|---|---|---|
| **30 fps release → v8 PNG** (9 phases per scene, both scenes) | 267–333 ms | **200–233.3 ms** (7 frames worst) |
| 30 fps last touchdown → v8 | 167–200 ms | **67–133 ms** |
| 30 fps release → at rest (last visible change) | — | 167–200 ms |
| 60 fps release → v8 (18 phases per scene) | 150–200 ms | **150–200 ms** (unchanged; same frames) |
| 60 fps last touchdown → v8 | 67–83 ms | 67–83 ms |
| 144 fps release → v8 (15 phases, city-bright) | 125–174 ms | 139–188 ms |
| 144 fps last touchdown → v8 | 56–63 ms | 62–76 ms |
| Longest raised boot after a release | 100 / 83 / 76 ms (30 / 60 / 144 fps) | **100 / 83 / 76 ms** (limit 100) |
| Settle changes per frame after touchdown | 1 | 1 at 60 / 144 fps; **2 at 30 fps** |
| Planted-boot world slip (every walk, stop, re-press, showreel and reversal tick) | 0 px | **0 px** |
| Switch to the v8 PNG | 0 changed px | **0 changed px** |
| Neck shear | 0 | **0** on every captured tick |

**Re-press:** 129 cases, all alternate (the next touchdown is the other boot) with the planted boot pinned.
- 60 fps: 54 cases.
- 30 fps: 39 cases (new).
- 144 fps: 36 cases (new).
- Next touchdown after the re-press: 33–139 ms.

**Reversal sweep:** 9 cases at 60 fps. Every final stop reaches v8 at 183 ms with 0 changed px. Re-entry first touchdown is 150 ms (unchanged).

**Gait-driver sweep** (`--sim=1`: state-level only, deterministic, no pixels). Release → v8 by frame rate:

| fps | release → v8 |
|---|---|
| 30 | 200–233.3 ms |
| 40 | 150–225 ms |
| 48 | 167–229 ms |
| 60 | 150–200 ms |
| 72 | 153–208 ms |
| 90 | 133–189 ms |
| 120 | 117–192 ms |
| 144 | 125–188 ms |
| 240 | 113–179 ms |

The sweep also ran 970 re-press cases from 24 to 240 fps with no alternation failures.

**Focused check: 38/38 OK.** It ran with `--pixelorama --receipt <capture receipt> --sim-receipt <sim receipt> --import-receipt <import receipt>`. New checks:
- **13:** v03, v04 and v05 immutability;
- **19:** art and gait equal v05;
- **16b:** per-fps settle limit, with no torso or arm change on the touchdown frame;
- **20:** every 30 fps release, including both 30 fps showreels, reaches v8 within 7 frames (22 releases); 60 fps is not slower than v05; no boot is raised more than 100 ms;
- **21:** the sim receipt.

Isolated-copy import: `RUN_V06_IMPORT PASS` (86 PNGs lossless, no mipmaps, Nearest).

## Normal-speed review clips (Codex)

These are the main clips, all `outputs/…south-run-v06-preview-…_20261017-213159-3a390f7c.mp4`. Each covers idle, start, sustained run (2 cycles), a quick release and re-press, more run, reversal to north and back, a release to v8, a short run and another release to v8.
- **60 fps showreels:**
  - `rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-run-v06-preview-showreel-1x-60fps-h48_unapproved-nonruntime_20261017-213159-3a390f7c.mp4`
  - `rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-run-v06-preview-showreel-1x-60fps-h48_unapproved-nonruntime_20261017-213159-3a390f7c.mp4`
  - Each is 1280×720, 60/1, 187 frames.
- **30 fps showreels (new):**
  - `rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-run-v06-preview-showreel-1x-30fps-h48_unapproved-nonruntime_20261017-213159-3a390f7c.mp4`
  - `rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-run-v06-preview-showreel-1x-30fps-h48_unapproved-nonruntime_20261017-213159-3a390f7c.mp4`
  - Each is 1280×720, 30/1, 94 frames, captured with 30 fps frame times. Both uninterrupted releases reach v8 at 233.3 ms.
- **Every 30 fps stop phase (new), per scene:** `…-preview-stop30-ph{53,63,72,81,07,16,25,35,44}-r0xx-{1x,2x}-30fps-…mp4`. These are real-time 30 fps hero crops.
- **60 fps entry phases:** `…-stop-{landing-r027,mid-stance-r029,late-stance-r030,flight-r034}-2x-60fps…mp4`.
- **Re-press:**
  - `…-repress30-r0xx-g0{1,4}-2x-30fps…mp4` (new, 30 fps);
  - `…-repress-r016-g{01,08}-2x-60fps…mp4`.
- **Reversal:** `…-reversal-r020/-r029…` (city-bright).
- **Totals:** 79 MP4 + 19 GIF previews, and 58 colour-exact 1280×720 PNG stills (stills are diagnostic only).

## Remaining defects and trade-offs (plainly)

1. **The 30 fps limit is met at the boundary, not with margin.**
   - The worst 30 fps stop is exactly 7 frames (233.3 ms). This holds for 7 of 9 phases per scene (the other 2 take 200 ms) and both 30 fps showreel releases.
   - At 30 fps, three frames are needed to bring both boots down from a two-boot-airborne release without breaking the ≤ 100 ms raised-boot limit or the one-boot-change rule. Those rules and the touchdown-first rule fix the floor at 4 + 3 frames.
   - Going lower would mean dropping a rule: letting both boots change on one frame, or putting the torso change on the touchdown frame. I judged both as pops and did not do it.
2. **At 30 fps two settle changes can share a frame.** Examples: hair catch-up plus torso re-centre, or torso plus arm step.
   - That is how a time-based motion samples at 33 ms. Each is a 1-texel or 1-row move of the rigid upper body, and neck shear stays 0.
   - Per-frame silhouette change in 30 fps stops is ≤ 319 px (run at 30 fps: 473).
   - Whether the 30 fps settle reads as a "snap" is for Codex's eye on the 30 fps clips.
3. **The 144 fps stop is slightly longer than v05** (139–188 ms against 125–174 ms).
   - v05's 144 fps settle was compressed because it gave each change one 7 ms frame.
   - v06 spaces changes in time, so 144 fps now matches 60 fps (post-contact 62–76 ms against 67–83 ms).
4. **At 30 fps the second boot hangs for one frame.**
   - In the two-boots-airborne phases, the boot held by the one-boot-change rule shows the same pose on two consecutive frames (33 ms) before its mid key.
   - This is still within 100 ms raised.
5. **A 30 fps re-press late in stance can lift both boots on one frame.**
   - Case: city-bright, release at frame 6 inside the first stride, re-press after 1 frame. The planted boot passes its lift-off point within one 9.3 px frame, so both boots lift together.
   - That frame's silhouette change is 484 px, against the run's 473 at 30 fps. Alternation still holds.
   - This is the v05 re-press rule, which v05 never tested at 30 fps. It was not changed in this one-pass correction.
6. **Mixed frame times are slower.** In the jittered sweep (random 30/45/60/144 fps frames, fixed seed) the worst stop takes 271 ms: the feet phase took 181 ms through repeated holds. The median is 204 ms. Diagnostic only.
7. **24 fps fails the raised-boot limit** (125 ms, three 42 ms frames). It is recorded only and outside the target frame rates.
8. **Inherited from v05, unchanged:**
   - it is still a run (50% of the cycle airborne);
   - the trailing boot rises to about knee height;
   - 6.67 steps/s may read as busy;
   - reversal is a hard cut to the runtime placeholder north walk (no north art exists, by scope);
   - re-entry takes 150 ms to the first touchdown;
   - 1-px head sway with the torso;
   - a test-only contact shadow.
9. **Agent review only.** I inspected real captured frames as strips; I cannot play the MP4s in real time.

## Files (all new; nothing existing modified)

| Path | sha256 (first 16) |
|---|---|
| `game/assets/characters/run-v06-unapproved/` (90 files incl. empty `.gdignore`: 62 parts, 12 keyframes, 12 shadows) | in the manifest |
| `…/…south-run-v06-manifest_unapproved-nonruntime_20261017-211600-c619ea83.json` (`v06_changes`, v06 `stop` block) | `f59b04fa672250c7` |
| `…/…south-run-v06-keyframes-editable_…-aa59bf26.pxo` (12 frames × 13 layers) | `63f30e19261ae6c5` |
| `…/…south-run-v06-part-library-editable_…-4a0d93e6.ora` (62 layers) | `183fcec811181275` |
| `tools/…south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py` (rebuild byte-identical) | `2b83a2216438384c` |
| `tools/…south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd` (time-based Loco, `--sim=1`) | `51f389a8b1a119df` |
| `tools/…south-run-v06-godot-import-validation_m8-w09_20261017-211600-26392641.gd` | `e2490ca3ecc3814a` |
| `tools/…south-run-v06-preview-gif-mp4_m8-w09_20261017-211600-8ae57ec2.py` | `75ef0ab5bce168ff` |
| `tests/protagonist-female-south-run-v06/…_focused-check_unapproved-m8-w09_20261017-211600-08ee01ad.py` | `d0fe4c4400d90d76` |
| `outputs/…city-annex_…-south-run-v06-capture-receipt-h48_…_20261017-213159-3a390f7c.json` | `d32ef345140fd36f` |
| `outputs/…city-annex_…-south-run-v06-preview-receipt-h48_…_20261017-213159-3a390f7c.json` | `4e26f7eb46fc00f1` |
| `outputs/…gait-driver_…-south-run-v06-sim-timing-receipt_…_20261017-213201-0e8fbdc3.json` | `8a1c134b5dade635` |
| `outputs/…south-run-v06-import-validation-receipt_…_20261017-213311-26392641.json` | `0124253270ef077b` |
| `outputs/*south-run-v06*` (58 PNG, 19 GIF, 79 MP4, 4 JSON; about 107 MB) | see the receipts |

Scratch work is in `work/loco-v06-scratch/` (gitignored): per-tick frames, patch scripts, strips and the quick runs. The isolated import copy under `%LOCALAPPDATA%\Temp` was deleted.

## Reproduce

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
GD=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
$PY -I -B tools/…south-run-v06-build_…-f8e736cc.py --out-dir <scratch>          # byte-identical rebuild (--write = asset folder)
APPDATA=<scratch> $GD --path game -s <abs …v06-godot-capture_…-ff47ce98.gd> -- --motion-dir=<abs scratch>   # windowed; writes outputs/
APPDATA=<scratch> $GD --headless --path game -s <abs same tool> -- --sim=1                                 # gait-driver timing sweep
$PY -I -B tools/…v06-preview-gif-mp4_…-8ae57ec2.py --motion-dir <abs scratch> --receipt outputs/<capture receipt>.json
$PY -I -B tests/protagonist-female-south-run-v06/…-08ee01ad.py --pixelorama --receipt outputs/<capture receipt> --sim-receipt outputs/<sim receipt> --import-receipt outputs/<import receipt>
```

**Reversal:** delete the following. Nothing else was changed.
- `game/assets/characters/run-v06-unapproved/`
- `tests/protagonist-female-south-run-v06/`
- the four `tools/…south-run-v06…` files
- this note
- `outputs/*south-run-v06*`

## Decision for Codex / the creator

1. Watch the 30 fps showreels and the nine `stop30` clips per scene at 1×. Is a 200–233 ms stop with up to two 1-texel changes per frame smooth enough? Or should a rule be relaxed (see defect 1) to buy another frame?
2. If accepted as the stop clock, the next separate pass could address the 30 fps late-stance re-press double lift (defect 5).
3. Other directions and combat motion stay out of scope until the south motion is approved.
