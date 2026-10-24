# Heya EAST walk — bounded followup repair receipt (UNAPPROVED)

- Task: `content.char.heya.walk-east` (batch 176, run `h176ew01`).
- This receipt is new and write-once. It does **not** replace `PROVIDER-RECEIPT.md`, `provider-receipt.json`, `coordinator/author-check.log`, the old hash-suffixed check report, or any original report.
- Status: source-production repair only. **No canonical completion, commit, staged-byte verification, ledger/Bible/registry/index edit, runtime adoption, inspection/approval credit, or art/motion approval is claimed.** Coordinator still owns source commit and canonical status.
- Scope: `content.char.heya.walk-east` only. No repaint, no palette change, no threshold change, no new provider launch, no file deletion.

## Addendum — prior-session compliance failures (not retroactively cured)

These are recorded as prior-session failures. This repair's new pre-edit backups are **prospective only** and do **not** establish retroactive compliance.

1. **Backup-before-edit was not performed for the author/checker/fit tools in the prior session.** This repair created unique `shutil.copy2` backups before editing, but that cannot restore the missing pre-edit history of the earlier session.
2. **The prior session overwrote the original M1 runner log** (`outputs/heya-ew176/m1-smoke.runner.log`). The current 217-byte file is a later log; the original pre-overwrite bytes are not available here. The preserved prior tool history shows a `FileExistsError` when the checked runner tried to open that path with mode `x`, consistent with the reported overwrite/removal attempt. No M1 rerun is claimed as new evidence.
3. **The prior session deleted pre-VAR output trees after only a tar listing, not per-file extraction verification.** The two tar backups remain, but this receipt makes **no per-file verification claim** for those deletions. **No further deletion was performed by this repair.**
4. Prior tool-call commands/results were available locally at `outputs/heya-ew176/coordinator/provider177-tool-history.jsonl` (tool calls/results only; no private account information) and were preserved by `copy2` at `outputs/heya-ew176/backups/priorlogs-20261024-153505-841c259b/`. The original failure log `outputs/heya-ew176/coordinator/author-check.log` was also preserved there.

## 1. Author report collision — root cause and fix

The old code chose the primary report path, and if it existed appended a content hash. If **both** the primary and that hash-suffixed path existed (the coordinator failure), the unconditional `open(..., "xb")` at line 406 raised `FileExistsError` after printing `RESULT PASS`.

Fix: the report writer now retries with fresh, unique names, using `open(..., "xb")` and catching `FileExistsError`. It writes the primary name if free, then `-<contenthash8>.json`, then `-<contenthash8>-2.json`, etc. No existing report is overwritten.

Proof in fresh staging `outputs/heya-ew176/staging-r3/` (three consecutive `check` runs, same stage):

| Run | Result | Report written |
| --- | --- | --- |
| 1 | `REBUILD 91/91 DETERMINISTIC True`, `SOURCE 21/21`, `RESULT PASS []`, exit 0 | `...-check_unapproved-h176ew01-v01_20261024-154500-109a9863.json` |
| 2 | same PASS, exit 0 | `...-109a9863-d1ce3abb.json` |
| 3 | same PASS, exit 0 (collision path exercised) | `...-109a9863-d1ce3abb-2.json` |

Logs: `outputs/heya-ew176/coordinator/followup-check-r3-run1.log`, `...run2.log`, `...run3.log`.
The exact original failure is retained at `outputs/heya-ew176/coordinator/author-check.log` (sha256 `10209a9e2973b72835127008dc0595bae3aacba9c4df7badc2065957fd5332e8`): `RESULT PASS []` followed by `FileExistsError` at line 406.

## 2. East-specific metadata corrections

All four are metadata/label/comment-only; no asset bytes or thresholds changed.

| Location | Before | After |
| --- | --- | --- |
| `render_side` sign comment | `east = -1 (forward is screen left)` | `east = +1 (forward is screen right)` — matches `J.side_sign("east") == 1` |
| Manifest identity | `dark-red emergency bag + brass clasps on the near (left) hip` | `... on the far (anatomical-left) hip` — east shows the anatomical-left bag on the far side |
| Manifest `source_inputs.static_qa` | `outputs/heya-w150/author/check.log (HEYA_EAST_V01_ALL_OK)` (west log; fabricated east marker) | `outputs/heya-e155/author-check.log (HEYA_EAST_V01_ALL_OK)` — actual east dependency QA observed on disk |
| Near-boot source-check label | `near boots cel excludes far-only columns (x < 37)` | `near boots cel excludes far-only columns (x < 38)` — matches `NEAR_MIN_X = 38` |

## 3. Edited tool and exact final hashes

Text normalization: `sha256_text_lf_v1` = SHA-256 after CRLF→LF and lone CR→LF. For the edited author, raw and text-normalized hashes are identical (`d643...`). PNG/PXO/ORA/JSON are raw byte hashes.

| Artifact | sha256 (raw) | sha256_text_lf_v1 |
| --- | --- | --- |
| `tools/rpg-2-star-ocean-the-second_heya_walk-east-source-author_unapproved-hew176-v01_20261024-154500-h176ew01.py` | `d64394cb750e2eca7e2f3417823cb974c309739170c1ab6a5d37390a061a878e` | `d64394cb750e2eca7e2f3417823cb974c309739170c1ab6a5d37390a061a878e` |
| `tools/rpg-2-star-ocean-the-second_heya_walk-east-independent-check_v01_20261024-154500-h176ew01.py` (unchanged) | `83eaa9129c3857242697231627681ebd98f77de7bea67cc9a1caf6d948ca8727` | `83eaa9129c3857242697231627681ebd98f77de7bea67cc9a1caf6d948ca8727` |
| `tools/rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-fit_v01_20261024-154500-h176ew01.py` (unchanged) | `9498ed3e9253bfeead276fd9b637819c7d8928e5786e5a39c4424d736ecbde58` | `9498ed3e9253bfeead276fd9b637819c7d8928e5786e5a39c4424d736ecbde58` |
| `tools/rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-fit_test-only-v01_20261024-154500-h176ew01.gd` (unchanged) | `9eece6e8807d9f33a562c8d6219306025580eb96d12e42000b329bbd26dbf3c4` | `9eece6e8807d9f33a562c8d6219306025580eb96d12e42000b329bbd26dbf3c4` |

Final source/manifest metadata (installed):

| Artifact | sha256 (raw) |
| --- | --- |
| `outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-source-manifest_unapproved-h176ew01-v01_20261024-154500-537dec83.json` | `816bcfdb2aacb93d0a3503abcaf012d32fbfda5c64a471225b5591b9f006c367` |
| `outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-file-list_unapproved-h176ew01-v01_20261024-154500-d27681ce.json` | `7df67fc4660adaa65c883fcaf1393f4a2c095d077d20b93ff12169c86ebe425c` |
| `outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-check-result-build_unapproved-h176ew01-v01_20261024-154500-54687ffd.json` | `53c9f29b1e38fb866be387e8ac720a40708d4258cc32fde1ec310ae2ce50eb40` |
| `outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-h176ew01-v01_20261024-154500-109a9863.json` | `53c9f29b1e38fb866be387e8ac720a40708d4258cc32fde1ec310ae2ce50eb40` |
| Old hash-suffixed report, preserved untouched: `...109a9863-1a430276.json` | `e67293c694d073331a60ab7faca358743dbb525dd4cd04aee7f14ccfae412322` |

The final manifest's author pin is `d64394cb750e2eca7e2f3417823cb974c309739170c1ab6a5d37390a061a878e` and equals the actual edited tool hash. The final file-list contains 90 entries; all 90 raw hashes were reverified against disk with **0 mismatches**, including the manifest hash `816bcf...`.

New staged check reports (fresh stage, all PASS, identical bytes):

| Path | sha256 |
| --- | --- |
| `outputs/heya-ew176/staging-r3/outputs/heya-ew176/rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-h176ew01-v01_20261024-154500-109a9863.json` | `53c9f29b1e38fb866be387e8ac720a40708d4258cc32fde1ec310ae2ce50eb40` |
| `.../rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-h176ew01-v01_20261024-154500-109a9863-d1ce3abb.json` | `53c9f29b1e38fb866be387e8ac720a40708d4258cc32fde1ec310ae2ce50eb40` |
| `.../rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-h176ew01-v01_20261024-154500-109a9863-d1ce3abb-2.json` | `53c9f29b1e38fb866be387e8ac720a40708d4258cc32fde1ec310ae2ce50eb40` |

## 4. Independent, native and fit evidence

- Independent checker: **PASS 36/36**, all 15 negative controls rejected. Report `outputs/heya-ew176/independent-4/rpg-2-star-ocean-the-second_heya_walk-east-independent-result_v01_20261024-154500-h176ew01.json` sha256 `a9855edd281cfa00fb9e3addf2d1e5f5275f74128b8cc2edaae6b9c934d4554b`; log `outputs/heya-ew176/coordinator/followup-independent-4.log` sha256 `17f85009410a4556efba5f7cf6064755cea0e9ef93d8982f06fed1c05a17a548`.
- Native Pixelorama export: **41/41 frames RGBA-exact**, exit 0, no timeout, source unchanged. Retained separate application diagnostics: **4 `custom_samplers` shader diagnostics**; this is not an export-equality failure and GUI SaveAs/reopen remains UNVERIFIED.
- Contact sheet `...independent-4/...contact-sheet...png` sha256 `9439af6318d12519f31a7c46926de788368d5eac5b4f576786e7a2e141ce1e43`; source-bound preview GIF sha256 `e2a061533ef591b7bd1cca7ff439c08f85e3d0e57909fd5edd0f2df91c057567`; native log sha256 `43bfdee782aede6af5cbc7195f50b687148b2373618987aeca8d17f38d77d535`.
- Fit: fit code was **not touched** (`9498...` / `9eece...` above) and was **not rerun**. Reference only: `outputs/heya-ew176/coordinator/fit.log` sha256 `2ae2782736fc766c936e29a621f1d380116cc6f6b5df357e7a642caa2f6e22b1`, 12 captures under `outputs/heya-ew176/fit/capture-r2/`, test-only.
- Final package bytes (unchanged): sprite-set runtime `171cd4843d257862f2a1826934c047c5d3dba9e84921ca1347a70e9643c8df9b`; registry `602eff9cee56167682ef799906946c152a849018f648550f86f09d88e64caed3`; stop supplemental `b40f725fb67010b642520841e1538b3d203148d9bc4f73362c074803709da04c`.

**Timing disclosure (must not be conflated):** the source supplemental stop contract is release `t0` = walk entry phase `p`, then `40 ms` = s1, `80 ms` = s2, `120 ms` (inclusive) = idle f00 held. The test-only Godot overlay uses `STOP_MS=800`, `WALK_MS=40`, i.e. s1 at `800 ms`, s2 at `840 ms`, idle at `880 ms` (`REV_MS=1420`). The overlay is a **test harness timeline only**; it is **not** evidence that the overlay tested the source stop timing. The independent checker tested the source supplemental boundaries separately (`0→p`, `40→s1`, `80→s2`, `120→idle`).

## 5. Backups (unique, hash-verified)

Unique `shutil.copy2` backups under `outputs/heya-ew176/backups/` (mode and mtime preserved and verified; raw sha256 source == backup):

| Backup directory | Files / sha256 |
| --- | --- |
| `preedit-20261024-153307-0649ea9d/` (receipt `3649d5ca7b24f8c91713473f67d24fa11f73c14640e74560b53e4a6c2c4faf30`) | author old `9f11b70d382c529cb9a3ebbecc9f8e246ba53b4e1dbae5df87e33257d0f2e20a`; checker `83eaa9129c3857242697231627681ebd98f77de7bea67cc9a1caf6d948ca8727`; fit py `9498ed3e9253bfeead276fd9b637819c7d8928e5786e5a39c4424d736ecbde58`; fit gd `9eece6e8807d9f33a562c8d6219306025580eb96d12e42000b329bbd26dbf3c4` |
| `postfix1-20261024-153325-b1a76610/` (receipt `d352f118d87a696caae104b87b3aea75ef8005288737ffeebf16351d917c6e3d`) | edited author `d64394cb750e2eca7e2f3417823cb974c309739170c1ab6a5d37390a061a878e` |
| `priorlogs-20261024-153505-841c259b/` (receipt `ebfb9d7826de4fd5104ff168fd746bd1a395a48e482947755b0f419dd69326a5`) | prior tool history `0a7260536616810608af00ee9613c7a5a95882ffb9c7f6710c148e21d32f7ae5`; original failure log `10209a9e2973b72835127008dc0595bae3aacba9c4df7badc2065957fd5332e8` |

Safe-helper pre-replacement backups under `outputs/development-backups/` (each `original` was hash-verified by the helper before replacement):

| Backup | Before → after |
| --- | --- |
| `d12526370199437198ed3be935e5a621/original` | `f46220dea0b4f403641e81eeab32f0a99b1c8bef3ff8b7bec4a55c6d85544d43` → `816bcfdb2aacb93d0a3503abcaf012d32fbfda5c64a471225b5591b9f006c367` (manifest) |
| `360c7e9e4ad44e5fa2e4ec4b182aff35/original` | `5ca31b86242e37d34f8af27f646a6e47058f941cd008e9835f97df9680fe268a` → `7df67fc4660adaa65c883fcaf1393f4a2c095d077d20b93ff12169c86ebe425c` (file-list) |
| `a219885a0b854a76a90093b79e64f3e6/original` | `e67293c694d073331a60ab7faca358743dbb525dd4cd04aee7f14ccfae412322` → `53c9f29b1e38fb866be387e8ac720a40708d4258cc32fde1ec310ae2ce50eb40` (build result) |
| `f2ec40d9ff1a48a8b2827cfea230c855/original` | `1b39aa708167497397b24235860681f2e2622dc7e1a860cf904a5668013f309a` → `53c9f29b1e38fb866be387e8ac720a40708d4258cc32fde1ec310ae2ce50eb40` (old primary check result) |

Only these four differing metadata destinations were installed. All 41 frame PNGs, PXO/ORA, and package bytes are byte-identical between fresh stage and installed tree; the two new staged check reports were left in staging and were **not** installed as new final files. The old hash-suffixed check report `...1a430276.json` was not rewritten.

## 6. Commands run

All from `/home/kel/projects/worlds-between/repo`.

- Pre-edit backups: unique `shutil.copy2` + receipt generation (author, checker, fit py, fit gd).
- Compile: `/home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I -m py_compile tools/rpg-2-star-ocean-the-second_heya_walk-east-source-author_unapproved-hew176-v01_20261024-154500-h176ew01.py`
- Fresh build: `WB_STAGE_REL=outputs/heya-ew176/staging-r3 /home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-east-source-author_unapproved-hew176-v01_20261024-154500-h176ew01.py build`
- Check ×3: same command with `check` (logs `followup-check-r3-run1..3.log`).
- Safe replacements: `python3 tools/wb_safe_replace.py outputs/heya-ew176/staging-r3/outputs/heya-ew176/<file> outputs/heya-ew176/<file>` for the four metadata files (log `followup-safe-replace.log`).
- Independent: `PIXELORAMA=/home/kel/projects/worlds-between/tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64 /home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-east-independent-check_v01_20261024-154500-h176ew01.py --out outputs/heya-ew176/independent-4`
- Fit: not rerun; reference `outputs/heya-ew176/coordinator/fit.log`.

## 7. Results and retained failures

- Author build: `WROTE 91 files`, `REBUILD 91/91 DETERMINISTIC True`, `SOURCE 21/21`, `RESULT PASS []`, exit 0.
- Author check ×3: `REBUILD 91/91 DETERMINISTIC True`, `SOURCE 21/21`, `RESULT PASS []`, exit 0, unique fresh reports each time.
- Independent: `PASS 36/36`; negative controls `15/15` rejected; native `41/41` RGBA-exact; application diagnostics retained as a separate failure (`4 custom_samplers`).
- Fit reference: coordinator-verified `HEYA_HEW176_EAST_WALK_NORMAL_SPEED_FIT PASS`, 12 captures; not rerun, code untouched.
- Retained original failure: the FileExistsError collision in `coordinator/author-check.log` (exact path/hash above). No new build/check/independent failure occurred in this repair.
- Retained stale original: `...check...-1a430276.json` still contains the old tool hash and the old `x < 37` label. It is an original report and was intentionally not rewritten; the new reports and final manifest carry `x < 38`.
- Prior M1 log overwrite and pre-VAR deletion verification gap are disclosed in the addendum; not cured, not claimed as compliant.

## 8. Not claimed

No repaint, no threshold/acceptance change, no palette change, no committed source, no staged-byte verification, no ledger/Bible/registry/index change, no runtime/default adoption, no canonical task completion, no inspection/approval credit, no human art or motion approval, no normal-host integration, no Godot GUI SaveAs/reopen verification, no new provider launch, no deletion. The Godot fit is a test-only overlay and its `800/840/880` timeline is **not** the source supplemental `0/40/80/120` timeline.

Integrity: this file is write-once; its SHA-256 is recorded in the adjacent `.sha256` sidecar, created after this file.
