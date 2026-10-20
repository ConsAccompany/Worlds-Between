# Patrol battle animation v01 — normal-speed 1x motion evidence (UNAPPROVED, default-off candidate)

Producer: Claude, 2026-10-19 20:00–20:09 local, worktree `work/dual03/cl-patrol`, HEAD `e600241b`, uncommitted. These clips are technical motion evidence only. They are not art acceptance, approval, adoption or points.

## Source binding (sha256-bytes, frozen at run start and rechecked at end: unchanged)
- `game/scripts/battle_arena.gd`: `799308e292b0…`
- The loader `.gd` is `f051d5938afa…`. It differs from `fe4e95f0…` in the v01 QA note: the concurrent Codex loader fix landed before this run, and this run tested that version.
- The runtime package JSON is `075a438e13d8…`, the strip PNG `e91f4373fb8f…` and the manifest `3f34afc6f5aa…` (the QA note listed `a54b8fa3…`; it changed before this run).
- The harness is `af3fd15c53af…`. The run/encode tool is `a48b93a5d298…`.
- Full hashes are in `*_motion-report_*.json` → `boundSha256AtStart` / `boundSha256AtEnd`.

## Method
- **Engine:** windowed Godot 4.7.2 (OpenGL3 Compatibility, RTX 3080), with the real `battle_arena.tscn` at a 640x360 root viewport.
- **Pilot switch:** enabled only by the real CLI flag `--patrol-battle-animation-pilot`; no static override is set.
- **Battle setup:** the same party setup as the v01 harness (male lead plus Liang Xu, Zhao Ling and Ji Cheng), Outskirts, Patrol.
- **Input:** one synthetic `T` key event (keycode plus physical_keycode) via `Input.parse_input_event` at about 0.25 s. It reached the arena's real `_input`, which turned on `battle_auto`.
- **Capture:** the battle runs its own `_process` at real engine delta. The viewport image is copied every engine frame and saved to PNG only after the clip. Each frame logs:
  - wall-clock time;
  - `get_process_delta_time()`;
  - Engine frame counters;
  - enemy state and frame, HP and x.
- **Encode:** ffmpeg 8.1.1 (gyan.dev full build, already installed) via an `ffconcat` list.
  - Each captured frame is used exactly once, with its measured duration, at a 1 µs image timebase.
  - Settings: `-fps_mode passthrough`, libx264 High, `-preset slow -crf 12`, yuv420p, MP4 timescale 1 000 000. The result is VFR.
  - No frames are duplicated, dropped or interpolated, and there is no sprite-sheet playback.
  - ffprobe confirms `nb_read_frames == captured frames` and packet PTS gaps reproduce the captured frame times (max error < 1e-15 s).
- **Runner:** checked runner `…checked-runner_v01_20261018-203400-f74ac6d1.py`, unfiltered, 300 s deadline, expects `PATROL_MOTION_CAPTURE OK`, with fresh isolated APPDATA/LOCALAPPDATA (`app-200602`, `local-200602`).
  - Result: `CHECKED_RUN PASS`, 60.0 s, 0 `ERROR` lines.

## Clips (outputs/patrol-motion-v01/)
| clip | label | frames | span s | first-seen states (s) | hold writes | MP4 sha256 |
|---|---|---|---|---|---|---|
| `…motion-normal-en-normal1x-640_…mp4` | **normal unmodified combat** | 688 | 2.896 | move 0.037, hit 0.645, defeat 1.425 | 0 | `156ed19ae702…` |
| `…motion-normal-zh-normal1x-640_…mp4` | **normal unmodified combat** | 690 | 2.889 | move 0.030, hit 0.630, defeat 1.412 | 0 | `272c2503e0d2…` |
| `…motion-held-en-normal1x-640_…mp4` | **TEST-ONLY durability hold** | 1437 | 6.003 | move, hit 0.600, windup 1.443, strike 2.097, idle 2.723, defeat 4.499 | 18 | `ef06fc07c2f8…` |
| `…motion-held-zh-normal1x-640_…mp4` | **TEST-ONLY durability hold** | 1426 | 6.004 | move, hit 0.613, windup 1.460, strike 2.110, idle 2.736, defeat 4.509 | 18 | `90bbb5be4274…` |

- **Normal clips:** the standard auto party destroys the Patrol in about 1.4 s, before its first windup. So **idle, windup and strike do not appear in normal unmodified play**; only move, hit and defeat do. This is a genuine gameplay observation, not a capture defect.
- **Held clips:** the only write is `enemy_hp = 40` whenever HP drops below 40, until the Patrol has struck twice; then the hold is released. The hold fired 18 times per clip. Combat code is unchanged. **This is not normal gameplay.** The held clips cover all 6 states.
- **Frame timing:** the engine ran uncapped with vsync on a 240 Hz display, giving about 237–239 captured fps.
  - process delta: mean 4.2 ms, max 18.4 ms; wall delta max 20.9 ms.
  - No frame exceeded 25 ms in any clip.
  - These are counts and timings only. They are **not a smoothness claim**; that needs the creator's viewing.
- **Per-frame records:** each frame PNG's sha256 and its state are in `*_motion-capture-raw_*.json`. The report carries a hash of each clip's frame-hash list. The frames are in `frames/<clip>/f#####.png` (688 + 690 + 1437 + 1426).

## Observed limitations
- **Viewing the MP4s:** the frame rate is about 238 fps VFR, and on a 60 Hz player most frames are never shown. Viewers should treat these as real-time recordings, not frame-by-frame review. The PNG frames are kept for that.
- **Label offset:** `get_image()` after `process_frame` returns the most recently drawn frame. The logged state/frame label can lead the pixels by one engine frame (about 4 ms).
- **Colour:** yuv420p chroma subsampling, so the MP4s are lossy in colour. The PNG frames are lossless.
- **Encoder cost:** each frame is read back from the GPU, which could perturb timing slightly. No over-25 ms frames were observed.
- **Party setup:** the setup calls the AppState API directly (begin_new_run / recruit). It is not menu-driven.
- **Coverage:** the auto party is the only input mode; no manual attack input clip was made. No PCK/export run was done.
- **Failed attempts, kept honestly:**
  - **Attempt 1** (`…report-attempt1-failed-pts_…json`, log `…runner-log-attempt1_…`) captured fine. Its MP4s had one extra trailing duplicate frame, and the timestamps were quantized by the default 1/25 image timebase (PTS bunched at 0.04 s). It FAILED and was not used; its frames and MP4s were replaced.
  - **Attempt 2** read stale attempt-1 data after the runner refused the existing log name. The tool now uses a unique log per run and clears its own stale outputs.
  - **Attempt 3** (`…report-attempt3-failed-shader-diag_…json`, log `…runner-log-200543_…`): the checked runner failed on 8 `shader_gles3.cpp:802` ERRORs at startup when reusing attempt 1's isolated AppData. Fresh AppData per run fixed it.
- **Isolated AppData dirs:** `appdata/` and `localappdata/` (attempts 1–3) and `app-200602/` and `local-200602/` (final) remain inside `outputs/patrol-motion-v01/`.
- **Scope:** no source outside scope was touched. `git status` shows only the pre-existing candidate changes plus these two new tools and this output directory.

## Reproduce
`<python> -I tools/rpg-2-star-ocean-the-second_patrol_motion-capture-run_v01_20261019-200500-5b7c2e19.py` prints `PATROL_MOTION_RUN PASS`. It checks the global stop file before the capture and before each encode.
