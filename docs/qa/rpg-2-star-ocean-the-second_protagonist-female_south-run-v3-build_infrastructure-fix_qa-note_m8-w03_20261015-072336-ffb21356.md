# Female south run v3 (m8-w03) builder: infrastructure fix and deterministic checks

M8, 2026-10-15 (UTC 07:23), by Claude. This note follows the pre-run audit `…south-run-v3-build_pre-run-technical-audit_qa-note_m8-w03_20261015-071053-86f9c79f.md`. It contains no art verdict.

- **Not visually reviewed.** No frame of v3 has been looked at by Claude or by anyone else. No preview image was produced.
- **No art was approved or produced.** Nothing was written under `game/`. `--write` was not run. No existing image was edited, and the v8 source hash is unchanged (`ccf9d2a2…b6fd`).
- **Scratch frames only.** The builder ran only into temporary folders under `%TEMP%`, which were deleted afterwards. Those frames fed algorithmic checks and were never opened as images.
- **Approval scope is unchanged.** The creator approved only the selout v8 south idle **static** frame at the 48-logical-px displayed scale. Any v3 output is an unapproved pilot, not a production sprite.
- Nothing was staged, committed or pushed. No `game/scripts`, Game Bible or `docs/progress.md` file was touched.

## Files

| File | State | Hash (sha256-text-lf-v1) |
| --- | --- | --- |
| `tools/…south-run-v3-build_m8-w03_20261015-034327-4be0c7a2.py` | Edited in place (untracked). 1038 lines, LF, ASCII. | `e8b38858…99ce` |
| `tests/protagonist-female-south-run-v3/…south-run-v3-build_deterministic-check_m8-w03_20261015-072133-7e6c5e0d.py` | New. 361 lines, LF, ASCII. | `24606741…24eb` |
| This note | New | n/a |

## What changed in the builder

The leg art tables were left unchanged: `GUARD`, `FEET`, `KICK`, `LEG_W`, `leg_pose`, `STEP`, `draw_leg` geometry and `split_v8`.

**Docstring corrected.** It now states the status at the top: an unapproved, legs-only pilot that has not been visually reviewed. It drops these claims that the code did not implement:
- arm swing;
- torso lean;
- cape and coat lag;
- start and stop transitions;
- "~4.75 texels per tick".

Those four features now live in `PENDING_VISUAL_DECISIONS`, which is copied into the manifest. Each entry records what was planned, what is built (nothing) and what decision it needs.

**Hash gate in every mode.** `v8_path_checked()` runs first in `--out-dir`, `--write`, `--check` and `--preview`. If the source is missing or its hash differs, the builder exits non-zero before it creates any folder.

**Lossless split gate.** `split_checked()` verifies that the parts (cape, upper body, skirt, fist, right arm, left leg, right leg) partition v8 exactly. The two leg parts are the only ones discarded.

**Build (`--out-dir` / `--write`)** writes:
- 16 PNGs;
- a 7-layer Pixelorama `.pxo`, whose frame durations are proportional to `hold_px`;
- a manifest.

For each frame, the manifest records:
- `bob` and the leg phases;
- the near leg and the planted leg(s);
- the sole row per leg (`null` when the foot is hidden) and the toe x;
- `hold_px` as both a float and an exact fraction;
- `root_lock` (`r_start_px` and `slope`) as both a float and an exact fraction;
- `kick_boot_visible_texels` (report only);
- a `sha256-bytes` hash.

At the top level, the manifest records:
- `art_approved`, `human_reviewed`, `runtime_integrated` and `production_sprite`, all `false`;
- `visual_review: "not performed"`;
- the transitions (`start_idle_to_run` and `stop_run_to_idle` are `null`).

Writing behaviour:
- If the output folder is under `game/`, an empty `.gdignore` is written before any PNG.
- Existing files with different bytes are never overwritten.

**Root lock.** This is v2's model, computed in `Fraction`s. The stance climbs (5 + 5 + 4 + 5 texels = 9.5 px) do not equal the stance travel (35/3 px). The lock absorbs the 13/6 px residual exactly and ramps it back over the flight frames at slope 13/140. The maximum |r| is 4/3 logical px.

**Naming.** Every output name follows the AGENTS format: `rpg-2-star-ocean-the-second_protagonist-female_south-run-v3-<key>_m8-w03_20261015-034327-<id>.<ext>`.
- The stamp is the script's fixed `STAMP`.
- The ids are `sha256(RUN_ID:role)[:8]`.
- Names are therefore deterministic. All 18 are unique, and so are their ids.

**`--check`** reads only the files on disk: the v8 PNG, the frame PNGs, the `.pxo` and the manifest. It never calls `compose` or `draw_leg`. It prints JSON with 25 named gates and exits 1 if any gate fails.

**`--preview`** now writes one 4× nearest-neighbour PNG per frame, with AGENTS-style names. It no longer writes the two collage strips `preview-a.png` and `preview-b.png`, which had generic names. It refuses any path under `game/`.

## Verification (algorithmic only)

The test file runs 13 tests in about 4 s, and all pass. Run it with `python -I tests/protagonist-female-south-run-v3/<file>` using the Codex-runtime Python 3.12.14, Pillow 12.3.0 and NumPy 2.3.5. Before and after the run, `git status --porcelain` was identical.

| Requirement | How it is tested | Result |
| --- | --- | --- |
| Source hash lock | A copied builder in a fake repo, with a missing v8 and with a different PNG under the v8 name. `--out-dir`, `--preview` and `--check` each exit non-zero, and nothing is written. With a genuine copy of v8, output under `game/…/run-pilots-v3` gets `.gdignore` and is byte-identical to the scratch build. | Pass |
| Determinism | Two builds produce identical file lists and bytes. A rebuild over a tampered folder refuses to overwrite. | Pass |
| `--check` has teeth | One off-palette texel at row 20 flips the gates for palette, sha256 and identity rows; the exit code is 1. | Pass |
| Palette / no filtering | Every frame is a subset of v8's 32 colours, and alpha is only {0, 255}. The build path contains no `resize`, `transpose`, flip or `::-1` tokens, and the only `resize` (in preview) is `NEAREST`. | Pass |
| Identity (head, hair, face, scarf, upper coat) | In every frame, rows 0..60+bob equal v8 rows 0..60 shifted by the bob, texel for texel, alpha included. The bob is found by a head search on the PNG and matches the manifest. | Pass, 0 mismatched texels |
| No mirror dependency | No frame equals the horizontal mirror of any frame. The manifest has `flip_h: false`. The 16 frames are unique, and none equals v8. | Pass |
| Frame count and names | 16 keys, from `run-f01-contact-vr` to `run-f16-flight3-vl`. Each leg follows the same 16-phase cycle, with vl offset by 8. Each step has 5 stance frames (7/3 px each) and 3 flight frames (70/9 px each). Cycle 70 px, step 35 px, 4 steps/s, mean frame rate 32 fps. | Pass |
| Seams and transitions | \|Δbob\| ≤ 1 at every change, including f16→f01. Root-lock continuity holds exactly at all 16 frame changes. Start and stop transitions are `null` and declared pending. | Pass |
| Sole readback | The planted sole rows read from the PNGs equal the manifest (110/105/100/96/91). The toe-row centre spread is 1.0 texel (vr) and 0.5 texel (vl). | Pass (≤ 1 texel) |
| Foot contact at 140 px/s | An exact rational runtime simulation over 3 s, at 4 start phases, using sole rows from the PNGs. | Pass |
| v2 parity | The same simulator on the existing v2 run manifest also gives < 0.01 px slip. The v2 capture measured 0 px, so this validates the simulator. | Pass |
| Unapproved status | Manifest flags, `visual_review`, the four pending ids, and the docstring markers are all checked. | Pass |

Foot-contact results by frame rate (start phase 0):

| fps | Planted slip, locked | Planted slip, unlocked (control) | Ticks per stance | Frames shown | Head step: nominal / min / max (window px) |
| --- | --- | --- | --- | --- | --- |
| 30 | 0 | 0.67 px | 2–3 | 11 of 16: f02, f04, f09, f11 and f13 never appear | 9.33 / 3.0 / 12.1 |
| 60 | 0 | 0.67 px | 5 | 16 | 4.67 / −1.0 / 6.1 |
| 144 | 0 | 4.17 px | 12 | 16 | 1.94 / −1.0 / 6.0 |

The locked slip is 0 both exactly and after rounding to window pixels. This is a model of the runtime, not a capture: the Godot capture harness has not been pointed at v3.

## Report-only metrics: art questions for a person, not gates

- **Gap under the belt** (audit risk 2): this counts transparent texels between opaque texels on the same row, rows 61–72 (+bob). v3 has 40–55 per frame; the v8 idle has 16. The wedge is real in pixel terms, and whether it reads at 48 px is a visual call.
- **Kick boot visibility** (audit risk 1): of the sole-up boot's texels, 13–15 remain visible on vr (f07, f08, f09), but only 3–5 on vl (f01, f15, f16). The vl kick is almost fully hidden.
- **Single-texel pinholes:** 0 in every frame.
- **Head motion:** the lock and bob make the head step 3.0 to 12.1 window px per tick at 30 fps, against a nominal 9.33. At 60 and 144 fps the head steps back up by 1 px on some ticks, against a nominal 4.67 and 1.94. Whether that reads as a jitter is a visual call.

## What remains before Codex should produce a visual preview

Technically, `--preview` into a scratch folder outside `game/` can be run now. It is gated, deterministic and named correctly. Codex should first decide whether a legs-only preview is worth judging or whether to wait for the items below. Running `--write` before a visual pass would only add an unapproved folder under `game/`; it is not needed for a preview.

1. **Decide the scope of the preview.** The current build has no arm swing, no lean, no cape or coat lag, and no start or stop transitions. A preview will show a static upper body over running legs. Either accept "legs-only" as the question for this review, or make the pose decisions first (see `PENDING_VISUAL_DECISIONS` in the manifest):
   - **Arms:** offsets or redrawn poses, plus a policy for texels the arms uncover. The identity check would then need to exclude the arm boxes, as v2's did.
   - **Lean:** what "forward" means in a south view.
   - **Cape and coat lag:** a split that keeps v8 rows 58–60 whole.
   - **Transitions:** foot re-placement between the v8 idle boots (x ≈ 26–28 and 49–53) and the run's planted boot centres (x 31.5 and 46).
2. **Resolve or accept the known geometry risks** quantified above: the vl kick boot is almost hidden, the gap under the belt is about 3× v8's, and the swing knee ignores the bob (audit risk 3; unchanged). These are pose edits, which I deliberately did not invent.
3. **30 fps drops 5 of 16 frames** at phase 0, including the vl contact frame f09; which frames drop depends on the phase. The foot is still pinned, but the stance reads with 2–3 drawings. Decide whether 30 fps matters for review.
4. **In-scene evidence** (separate work, outside this task's scope, since it means editing `game/tests`): point the v2 Godot capture harness and the slip tool at the v3 manifest. Then measure slip and head motion on captured pixels at 30, 60 and 144 fps in the city, the outskirts and the dark annex.

What Codex should judge visually once a preview exists is listed in the audit note's "When it is run" section, which still applies. The new metrics above say where to look first: the f01, f15 and f16 kick, the belt line, and the f03/f11 near/far swap.

**Not to conclude from this note:** whether any v3 frame or the animation is acceptable. That is the creator's call.
