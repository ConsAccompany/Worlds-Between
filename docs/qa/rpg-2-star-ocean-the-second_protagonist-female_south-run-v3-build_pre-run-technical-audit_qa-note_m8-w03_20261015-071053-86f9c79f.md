# Female south run v3 (m8-w03) builder: pre-run technical audit

M8, 2026-10-15 (UTC 07:10). This is a read-only static audit of an unexecuted builder script, done by Claude. It contains no art verdict.
- No image was generated or edited, and the builder was not run, not even `--preview`.
- No counter, gate, Game Bible, progress or Git state was touched.
- **Approval scope is unchanged.** The creator approved only the selout v8 south idle **static** frame at the 48-logical-px displayed scale. No animation is accepted, including v1 walk, v2 locomotion and anything v3 would produce.

## Verdict: **NOT READY** to run for visual review

The script is a partial draft. Its docstring describes a complete source-locked build and checker, but the code implements only the leg-pose art tables and an enlarged `--preview` strip writer. Most of the claimed art changes, the root lock, the transitions, the manifest, the per-frame output and every check are missing. Running what exists would produce a legs-only preview that cannot support the planted-foot claims, and it would show a figure with no arm swing.

## Audited inputs

| Item | Path | Evidence |
| --- | --- | --- |
| v3 builder (audited) | `tools/…south-run-v3-build_m8-w03_20261015-034327-4be0c7a2.py` | Untracked. 591 lines, 21 773 bytes, LF, ASCII. sha256-bytes `f88127b7…3eb2`. mtime 2026-10-14 23:49 −04:00. |
| v8 source | `game/assets/characters/pixelorama-pilots/…selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png` | sha256 `ccf9d2a2…b6fd`, which **matches** the script's `V8_SHA256`. 80×112 px; alpha is only 0 or 255; opaque rows 8–103. It has 32 colours, all 32 present in the script's `ROLES` table (0 missing, 0 unused). |
| v2 predecessor | `tools/…south-locomotion-v2-build_m8-w02_…-5b1e7c20.py`, the v2 QA note `…locomotion-v2_visual-qa-note_m8-w02_…-9d27f4b1.md` | Used as the reference for the expected build, check and lock structure. |
| Prior v8 and w01 QA notes | `docs/qa/…selout-v8_visual-qa-note…`, `…walk-pilot_visual-qa-note_m8-w01…` | Consulted for the cell, pin and approval context. |
| Execution traces | none | No `run-pilots-v3/` folder, no `outputs/*w03*` and no other file references the script. It has never been run. |

## Claim-by-claim consistency

| Docstring claim | Code status | Finding |
| --- | --- | --- |
| Modes `--out-dir`, `--write`, `--check`, `--preview` | **Only `--preview` exists** (`main()`, last lines) | **Blocker.** The script has no `build()`, `check()`, manifest writer, `.pxo` writer, `frame_name()` or `_write()`. `fid`, `STAMP`, `OUT_REL`, `V8_SHA256`, `sha256_file`, `png_bytes`, `PIN`, `zipfile`, `json` and `sys` are defined or imported but never used. |
| Source-locked to v8 | `preview()` calls `load_grid()` with **no hash check** | **Bug (latent).** The lock is declared but never enforced. Today it is harmless because the file hash matches. |
| Deterministic construction | Pure table and arithmetic, with no RNG or time inputs | **OK as code**, except that "byte-identical rebuild" cannot be tested because no build mode exists. |
| Legs redrawn per pose: tapered thigh and shin, trouser ramp, 3-view knee guard, hand-drawn boots | Implemented (`draw_leg`, `GUARD`, `FEET`, `KICK`) | Present. Every art glyph uses `ROLES` keys. The 15 leg phases cover both legs over 16 frames, and the pose sequence is continuous (contact→…→toeoff→lift→kick→tuck→tuck→tuckpass→pass→drive1→drive2→reach1→reach2→descend→contact). |
| Arms "re-drawn bent (~90°), opposing swing in five positions per side" | **Not implemented.** `fist` and `armr` are only shifted by the bob. | **Blocker for art review.** This is a regression from v2, which had a ±2-row pump. |
| Upper body "leans 2 texels forward" | **Not implemented.** Every shift uses `dx = 0` and the same `dy = bob`. | The claim is false for the current code. |
| "Cape and coat hems lag the bob" | **Not implemented.** The cape, skirt and upper body all get the same `shift(…, 0, bob)`. | The claim is false. Also, the split at rows 57/58 cuts through v8's belt and coat-bottom rows 58–60 (`owner()` puts those in the skirt). That split would need review before any lag is added. |
| Distance-keyed start (idle→run) and time-keyed stop (run→idle) per leg, root-locked | **Not implemented.** `run_frames()` yields only the 16 cycle frames. | **Blocker** for the "pinned through transitions" claim. Also, the v3 planted boot centres (`TOE_X` vl 31.5, vr 46) differ from the v8 idle boot bottoms (vl ≈ x 26–28 at row 100, vr ≈ x 49–53 at row 103). A start or stop transition will therefore need a deliberate foot re-placement. |
| Bounded draw-only root lock (from v2) | **No `root_lock()` and no manifest `root_lock` field** | **Blocker.** Without the lock data, the v2 Godot capture harness and the slip tool cannot test v3. The zero-slip claim is untestable. |
| 5-frame stance, planted toe climbing 110→105→100→96→91 | Matches the `leg_pose` `sole` values | The climbs are 5, 5, 4, 5 = 19 texels over 4 frame changes. The travel is 4 × 7/3 px = 9.333 logical px = 18.667 texels. The per-change error is +0.33/+0.33/−0.67/+0.33 texel, and the residual is +0.33 texel per step. The stated "~4.75 texels/tick" is the mean of 19/4, but the ideal value is 4.667. Without a root lock this gives about 0.3–0.7 window px of planted slip per tick at exactly 60 fps, and more at 144 fps, where v2 needed the lock to get from 5 px to 0. |
| Cycle 16 frames / 70 px, step 35 px, 4 steps/s at 140 px/s | 5 × 7/3 + 3 × 70/9 = 35 ✓; 16 frames ✓ | Consistent. Contact rises to 5 ticks (83 ms at 60 fps), compared with 4 ticks (67 ms) in v2. Flight holds are 70/9 ≈ 3.33 ticks, so flight frames alternate between 3 and 4 ticks. |
| Planted boots share a world-locked toe tip | `TOE_X` is constant per side; the bottom rows of the `FEET` glyphs vary | The x of the toe-row centre moves by up to 1 texel (0.5 logical px): vr strike/flat 46.5, heelup 45.5, toe 46; vl 31.5, 31.5, 31. This matches v2's measured 0.5 px and is acceptable, but it is "≤ 1 texel", not exact. |
| Frame naming | Keys are `run-f01-contact-vr … run-f08-flight3-vr, run-f09-contact-vl … run-f16-flight3-vl` | 16 unique keys, consistent with v2's convention. There is no filename builder, so the planned PNG names, ids and manifest are unspecified. `RUN_ID a3f7c901` ≠ script id `4be0c7a2`; that is only a note, since v2 did the same. |
| Output plan `game/assets/characters/run-pilots-v3/` | No writer exists | **Risk.** v2's folder needed a `.gdignore` so that Godot would not import it. Nothing here creates one. If a `--write` mode is added without it, Godot will generate `.import` files under `game/`. |
| v2-style gates: idle re-stack = v8, 0 colours outside v8, upper-body texel lock, knee guard on the viewer-left leg, 0 pinholes, unique frames, `.pxo` re-stack | **None implemented** | Blocker for a "checked" pilot. The idle re-stack gate also cannot carry over unchanged, because v3 discards v8's leg layers (`P["legvl"]` and `P["legvr"]` are computed but unused). |

## Objective risks visible from static geometry (estimates; confirm on render)

These come from the v8 texel map read from the PNG and the script's coordinates. None was rendered.

1. **The kicked-up "sole-up" boot is mostly hidden.** Its `KICK` box is drawn as a lowest-priority back layer at:
   - vl: x 25–31, rows 67–73;
   - vr: x 45–51, rows 68–74.

   Covering it are the same leg's thigh (vl x 27–35, vr x 39–48), the coat-left edge (x ≤ 26 to row 70), the right flap (x 43–48), and the hand (x ≥ 47 to row 70). Only a few texels are likely to show, so in f07/f08/f09 and f15/f16/f01 the swing leg may read as a knee-length stump.
2. **There is a transparent wedge under the belt.** The thigh spans at the hip are vl x 27–35 and vr x 39–48, so x 36–38 is empty from row 63 (+bob) downward; only rows 61–62 x 37–40 are covered by the belt texels. v8 has continuous trousers there. There is no pinhole or gap filling, unlike v2.
3. **The swing knee ignores the bob.** `ky` is absolute while the hip is `61 + bob`. The swing thigh therefore stretches and shrinks with the bob (3 rows at mid-stance), and `tuck` is held for 2 consecutive frames (f08→f09 and f16→f01).
4. **The planted leg's apparent length varies from 29 to 48 rows** (idle is ≈ 42): hip-to-sole is 48 at contact and 29 at toe-off. This is plausible foreshortening for a south run, but the contact leg is 6 rows longer than idle.
5. **During push and toe-off, the hanging swing foot sits lower on screen than the planted toe** (98/101 against 96/91). This is intended as a depth cue, but it may read as the swing foot being the planted one.
6. **The near/far leg order swaps at the mid frames** (f03 and f11), because it switches on the larger knee row.

## Before running (minimum to reach "ready")

1. Implement the build: per-frame PNGs, a manifest with `hold_px`, the sole row, bob and `root_lock`, a v8 hash gate in every mode, and a `.gdignore` (or keep the output outside `game/`).
2. Implement `--check` with v2-equivalent gates, adapted to the redrawn legs (palette, alpha, border, bob, upper-body lock, knee guard side, holes, uniqueness), plus a sole-row and toe-x readback against the manifest.
3. Either implement the arms, lean, lag and transitions, or **remove those claims from the docstring** and label the run "legs-only".
4. Make the climbs sum to the travel, or record the residual and let the lock absorb it.
5. Then run a scratch `--out-dir` twice to prove byte determinism, before any `--write`.

## When it is run: frames and conditions Codex should judge visually (not by script)

**At 1× and at the 48-logical-px displayed scale, with nearest-neighbour scaling:**
- f01/f09 (contact): leg-length read and the stump swing leg (risk 1).
- f03/f11 (mid): bob-3 squash and the near/far pop (risk 6).
- f04–f05/f12–f13 (push and toe-off): which foot reads as planted (risk 5).
- f07–f08/f15–f16 (kick and tuck): is the kick boot visible, and is the swing leg legible?
- Every frame: the belt-line gap (risk 2), whether the knee guard reads on the viewer-left leg, and whether the boot glyphs read as leather boots rather than blobs.

**In scene:**
- A real-time 140 px/s south run at 60, 30 and 144 fps in the city and outskirts areas, using the v2 capture harness after it is pointed at v3.
- Planted-sole slip per stance on captured pixels, with and without the lock.
- Head-step irregularity per tick.
- Loop seams at f16→f01 and f08→f09.
- A side-by-side with the v8 static idle, for identity drift in the head, coat and cape, which are v8 texels and should match exactly.
- The dark annex, which v2 skipped.

**Explicitly not to conclude:** whether any v3 frame or the animation is approved. That is the creator's call.

## Limitations

- **Static audit only.** No v3 frame was rendered, and the occlusion and gap findings are coordinate estimates.
- **What was read:** the v8 PNG was read once into a temporary helper (deleted after use) to list its texel roles and check palette coverage. The helper did not import or execute the builder. Nothing was written to the repository except this note.
- **What was not re-verified:** v2's measured results (zero slip, 0.5 px toe shift) were not re-run; they are cited from the v2 note.
- **Concurrent work:** other sessions are editing M2 scripts and air-route research concurrently. This audit does not cover those.
