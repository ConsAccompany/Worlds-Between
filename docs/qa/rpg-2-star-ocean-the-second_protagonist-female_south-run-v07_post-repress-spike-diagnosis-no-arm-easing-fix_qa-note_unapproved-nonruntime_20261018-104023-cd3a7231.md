# Female south RUN v07: post-re-press pose spike, diagnosed — no v08 arm-easing amendment made (QA note, m8-w11)

**Status: UNAPPROVED / NONRUNTIME, diagnosis only.** No v08 amendment, art, gait, timing, runtime, queue, receipt or ledger change. v06 and v07 sources are byte-identical to `f7571a1` (check 04). Sprites stay 0/52.

## Task and outcome

The task asked to remove the "arm-easing pose spike" that the v07 QA note lists as remaining defects 1–2:
- 30 fps: 477–484 px against the steady run's 473, 2–3 frames after the next touchdown;
- 144 fps: 374 against 345.

The constraints were to keep the v06/v07 bytes, the art, touchdown and stop timings, speed and alternation.

**Finding:** the spike is **not caused by the arm easing**. It is the steady per-px gait itself, sampled at 30 fps at phase pairs that the steady 30 fps run happens never to sample. A re-press re-derives the gait phase from the planted boot, so its frames land on those pairs.
- An arm-easing change cannot remove it.
- Removing it would mean changing the gait's per-px sequence (art and timing) or the phase/touchdown timing after a re-press. Both are outside this task's constraints.

So I stopped. I did not ship a change for a cause the evidence does not support.

## Evidence

Source: the receipt `outputs/…gait-driver_protagonist-female-south-run-v07-post-repress-spike-diagnosis-receipt_unapproved-nonruntime_20261018-104023-df69d961.json`. It was produced by real Godot 4.7.2 (official build, already in session scratch; no new download), running headless with the v07 compositor and gait driver unchanged.
- **Measure:** the v06/v07 `cell_silhouette_xor`. At the 0.5 display scale in a 1280×720 window of the 640×360 logical viewport (heroine 48 logical px), one cell texel is one window pixel.
- **Validity:** all four v07 spikes reproduce **exactly** (484, 480, 477, 374).

| Case (v07 tag) | Spike frame | v07 = re-simulated | Steady per-px gait, same two phases | Drawn state vs steady per-px |
|---|---|---|---|---|
| city-bright repress-30fps-006-gap-01 | +4 (lift-off) | 484 | **484** (phase 53 → 63) | cape shift −1/0; arms R F1/F2, L N/B1 (still easing) |
| repress-30fps-015-gap-01 | +4 | 480 | **484** | cape shift −1/0 only (arms already on the gait) |
| repress-30fps-005-gap-01 | +5 | 477 | **484** | arms R F1/F2, L N/B1 |
| repress-144fps-020-gap-12 | +21 (after touchdown) | 374 | **398** | cape shift 0/−1, hair −1/0 |

What the table shows:
- With the arms **fully on the gait** (release-15) the frame is still 480.
- With the arms forced onto the gait target in the release-6 and release-5 cases, the frame would be 513 and 506 (probe during this task). So the easing lowers the change rather than adding to it.
- At 144 fps the steady gait's own transition between the same phases is larger (398) than the drawn one.

**The steady gait's own envelope** (every phase, per-px states N px apart):

| Step | Max | Pairs over 473 |
|---|---|---|
| 1 px | 282 | 0 |
| 2 px | 398 | 0 |
| 4 px | 423 | 0 |
| 5 px | 444 | 0 |
| 9 px (30 fps) | **513** | 3 (12 → 21, 78 → 3, 79 → 4) |
| 10 px (30 fps) | **528** | 10, including 53 → 63 = 484 |

**Steady runs, 24 sub-pixel start alignments, 2.2 s each:**

| fps | Max | v07 walk |
|---|---|---|
| 30 | 473 | 473 |
| 60 | **418** | 371 |
| 144 | **374** at every alignment | 345 |

The v07 "steady" limits came from one alignment over a 0.83 s walk. The 144 fps "spike" is inside the steady envelope.

## What this means

- The 30 fps over-473 frames are lift-off frames where the per-px gait changes a lot within one 9–10 px step. The steady 30 fps run's alignment avoids them; a re-press does not.
- Two real options exist, both outside this task:
  - a gait or art change, for example softening the per-px transitions around phases 3, 21 and 63 (the 78/79/77 → 3 pairs reach 513–528);
  - a phase-alignment rule after a re-press, which changes touchdown timing.

  Either needs a creator or root decision.
- No number here measures fluidity. Whether the re-press reads as smooth at 1× is still Root's and the creator's judgment.

## Files (new; nothing else changed)

| File | Purpose |
|---|---|
| `tools/…south-run-v07-post-repress-spike-diagnosis_m8-w11_20261018-104023-553406e2.gd` | headless diagnosis; extends the v07 tool (v06/v07 tool and manifest hashes pinned); writes the receipt |
| `outputs/…v07-post-repress-spike-diagnosis-receipt_…df69d961.json` | the receipt (per-frame rows, sweeps, envelope) |
| `tests/protagonist-female-south-run-v07-spike-diagnosis/…focused-check…1401dff8.py` | 4/4: reproduction, the steady per-px comparison, the envelope, v06/v07 sources untouched vs HEAD |
| this note | |

## Not done (by design)

- No v08 source, showreels or diagnostic captures: there is no v08 behaviour to film, and filming v07 again would add nothing.
- No queue, receipt or ledger change.

The existing v07 focused check still scores 11/12 in this clean clone. Check 02 needs local-only v06 files, as disclosed earlier.
