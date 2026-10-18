# Female south RUN: bounded v08 cosmetic-retiming study — REJECTED (addendum, m8-w11)

**Status: no validated v08.** v07 remains the latest UNAPPROVED / NONRUNTIME motion candidate. There is no new showreel, motion card or queue change. Root stopped the study; the drafts are kept only in session scratch, uncommitted and unvalidated.

This study follows the reviewed diagnosis at `2d1e1a229d566285b3651f74d142b7594be15055`: `docs/qa/…south-run-v07_post-repress-spike-diagnosis-no-arm-easing-fix_qa-note…cd3a7231.md`. Its findings:
- the post-re-press spike is 30 fps sampling of the v06 per-px gait, not arm easing;
- the gait's own all-phase envelope at 9/10 px steps is 513/528;
- the v07 "steady" baselines were under-sampled: 144 fps reaches 374 at every start alignment, and 60 fps 418.

## What was tried (headless Godot 4.7.2 state-level A/B against v07; no renders)

Only cosmetic arm and bob transitions were retimed. Boots, contact, touchdowns, stride, speed and rules were unchanged.

**Envelope** (cell XOR at 1/2/3/4/5/9/10 px steps; v07 = 282/398/405/423/444/513/528):

| Candidate | Change | Envelope |
|---|---|---|
| A (arms + bob) | L F1→F2 +6 px, R B2→B1 −2, R N→B1 +4, dip q [6,14) | 227/342/349/367/401/471/493 |
| B (arms only) | L F1→F2 +5, R N→B1 +4 | 262/360/367/385/406/486/501 |
| arms-only aimed at the 30 fps pairs | (design search only) | pairs over 473 at 9/10 px: 13 → 7 |

**Held for both A and B:** boots and touchdown/lift-off/restart/release events identical to v07 in every A/B plan; 0 rise faults; 0 alternation failures; next-touchdown times equal.

**Parity failures (why rejected):**

| Candidate | Release → v8 differs | 30 fps spike cases | Other |
|---|---|---|---|
| A | 5 stops: 30 fps 1/9, 60 fps 1/18, 144 fps 2/22, mixed 1/12 (releases at phases 4 and 44–47, +1 frame) | 484 → 480, 480, 477 → 473 | 60 fps re-press window worse, 371 → 390 |
| B | 2 stops: 60 fps 1/18 (−1 frame), mixed 1/12 | unchanged: 484 / 480 / 477 | 144 fps worst 374 → 345 |

- **30 fps limit:** with the bob window fixed (needed for exact stop timing), arm retiming alone cannot bring the 53→63 pair below about 477. The per-pair floor (about 431–441) needs a bob change, and a bob change alters stop timing.
- **No demonstrated improvement:** none at normal 1× speed, and no showreel was produced.

## Standing

- v07 limits stand: the 30 fps post-re-press pose changes up to 484 px lie inside the gait's own all-phase envelope, a worst mixed-frame-time stop of 270.8 ms, and the placeholder north walk on reversal.
- The creator's existing smooth/fluid/well-paced request still stands. Future technical polish does not need a new creator decision.
- Sprites stay 0/52; nothing is approved.
