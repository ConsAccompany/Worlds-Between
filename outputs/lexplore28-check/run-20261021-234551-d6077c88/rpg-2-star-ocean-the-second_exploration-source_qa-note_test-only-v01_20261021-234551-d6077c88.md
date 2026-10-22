# Exploration source negative-contract check - short QA note

- Run tag: `20261021-234551-d6077c88`
- Checker: `tools/rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py`
- Checker SHA-256: `46d528ecaac00f67d630fa50b92bcc5910ffa704fec61b87d0a8fc1e6d77a8ba`
- Manifest: `outputs/zexplore25/rpg-2-star-ocean-the-second_zhao-ling_explore-source-manifest_unapproved-zexplore25-v01_20261021-172651-d473cf67.json`
- Manifest SHA-256: `e6c596384b6cb1e83e2685de2d15f696a504538ce5961fe28d0f99529cef1473`
- Python: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` (3.12.14)
- Timeout per checker run: 120.0 s

## Safety guard

- Referenced real assets: 176 (176 present, 0 missing).
- Aggregate SHA-256 before: `a2e3d1a5fd40c2189004143641677448fe439788a303cff15bdb4af0a92d2fdc`
- Aggregate SHA-256 after: `a2e3d1a5fd40c2189004143641677448fe439788a303cff15bdb4af0a92d2fdc`
- Real referenced assets unchanged: **True**.
- Fixture cleanup verified under marker-checked temp roots: **True**.
- Long-path probe: ok (path length 404, readBack=True, removed=True).

## Actual checker runs

| Case | Expected | Exit | Timed out | Classification | Passed |
|---|---|---:|---|---|---|
| positive-zexplore25 | accept | 0 | False | accepted | True |
| negative-altered-png-hash | refuse | 1 | False | refused-diagnostic | True |
| negative-missing-direction | refuse | 1 | False | refused-diagnostic | True |
| negative-truncated-pxo | refuse | 1 | False | refused-exception | True |
| negative-altered-ora-merged | refuse | 1 | False | refused-diagnostic | True |

## Case detail

### positive-zexplore25

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\zexplore25\rpg-2-star-ocean-the-second_zhao-ling_explore-source-manifest_unapproved-zexplore25-v01_20261021-172651-d473cf67.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\positive-native`
- Exit: `0`; elapsed: 0.734 s
- Checker proof: passed=True; checks=2676; failed=0
- NATIVE_BANK: `NATIVE_BANK True 2676 outputs/lexplore28-check/run-20261021-234551-d6077c88/positive-native/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-234552-389c9ba1.json`
- Fixture files copied: None; cleanup removed: None
- Full stdout/stderr preserved in the result JSON (201 / 0 chars).

### negative-altered-png-hash

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-altered-png-hash-0264c1f2\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-altered-png-hash-0264c1f2\checker-out`
- Exit: `1`; elapsed: 0.719 s
- Checker proof: passed=False; checks=2676; failed=1
- NATIVE_BANK: `NATIVE_BANK False 2676 outputs/lexplore28-check/run-20261021-234551-d6077c88/fixtures/negative-altered-png-hash-0264c1f2/checker-out/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-234553-a5f8e3ae.json`
- Diagnostic: `FAIL file hash C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-altered-png-hash-0264c1f2\files\0002.png`
- Mutation: `{"type": "altered-png-bytes-hash", "entry": "directions.south.idle[1]", "targetOriginal": "outputs/zexplore25/png/rpg-2-star-ocean-the-second_zhao-ling_explore-south-idle-f01_unapproved-zexplore25-v01_20261021-172651-dbde1daf.png", "bytesBefore": 2529, "bytesAfter": 2530, "originalSha256": "b7c877ca95dc4416e7faac8163a730fcb6a9ca80a90f81c7a08c8a4c453ddfbf", "mutatedSha256": "30528dd0c57e8cd7d455b17633e776e122150ed04ee0da9deeeb1db4deca7136", "declaredSha256Updated": false, "declaredSha256": "b7c877ca95dc4416e7faac8163a730fcb6a9ca80a90f81c7a08c8a4c453ddfbf"}`
- Fixture files copied: 172; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (464 / 0 chars).

### negative-missing-direction

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-missing-direction-ac7599e6\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-missing-direction-ac7599e6\checker-out`
- Exit: `1`; elapsed: 0.593 s
- Checker proof: passed=False; checks=1956; failed=1
- NATIVE_BANK: `NATIVE_BANK False 1956 outputs/lexplore28-check/run-20261021-234551-d6077c88/fixtures/negative-missing-direction-ac7599e6/checker-out/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-234554-f6e7af84.json`
- Diagnostic: `FAIL exactly four directions`
- Mutation: `{"type": "missing-direction", "removedDirection": "west", "remainingDirections": ["east", "north", "south"], "removedDirectionFileReferences": 43}`
- Fixture files copied: 172; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (272 / 0 chars).

### negative-truncated-pxo

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-truncated-pxo-8a183147\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-truncated-pxo-8a183147\checker-out`
- Exit: `1`; elapsed: 0.344 s
- Checker proof: passed=None; checks=None; failed=0
- Exception: `zipfile.BadZipFile: File is not a zip file`
- Mutation: `{"type": "truncated-pxo-archive", "entry": "directions.south.pxo", "targetOriginal": "outputs/zexplore25/rpg-2-star-ocean-the-second_zhao-ling_explore-south-editable_unapproved-zexplore25-v01_20261021-172651-1b6bd4da.pxo", "bytesBefore": 278104, "bytesAfter": 64, "originalSha256": "0b26020aaf7aaeb3adb0eb4896fb850689f16be00312fc22d0d4442617a37a3a", "mutatedSha256": "394c71f9fe44cb15d83b68b08b8e10480eeac514439a210755d2d956a5508b4e", "declaredSha256Updated": true}`
- Fixture files copied: 172; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (0 / 1035 chars).

### negative-altered-ora-merged

- Command: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -I C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\tools\rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-altered-ora-merged-a75fb882\manifest.json --out-dir C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle28\ds-lcheck\outputs\lexplore28-check\run-20261021-234551-d6077c88\fixtures\negative-altered-ora-merged-a75fb882\checker-out`
- Exit: `1`; elapsed: 0.719 s
- Checker proof: passed=False; checks=2676; failed=1
- NATIVE_BANK: `NATIVE_BANK False 2676 outputs/lexplore28-check/run-20261021-234551-d6077c88/fixtures/negative-altered-ora-merged-a75fb882/checker-out/rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_20261021-234556-01a818f0.json`
- Diagnostic: `FAIL ORA merged export exact south`
- Mutation: `{"type": "altered-ora-merged-composite", "entry": "directions.south.ora", "targetOriginal": "outputs/zexplore25/rpg-2-star-ocean-the-second_zhao-ling_explore-south-static-layers_unapproved-zexplore25-v01_20261021-172651-e9b4ba17.ora", "bytesBefore": 11789, "bytesAfter": 9341, "originalSha256": "7f1a621d36f00291e3f2a62453e88e77718fbe73ea600aa399e2cb8732cb6e8d", "mutatedSha256": "9fa67f4823aa2fded3c2bfdcace3bf91d4f47baac06f6606641c580862928ae6", "originalMergedSha256": "069acee4ba3c25c55cd381e19ab3a7453bb9ddd7fe27ff69eca7068c038859f7", "mutatedMergedSha256": "0277e2dcbcf6affeb75c388fbac4851911a42ea8afb267d7451fdec031893ce1", "stackXmlUnchanged": true, "mergedCompositeChanged": true, "declaredSha256Updated": true}`
- Fixture files copied: 172; cleanup removed: True
- Full stdout/stderr preserved in the result JSON (279 / 0 chars).

## Concrete checker blind spots observed

- `source_inputs` and `exact_source` provenance references are never opened or hash-checked by the checker. A manifest can cite missing or wrong source PNG/ORA files and still pass the direction-bank checks.
- Archive parse errors are uncaught. A truncated PXO exits nonzero with a traceback and writes no proof JSON; a consumer must treat that as refusal and must not require a result file.
- The checker validates the four-direction set and per-frame geometry, but does not schema-validate bank lengths, `duration_ms`, `walk_model`, or that `stop_bridges` has exactly one key per walk phase. Missing/extra keys can crash or go unchecked.

## Scope and limitations

- Positive fixture: existing `zexplore25` manifest. This proves that bank satisfies this checker; it is not art acceptance.
- Liang Xu exploration source package: **not checked**. No Liang Xu exploration source manifest/package was present at run time, so no Liang acceptance claim is made.
- No art generation, runtime integration, accounts, ledger, Git index/commit, or default changes. No true-fluidity or art-acceptance inference.
- Overall harness result: **True**.
