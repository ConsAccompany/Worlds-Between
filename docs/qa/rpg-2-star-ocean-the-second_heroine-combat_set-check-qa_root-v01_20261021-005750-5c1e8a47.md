# Heroine combat set — independent technical set check (qa.combat.protagonist-female.set-check)

Run 2026-10-21T00:54:05Z (UTC) on tested revision `85a32e34fc40b3bb4db6a9bc4ed6fcf8623d5c58`, from clean worktree `work/dual13/cl-check`. Claude ran the check. No art, arena, loader or test-harness source was changed, and no defect needed a fix.

## Why re-run

The previous closeouts bound arena raw SHA256 `2b214b6b…`. At this revision the arena is `956ee43d…` because 31c92aa added the opt-in `--battle-native-environment-v01` backdrop selector (+9/−2 lines, outside the heroine branch). This run re-binds the existing heroine harnesses to the current bytes.

## Method

`tools/rpg-2-star-ocean-the-second_heroine-combat_set-check-runner_root-v01_20261021-005402-5c1e8a47.py` (sha256-text-lf-v1 `1e225ac2…7c36`):

- Exports HEAD (`game`, `tools`) and default-off base `11973af` (`game`) with `git archive` and `core.autocrlf=false` into `%LOCALAPPDATA%\Temp\hsc\<id>`. The tested bytes are the committed blobs, and import side effects stay out of the worktree.
- Imports each export, then runs every existing harness through the bounded checked runner (`…checked-runner_v01_…f74ac6d1.py`). Each run has a finite deadline, an exact expected marker, fresh APPDATA/LOCALAPPDATA profiles and a unique log.
- Fails any run that has an `ERROR` line, even with exit 0.

## Results (all source-bound to the hashes in the proof JSON)

| Area | Harness | Result |
|---|---|---|
| All 8 actions (frames, pivot 32/68, 30 Hz integer ticks, loop starts, 29 exact RGBA cells, provenance) | package verifier v01 (Python, no Godot) | 569/571 content PASS; 2 raw FAIL `base_revision`, `scope_untracked`. Both assert the producer checkout state (HEAD==11973af, no other untracked files), so they fail by construction at any later revision. They are retained, not relabelled. |
| Authored timing/rational clock | rational-clock root check | `ROOT_RATIONAL_CLOCK_PASS checks=220` |
| Attack request → contact 5/30 → recovery 12/30, cooldown; cancellation by dodge/skill/hit/down | contact timing check | `HEROINE_CONTACT PASS checks=80` |
| Direction continuity: facing latch for dodge/hit/skill/defeat, both facings, restart, release on idle/move/guard, legacy isolation | facing root check (actual packed set) | `ROOT_FACING_PASS checks=251` |
| Shared bonus consumed only at contact, hit orders, cancel, ally finisher | shared-bonus root check (staged fixtures) | `ROOT_SHARED_BONUS_PASS checks=16` |
| Half-scale playback | half-scale check | `COMBAT_HALF_SCALE PASS checks=273 failures=0` |
| Normal arena + scripted Input, actual art, 30/60 fps: request, before-contact, contact, finishing contact, result reveal | normal-input root check (1280×720) | `ROOT_NORMAL_CONTACT_PASS checks=46`, 8 captures |
| Default-disabled behaviour plus action-mix/guard/dodge/defeat/fallback (640×360) | legacy pilot check, compared against 11973af flag-off baseline captures | baseline `PASS checks=8`; `COMBAT_SET_PILOT PASS checks=261 captures=12` |
| Optional natural encounter (explore → battle → result click → return → reload) | natural flow harness, patrol | `NATURAL_FLOW_ALL_PASS scenario=patrol checks=30`, 6 critical captures |

Diagnostics: 0 `ERROR`/`SCRIPT_ERROR` lines in any run. Baseline warnings disclosed:
- "N ObjectDB instances leaked at exit" in contact80, shared-bonus16, normal-input46, both legacy runs and natural-patrol.
- "Exponent too high" in half273, from its intentional malformed `1e999` input.

Coverage of the eight actions:
- **Idle and attack:** clock, contact and normal-input checks. Contact damage and VFX resolve once; finishing contact stays visible before results.
- **Guard:** intro plays once; covered by the package and legacy action-mix checks.
- **Dodge, hit, skill:** one-shots that cancel any pending attack. Covered by contact80 and facing251.
- **Down:** mapped to defeat and held until revive. Covered by facing251 and the legacy dodge-defeat capture.
- **Recovery:** 12/30 presentation recovery. Covered by contact80 and normal-input46.

## Evidence

- Proof: `outputs/hsc-v01/20261021-005405-259b6294/rpg-2-star-ocean-the-second_heroine-combat_set-check-proof_root-v01_20261021-005405-259b6294.json` (sha256-bytes `26ae7f97…d476`). It has per-run commands, logs, warnings and ERROR scans.
- Source sha256-bytes (committed blobs):
  - arena `956ee43d3f0f14c3…`
  - loader `ac8cd3dce945de02…`, unchanged from the natural-facing closeout
  - sheet PNG `f55db8cca615d4d6…`
  - manifest `6a4c663d859818d8…`
  - index `1abb5b67b3bf59c0…`
- Actual-art gameplay captures: `cap/` (1280×720 normal-input) and `natural/` (1280×720 patrol). The 640×360 captures in `head640/` are the loader-path fixture set labelled TEST. They prove the default-off and fallback paths, not heroine art.

## Retained failures and limits

- First attempt (deleted output): the package verifier showed the same 2 checkout-state failures, then the tar export raised `FileNotFoundError` on a long `.ora` path.
- Second attempt (`outputs/hsc-v01/20261021-005344-56d9f56e`, verifier report retained): the extended-length export failed on mixed `/` separators (`WinError 123`).
- One runner-only repair: manual long-path extraction. No harness, threshold or marker was changed.
- Scripted input only: no human playthrough. The natural flow covered patrol only (sentry was not re-run), and continuous normal-speed fluidity was not judged.

## Verdict

**Technical set check: PASS** at 85a32e3 for the opt-in heroine combat set: all 8 actions, timing/contact, facing, default-off parity and the optional natural encounter. Two producer-checkout-state verifier predicates are disclosed above.

It does not establish:
- creator motion or full-sprite acceptance
- art approval
- default adoption
- a human playthrough

Those remain separate. No ledger, Bible, registry or Git index change was made.
