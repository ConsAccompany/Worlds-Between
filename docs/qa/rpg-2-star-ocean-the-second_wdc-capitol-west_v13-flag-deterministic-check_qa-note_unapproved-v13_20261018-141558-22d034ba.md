# Washington Capitol west — v13 flag: reproducible technical check (QA note; technical check only, art UNAPPROVED)

- **Date:** 2026-10-18, about 14:15–14:30 EDT (wall clock). Stamp `20261018-141558` and id `22d034ba` are run labels.
- **Author:** Claude Code (Opus 5.5), signed in on the Max subscription (claude.ai, firstParty). No API key, cloud credits, paid fallback or image model was used. There was no quota stop.
- **Worktree:** `work/max0840-wdc-ruin` at the pushed merge `54a5894` (clean).
- **Scope:** check tooling, a failure receipt, verification evidence and this note.
  - **No art, runtime, selector, scene or default change.**
  - No Bible, progress, ledger, queue or metric files. Not pushed.

## Why

The published flag checker (`tools/…v13-flag-integration-check…63201688.py`) was **red after the merge: 18/21**. Its historical 21/21 report (`outputs/wdc-cw-v13flag_20261018-135539-63201688/`) is kept unchanged. The merge-time combined check did **not** pass.

- **F01/F02 (design fault):** they compare the worktree's *uncommitted* `game/` delta with HEAD. A clean committed checkout can never pass them.
- **F13 (nondeterminism):**
  - The hero moves `MOVE_SPEED * delta` per frame (v12 selector `_process`), and the harness ran with wall-clock deltas. So where a real-time walk stops varies by a frame step from run to run.
  - The v12r2 camera rate of 1.7 turns a 1.4 px difference at the feet into 2 scroll rows.
  - At 14:12 the **unchanged v12r2 path** stopped zh traversal-end at scroll **12** against the committed **14**, with the hero 2.37 px away.
  - At 14:16 the same unchanged checker, re-run on clean HEAD, passed F13 (19/21, still failing F01/F02).
- **Earlier runs:** the 13:58 run (18/21) and the 14:01 run (20/21) of that checker had their outputs deleted before re-runs reused the same names. They **cannot be recovered**. The 14:12 run's raw log and temp tree were deleted during cleanup at about 14:13, so its values in the receipt are transcribed from the console output read in the session. No log was reconstructed.

## Fix (root cause, no wider tolerance)

New tool: `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v13-flag-deterministic-check_unapproved-v13_20261018-141558-22d034ba.py`.

It reuses the published flag-path harness unchanged and imports the published checker's helpers. Nothing is duplicated in `game/`.

1. **Committed-tree validation** (git only, so it works on a fresh clean checkout):
   - **D01:** the WDC commits since the pinned predecessor `6406bb8` (`b674c7e`, `9071882`) change in `game/` only the 7 v13 candidate files and the 3 flag files.
   - The other 8 `game/` changes since `6406bb8` come only from non-WDC commits `3a0a97d` (Sentry, including `battle_arena.gd`) and `31705c4` (Ji Cheng). They are recorded as info.
   - **D02:** HEAD's selector, scene and sidecar equal their pins. The selector extends v12r2. The scene differs from `6406bb8` by exactly the one script-path line (v12r2 → v13). The v13 rt-base equals its manifest hash.
   - **D03:** the base script, survey annex, v12/v12r1/v12r2 selectors, the 21 v12 candidate files and the replay base (27 files) are byte-identical to `6406bb8`. The v13 harness is unchanged since the one commit that added it.
   - **D04:** all test tools live in `tools/`, and no `game/` file loads one (no `res://../tools`). Two `game/` files *name* a tool as documentation: the v13 manifest's `harness` field and the selector's `# Checks:` comment. These are recorded as info.
   - **D05:** the temp tree is `git archive HEAD`, with 1,776 blobs re-verified. No worktree overlay.
2. **Deterministic moving routes:**
   - Every harness run uses Godot `--fixed-fps 60`: delta is 1/60 per frame, and real-time sync is off. The same scripted inputs then give the same deltas in the base (v12r2 flag) and the candidate (v13 flag).
   - **Each mode runs twice.** The declared moving-shot bound stays **one scroll row / 3 px**; the actual values are reported below.

## Result: `check --write-report` → **22/22 PASS** (attempt 2, 14:22:22–14:23:30 EDT, 67.5 s)

Attempt 1 (14:20:44–14:21:52) gave **20/22 FAIL**. Both failures were bugs in my new gates:
- D03 compared the v13 harness with `6406bb8`, which predates that harness.
- D04 rejected any mention of a tool's name in `game/`.

I fixed both definitions as described above. Attempt 1's stdout is kept; it wrote no other evidence.

| Gate | Result | Actual |
|---|---|---|
| D01–D05 committed tree vs `6406bb8` | PASS | as above |
| D06 import | PASS | |
| D07 four fixed-fps runs, no errors | PASS | |
| D08 repeatability | PASS | v13 a vs b and v12r2 a vs b: **0 differing px** over 16 shots each; recorded runs equal |
| D09 flag selection | PASS | the scene runs the v13 selector; `-v13` enables v13; `-v12r2` leaves v13 off |
| D10 off by default | PASS | city/outskirts/ruins equal the base script and the pre-change frame hashes |
| D11 / D12 layers | PASS | v13 draws `ba106505…` from the v13 path; v12r2 draws `058fb629…`; every other layer path, the walk mask and the foreground are identical |
| D13 20 fixed-position shots vs committed frames | PASS | **20/20 pixel-exact with equal state**; the label-slot allowance was not used |
| D14 moving shots, base vs candidate, same inputs and deltas | PASS | zh/en traversal, traversal-end and battle-return: **state equal, scroll equal, 0.0 px**; 2,081–2,143 changed px, **0 outside** the projected v13 change; v13 art texel-exact (2,039–2,138 bare texels) |
| D15 fixed shots, base vs candidate | PASS | 2,141–2,144 changed px, 0 outside the projected change, v13 art exact, collapse visible |
| D16 records | PASS | real `interact` |
| D17 traversal, battle, return | PASS | both flags × zh/en: real sentry battle, real result button; return texel (533.26, 289.60), scroll 78, 106 approach frames, 101 traversal frames, identical in all four |
| D18 play band / D19 saves | PASS | |
| D20 accepted rooms | PASS | 8/8 frames **0 px** with `--wdc-capitol-west-v13` present; 3/3 interactions; `ACCEPTED_REPLAY_ALL_OK` |
| D21 worktree untouched / D22 contract | PASS | |
| Sentry 281/5 | not applicable | no runtime change since the merge-time 281/5 pass |
| smokes m4/m6/m7/m8 | not run | not in this bounded scope; no runtime change |

**Limits:**
- **Fixed time-step only.** D14 proves base and candidate move identically at a 1/60 s time-step. It does not prove that real-time play at variable frame rates matches pixel for pixel; real-time variance is inherent to the delta-based movement.
- **Reference frames are still real-time.** D13 compares fixed-position shots with the committed real-time frames. Moving shots are compared base against candidate, not against the old real-time captures, although several fixed-fps frames happen to be byte-identical to them (for example en traversal `75a5ff69…`).
- **v12r1 label hysteresis is still there.** It is not exercised here because the routes are deterministic.
- **No creator review.** Art UNAPPROVED.

## Files

Evidence is in `outputs/wdc-cw-v13flagdet_20261018-141558-22d034ba/` (43 files: 32 frames + 11 JSON/TXT; JSON and TXT are LF with exact-path `eol=lf` rules; no machine paths):

- **Failure receipt** `failure-receipt_…json` (`9f31727f…`).
  - It pins: the published-checker re-run log (`0324d545…`); its two harness reports (`d0308f73…`, `70aa4ba0…`); the attempt 1 and attempt 2 stdout logs (console output, CRLF normalized to LF before hashing).
- **Verification:**
  - `deterministic-check-report` (`93498348…`);
  - `deterministic-check-manifest` (`bd7e6397…`), which pins 36 evidence files and the tool;
  - `fixedfps-harness-report-v13flag` / `-v12r2flag`;
  - `fixedfps-accepted-rooms-replay-log`;
  - 32 frames `rt640-<zh|en>-<view>_flag-<v13|v12r2>-fixedfps_…png`, for example v13 zh entry `a4b1e573…`, en battle-return `9888b668…`, zh battle-return `dfc682c3…`.
  - Run b's capture hashes are in the report.
