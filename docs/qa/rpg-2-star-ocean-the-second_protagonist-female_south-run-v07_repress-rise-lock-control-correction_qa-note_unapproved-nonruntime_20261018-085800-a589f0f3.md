# Female protagonist south RUN v07: re-press rise lock (one bounded control correction to v06) — QA note, m8-w10

**Status: UNAPPROVED / NONRUNTIME.** This is a single-direction, test-only motion candidate. It is not a production sprite, it is not wired into the runtime, and it is not accepted.
- Every approval flag in the amendment manifest and the receipts is `false`.
- Only Claude has reviewed it, as an agent. Root, Codex and the creator own the native, browser and visual judgment.
- Nothing was staged, committed or pushed. No Codex memory was written.
- Not touched:
  - shared runtime scripts and scenes;
  - the Game Bible, `docs/progress.md` and the git index;
  - any WDC rooms, Git-prep or WDC exterior file.

**Auth.** Checked with `claude auth status` before any work:
- `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`;
- `ANTHROPIC_API_KEY` is absent.

No API key, credits or paid fallback was used, and there was no quota or auth failure.

**Inputs read:**
- the v06 QA note (`…south-run-v06_time-based-stop-settle-correction_qa-note_unapproved-nonruntime_20261017-214234-c233b100.md`);
- the creator motion standard (`docs/design/…character-motion_smooth-fluid-well-paced-creator-standard_v01_20261016-233420-702db4c9.md`);
- `~/.codex/AGENTS.md` (naming rules). The repository has no project-level AGENTS.md.
- the v06 capture tool, manifest, check and receipts.

## The defect: what it actually was

**v06 defect 5:** at 30 fps, a late-stance release followed by a re-press 1 frame later lifts both boots on one frame.

**Cause** (exact gait values: stance q 0..21, lift-off at offset −19, land +2):
1. At the re-press, the restart rule keeps the planted boot as the stance boot, with phase re-derived from it. It re-plans the other boot into a fresh swing whose lift rises to `replan_lift_min` = 2 at mid-swing.
2. In the defect case (city-bright, release at frame 6):
   - vl is planted at q = 16;
   - vr was coming down onto its v8 spot at lift 1.
3. One 30 fps frame is 9.3 px. So on the re-press frame:
   - vl passed its lift-off point (0 → lift 2);
   - vr was pushed back **up** (1 → 2).

   Both boots rose on the same frame. The same mechanism also appears one frame after every 30 fps start from idle, and after re-presses from both-planted states: there the stance boot leaves the floor before the re-planned swing has peaked.
   - In v06's captured receipts this happened on 16 frames in 11 of 129 re-press cases, plus once in each 30 fps walk start.
   - In the v07 sim with the lock off: 217 frames in 190 of 4,430 cases at 14 frame rates.

**Correction to the v06 note's attribution of "484 vs 473":**
- In the v06 receipt, the frame where both boots rise (tick 8) changes only **80 px** of silhouette.
- The **484 px** frame is tick 12, four frames after the re-press: vr's ordinary lift-off after its touchdown, with the arms still easing back to the gait pose.
- That frame is outside the re-press handoff, and it is identical in v07 (see remaining defect 1).

**The steady run never does this** (check 05: the v06 per-px table at every frame step from 1 to 10 px):
- both boots never rise on the same step;
- while both boots are in the air, the boot that lands next never rises.

## The fix (v07 rise lock)

A boot on a re-planned swing (re-press, start from idle, re-entry after a reversal) never rises while the other boot is off the floor. On each moving frame where the other boot is not in contact, the re-planned boot's lift is capped at the lift it was drawn with on the previous frame. It does not increase until its touchdown.

When the stance boot pushes off, the boot that lands next reaches for the floor, as it does in the steady run. A boot that leaves contact on this frame is never clamped. An airborne boot keeps lift ≥ 1.

**Only the drawn lift changes**, plus the lift a later release would start its landing from. All of these are exactly v06's:
- the re-planned boot's offset, view and knee lean;
- the scheduled touchdown distance, so the gait phase, stride sync and alternation;
- the planted boot's world position;
- every timing.

**Implementation:** the v07 capture tool **extends** the v06 tool. Its first line is `extends "<v06 tool file name>"`, and it checks the v06 tool's hash at start.
- `Loco7` subclasses v06's `Loco` and adds about 20 lines in `tick()`.
- The tool reads the v06 art read-only, plus a 5 KB amendment manifest (`restart_amendment.rise_lock`).
- v06 files are byte-identical: check 02 matches a 258-file listing pinned at 2026-10-18 08:22:39 UTC, before any v07 file existed.

**What did not change:**
- The art: 62 parts, 12 keyframes, 12 shadows, and the `.pxo` (12 frames × 13 layers) and `.ora` (62 layers) editable sources are v06's own files. No pixel was added or repainted, and no frame was added.
- The gait: stride 84 px, 6.67 steps/s at MOVE_SPEED 140, land +2, swing lift ≤ 2.
- Speed is unchanged.
- The v06 event-clock stop is unchanged.
- The approved selout v8 south static (`ccf9d2a2…68b6fd`) is unchanged against git HEAD.

## Results (real Godot 4.7.2, windowed, 640×360 canvas in 1280×720, scenes' own `_process`, isolated APPDATA)

Capture stamp `20261018-083355-72933ba3`, `RUN_V07_CAPTURE PASS`, exit 0, 19.4 min. Sim stamp `20261018-083358-56fe7deb`, `SIM7 PASS`.

**Main gates:**

| Measure | v06 | **v07** |
|---|---|---|
| Frames where both boots rise or both leave the floor: captured walk, stop, re-press, mixed-dt, showreel and reversal | 16 frames in re-press windows + 1 per 30 fps start | **0** (every captured sequence) |
| Same, gait-driver sweep (lock off = v06; every release frame × gaps 1..30 at 14 fps + 600 mixed-dt) | 217 frames / 190 cases | **0 / 4,430 cases** |
| Re-press alternation (the next touchdown is the other boot) | all | **all**: 502 captured + 4,430 sim |
| Re-press → next touchdown | 33–139 ms | **unchanged**: 30 / 60 fps 33.3–133.3 ms, 144 fps 34.7–145.8 ms; sim per-fps ranges equal v06 |
| Planted-boot world slip (every captured tick) | 0 px | **0 px** |

**The defect case** (`city-bright_repress-30fps-006-gap-01`):
- Re-press frame: vr is held at lift 1 instead of 2 (1 window px lower). It lands 2 frames later, at the same time as in v06.
- Per-frame silhouette change from the re-press:

| Frame from re-press | +0 | +1 | +2 (touchdown) | +3 | +4 | +5 | +6 |
|---|---|---|---|---|---|---|---|
| v06 (px) | 80 | 373 | 250 | 438 | 484 | 114 | 315 |
| v07 (px) | 101 | 370 | 250 | 438 | 484 | 114 | 315 |

  Frames +3 to +6 are unchanged from v06.

**Re-press handoff gate** (re-press frame through the next touchdown, against the steady run's per-frame maximum):

| fps | v07 handoff max | steady run max |
|---|---|---|
| 30 | 454 | 473 |
| 60 | 339 | 371 |
| 144 | 272 | 345 |

All 502 fixed-rate cases pass, and the gate is enforced.

**Stops:** 98 captured stops. Of these, 69 share a tag with v06, and every one draws the same state from the last moving frame to the v8 PNG, with the same time.

| fps | release → v8 | raised boot (limit 100) |
|---|---|---|
| 30 | 200–233.3 ms | ≤ 100 ms |
| 60 | 150–200 ms | ≤ 83 ms |
| 144 | 125–187.5 ms | ≤ 83 ms |

- In the sim, the stop times equal v06's sim receipt at all 14 frame rates.
- Every stop switches to the v8 PNG with 0 changed px.

**Mixed frame times:**
- Captured, city-bright, scenes' own `_process` with random dt: 16 re-presses (alternation and 0 faults) and 8 stops (182–250 ms to v8, raised ≤ 86 ms, 0 faults).
- Sim jitter: worst stop **270.8 ms**, identical to v06.

**Showreels:**
- All uninterrupted releases end on v8: 60 fps 183.3 ms, 30 fps 233.3 ms.
- The rise lock acts 3 times per 30 fps reel (the start and the quick re-press) and 0 times at 60 fps.

**Re-press sweep:**
- 30 fps: every release phase of one stride plus first-stride frames 5–9.
- 60 fps: every phase.
- 144 fps: every 2nd phase.
- Gaps: 30 fps 1–15 frames; 60 fps 1–30; 144 fps 1–34.
- Both scenes. Total 486 fixed-rate + 16 mixed-dt.

**Focused check: 13/13 OK** (`--receipt --sim-receipt --run-v06-check`). Check 10 runs the untouched v06 check, which scores **38/38**: rebuild byte-identical, compositor and palette parity, and Pixelorama `.pxo`/`.ora` split-layer editability.

## Remaining defects (plainly)

1. **A pose spike after the handoff at 30 fps is not fixed.**
   - In 5 of 156 cases at 30 fps (gap 1, phases 7 and 16, both scenes), the 2nd–3rd frame after the next touchdown changes 477–484 px. The steady 30 fps run peaks at 473.
   - That frame is the landing boot's ordinary lift-off while the arms are still easing (one pose step per tick, never on a boot-event tick; v05 rule).
   - It is identical in v06, and it is the "484" the v06 note quoted.
   - Fixing it means changing the arm easing. That is a separate change outside this fix; I did not make it.
2. **The same at 144 fps:** 42 of 150 cases show 374 px against the steady run's 345, on the frame after the next touchdown, with no boot event.
   - It is identical in v06 for every shared tag, and it is also present in the 144 fps start from idle.
   - It is outside the handoff. Not changed.
3. **The visible size of the fix is small.** On the defect frame the leading boot sits 1 window px lower (lift 1 instead of 2) and does not re-rise. The improvement is about boot order and contact logic, not a large silhouette change. Whether the re-press now reads as fluid is a judgment for Root and the creator at 1×; the math does not show it.
4. **At high frame rates the re-planned start/re-press step is lower.** The lock acts on frames where v06 raised the leading boot while the other was airborne (sim: 1,856 clamps at 240 fps, 546 at 144 fps). That step now skims at lift 1 for part of its swing. The floor gap is smaller, not larger, and the steady gait is untouched (per-px gate 100%).
5. **Mixed frame times are still slower.** The worst jittered stop is still **270.8 ms** (sim: 30/45/60/144 fps random, seed 6061), and the worst captured jittered stop is 250 ms. This is the v06 stop clock's limit; v07 does not change the stop.
6. **Inherited from v06, unchanged:**
   - 30 fps stops sit at the 233.3 ms boundary;
   - 24 fps raised boot 125 ms (recorded only);
   - it is still a run (50% airborne);
   - 6.67 steps/s may read as busy;
   - reversal is a hard cut to the runtime placeholder north walk;
   - re-entry takes 150 ms to the first touchdown;
   - 1 px head sway;
   - a test-only contact shadow.
7. **Agent review only.** I inspected captured frames as zoomed strips (scratch, not delivered). I cannot play the MP4s in real time.

## Review package (bounded; all `outputs/…south-run-v07-…_20261018-083355-72933ba3.*`)

Every file is a separate single view: no collage, no contact sheet.

**Normal-speed 1× showreels** (full 1280×720 window):
- `…city-bright…-preview-showreel-1x-60fps…mp4` and `…annex-dark…-preview-showreel-1x-60fps…mp4`: 60/1, 187 frames each.
- `…city-bright…-preview-showreel-1x-30fps…mp4` and `…annex-dark…-preview-showreel-1x-30fps…mp4`: 30/1, 94 frames each.
- Each covers: idle on v8 (48 px logical hero), start, sustained run, quick release and re-press, reversal (runtime placeholder north, not pilot art), south again, and two releases to the v8 stop destination.

**Worst-case clips** (hero crop, real time, 2× nearest):
1. `…city-bright…-worst-repress30-r006-g01-2x-30fps`: the v06 defect case.
2. `…city-bright…-worst-repress30-r015-g03-2x-30fps`: the largest 30 fps handoff, 454 px.
3. `…annex-dark…-worst-repress30-r018-g01-2x-30fps`: the largest dark-scene 30 fps handoff, 428 px.
4. `…city-bright…-worst-repress60-r037-g02-2x-60fps`: the largest 60 fps 200 ms change, 371 px.

Mixed-dt runs are not filmed: a fixed-rate MP4 would misstate them, so their timings are in the receipt.

**2 diagnostic stills:** `…-diag-repress30-r006-g01-{before-repress,repress-frame}…png`, full window and colour-exact.

**Receipts:**
- `…city-annex…-v07-capture-receipt…json` (4.0 MB);
- `…city-annex…-v07-preview-receipt…json`;
- `…gait-driver…-v07-sim-timing-receipt…20261018-083358-56fe7deb.json`.

## Exact dependency list

All v07 files are new and untracked. Existing files were only read.

| v07 file | sha256-text-lf-v1 (first 16) |
|---|---|
| `game/assets/characters/run-v07-unapproved/.gdignore` (empty) | `e3b0c44298fc1c14` |
| `…/…south-run-v07-restart-amendment-manifest_unapproved-nonruntime_20261018-082500-a07441de.json` | `cae11828fa90be6b` |
| `tools/…south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd` (1036 lines; extends v06) | `1be872365334ffe5` |
| `tools/…south-run-v07-preview-mp4_m8-w10_20261018-082500-476ee16b.py` | `aff100a7014a7fa3` |
| `tests/protagonist-female-south-run-v07/…_focused-check_unapproved-m8-w10_20261018-082500-ceb842bf.py` | `c4821736dd7a7781` |
| `outputs/…v07-capture-receipt…72933ba3.json` | `2a8f7f3c4a8c9df0` |
| `outputs/…v07-preview-receipt…72933ba3.json` | `156ca8f885e188f3` |
| `outputs/…v07-sim-timing-receipt…56fe7deb.json` | `b0c664381c248c2c` |
| 8 MP4 + 2 PNG in `outputs/` | in the preview / capture receipts (sha256-bytes) |
| this note | — |

**Read-only dependencies, pinned by hash:**
- the v06 capture tool `…v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd` (`51f389a8…`), which is the parent script;
- the v06 manifest (`f59b04fa…`);
- the v06 builder (`2b83a221…`);
- the v06 asset folder (90 files);
- the v06 check and receipts (for checks 08 and 10);
- the v8 PNG;
- `game/scenes/scifi_exploration_area.tscn` and `survey_annex.tscn` with their scripts (MOVE_SPEED 140; read and run only, not modified);
- Godot 4.7.2 console, Pixelorama 1.2.3 (check 10), ffmpeg, Python 3.12 (runtime path).

Total new files: 18 (10.2 MB) plus this note. Scratch is in `work/loco-v07-scratch/` (gitignored, 2.5 GB of per-frame crops and inspection strips). `git status game/` shows only the new `run-v07-unapproved/` folder.

## Reproduce

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
GD=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
T=<abs>/tools/…south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd
APPDATA=<scratch> $GD --headless --path game -s $T -- --sim=1                       # sim receipt -> outputs/
APPDATA=<scratch> $GD --path game -s $T -- --motion-dir=<abs scratch>               # windowed capture -> outputs/ (~20 min)
$PY -I -B tools/…v07-preview-mp4_…-476ee16b.py --motion-dir <abs scratch> --receipt outputs/<v07 capture receipt>
$PY -I -B tests/protagonist-female-south-run-v07/…-ceb842bf.py --receipt outputs/<capture receipt> --sim-receipt outputs/<sim receipt> --run-v06-check
```

**Reversal:** delete the following. Nothing existing was modified.
- `game/assets/characters/run-v07-unapproved/`
- `tests/protagonist-female-south-run-v07/`
- the two `tools/…south-run-v07…` files
- this note
- `outputs/*south-run-v07*`

## Closeout proposal (zero impact)

This is a technical candidate only. Proposed counter state, unchanged:

| Counter | Value |
|---|---|
| Overall | **40.8%** |
| Accepted scenes | **3/12** |
| Full sprites | **0/52** |
| Human playtests | **0/2** |

- No acceptance, approval or runtime integration is proposed.
- If Root wants a ledger receipt, it would be a zero-change receipt pointing at this note. That is for Root or the ledger stream to write; this stream did not touch the ledger, the Bible, progress or the index.

## Decision for Root / Codex / the creator

1. Watch the two 30 fps showreels and the four worst-case clips at 1×. Does the re-press now read as one boot pushing off while the other reaches down? Is the remaining post-touchdown arm-easing frame (defect 1) acceptable, or should arm easing get its own bounded pass?
2. The v07 rule can be folded into a later runtime candidate only after the south run is approved as a motion baseline. Other directions and combat stay out of scope until then.
