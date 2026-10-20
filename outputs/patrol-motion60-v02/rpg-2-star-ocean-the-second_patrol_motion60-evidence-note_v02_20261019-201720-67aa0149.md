# Patrol battle animation v01 — 60 fps engine recording, normal 1x (v02 display-compatibility fix; UNAPPROVED, default-off candidate)

- **Producer and run:** Claude, 2026-10-19, run `v02_20261019-201401-67aa0149` (local EDT; UTC 2026-10-20 00:14).
- **Checkout:** worktree `work/dual03/cl-patrol`, HEAD `e600241b`, uncommitted.
- **Scope:** a single display-compatibility fix for the existing Patrol motion evidence.
  - The v01 recordings ran at about 238 fps VFR on a 240 Hz display. They are valid technical recordings but poor review files for phones and 60 Hz screens.
  - v02 records the engine itself at 60 fps. It is not a conversion, frame drop or interpolation of the v01 videos, and no v01 frame, video or timing is used.
- **What this is not:** a new art version, new points, a smoothness claim, a fluidity claim or creator approval.
- **Untouched:** no shared file, index, commit, ledger, Bible, Site or account was touched. The PCK export was not redone (root already validated it).

## Provenance and frozen sources
- **Adapted from (read-only, unchanged at start and end):**
  - `tools/…patrol_motion-capture-harness_v01_20261019-200500-5b7c2e19.gd`, sha256 `af3fd15c53af…`
  - `tools/…patrol_motion-capture-run_v01_20261019-200500-5b7c2e19.py`, sha256 `a48b93a5d298…`
- **New v02 tools (in this directory only):**
  - harness `…motion60-capture-harness_v02_20261019-201213-12f10190.gd`, sha256 `826b9fb87428…`
  - run/encode tool `…motion60-capture-run_v02_20261019-201213-12f10190.py`, sha256 `fcfdb4aa754d…`
- **Changes from v01, capture side only:**
  - The harness sets `Engine.max_fps = 60`. Before that it was 0, and the game sets no `max_fps` anywhere.
  - Each run gets a unique run id, fresh APPDATA/LOCALAPPDATA and an ignored per-frame cache in `cache/<run>/` (`cache/.gitignore` = `*`). Nothing from an earlier run is deleted or reused.
  - The scene-entry sample (row 0) is reported separately from the post-start frames.
  - One critical still per state and language is copied byte-exact from the captured frames.
  - The encode adds `-profile:v high -level:v 4.0`.
- **Kept as in v01:**
  - vsync, physics ticks (60), time scale (1.0), `battle_arena.tscn`;
  - the real `--patrol-battle-animation-pilot` CLI flag;
  - the arena's own `_process` at real engine delta;
  - one real synthetic `T` (battle_auto) key event via `Input.parse_input_event`;
  - the party setup and the combat code.
- **Frozen sources (sha256-bytes, no text normalization):** the run tool hard-fails if any of these differ from the root-validated bytes. All were identical at start and end:
  - `battle_arena.gd` `799308e292b0…`
  - loader `f051d5938afa…`
  - runtime package `075a438e13d8…`
  - strip PNG `e91f4373fb8f…`
  - manifest `3f34afc6f5aa…`

## Run (single attempt, PASS — no failed attempts this time)
- **Checked runner:** the existing runner `tools/…checked-runner_v01_20261018-203400-f74ac6d1.py`, unfiltered, 300 s inner deadline, 420 s outer subprocess bound, 590 s shell bound. It expected `PATROL_MOTION60_CAPTURE OK`.
  - Result: `CHECKED_RUN PASS`, exit 0, 30.6 s.
  - The runner log contains 0 `ERROR` lines.
- **Fresh isolated AppData:** `cache/r201401/app` and `cache/r201401/local`.
- **Engine:** Godot 4.7.2 official, OpenGL3 Compatibility, RTX 3080, windowed, 640x360 root viewport.
  - Screen refresh 239.76 Hz, vsync mode 1, `max_fps` 60 for the whole capture (every row records `maxFps = 60`).
  - `BATTLE_TRANSITION_MS` 524.16 / 12.57 / 13.18 / 13.14.

## Clips (640x360, normal 1x, H.264 High@4.0, yuv420p, faststart, VFR at measured wall-clock PTS)
| clip | label | frames = MP4 nb_read_frames | span s | post-start fps | first-seen states (s) | hold writes | MP4 sha256 |
|---|---|---|---|---|---|---|---|
| `…motion60-normal-en-normal1x-640_…mp4` | **normal unmodified combat** | 177 | 2.933 | 60.228 | move 0.041, hit 0.674, defeat 1.442 | 0 | `b653d7733859…` |
| `…motion60-normal-zh-normal1x-640_…mp4` | **normal unmodified combat** | 176 | 2.920 | 60.349 | move 0.028, hit 0.648, defeat 1.416 | 0 | `bfbabac49906…` |
| `…motion60-held-en-normal1x-640_…mp4` | **TEST-ONLY durability-held supplement** | 362 | 6.016 | 60.022 | move, hit 0.585, windup 1.419, strike 2.085, idle 2.735, defeat 4.487 | 18 | `81fbfd8bb098…` |
| `…motion60-held-zh-normal1x-640_…mp4` | **TEST-ONLY durability-held supplement** | 362 | 6.016 | 60.034 | move, hit 0.611, windup 1.411, strike 2.077, idle 2.727, defeat 4.501 | 18 | `15601b5b565e…` |

- **Held clips:** the only write is `enemy_hp = 40` whenever HP falls below 40, until the Patrol has struck twice. This is not normal gameplay.
- **Normal clips:** they still show only move, hit and defeat. The Patrol dies in about 1.4 s, before its first windup.
- **Per language:** all six states appear across normal + held for both EN and ZH.

### Timing: scene-entry sample vs post-start frames
- **Initial scene-entry sample (row 0 of each clip; kept in the clip and the MP4).** This is the first frame after `instantiate()` + `add_child()`, including scene load and the first `_process`. Its process delta was:
  - normal-en 0.142181 s (wall 0.040565);
  - normal-zh 0.139486 s (wall 0.028137);
  - held-en 0.147969 s (wall 0.002136);
  - held-zh 0.138701 s (wall 0.010697).
  - The largest row-0 wall delta was 0.040565 s.
- **Post-start frames (rows 1..end).**
  - Wall p50 is 16.665–16.666 ms in all clips.
  - Wall max: 18.15 / 23.56 / 18.05 / 23.48 ms (normal-en / normal-zh / held-en / held-zh).
  - Process max: 17.58 / 21.01 / 20.83 / 23.53 ms.
  - No post-start frame exceeded 25 ms. Wall >20 ms: 0 / 3 / 0 / 2.
  - **Settling transient:** the first 1–3 post-start frames are irregular. There are short catch-up intervals of 1.9–5.7 ms, and held-zh row 1 has a 23.5 ms process delta. These are included in the post-start statistics, not removed.
  - The report's `allFramesIncludingEntry` block gives the same statistics with row 0 included (process max 0.138–0.148 s).
- **Correction of v01 wording.** The v01 note said "process delta … max 18.4 ms" and "no frame exceeded 25 ms in any clip". Its statistics silently excluded row 0.
  - The v01 raw row-0 process deltas are 0.136612 / 0.146536 / 0.134750 / 0.133238 s.
  - The v01 row-0 wall deltas are 0.037346 / 0.030387 / 0.002633 / 0.010281 s (max 0.037346).
  - The v01 claim holds only for post-start frames. The v01 files are frozen and were not edited; this note records the correction.

### MP4 checks
- Each captured frame is used exactly once, through an `ffconcat` list with a 1 µs image timebase and MP4 timescale 1 000 000.
- **Run tool checks (all passed):**
  - ffprobe `-count_frames` `nb_read_frames` equals the captured frame count (177 / 176 / 362 / 362);
  - packet PTS gaps reproduce the captured frame times (max error ≤ 9e-16 s);
  - duration matches the captured span;
  - every MP4 is 640x360.
- **ffprobe summaries:** `avg_frame_rate` is about 60.2–61.0. That is ffprobe's frames/duration figure; its duration omits the last frame's display time.
  - **Limitation:** `r_frame_rate` reports 120/1, 240/1, 60/1 and 240/1. That is ffprobe's guess for a VFR stream with an irregular settling start, not a frame rate actually captured.
- **Independent decode check** (`…decode-psnr-check-log_v02_20261019-201612-67aa0149.log`): decoded MP4 frame N matches captured row N at about 45.6–46.4 dB PSNR, against 34.4–36.4 dB for frames N±1. So there is no index shift or duplicate frame at the sampled points.

## Critical stills (byte-exact copies of captured frames; sha256-bytes equals the raw-JSON row hash)
| PNG | source clip, row (state run) | sha256 |
|---|---|---|
| `…critical-strike-en-held-640_…png` | held-en row 135 (126–145), **TEST-ONLY held** | `3807895bcdbb…` |
| `…critical-strike-zh-held-640_…png` | held-zh row 134 (125–144), **TEST-ONLY held** | `35e13a0dab63…` |
| `…critical-hit-en-normal-640_…png` | normal-en row 47 (39–55) | `bc9040e8c3be…` |
| `…critical-hit-zh-normal-640_…png` | normal-zh row 46 (38–54) | `4c7d619c7cd6…` |
| `…critical-defeat-en-normal-640_…png` | normal-en row 130 (85–176) | `8ab36fd5979e…` |
| `…critical-defeat-zh-normal-640_…png` | normal-zh row 129 (84–175) | `f9f0fea6a6e3…` |

- **Rule:** each still is the middle of the state's first contiguous run, which keeps clear of the possible one-frame label lead.
- **Strike** occurs only in the labelled held supplement, because normal play never reaches it.
- **Defeat finding (actual normal gameplay, not a capture defect):** `battle_finished` is already true on the first defeat row. The modal Victory / 战斗胜利 panel and the dimmed scene cover the Patrol in every defeat frame I inspected (rows 85, 87, 94 and 130 of normal-en). Only its dim lower edge shows under the panel.
  - So no unobstructed defeat frame exists in the actual capture. The defeat stills record that faithfully.
  - Showing the defeat animation would need a gameplay or UI timing change. That is out of scope here and is left for root/creator decision.

## Limitations
- **Label lead:** `get_image()` after `process_frame` returns the most recently drawn frame. The logged state/frame label may lead the pixels by one engine frame (about 16.7 ms at 60 fps).
- **Cap effects:**
  - `max_fps` is a CPU-side limiter (sleep) on top of vsync on a 240 Hz display.
  - Captured frames are not vsync-locked 60 Hz presentations, and per-frame GPU readback adds load.
  - Post-start median is 16.67 ms, but this is one machine and one run. **This does not establish 60 fps on other hardware or universally.**
  - Game logic still runs on real delta, so animation timing follows the measured frame times.
- **Setup limitations:**
  - The party setup calls the AppState API directly (begin_new_run / recruit), not the menus.
  - The only input mode is auto (one `T` key).
  - Windowed run on the developer desktop.
- **Colour:** yuv420p chroma subsampling. The MP4s are lossy; the stills and cached frames are lossless.
- **Cache paths:** the per-frame cache and concat lists stay local and ignored in `cache/r201401/` (frames 177 + 176 + 362 + 362). Their hashes are in the raw JSON and report. The concat lists reference absolute local cache paths.
- **Not done:** no smoothness or fluidity judgement, and no creator approval. Normal-speed viewing by the creator is still required.

## Reproduce
`<python> -I outputs/patrol-motion60-v02/rpg-2-star-ocean-the-second_patrol_motion60-capture-run_v02_20261019-201213-12f10190.py`
- It prints `PATROL_MOTION60_RUN PASS` and creates a new run id and fresh AppData each time.
- It checks the global stop file before the capture and before each encode. The real Python is `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
