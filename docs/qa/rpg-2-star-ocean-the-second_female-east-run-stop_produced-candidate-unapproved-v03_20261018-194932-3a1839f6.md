# Female EAST run/stop v03 - produced candidate, unapproved

Task: `content.char.protagonist-female.walk-east`. This is the production package for one EAST run and one representative stop. Producer checkout: `work/max0840-male`, base `4b0ff58`. Nothing was staged, committed or pushed. No game, default, navigation, registry, Bible, ledger or Site file changed.

**Not claimed:** art, fluidity, full-sprite or motion approval, and no ledger credit. Only the SOUTH v8 static and the 48-logical baseline are creator-approved. The EAST static and all motion remain unapproved.

## Original failures and the source fix (root)

- **Slow body probe.** v01 failed 44 trajectory gates and v02 failed 26 step gates. Root kept both raw slow reports as lossless gzip in `outputs/female-east-run-v03/*slow-failure-evidence*.json.gz`.
- **Optimized checker.** Root's source-bound checker reproduced the v02 result exactly: 15744 gates, the same 26 failed keys and details, the same summary, in 72.324708 s, with 9/9 full-render coat parity.
- **Source fix.** Root fixed the source, not the thresholds. The locked model is `tools/rpg-2-star-ocean-the-second_female-east_run-stop-source_unapproved-v03_20261018-193030-48da69c1.gd`, SHA256 `e783de5d8ab6b1e3f678299eb8cffde11109d1aab06c47155831ebc4388bb07f` (raw LF; verified before and after every step). It keeps the v02 textured leg warp, the EAST static identity and the kinematics. In run only, it adds an integer-pixel torso step guard with budget `ceil(48*delta - eps)`. World speed, gait phase and boots are unchanged.
- **Root body report.** `outputs/female-east-run-v03/rpg-2-star-ocean-the-second_female-east_body-continuity-report_v03_20261018-193030-6d8bd4ef.json`: 15744/15744, 0 failed, 68.297937 s.
  - Step limits: 30 fps 2/2, 60 fps 1/1, mixed 2/2. No-rise 0. Final static exact.
  - It was **not rerun** here. Its checker is in the sibling `max0840-wdc-ruin/tools/*projection*test-only-v02*5ce91065.gd`, SHA256 `0b110a62...a4f3`; its bytes match the report.
  - Its field `fullStopRendersRetained=384` counts the **initial (release) frame** of each of the 384 full plain-stop sequences (128 phases × 3 schedules). Every later settle frame in those sequences is also fully rendered but is not counted there, so 384 is not the total number of full `render_pose` calls.

## Editable native sources

The bake tool `...native-bake_test-only-v03...gd` produces every cel from a real `advance()` state rendered by the model's own `render_pose()`, including the torso. No approximation helper is used.

- **Run cels.** 400 ticks at 1/280 s, +0.5 world px each. States are kept after tick 256, giving all 128 phases. Each torso equals `round(steady_body(q))`, checked independently.
- **Stop cels.** For each of the 128 release phases, the same 280 Hz run is released and advanced at 1/60 s until idle. The representative phase is the worst final-settle case, **q060**: 15 frames, with the last moving frame f12 and stop age 0.200 s. Frame f13 equals the final static f14.
- **Determinism.** Two independent bakes were identical.

PXOs follow the WEST packager conventions: 12 named EAST role layers in the EAST static order, plus a hidden, locked `guides` layer with the v8 border, body rows and pin (40,104).

| PXO | Frames | Cel timing | Playback |
|---|---|---|---|
| `outputs/female-east-run-v03/...female-east-run_animated-source_unapproved-v03_...pxo` | 128 | 70 fps × 0.25 | cycle 128/280 s |
| `outputs/female-east-run-v03/...female-east-stop_animated-source_unapproved-v03_...pxo` | 15 | 60 fps × 1 | 0.25 s |

The full-frame PNG and RGBA bake stayed in Temp. The native manifest stores every frame's PNG and RGBA hashes and the hashes of all 13 role cels.

## Native validation

- **Native gates: 731/731.** Covered for every cel and frame:
  - roles composite to the full frame;
  - binary alpha;
  - approved v8 palette (SOUTH idle phase00 PNG `ccf9d2a2...6fd`);
  - no cell-edge texels;
  - no guide/sprite overlap, and the guide pin is set;
  - PXO metadata: 80x112, frame count, fps, durations, layer names, hidden locked guides;
  - PXO cels byte-equal to the roles;
  - the final stop equals both the EAST static composite and its preview.
- **Pixelorama 1.2.3 CLI.** Each PXO was reopened in a separate process with isolated APPDATA/LOCALAPPDATA, then exported with `--split-layers`.
  - Run: exit 0, 1536/1536 role cells exact.
  - Stop: exit 0, 180/180 role cells exact.
  - Hidden guides were not exported.
- **Diagnostics are not clean.** Each process printed **4 inherited headless shader-compiler errors** (`custom_samplers ... shader_compiler.cpp:1329`), kept verbatim. They are not counted as clean-app success: `cleanAppSuccess=false`. There were no other diagnostics.
- **No GUI claim.** No GUI Save As or reopen is claimed for EAST, and no animated ORA.
- **Visible extent.** Run x0 13-24, x1 59-70, y0 6-10, y1 98-104. Stop x0 20-23, x1 57-70, y0 7-8, y1 103-104. Alpha height is 91-97 source px (45.5-48.5 logical); the static baseline is 96/48.

## Exact rendered boundaries (`...transition-check_test-only-v03...gd`)

**Result: 25381/25381, 0 failed, 58.4 s, no caching needed.** This is the v02/WEST exact-boundary matrix unchanged:

- Schedules: 30, 60 and mixed 24/60/48/30.
- All 128 phases with no seam or flight exclusion.
- Covered paths: initial run from idle, release, 1/2/3-frame re-press, and final static.
- Rendered boot texels are world-locked and checked across the full floor row.
- Thresholds are the same.

One addition: 128 `seed-real-advance-state` checks. In v03 the torso is integer and guarded, so the old continuous `steady_body()` seed is not a reachable state. Each phase is therefore seeded with the real 280 Hz `advance()` state (the native cel) and checked first against independent `expected_body()`/`gait_foot()`.

Measured maxima (30 / 60 / mixed):

| Measure | 30 fps | 60 fps | mixed | Limit |
|---|---|---|---|---|
| Settle | 233.3 ms | 233.3 ms | 225.0 ms | 250 ms (300 ms mixed) |
| Raised-foot landing | 66.7 ms | 66.7 ms | 79.2 ms | 100 ms |
| Re-press first support | 33.3 ms | 50.0 ms | 41.7 ms | 100 ms |

Body step and no-rise checks are covered by root's report and are not duplicated here.

## Actual ordinary-Input gameplay (`...actual-prototype_test-only-v03...gd`)

Setup: Godot 4.7.2 with `--fixed-fps` and `--resolution 640x360`, CANVAS_ITEMS 640x360, normal 1x, isolated APPDATA. Input is `Input.action_press/release` on `move_left`/`move_right`. The unmodified scene script moves the hidden hero, and a test presenter draws the model at scale 0.5, offset (-40,-104). The lane is the same as v01/v02 (x 160 to about 505).

| Capture | Frames | Duration | Internal checks | Steady frames = native cel |
|---|---|---|---|---|
| City bright EN, 30 fps | 120 | 4.000 s | 480/480 | 68/68 |
| Annex room 2 dark ZH, 60 fps | 238 | 3.967 s | 952/952 | 131/131 |

- **Internal checks** per frame: fixed delta, physical Input delta, viewport, and presented texture == source RGBA.
- **Steady frames** are RGBA-equal to their native cel. 0 steady frames were torso-held by the guard in these two captures.
- **Other frames.** Idle frames (15 / 27) and the final frame equal the EAST static exactly. WEST-input frames (6 / 12) show the WEST static placeholder.
- **Capture/source deltas.** The sprite canvas origin equals the source `renderX` (`round(heroX*2)/2`), with constant y, scale 0.5 and offset (-40,-104). Where both source RGBA and origin are unchanged (12 / 27 frame pairs), the 42x54 sprite window changes 0 pixels. The full per-frame heroX/renderX/window/frame deltas are in the evidence manifest.
- **Diagnostic only, not a gate.** On-screen sprite pixels equal their unambiguous 2x2 source texel in 14552/17387 compared texels (bright) and 32746/33252 (dark). The remainder are covered by scene overlays: y-sorted NPCs and props, name labels and interaction markers. The bright idle start is partly covered by a kiosk label and marker.
- **Movies.** h264 yuv420p 640x360; 30/1 with 120 frames, and 60/1 with 238 frames. The logs contain no ERROR or SCRIPT lines.

## v02 comparison (disclosure)

- **Run cels.** 119 of the 128 v03 run cels differ from the v02 renderer by 1-77 texels (mean 24.9), mostly in near-arm rows 40-75. The cause: v03 makes the torso y an integer, and `render_pose` places the near-arm shoulder at the body vector, so the arm pivot is now pixel-aligned.
- **Representative poses.** q000, q019, q051 and the whole q060 stop sequence are byte-identical to v02. The six critical native PNGs therefore look the same as v02's.

## Critical PNGs (separate files)

- **Native** (80x112, exact bake bytes):
  - run contact q000, passing q019, flight q051;
  - stop last-moving f12, penultimate f13 and final f14 at q060, 60 fps.
- **Gameplay** (640x360, 7 per scene, original capture bytes): contact, passing, flight, release-first, repress-first, settle-before-idle and final-static.

## Remaining limits (not fixed here; no retune)

- WEST input shows the WEST **static placeholder**. No WEST motion or reversal animation is claimed.
- The presenter is test-only. The game still shows its existing hero, with no default, nav or registry integration.
- Pixelorama CLI export is exact, but the app diagnostics are not clean (see above). There is no EAST GUI Save As claim.
- Native cels are the 280 Hz reference. Live 30/60 fps rendering may hold the torso 1 source px for a frame. This did not occur in either capture's steady frames.
- Art is as reviewed:
  - the contact far thigh is barely visible below the coat hem;
  - the near-arm back-swing exposes light chest specks;
  - the passing pose reads as a narrow leg column;
  - the moving alpha height varies, at 91-97 source px.
- One language per scene. The bright idle start is partly covered by an overlay.

## Reproduce

Run from the checkout root, with Godot `work/tooling/godot-4-7-2/..._console.exe` and an isolated APPDATA.

1. Bake: `--headless --path game -s <bake.gd> -- <temp>/bake_a`
2. Package: `python -I <native-package.py> <temp>/bake_a`
3. Boundary matrix: `--headless --path game -s <transition-check.gd> -- <temp>/trans_v03.json`
4. Capture: `--path game --fixed-fps {30|60} --resolution 640x360 -s <actual-prototype.gd> -- <temp>/cap{30|60} {30|60} {city-bright|annex-room2-dark}`
5. Movies: ffmpeg x264 crf 12, yuv420p.
6. Evidence: `python -I <package-evidence.py> <temp>`
7. Portable check: `python -I <evidence-check.py>`

The temp root also needs `v02np/all` from the v02 native-poses tool; it is used for the comparison only.

Evidence manifest: `outputs/female-east-run-v03/rpg-2-star-ocean-the-second_female-east-run-stop_evidence-manifest_v03_20261018-194932-3a1839f6.json`.
