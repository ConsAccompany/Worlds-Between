# Female south locomotion v2 (m8-w02): visual QA note

M8, 2026-10-14 local (file stamps are UTC, 2026-10-15). This is an isolated v2 locomotion prototype for the female protagonist facing south. It is built from the user-approved **static** selout v8 idle and responds to walk v1 (m8-w01), which slid about 44 screen px per stance.

**Status: technical prototype for human review. Unapproved. Not runtime-integrated.**
- No acceptance gate or counter changed.
- v1 is untouched.
- Every judgement below is Claude's technical observation, not a user verdict.

## 1. Why v1 slid, and what is physically possible at 48 px

**What the runtime does** (`game/scripts/scifi_exploration_area.gd`, `survey_annex.gd`):
- `MOVE_SPEED = 140` logical px/s on the 640×360 canvas.
- The walk is time-driven: 4 phases × 0.12 s, which is 4.17 steps/s and a 33.6 px step.

At 1280×720, 1 texel = 1 window px = 0.5 logical px, so 140 px/s is 280 window px/s.

**A planted foot is world-locked.** Moving south, the body passes over the planted foot. Inside the cell, that foot's sole must therefore rise by exactly the stance travel × 2 texels. The v8 leg runs from hip row ~61 to sole row 103 (≈42 texels). Its sole can climb only about **12–16 texels (6–8 logical px)** before the leg disappears into the coat or behind the other leg.

**Consequences:**

| Gait | Constraint | Result |
| --- | --- | --- |
| Walk (a foot always down) | The body can advance only as far as the sole climbs per stance | **≈16 px/s** at a normal 2 steps/s cadence. 140 px/s is ≈8.75× faster. This is impossible at 48 px without slip. |
| Run (flight phase) | Only the short ground contact must match the climb; the body covers the rest of the step in the air | **Feasible at 140 px/s.** 140 px/s ≈ 2.9 body heights/s, a sprint pace for a 48 px figure. |

Hence two alternatives:
- **A:** a run at the real 140 px/s.
- **B:** a planted walk at its physically consistent speed, 16 px/s.

Neither changes the runtime.

## 2. Design (both alternatives)

**Distance-keyed pacing.**
- The frame comes from the distance travelled through a per-frame `hold_px` table in the manifest, never from time.
- So cadence always tracks speed.

**Climb matched to travel.**
- Each stance frame's planted sole climbs in the cell by the travel it covers.

**Root lock.**
- This is a bounded draw-only offset `r`; logical and collision position are untouched.
- While a frame has a planted leg, the sprite is frozen (`slope −1`).
- At a frame change it moves by that sole's climb/2, so the sole never moves on screen.
- Flight frames ramp `r` back, so the loop is periodic.
- `|r|` ≤ 1.33 logical px (run) and ≤ 1 px (walk).

| | A: run @ 140 px/s | B: walk @ 16 px/s |
| --- | --- | --- |
| Frames | 12 (4 stance + 2 flight per step) | 8 (contact, down, pass, up per step) |
| Cycle / step / cadence | 70 / 35 px / 4.0 steps/s (runtime walk: 4.17) | 16 / 8 px / 2.0 steps/s |
| Planted sole rows | 109 → 104 → 100 → 95 (climbs 5, 4, 5 texels) | 110 → 106 → 102 → 98 → 94 (4 texels each) |
| Hold per frame | stance 7/3 px (exactly one 60 fps tick); flight 77/6 px | 2 px (7.5 ticks) |
| Ground contact | 9.33 px = 67 ms per step | double support, a foot always planted |
| Bob (texels) | +1, +2, +2, +1, −1, −2 | +1, +1, 0, 0 |

**Art method.** This is the same discipline as w01, with no generative redraw, resampling, filtering, flip or mirror.
- v8 is split into 5 texel layers, and the idle re-stack equals v8.
- Legs are rebuilt per pose from v8's own thigh, knee and shin rows, using whole-row repeats and overlaps.
- Boots reuse v8 and the w01 drawings. Two new "tuck" boots show a foot kicked up behind the knee.
- The upper body is texel-locked to v8 plus the bob. The forearm and fist pump ±2 rows; the cape tip lags ±1.
- The swing foot is kept lower on screen than the push-off foot, because it is ahead in depth.
- The planted boots use per-pose `dx`, so the toe centroid stays within 0.5 px.
- Pinholes opened by limb swings are closed with the neighbours' majority colour: 0–3 texels per frame, recorded in the manifest.

## 3. Files (all new; v1 untouched)

**Frames.** 20 frames, 80×112 RGBA, one PNG each, in `game/assets/characters/walk-pilots-v2/`. The folder has a `.gdignore`, so Godot makes no `.import` entries.
- `…south-locomotion-v2-run-f01-contact-vr … run-f12-flight2-vl_m8-w02_20261015-030458-<id>.png`
- `…walk-f01-contact-vr … walk-f08-up-vl_…png`

**Same folder:**
- the manifest, `…locomotion-v2-manifest_m8-w02_20261015-030458-eb352ac8.json`:
  - hash `fd85f643…` (sha256-text-lf-v1; the bytes are LF);
  - contents: holds, soles, bob, poses, root lock, pinholes, per-frame SHA-256;
- the run `.pxo` (`…-63efaa2e.pxo`, `422958ca…`; 12 frames × 5 layers);
- the walk `.pxo` (`…-bf091d76.pxo`, `b3f72180…`; 8 frames × 5 layers).

**Tools:**
- builder/checker `tools/…south-locomotion-v2-build_m8-w02_…-5b1e7c20.py`;
- slip and media tool `tools/…south-locomotion-v2-slip-and-media_m8-w02_…-c3d9a512.py`.

**Godot harness:** `game/tests/…south-locomotion-v2-capture_m8-w02_…-7d42c9e1.gd` and `…-a6f3d018.tscn`.

**Evidence** in `outputs/`, run `20261015-032236-ff6b740f`, 96 files:
- **Receipt:** `…locomotion-v2-capture-receipt_…json` (`07e1ace0…`).
- **Slip report:** `…locomotion-v2-slip-and-media_…json` (`e58f6d33…`), with per-tick sole and head data and media hashes.
- **Stills, 42 PNGs (1280×720):** each of the 20 frames plus the v8 reference, at one fixed pin, in each area.
- **Motion samples, 20 PNGs.**
- **Per area × mode:** a real-time MP4 at the tick rate (60, 30 or 144 fps; 2× nearest crop) and a real-time 30 fps GIF.
- **Run-140:** a `slowmo-quarter-speed` MP4, labelled as slow motion and meant for inspection only.
- **In-place loops:** one GIF for run and one for walk.
- GIF and MP4 are lossy review aids; the PNGs are the exact evidence.

## 4. Evidence

**Build and PNG gates** (`--check` on the shipped folder, all 20 frames):
- v8 SHA-256 lock passes; the idle re-stack equals v8.
- Colours: 32 per frame, **0 outside v8**.
- Alpha ∈ {0, 255}; 0 opaque texels on the border.
- Head-search bob equals the declared bob.
- Locked upper body vs v8+bob: **0 mismatched texels**.
- Knee guard stays on the viewer-left leg 20/20 (no leg swap).
- 0 pinholes; all 20 frames unique.
- Each `.pxo` re-stacks to every PNG.
- **Determinism:** two scratch rebuilds are byte-identical to the 23 shipped files.

**Godot 4.7.2, windowed, real movement code.**
- Each tick, the harness holds `move_down` and calls the area scene's own `_process(delta)`.
- The hidden hero therefore moves at the script's own `MOVE_SPEED`, which the harness asserts is 140. It measured exactly **2.3333 px/tick at 1/60**, 4.6667 at 1/30 and 0.9722 at 1/144.
- The v2 sprite is drawn at the hero position plus the root lock.
- Exact-RGB texel fidelity: every still and every 5th motion tick.
- Areas: city (x 340, y 165→305) and outskirts (x 250, y 150→290).
- The run exited 0.

**Slip is measured on the captured pixels:** the per-tick capture is diffed against a sprite-free background, and the lowest masked row in the planted leg's column band gives the sole. Results were identical in both areas:

| Mode (both areas) | Complete stances | Planted-sole slip per stance (window px) | Per-tick drift max | Toe x shift | Head step per tick (nominal) |
| --- | --- | --- | --- | --- | --- |
| **w01 baseline @ 140, 60 fps** | 4 | **44, 40, 40, 45** | 5 (38/38 planted ticks > 1 px) | 0 | 3–6 (4.67) |
| **A run-140 @ 60 fps (lock)** | 3 | **0, 0, 0** | 0 | 0.5 | 1–6 (4.67) |
| A run-140 @ 30 fps (lock) | 3 | 0, 0, 0 | 0 | 0.5 | 5–12 (9.33) |
| A run-140 @ 144 fps (lock) | 3 | 0, 0, 0 | 0 | 0.5 | −1–6 (1.94) |
| ablation: run @ 60 fps, no lock | 3 | 0, 0, 0 | 0 | 0.5 | 3–8 (4.67) |
| ablation: run @ 144 fps, no lock | 3 | **5, 5, 5** | 3 (27/27 > 1 px) | 0.5 | 0–5 (1.94) |
| **B walk-16 @ 60 fps (lock)** | 2 | **0, 0** | 0 | 0.5 | 0–5 (0.53) |

**Reading the table:**
- Most of the gain comes from the frame design: contact is short and each stance frame's climb matches its travel.
- At exactly 60 fps that alone gives 0 slip.
- The lock is what keeps it at 0 when a frame is held for several ticks (144 fps: 5 → 0).

**The cost: body motion is no longer perfectly uniform.**
- The head's residual against uniform motion is 5 px peak-to-peak (run @ 60), of which about 4 px is the intended run bob.
- At 144 fps it is 6.7 px, and the head can move up 1 px for one tick.

**Visual inspection by Claude** (zoomed captures):
- During each run stance, the planted boot sits on one fixed screen row for all 4 ticks while the body passes over it.
- Flight frames clearly show one foot kicked back and the other reaching.
- The walk alternates legs with a visible 16-texel depth stride.

## 5. Known flaws (honest; not a pass)

1. **The run's planted pose is brief.**
   - Contact lasts 67 ms (4 ticks at 60 fps); a real sprint is ~90–110 ms.
   - At full speed the eye mostly sees the two flight frames, each held ~92 ms, so the motion reads as a bounding sprint.
   - Whether the foot plant *reads* at 1× is a human call. The measurement says it does not slide.
2. **The root lock makes torso speed slightly uneven.**
   - At 60 fps the sprite advances 3–5 window px per tick (nominal 4.67), measured from the receipt.
   - Each step has two 3-px ticks, at stance→flight and at flight→contact; the bob comes on top.
   - At high refresh rates (144 fps) there is a 1-tick freeze and hop per stance frame.
3. **Walk B moves at 16 px/s, 1/8.75 of game speed.**
   - It suits a cutscene or a slow-walk tier only, and the runtime has no such tier.
   - Its body advances in 4-window-px hops at 8 Hz, because the sprite is frozen within each held frame.
4. **The art is functional, not finished:**
   - leg lengths change by whole-row repeats, so shading stripes repeat;
   - the "tuck" boots are small blobs;
   - the run mid frames (f03/f09) show both feet at nearly equal height;
   - the arm pump is small (±2 rows, no elbow redraw);
   - the cape moves only ±1;
   - there is no torso lean;
   - every redraw was done by Claude as texel text, not by a pixel artist.
5. **Scope:**
   - south only, straight-line motion only. A runtime would need distance along the path, per-direction sets, and handling for diagonals and stops;
   - no shadow;
   - the dark annex was not captured;
   - no Pixelorama GUI or CLI round trip this time (the `.pxo` re-stack is verified in Python only).
6. **Harness caveats:**
   - The harness calls `_process` with a fixed delta rather than relying on real-time frame pacing.
   - Walk B is moved by the harness itself, because `MOVE_SPEED` is a constant and was not edited.

## 6. Unchanged

- **v1:** v1 (`walk-pilots/`) frame hashes were verified by the harness; the manifest is still `c07853b7…` and the `.pxo` `2bb379cf…`.
- **v8:** still `ccf9d2a2…`.
- **Runtime:** 0 runtime references to v2; no `.import` files were created.
- **Not edited:** runtime scripts and scenes, `MOVE_SPEED`, Game Bible, progress, readiness checklist, battle and sentry files, hash-fix files.
- **Pre-existing edits.** The 5 tracked modifications present before this work came from other sessions.
- **Superseded outputs.** Outputs of my own superseded capture runs (`031109-c1ca7b84`, `031301-25899f6d`, `031853-97c9755c`) were deleted.
- No commit, stage or push.

## 7. Reproduce (repository root; Codex-runtime Python with `-I`)

```
python -I tools/…south-locomotion-v2-build_m8-w02_20261015-030458-5b1e7c20.py --out-dir <scratch>   # byte-identical rebuild
python -I tools/…south-locomotion-v2-build_m8-w02_20261015-030458-5b1e7c20.py --check game/assets/characters/walk-pilots-v2
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-v2-capture_m8-w02_20261015-030458-a6f3d018.tscn -- --motion-dir=<abs scratch dir>
python -I tools/…south-locomotion-v2-slip-and-media_m8-w02_20261015-030458-c3d9a512.py --receipt outputs/<receipt>.json --motion-dir <abs scratch dir>
```

**Rollback.** Delete these and nothing else:
- `game/assets/characters/walk-pilots-v2/`;
- the two `game/tests/…locomotion-v2-capture…` files;
- the two `tools/…locomotion-v2…` scripts;
- this note;
- `outputs/*locomotion-v2*032236-ff6b740f*` (96 files).
