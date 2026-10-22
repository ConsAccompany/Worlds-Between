# Exploration source negative-contract check - short QA note

- Run tag: `20261021-235656-a3556a24`
- Checker: `tools/rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py`
- Checker SHA-256: `46d528ecaac00f67d630fa50b92bcc5910ffa704fec61b87d0a8fc1e6d77a8ba`
- Manifest: `outputs/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-source-manifest_unapproved-lexplore28-v01_20261021-194350-2ceb83e8.json`
- Manifest SHA-256: `6198eafca26c0d76e4a636d953eccab0a8ea4e628c9e734c77fe05535094bdc2`
- Python: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` (3.12.14)
- Timeout per checker run: 40.0 s

## Safety guard

- Referenced real assets: 177 (177 present, 0 missing).
- Aggregate SHA-256 before: `bc1a2fadaf37be8c0762e9983cc3f86779e61ee9c1bcbfb3b5c4a381b605e311`
- Aggregate SHA-256 after: `bc1a2fadaf37be8c0762e9983cc3f86779e61ee9c1bcbfb3b5c4a381b605e311`
- Real referenced assets unchanged: **True**.
- Fixture cleanup verified under marker-checked temp roots: **True**.
- Long-path probe: ok (path length 405, readBack=True, removed=True).

## Actual checker runs

| Case | Expected | Exit | Timed out | Classification | Passed |
|---|---|---:|---|---|---|
| positive-liang-xu | accept | 0 | False | accepted | True |
| negative-altered-png-hash | refuse | 1 | False | refused-diagnostic | True |
| negative-missing-direction | refuse | 1 | False | refused-diagnostic | True |
| negative-truncated-pxo | refuse | 1 | False | refused-exception | True |
| negative-altered-ora-merged | refuse | 1 | False | refused-diagnostic | True |

## Case detail

### positive-liang-xu

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28\rpg-2-star-ocean-the-second_liang-xu_explore-source-manifest_unapproved-lexplore28-v01_20261021-194350-2ceb83e8.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\positive-native`
- Exit: `0`; elapsed: 0.625 s
- Checker proof: passed=True; checks=2430; failed=0
- NATIVE_BANK: `NATIVE_BANK True 2430 outputs/lexplore28-check/run-20261021-235656-a3556a24/positive-native/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-235656-9283770b.json`
- Fixture files copied: None; cleanup removed: None
- Full stdout/stderr preserved in the result JSON (201 / 0 chars).

### negative-altered-png-hash

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-altered-png-hash-98397a93\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-altered-png-hash-98397a93\checker-out`
- Exit: `1`; elapsed: 0.609 s
- Checker proof: passed=False; checks=2430; failed=1
- NATIVE_BANK: `NATIVE_BANK False 2430 outputs/lexplore28-check/run-20261021-235656-a3556a24/fixtures/negative-altered-png-hash-98397a93/checker-out/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-235657-6d8ab22b.json`
- Diagnostic: `FAIL file hash C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-altered-png-hash-98397a93\files\0003.png`
- Mutation: `{"type": "altered-png-bytes-hash", "entry": "directions.south.idle[1]", "targetOriginal": "outputs/lexplore28/png/rpg-2-star-ocean-the-second_liang-xu_explore-south-idle-f01_unapproved-lexplore28-v01_20261021-194350-a079d6fb.png", "bytesBefore": 2588, "bytesAfter": 2589, "originalSha256": "a93302bacf724324697e2af9d4d8fd4b3c46289777f349952cb17b58a0579fec", "mutatedSha256": "505d7a5a4673f6f96753f8fb3951119ca5307cc966a642599fd4f3535a4f8c92", "declaredSha256Updated": false, "declaredSha256": "a93302bacf724324697e2af9d4d8fd4b3c46289777f349952cb17b58a0579fec"}`
- Fixture files copied: 173; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (465 / 0 chars).

### negative-missing-direction

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-missing-direction-7497c877\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-missing-direction-7497c877\checker-out`
- Exit: `1`; elapsed: 0.531 s
- Checker proof: passed=False; checks=1792; failed=1
- NATIVE_BANK: `NATIVE_BANK False 1792 outputs/lexplore28-check/run-20261021-235656-a3556a24/fixtures/negative-missing-direction-7497c877/checker-out/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-235658-98999edb.json`
- Diagnostic: `FAIL exactly four directions`
- Mutation: `{"type": "missing-direction", "removedDirection": "west", "remainingDirections": ["east", "north", "south"], "removedDirectionFileReferences": 43}`
- Fixture files copied: 173; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (272 / 0 chars).

### negative-truncated-pxo

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-truncated-pxo-154fdd85\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-truncated-pxo-154fdd85\checker-out`
- Exit: `1`; elapsed: 0.296 s
- Checker proof: passed=None; checks=None; failed=0
- Exception: `zipfile.BadZipFile: File is not a zip file`
- Mutation: `{"type": "truncated-pxo-archive", "entry": "directions.south.pxo", "targetOriginal": "outputs/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-south-editable_unapproved-lexplore28-v01_20261021-194350-634ecc3f.pxo", "bytesBefore": 254464, "bytesAfter": 64, "originalSha256": "b89c23200659aae2a2b5fb88a4f17227da372cc0a23a42a2933ee321bd5b892c", "mutatedSha256": "03409df6bb90e9b80faf4547276c48be14c77e981b90eb661121aabbf0dabfc0", "declaredSha256Updated": true}`
- Fixture files copied: 173; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (0 / 1037 chars).

### negative-altered-ora-merged

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-altered-ora-merged-4a48ac38\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\lexplore28-check\run-20261021-235656-a3556a24\fixtures\negative-altered-ora-merged-4a48ac38\checker-out`
- Exit: `1`; elapsed: 0.625 s
- Checker proof: passed=False; checks=2430; failed=1
- NATIVE_BANK: `NATIVE_BANK False 2430 outputs/lexplore28-check/run-20261021-235656-a3556a24/fixtures/negative-altered-ora-merged-4a48ac38/checker-out/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-235700-7a505d40.json`
- Diagnostic: `FAIL ORA merged export exact south`
- Mutation: `{"type": "altered-ora-merged-composite", "entry": "directions.south.ora", "targetOriginal": "outputs/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-south-static-layers_unapproved-lexplore28-v01_20261021-194350-00af5516.ora", "bytesBefore": 11751, "bytesAfter": 9246, "originalSha256": "13dbf076f9df2a5b03509714556dc8662295105c5be8cdd30494aee836d32867", "mutatedSha256": "0b6ea2f5f8f6159724f504d11ddf2ff1249c88da1b476d546eb47d62913855c5", "originalMergedSha256": "9fee901809d33128839779cc1e926fc314f4d92fd11baa3b857d4cffebfe38ab", "mutatedMergedSha256": "0277e2dcbcf6affeb75c388fbac4851911a42ea8afb267d7451fdec031893ce1", "stackXmlUnchanged": true, "mergedCompositeChanged": true, "declaredSha256Updated": true}`
- Fixture files copied: 173; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (279 / 0 chars).

## Concrete checker blind spots observed

- `source_inputs` and `exact_source` provenance references are never opened or hash-checked by the checker. A manifest can cite missing or wrong source PNG/ORA files and still pass the direction-bank checks.
- Archive parse errors are uncaught. A truncated PXO exits nonzero with a traceback and writes no proof JSON; a consumer must treat that as refusal and must not require a result file.
- The checker validates the four-direction set and per-frame geometry, but does not schema-validate bank lengths, `duration_ms`, `walk_model`, or that `stop_bridges` has exactly one key per walk phase. Missing/extra keys can crash or go unchecked.

## Scope and limitations

- Positive fixture: the selected manifest recorded above. Passing proves only the checked native-bank contract; it is not art acceptance.
- Selected actor: `liang-xu`. Liang source checked: `True`. No artistic acceptance claim.
- No art generation, runtime integration, accounts, ledger, Git index/commit, or default changes. No true-fluidity or art-acceptance inference.
- Overall harness result: **True**.
