# Female south run v3r2 (m8-w03): gameplay-scale preview in Godot

M8, 2026-10-15 (UTC 08:09–08:25), by Claude (Claude Code). Before any work, `claude auth status` reported: logged in via claude.ai, provider firstParty, subscription Max. Neither `ANTHROPIC_API_KEY` nor `ANTHROPIC_AUTH_TOKEN` was set, and neither Bedrock nor Vertex was selected.

- **v3r2 is still unapproved.** This preview is review evidence, not art acceptance. Quality is **not** declared passed. The creator's approval still covers only the selout v8 SOUTH IDLE static frame at the 48 logical px display scale.
- **Test-only and reversible.** No runtime sprite, scene, script, save or asset was edited or integrated. Delete the two `game/tests` files and the outputs listed below and the repository is back where it was.
- **Untouched:** Game Bible, tracker, readiness ledger, v3 builder, and the v3r2 and v8 PNGs. Their hashes were checked on every run. No Git operation was performed.

## Files

| File | State | Hash |
| --- | --- | --- |
| `game/tests/…_south-run-v3r2-gameplay-preview-capture_m8-w03_20261015-080950-d66e3403.gd` | New, 581 lines, LF, ASCII | sha256-text-lf-v1 `5f28ae22…a45d` |
| `game/tests/…_south-run-v3r2-gameplay-preview-capture_m8-w03_20261015-080950-30366cc6.tscn` | New, runner scene | sha256-text-lf-v1 `64fddd84…e712` |
| This note | New | n/a |
| 12 PNG + 6 GIF + 1 JSON receipt in `outputs/`, run id `20261015-081409-c274b009` | New | receipt `a9fa3cc4…403c`; each PNG's sha256-bytes is in the receipt (`outputs_sha256_bytes`) |

**Run** (windowed, from the repository root):

```
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/rpg-2-star-ocean-the-second_protagonist-female_south-run-v3r2-gameplay-preview-capture_m8-w03_20261015-080950-30366cc6.tscn -- --motion-dir=<abs scratch dir>
```

It takes about 80 s and exits 0. Per-tick captures, all 16 per-frame stills and the sprite-free backgrounds go to the scratch dir (`%LOCALAPPDATA%\Temp\wb-v3r2-d66e3403\`, 948 files, outside the repository). Images bound for `outputs/` are held in memory and written only after every gate has passed. A first run failed (see "Run history"), and its partial outputs were deleted.

## How the preview works

**Scenes.** These are existing game scenes, instantiated read-only through `AppState` with a test save root.

| Key | Scene | Hero start (logical) | Note |
| --- | --- | --- | --- |
| `city-bright` | `scifi_exploration_area.tscn`, `scifi.city` | (340, 165) | default first-visit layout |
| `outskirts-bright` | `scifi_exploration_area.tscn`, `scifi.outskirts` | (250, 150) | sunlit paving |
| `annex-dark` | `survey_annex.tscn`, `scifi.city`, room 2 | (240, 150) | The darkest annex floor of the six rooms: relative luminance ≈ 0.13 against 0.16–0.26 for the others. It is dark stone, **not** a night scene. |

**Movement is the runtime's own code.**
- Each tick calls the scene's `_process(delta)` with `move_down` held.
- `MOVE_SPEED` is read from both scripts and asserted to be 140.
- Measured speed is 140.000 logical px/s in every mode; the 144 fps modes measure 140.001 in the outskirts and the annex.
- The runtime hero is hidden, and a v3r2 `Sprite2D` is drawn at its position with these settings:
  - nearest filtering, scale 0.5, cell pin (40, 104), no flip and no shadow;
  - frame chosen by distance from the manifest's `hold_px` table (70 px cycle);
  - root lock `r = r_start + slope·s` from the manifest;
  - start 1 px into the loop, as in the v2 harness.
- Display is a 640×360 canvas in a 1280×720 window, so 1 texel = 1 window px = 0.5 logical px.

**Modes per scene.** Each mode covers 140 logical px, which is two loops.

| Mode | Tick rate | Ticks | Root lock |
| --- | --- | --- | --- |
| `run-140` | 60 fps | 61 | on |
| `run-140-30fps` | 30 fps | 31 | on |
| `run-140-144fps` | 144 fps | 145 | on |
| `run-140-nolock` | 60 fps | 61 | off (ablation) |

## Gates (all pass; any failure exits 1)

- **Source locks:**
  - the manifest's sha256-text-lf-v1 is `dbf41fdb…3c3a`;
  - all 16 frames match the manifest's sha256-bytes;
  - v8 is `ccf9d2a2…b6fd`.
- **Manifest contract:** cell 80×112, pin (40, 104), `logical_height_px` 48, scale 0.5, `flip_h` false, and the `hold_px` values sum to the 70 px cycle.
- **Alpha:** every frame's alpha is only {0, 255}.
- **Capture size:** every capture is 1280×720.
- **Stills.** All 16 frames plus v8 were captured at the hero's start ground point in each scene, 51 stills in all.
  - Every opaque texel is exact RGB in the capture: for example, 2322/2322 (f01), 2272/2272 (f07) and 2419/2419 (v8).
  - **No transparent texel changed the background**: 0 changed in every still. So there is no halo, no fringe and no filtering.
- **Motion:** exact-RGB fidelity on every 5th tick, |root offset| ≤ 4/3 logical px, and straight-south movement on every tick.

## Measured on captured pixels (report-only, not quality verdicts)

**Foot slip.** This is the lowest masked sprite row of the planted leg's foot band, measured against the sprite-free background over consecutive planted ticks. The camera is static.

| Mode | Ticks per stance | Slip per stance (window px), all 3 scenes |
| --- | --- | --- |
| run-140, lock | 5 | **0** |
| run-140-30fps, lock | 2–3 | **0** |
| run-140-144fps, lock | 11–12 | **0** |
| run-140-nolock | 5 | 1 |

At 60 fps the lock removes only about 1 window px (0.5 logical px) of slip per stance.

**Frames shown.**
- At 60 and 144 fps, all 16 frames appear.
- At 30 fps, 11 of 16 appear. f02, f04, f09 (vl contact), f11 and f13 never appear at this start phase, as the v3 infrastructure note predicted.

**Pixel scale and ground pin.**

| | Opaque height | Lowest opaque row vs. the hero's ground line |
| --- | --- | --- |
| v8 | 96 texels = **48.0 logical px** | 1 window px above |
| v3r2 contact frames (f01/f09) | 102 texels = 51 logical px | 6 window px **below** |
| v3r2 flight frames | 100 texels = 50 logical px | 2 window px below |

- The texel-to-pixel mapping is exactly 1:1; the fidelity gate proves this.
- The run is **2–3 logical px taller than the approved 48 px figure**, because of the long contact leg already listed in the r2 note.
- In motion, the planted sole stays world-fixed while the hero point advances. Relative to the hero's logical ground line, it runs from 6 window px below to 13 above (3 below to 6.5 above logical).

**Head step per tick** (window px; the cost of the lock plus the bob):

| Mode | Nominal | Measured | Most common |
| --- | --- | --- | --- |
| 60 fps, lock | 4.67 | 1 to 6 | 5 (24 of 60) |
| 60 fps, no lock | 4.67 | 3 to 6 | — |
| 30 fps | 9.33 | 5 to 12 | — |
| 144 fps | 1.94 | −1 to 6 | — |

At 144 fps the head moves back up by 1 px on 4 ticks and stalls on 28.

**Display contrast.** This is the WCAG-style ratio of each silhouette-edge texel against the captured background pixel just outside it. "Figure vs ring" compares mean luminances.

| Scene | Frame | Edge median | Edge p10 | Edges ≥ 3:1 | Figure vs ring |
| --- | --- | --- | --- | --- | --- |
| city-bright | v8 / f01 / f07 | 3.77 / 3.81 / 3.78 | 1.36 / 1.35 / 1.34 | 59% / 58% / 59% | 1.15 / 1.13 / 1.13 |
| outskirts-bright | v8 / f01 / f07 | 3.42 / 3.44 / 2.91 | 1.35 / 1.28 / 1.29 | 57% / 57% / 49% | 1.52 / 1.51 / 1.50 |
| annex-dark | v8 / f01 / f07 | 2.99 / 3.20 / 3.09 | 1.31 / 1.25 / 1.25 | 50% / 54% / 53% | **1.03 / 1.02 / 1.02** |

v3r2's contrast matches the approved v8 in each scene; the run neither improves nor worsens it. In the annex the figure's mean luminance equals the floor's, so the figure separates from the floor almost entirely through its dark outline: about 10% of edge texels are below 1.25:1.

## Visual limitations Claude saw (agent observation at 1:1 and 3× crops, not a human review)

1. **The upper body is static.** Hair, cape, coat, torso and arms read the same as the v8 idle. The 1–2 texel arm pump is not visible at 1:1. At 48 px this looks like running legs under an idle torso. This is the r2 note's open item 1.
2. **The run is taller than the idle.** The contact leg makes the figure 51 px against 48, and the feet reach 3 logical px below where the idle stands. With no run→idle stop transition, stopping will show the figure shrinking and the feet jumping.
3. **The head moves unevenly at 60 fps**, stepping 1–6 px per tick. This may read as a vertical judder, and it is worse with the lock than without. It needs a person to watch the GIFs (or an in-game run at 60 Hz).
4. **The dark annex is weak for readability.** The dark trousers and brown boots sit close to the floor's value, and the silhouette relies on the outline. The city and outskirts read clearly.
5. **No ground shadow.** In the bright city especially, the flight frames (about 67% of screen time) can look like they float. The runtime hero has no shadow either, so this is a policy question, not a v3r2 defect.
6. **Style contrast with the city NPCs.** The existing NPC sprite near the path (梁序) is chunkier and lower-detail. This mismatch existed before v3r2.

## Outputs (`outputs/`, separate files, no sheet or collage)

All names start with `rpg-2-star-ocean-the-second_<scene>_protagonist-female-south-run-v3r2-gameplay-preview-` and end with `-h48_m8-w03_20261015-081409-c274b009`.

**PNGs** (1280×720, colour-exact). Each scene has four:
- `still-v8-idle-reference`: the approved idle at the start pin, for comparison;
- `run-140-motion-tick-000-run-f01-contact-vr`;
- `run-140-motion-tick-002-run-f03-mid-vr`;
- `run-140-motion-tick-008-run-f07-flight2-vr`.

**GIFs** (lossy review aids; the PNGs are the evidence). Each scene has two:
- `run-140-realtime-30fps-1x`: the 31 ticks of the 30 fps mode, crop 200×416 at 1:1 window px. Delays alternate 30/40/30 ms, so it plays at true real time, 33.3 ms per tick. This is what a 30 Hz runtime shows, with 11 of 16 frames.
- `run-140-quarter-speed-2x`: the 61 ticks of the 60 fps mode, 2× nearest, with delays of 70/60/70 ms (¼ speed). It shows all 16 frames.

GIF delays have a 10 ms granularity, so 60 fps real time cannot be shown as a GIF. The `run-140` scratch PNGs are the real-time 60 fps evidence. Re-timing changed no pixels; this was verified frame by frame.

**Receipt:** `…city-outskirts-annex_…capture-receipt-…json`. It has every tick (frame, root offset, cell origin, measured soles and head), every still's fidelity and height, contrast, slip per stance, and the output hashes.

## Run history

1. **The first run exited 1.** In the annex, the start position y 92 put the head under the annex's top UI bar, and f01 fidelity was 1533/2322. The gate worked as intended. The start was moved to (240, 150). The first run's 8 partial PNGs in `outputs/` were deleted, and the harness was changed to write outputs only after every gate passes.
2. **The second run passed.** The GIFs were then built from its scratch ticks with ffmpeg (palettegen with full stats, `dither=none`) and re-timed with Pillow. Their names were shortened because the original long name pushed the full path past Windows MAX_PATH.

## Not done

- **No human or Codex review.** Claude did not watch the motion in real time. The GIFs and receipt are for Codex and the creator.
- Start and stop transitions do not exist, so they were not previewed.
- No north, east or west run exists.
- Nothing was integrated into `scifi_exploration_area.gd` or `survey_annex.gd`.
- A real-time 60 fps video was not made; GIFs were requested, and the scratch PNGs cover 60 fps.
