# Heya four-direction idle — repair addendum v02 (UNAPPROVED, batch159)

Task: `content.char.heya.idle-anim`. Scope: bounded QA repair of the existing i159 source bank only.
Status: **UNAPPROVED technical source-fit repair**; not runtime/default integration, not SpriteFrames engine
playback, not human motion review, not art/style/gameplay acceptance. This is a NEW addendum. The producer
QA (`docs/qa/..._heya_idle-four-direction-source-qa_unapproved-v01_20261024-141500-h159i001.md`) and the
producer receipt are preserved and were **not** overwritten or retroactively corrected.

## 1. Normal-speed source-fit loop and boundaries

The v01 `frame_at()` returned frame 3 forever after 1500 ms. The repaired v02 harness uses a real
`elapsed_ms % 1500` cycle over durations `[700, 200, 400, 200]`. It retains the v01 **120 ms** elapsed
tolerance; the 250 ms relaxation used by the v01 Python check is not reused.

Executed 16 explicit boundary checks with independent literal expected constants, not values derived from
the same elapsed calculation as the actual capture frame:

| elapsed ms | expected frame | result |
|---|---:|---:|
| 699 / 700 | 0 / 1 | pass |
| 899 / 900 | 1 / 2 | pass |
| 1299 / 1300 | 2 / 3 | pass |
| 1499 / 1500 / 1501 | 3 / 0 / 0 | pass |
| 2199 / 2200 | 0 / 1 | pass |
| 2699 / 2700 | 2 / 2 | pass |
| 2999 / 3000 / 3001 | 3 / 0 / 0 | pass |

Twelve fresh 640x360 captures remain (city/ruins × EN/ZH × three phases), with target frame indices
`f00` at ~0.10 s, `f02` at ~1.00 s, `f03` at ~1.35 s. These are **source-fit overlay captures only**, not
ordinary actor integration and not acceptance evidence. Loop proof is at the source-fit frame-function
level; no `SpriteFrames`/runtime engine loop is claimed.

Malformed runtime-manifest coverage was executed through the same checked runner: changed duration
(`west[1]=201`) and three-frame direction (`north` truncated) were both rejected by the GDS validator
(2/2, marker `HEYA_I159_IDLE_MALFORMED_REJECTED`). During repair, an incorrect independent constant for
2700 ms (`3` instead of `2`) was caught by the boundary run; that failed run/log/proof is retained under
`outputs/heya-i159/repair2/logs/failed-boundary-constant/`. The corrected `2700 = frame 2` passes.

## 2. Native Pixelorama export gate and cell count

The v01 native checker ignored the export subprocess exit code and timeout when computing its equality
verdict. Repair v02 gates export success explicitly: `exit == 0`, `timeout == false`, and input PXO
unchanged must all hold before `export_gated_verdict_passed` can be true. Image equality, export success,
and diagnostic cleanliness remain separate fields.

Actual v02 result: **48/48 gates pass**, export-gated verdict true, image equality true, all eight split/flat
exports exited successfully with unchanged inputs. The known `custom_samplers` shader diagnostics are
retained verbatim: 8 lines per direction, `diagnostic_clean: false`; they are not hidden or relabelled as a
pass.

**Cell-count correction:** 13 visible roles × 4 frames × 4 directions = **208** per-frame/per-layer cells.
The producer QA's "224" is a false arithmetic claim and is corrected here, not by editing the producer QA.
The v02 report records `cells_exact_total: 208 == cells_expected_total: 208`.

## 3. Lower-body "rows 76..103 frozen" claim

Producer manifests state in `idle_model.planted_feet`: "boots and lower-body rows 76..103 unchanged; no
global sprite bob". The author and independent checks only froze composite rows **90..103**. Measuring the
installed frame bytes against f00 gives:

| direction | rows 76..89 | rows 90..103 |
|---|---|---|
| south | changed f01/f02: 76,78,79,80,82,83,85,87,88,89 | frozen all frames |
| west | changed f01/f02: 76,77,80,81,82,85,87,88,89 | frozen all frames |
| north | changed f01/f02: 76–82,85,87,88,89; f03: 76,77 | frozen all frames |
| east | changed f01/f02: 76,78,79,80,81,82,83,85,87,88,89 | frozen all frames |

**The `76..103` claim is false.** Rows 76..89 do move (because torso groups settle), while sole/lower rows
90..103 remain frozen in all four directions and all frames. No animation was modified and no contract was
weakened to manufacture a pass. No source asset replacement is needed for the 90..103 sole freeze. This
addendum makes no artistic "global bob" adjudication either way.

## 4. Preservation and evidence

- Producer QA, producer receipt, existing v01 tools, `outputs/heya-i159/qa/native-check.stdout.log`,
  `file-list.json` and existing failure logs were preserved untouched.
- The first provider's earlier overwrite/unverified-copy failures are acknowledged as history and are not
  retroactively excused or claimed compliant. This repair cannot restore bytes that were already lost.
- All repair tools are **new versioned files**. Each differing edit made by this repair to its own new tools
  was preceded by a unique metadata-preserving backup whose SHA256 was verified before the edit; receipts
  are in `outputs/heya-i159/repair2/backups/`.
- No `game/assets/` replacement was performed. No `/tmp` scratch was used.
- No shared ledger, Bible, registry, Git index, commit, default or provider/account setting was written.

## Executed repair commands and fresh outputs

```bash
cd /home/kel/projects/worlds-between/repo
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-fit-repair_v02_20261024-141104-h159r002.py
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_native-pixelorama-check-repair_v02_20261024-141104-h159r002.py
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_lower-body-claim-measure_v01_20261024-141104-h159r002.py
```

Expected: `HEYA_I159_IDLE_NORMAL_SPEED_REPAIR PASS`; native `export_gated_verdict_passed: true` with
`diagnostic_clean: false` and `cells_exact_total: 208`; lower-body measurement
`claim_76_103_is_false: true`, `actual_90_103_frozen_all_directions: true`. Exact paths, hashes and
pass/fail detail are in `outputs/heya-i159/repair2/provider-receipt.json`.

## Limits

Source-fit timing/boundary proof only; no engine `SpriteFrames` loop, no ordinary runtime integration, no
GUI SaveAs/reopen, no save/reload, no performance or human playtest. Native diagnostic cleanliness remains
false. The false manifest row claim remains in the preserved producer manifest text and is corrected only
by this addendum. Art/motion/creator approval is not claimed.
