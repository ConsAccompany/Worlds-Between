# Female protagonist south RUN v10r1: bounded amendment of v10 (QA note, m8-w14)

**Status: UNAPPROVED / NONRUNTIME, produced candidate for Root review. Fluidity is NOT accepted.** Single direction (south), test-only, not wired into the runtime.
- Every approval flag in the r1 manifest is `false`. Sprites stay at 0/52.
- No Game Bible, meter, ledger, default-runtime, north-direction, memory or schedule change was made. Nothing was pushed or merged.
- Worktree `work/max0840-motion` only, base `160b823`.
- Auth: Max, first-party (claude.ai login, no API key in the environment). No cloud, paid usage or fallback; no quota stop.

**Parent: v10, preserved unchanged.** The v10 builder, capture tool, MP4 tool, asset folder, receipts, MP4s and PNGs are byte-identical; check 01 verifies them against their hashes.

The only edit to v10 files is a correction in the v10 QA note. It now states plainly that v10 **violates** Root's ≤ 100 ms raised-boot criterion: one existing mixed-frame-time stop held a boot for 105.6 ms, although v10's focused check reported 9/9 PASS.

## Root review that started r1

- The slower cycle is visibly different, and body and identity are retained.
- The leading leg is still a long diagonal.
- The 105.6 ms mixed-frame raised boot is non-compliant.

## What r1 changes (two items, nothing else)

**1. Shorter leading reach: 4 source px (Root's choice).**
- The 44 px stance on the 128 px stride is split **+8 / −36** instead of +12 / −32.
- Unchanged: 4.375 steps/s, 68.75 % of the cycle with a boot on the floor (measured 4.35 / 4.38 / 4.38 steps/s at 30 / 60 / 144 fps).
- The planted boot still keeps its world row for the whole stance. The knee lean returns to 0 at the v8 spot (q 8).
- Stance roll, torso compression and torso-shift timing stay on v10's q table.
- **The swing curve was re-authored, not uniformly stretched:**
  - the knee stays tucked forward through passing (`hang` until u 740, o −2);
  - the leg opens late and short (`reach` u 740–940, o −2 → +7);
  - the heel strike is a short lift-1 pose (o +7 → +8).
  - In v10 the leg opened at u 650 (o −5) and reached o +12.
- Art, leg rule, push-off boots, coat lag, seam ink and the island rule are v10's. No new part PNGs.

**2. One landing rule: staggered touchdown** (manifest `stop.v10r1_landing_rule`; driver `Loco10r1`).
- After a release, each landing boot moves on its own event clock. A landing boot's change to its mid key is no longer held back by the other boot's change.
- Only touchdowns are staggered: two boots never touch down on the same frame.
  - The boot due first lands (tie: the earlier move start, then vl).
  - The other keeps its last in-air key (u 999) and lands on the next frame.
- There is still no teleport: v06's no-pose-skip still makes every boot show its mid key before touchdown.
- Stop durations, the shuffle (one boot at a time, after the landings), the body settle order and the event clock are unchanged.
- **Why this rule:** v06/v10 allowed only one boot view change per frame. A stop released with both boots in the air could push the second boot back frame after frame (105.6 ms in v10).

## Results (real Godot 4.7.2, windowed 1280×720 of the 640×360 canvas, scenes' own `_process`, isolated `%TEMP%\v10m` copy + APPDATA)

**Focused check: 16/16 OK.** Every gate is listed separately.

| Gate | r1 | v10 |
|---|---|---|
| GDScript Comp10 == r1 builder (neutral, 16 keyframes + shadows, all 128 per-px sha256) | exact | exact |
| Planted boot world slip, every captured tick | 0 px | 0 px |
| **Boot down after release, 30 fps** (sim, every phase) | **≤ 66.7 ms** | 100 |
| **Boot down after release, 60 fps** | **≤ 50.0 ms** | 83.3 |
| Boot down, every other constant rate ≥ 30 fps | ≤ 62.5 ms | ≤ 83.3 |
| **Boot down, mixed frame times: 24 existing seed-6061 stops** | **max 88.9 ms, 0 over 100** | **105.6 (non-compliant)** |
| Boot down, mixed: 300 more (choice) + 300 more (uniform) | max 88.9 / 81.5, 0 over 100 | — |
| Same r1 gait through v10's landing rule (comparison only) | 6061: 90.3; extra sets: 111.1 / 106.9, 4 stops over 100 | — |
| Release → v8, 30 fps / 60 fps (sim, every phase) | 200–233.3 / 150–216.7 ms | same |
| Release → v8, mixed (624 stops) | 140.3–272.2 ms (≤ 300) | 150–250 (24 stops) |
| Captured stops (city 30 + 60 fps, annex 30 fps, every phase) | v8 150–233.3 ms; raised ≤ 66.7 ms | raised ≤ 100 |
| Switch to the v8 PNG | 0 changed px | 0 |
| Re-press | 140 captured + 6,400 sim; 0 alternation failures, 0 both-rise frames; next touchdown 33–217 ms | 33–200 |
| Reversal final stop | 150 ms | 166.7 |
| Showreel releases (same inputs) | city 30 fps 200 / 200 ms; annex 60 fps 150 / 150 ms | same |
| Steady pose change per frame, 30 / 60 / 144 fps (cell XOR) | 417 / 277 / 205 | 481 / 351 / 226 |
| Pixelorama 1.2.3 headless round trip | `.pxo` 16 × 13 layers exact; `.ora` (v10 parts) exact | exact |

- **24 fps (informative, not gated):** release → v8 250–291.7 ms; boot down ≤ 83.3 ms (v10: 125 ms).
- **All-boots-down time:** 30 fps stops still take 100–133 ms until the second boot's shuffle ends. Root's criterion is per boot (each boot back on the floor ≤ 100 ms), and that holds. The full settle is the ≤ 250 ms v8 gate.

## Agent inspection (not a fluidity judgement)

I compared the v10 and r1 heel-strike frames at the same tick in the city reel. The r1 leading leg is visibly shorter but is **still a diagonal leg**; 4 source px is 2 window px at gameplay size.

Because lift-off is now 4 rows further back:
- the rear heel-kick boot sits higher behind the hips and is hidden on more frames;
- at −36 the planted rear boot is fully behind the hips on its last stance ticks.

The planted gate therefore treats any same-view tick pair whose every boot texel keeps its world position and RGB as occlusion, not slip. The capture equals the composite exactly on every tick. Such pairs are counted in the receipt (up to 8 per walk at 144 fps, 4 at 60 fps). I did not judge whether the result reads fluid; only Root/creator viewing at 1× can.

## Limits

1. The leading leg is still a long diagonal; the reduction is modest by Root's chosen size.
2. The re-press and reversal sweeps keep v10's half-stride release window and the y 160 city start (navigation limit).
3. Arms, hair, cape, torso and head are still v06 parts re-timed to the cycle. Reversal still cuts to the runtime placeholder north walk.
4. "annex-dark" is v07's darkest annex floor (tan), not a night scene.

## Files (new, untracked until the selected commit)

| File | Hash (first 16) |
|---|---|
| `tools/…v10r1_reach-landing-amendment-build_m8-w14_…249dbf66.py` (imports the pinned v10 builder read-only) | lf `0ec1a07cd1a57a5b` |
| `tools/…v10r1-godot-capture_m8-w14_…249dbf66.gd` (extends the pinned v10 tool) | lf `0cb300fd528f8608` |
| `tools/…v10r1-showreel-mp4-and-critical-frames_m8-w14_…249dbf66.py` | lf `7d7112680a892a0a` |
| `tests/female-south-run-v10r1/…focused-check_m8-w14_…249dbf66.py` | lf `35bd6a18c9eade83` |
| `game/assets/characters/run-v10r1-unapproved/` (35 files: `.gdignore`, 16 keyframe + 16 shadow PNGs, `.pxo`, manifest) | — |
| manifest `…v10r1_gait-pose-manifest_…4b035d3e.json` (`parent` = the v10 manifest, sha256-text-lf-v1 `de1789e376c34340…`) | lf `d3721d47ed3da00e` |
| keyframes `.pxo` | `f52c09fc2d65537d` |
| `outputs/…city-bright_female-south-run-v10r1-showreel-1x-win1280-of-640-30fps-h48_…68e7ba6b.mp4` (94 frames) | `34f49343bbce9761` |
| `outputs/…annex-dark_female-south-run-v10r1-showreel-1x-win1280-of-640-60fps-h48_…ec71ab8a.mp4` (187 frames) | `ac7e1efe10c2ab8b` |
| 12 critical-frame PNGs (per reel: strike, flight, repress-land, stop-release, stop-land, stop-v8; full 1280×720 window, byte copies) | in the reel receipt |
| `outputs/…v10r1-sim-timing-receipt_…182712-115d7256.json` | lf `4bddde24314816fa` |
| `outputs/…v10r1-capture-receipt-h48_…182800-9ee66cb8.json` | lf `939fccf6b886d30e` |
| `outputs/…v10r1-showreel-and-critical-frames-receipt_…ee3b1fdf.json` | lf `d1a4b12f005b32f3` |

The r1 Godot tool, MP4 tool and focused check were generated from the pinned v10/v06 bodies by scratch generators in `%TEMP%\v10s` (not part of the deliverable). The generated files are the sources.

## Reproduce (worktree root)

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
$PY -I -B tools/<r1 build>.py --out-dir game/assets/characters/run-v10r1-unapproved
# isolated copy %TEMP%\v10m: game/ (incl. run-v09/v10/v10r1 folders) + the v06, v07, v09, v10, v10r1 capture tools; --import once
APPDATA=<copy>/appdata Godot_console --headless --path <copy>/game -s <copy>/tools/<r1 gd> -- --sim=1 --out-dir=<abs>
APPDATA=<copy>/appdata Godot_console --path <copy>/game -s <copy>/tools/<r1 gd> -- --motion-dir=<abs> --out-dir=<abs>
$PY -I -B tools/<r1 mp4>.py --frames <motion dir> --receipt <capture receipt> --out-dir outputs
$PY -I -B tests/female-south-run-v10r1/<check>.py --pixelorama --sim-receipt … --receipt … --reel-receipt …
```

**Reversal of r1 only:** delete `game/assets/characters/run-v10r1-unapproved/`, the three r1 tools, `tests/female-south-run-v10r1/`, this note and `outputs/*female-south-run-v10r1-*`. v10 is unaffected.

## Decision for Root

1. Watch the r1 1× MP4s next to the v10 1× MP4s (same inputs). Is the shorter, later-opening reach an improvement, or is the leading leg still too long a diagonal at 48 px?
2. Watch the stop moments (`stop-release` → `stop-land` → `stop-v8`, and `repress-land`). Do the staggered touchdowns read as a planted stop without a snap?
