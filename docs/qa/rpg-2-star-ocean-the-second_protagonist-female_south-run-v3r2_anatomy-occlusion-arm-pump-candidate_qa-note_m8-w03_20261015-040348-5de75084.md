# Female south run v3 candidate r2 (m8-w03): leg anatomy, occlusion, poses and arm pump

M8, 2026-10-15 (local 04:03), by Claude (Claude Code, signed-in Claude Max, first-party; `claude auth status` checked before work).

This note follows Codex's visual rejection of the first v3 build and the earlier v3 notes, `…south-run-v3-build_pre-run-technical-audit_qa-note_m8-w03_20261015-071053-86f9c79f.md` and `…south-run-v3-build_infrastructure-fix_qa-note_m8-w03_20261015-072336-ffb21356.md`.

- **Not approved.** r2 is a candidate for Codex and human visual review. It is not art-approved, not human-reviewed, not runtime-integrated and not a production sprite, and the manifest says so.
- **Approval scope is unchanged.** The creator approved only the selout v8 south idle **static** frame at 48 logical px. That PNG is untouched (sha256 `ccf9d2a2…b6fd`).
- **Review so far is agent-only.** Claude looked at every frame (see "Frame-by-frame review"). That is not a substitute for Codex's or the creator's judgment, and the motion itself was not watched (see "Unsolved").
- **No Git operations.** Nothing was staged, committed or pushed. No runtime sprite, M2 file, Game Bible file, `game/scripts` file or `docs/progress.md` was edited.

## Files

| File | State | Hash |
| --- | --- | --- |
| `tools/…south-run-v3-build_m8-w03_20261015-034327-4be0c7a2.py` | Edited in place (untracked). 1079 lines, LF, ASCII. | sha256-text-lf-v1 `8b68573d…84e2` |
| `tests/protagonist-female-south-run-v3/…deterministic-check_m8-w03_20261015-072133-7e6c5e0d.py` | Edited (untracked). 486 lines, LF, ASCII. | sha256-text-lf-v1 `1dc7ab10…0acd` |
| `game/assets/characters/run-pilots-v3r2/` | **New folder.** `.gdignore` (empty, written first), 16 frame PNGs, 1 `.pxo`, 1 manifest. | manifest sha256-bytes `dbf41fdb…3c3a`; `.pxo` `e41e6421…37da` |
| This note | New | n/a |

All r2 names use part `south-run-v3r2`, stamp `20261015-035446` and run id `8c1f70ee`, for example `rpg-2-star-ocean-the-second_protagonist-female_south-run-v3r2-run-f07-flight2-vr_m8-w03_20261015-035446-81fdff77.png`. No name reuses the rejected build's stamp `20261015-034327`, and a test enforces this. The first v3 build was never written into the repository, and nothing of it was overwritten.

Scratch review media are in `%LOCALAPPDATA%\Temp\wb-preview-8c1f70ee\`, outside the repository:
- 4× nearest-neighbour PNGs of v8 and of each frame;
- a 2× sheet (v8, then f01–f08 and f09–f16);
- an in-place GIF. Its timing is approximate because GIF delays have a 20 ms minimum: stance frames show for 20 ms against 16.7 ms true, flight frames for 60 ms against 55.6 ms true.

## What was wrong with the first v3 build (from its pixels, not just its metrics)

| Codex finding | Cause in the code / texels |
| --- | --- |
| f07/f08/f11: one long tube leg, other leg nearly absent | The stance leg was a single segment with hip x = knee x = boot x, so the taper rounded away. In f01, vr repeats the row `K6556633K` for about 30 rows. The kick/tuck foot was a sole-up boot placed at the knee ±4 x, −6 to −8 rows, which is beside the thigh, under the coat flap and the hand. Below the coat, f07 vr had 10 opaque texels and 0 boot texels. |
| f01: vertical extended leg, cropped opposing boot | The contact leg was vertical. The opposing tuck leg ended at the knee guard, and its sole-up boot was covered. |
| Arms and torso frozen | The arms were v8 texels moved by the bob only. |
| Not noted by Codex | Legs and boots were 2–3 texels wider than v8's (9–10 against 7–8). There was a 3-texel transparent gap between the thighs under the belt: 40–55 gap texels per frame, against 16 in v8. |

Measured on the rejected build's PNGs: one leg band (rows ≥ 77 + bob) had **0 boot-leather texels in 9 of 16 frames**: f01–f03, f07–f11 and f15–f16.

## What r2 changes

The locomotion model is unchanged:
- 16 frames, 70 px cycle, 140 px/s, 4 steps/s, 32 fps mean;
- stance soles 110 / 105 / 100 / 96 / 91;
- the root lock as exact fractions, max |r| = 4/3 logical px;
- the identical bob table.

The art is replaced. Every texel is still placed by the script at 1:1 in v8's palette, with no generative redraw, resampling, flips or mirrors.

**Legs.** Each leg is a set of tapered capsules: hip → knee → calf → ankle.
- Half-widths are 4.7–4.9 at the hip, 3.6–3.8 at the knee and 3.2–3.3 at the cuff, which matches v8's widths.
- Each leg has its own axis. vr leans outward like v8's (hip 41, knee 42.5, cuff 45.5); vl runs hip 31 → cuff 31.
- Shading uses v8's trouser ramp (K | 6 | 5 | 6 | 3 | K). The lit band narrows at the knee and drifts ±1 texel with a fold table, so no stripe runs straight down a leg.
- vr has a knee-cap light and crease, as in v8 rows 77–79.

**Crotch.** v8's own trouser seat (leg rows 61–66) is a `hips` layer behind the legs, so the under-belt gap is closed. It is now 20–27 texels per frame, against 16 in v8 and 40–55 before.

**Boots.** The shaft rows are v8's exact boot texel strings (cuff, plain shaft, lace band), set on the leg axis. The feet are drawn per view in v8 leather: strike, flat, heel-up, toe, hang, reach.
- The stance views of each leg keep their lowest-row centre within 0.5 texel relative to the cuff. In the PNGs, the planted toe-x spread is 0.5 texel in both stances.
- The vl flat foot is v8's foot turned from its idle splay toward the camera. Placing the splayed v8 foot by its sole had pushed the vl shin 3 texels sideways.

**Swing leg, which is always visible.**
- Kicked back (kick, tuck, tuckpass): a sole-on boot just under the knee, showing the boot back, the heel counter, the seam and the tread. This is the 16-bit front-run convention, not strict projection.
- Passing and driving: a short, foreshortened thigh, a hanging shin and a toe-down boot.
- Reaching: a long shin and a toe-up boot.
- Descend differs from contact (knee 20 rows below the hip against 21, sole 46 rows below the hip against 48), so f08/f16 are no longer just f09/f01 shifted down a row.

**Knee guard.** The viewer-left knee keeps v8's plate (front), plus the raised and back views.

**Arm pump.** The fist (viewer-left) and the right forearm (cuff, wrist and hand, viewer-right) stay rigid v8 texel blocks.
- They translate by (dx, dy) in [−1, 1] × [−2, 0], only up and/or inward, so no coat texel behind them has to be invented.
- The pump is contralateral. The right forearm is up and in during f05–f09, while vl reaches. The fist is up and in during f13–f01, while vr reaches. The two arms are never both at their highest.
- A texel the arm vacates next to the body becomes a K seam: 0–5 texels per frame.

**Pinholes.** A single transparent texel closed on the left, right and above by a leg or hips texel is inked. That is 1–3 per frame, all at the thigh/flap/hand junctions. v8's own notch at the cape hem (x 21) is deliberately left alone.

**`.pxo`.** It now has 8 layers: cape, hips, leg-far, leg-near, coat-skirt, upper-body, arm-vl, arm-vr.

**Paths.** `--preview` used to crash with a raw `FileNotFoundError` traceback when a scratch folder under `%TEMP%` made folder + name exceed MAX_PATH; `LongPathsEnabled` is 0 on this machine. That is why Codex previewed into `C:\wb-preview-a3f7c901`. Now:
- every mode resolves relative `<dir>` arguments against the current directory and prints the absolute path to stderr;
- every file operation uses the `\\?\` extended-length form when needed;
- the `game/` guard uses `realpath`, so `--preview game/x` from the repository root is still refused.

The new `--preview` also writes the 2× sheet.

## Verification

`--check` on `game/assets/characters/run-pilots-v3r2/`: **30/30 gates pass**, exit 0. New or changed gates:
- `identity_rows_0_60_exact`: rows 0–60 + bob match v8 exactly outside the declared arm zones (each v8 arm box at its home and pumped positions, grown by 1);
- `arms_rigid_v8_texels`: each arm core equals v8 translated by bob + offset;
- `arm_pump_bounded`;
- `both_legs_visible_every_frame` and `both_boots_visible_every_frame`: at least 50 opaque and at least 20 boot-leather texels per leg band. The thresholds were calibrated on the rejected build, which fails them; r2's minimums are 57 and 33;
- `no_single_texel_pinholes`;
- `sole_rows_match_manifest`, which now covers every foot, because no foot is hidden.

Other results:
- Palette: exactly v8's 32 colours in every frame. Alpha is {0, 255}, and the cell border is clear.
- The written folder is byte-identical to a scratch `--out-dir` build.

**Tests:** 17/17 pass in about 5 s, using `python -I` with the Codex-runtime Python 3.12.14, Pillow and NumPy. The 13 earlier tests were kept; some were updated for r2, and four are new:
- two legs and two boots in every frame, plus a tamper case: erasing one leg band in f07 flips both gates and `--check` exits 1;
- the arm pump is rigid, bounded and opposed;
- no pinholes, and no reuse of the rejected stamp;
- `--preview` with a relative path, with a path over 260 characters, and with a relative `game/…` path (refused).

`tearDownClass` now deletes its long-path scratch folder through `\\?\` and fails if anything is left behind. An earlier run had left `wb-run-v3-test-2od2_blp` in `%TEMP%`; it was removed.

The planted-foot simulation still shows 0 px slip at 30, 60 and 144 fps, both exact and pixel-snapped.

## Frame-by-frame review (Claude, at 1:1 texel dumps and 2× / 4× / 7× nearest; not a human review)

| Frame(s) | Reads as | Remaining weakness |
| --- | --- | --- |
| f01 / f09 contact | A stride toward the camera. The near leg is angled, with a visible knee and calf, ending in a toe-up boot. The other knee is raised, with a sole-on boot under the guard. | The contact leg is still long: sole row 110, against 103 for v8's lowest sole, so it is about 48 rows against v8's 42. That length is kept on purpose (see "Unsolved"). |
| f02 / f10 load | A bent planted leg with a v8-shafted flat boot; the other foot is still back. | — |
| f03 / f11 mid | A passing position. The raised guard is on the near knee, and the hanging boot is 5 rows above the planted one. | At a still frame it looks like a walk. It is held for one 60 fps tick. |
| f04 / f12 push | A heel-up planted boot and a driving knee. | The two soles are within 1 row of each other, so the push is not obvious. |
| f05 / f13 toe-off | A short planted leg on its toe; the driving leg is longer. | **The planted foot is 8 rows above the swinging foot.** That follows from the screen projection (a foot behind the body is higher on screen), but on its own the frame can read as the planted foot lifting early. It is held for one tick. |
| f06–f08 / f14–f16 flight | **The strongest frames.** One leg reaches with a toe-up boot; the other is kicked back with its sole visible. They read as running. These three frames are about 67% of screen time. | The sole-on boot is a dark block at 1×. It reads as a foot, but its shape is not detailed. |
| Upper body, all frames | Identity is intact: head, hair, face, scarf, flask, coat and belts are exact v8 texels, shifted by the bob. | The pump moves the hands 1–2 texels (0.5–1 logical px). It reads as a small alternating pump, not a swing. The torso, cape, coat hem and hair are rigid. |

## Unsolved, stated plainly

1. **This is not a polished run yet.** The legs and occlusion are fixed, but the upper body has no lean, no cape or coat-hem lag and no hair motion. The arm motion is a rigid pump with no elbow bend or forearm foreshortening. At 48 px the upper half will look stiff against the legs.
2. **The contact leg is long** (f01, f09, and f08/f16 one row shorter). Shortening it means lowering the stance climb (soles 110 → 91). That makes the sprite's on-screen speed less even: stance frames at about 0.7× instead of 0.81×, flight frames at about 1.16× instead of 1.09×, and a larger root offset. Keeping the motion even was judged more important, but the choice needs a visual decision in motion.
3. **f05 and f13 (toe-off)** can read as the planted foot lifting early (see the table).
4. **Not watched in motion.** Claude reviewed still frames only. The GIF and sheet are for Codex and the creator. The timing review (60, 30 and 144 fps; 30 fps drops stance frames) and the city, outskirts and dark-annex captures in Godot have **not** been done.
5. **The `.pxo` has not been opened in Pixelorama**, which is not installed here. Its structure is checked only by re-stacking its 8 layers per frame, which matches the PNGs exactly.
6. The start/stop transitions are still absent; that is listed as pending in the manifest.

## What Codex should judge

1. Compare the 2× sheet with Codex's own preview of the first build, frames 01/03/07/08/11.
2. Watch the GIF at 1× and 2× for leg readability and the arm pump.
3. Decide whether the long contact leg and the f05/f13 toe-off read acceptably in motion.
4. Decide whether the upper body needs a lean and cape lag before a creator review, or whether a legs-and-pump review is enough for now.
