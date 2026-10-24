# Yanke south static — independent coordinator source verdict

Task: content.char.yanke.static-south. Source author and batch96 producer: DeepSeek through the authorized provider adapter. Coordinator: Hermes. Tested base: a376e8fc5ec26ab6ecc9475c0c87b34c1c3b030f. UNAPPROVED, source-only, not adopted by normal game defaults. All hashes below are SHA-256 of raw bytes, no normalization.

## Source-production judgment

The existing native south static meets the technical source-production boundary: 80x112 editable PXO/ORA and PNG; opaque rows8..103; display scale0.5; height48 logical pixels; pivot40,104; declared38-colour palette;12 contributing role layers. It is not the old32x48 placeholder. Source commit is required before the canonical task can be marked done. Commit identity and actual ledger outcome are recorded separately by the batch result; this note is not creator approval.

Protected static PNG: 4f6bcf937390e300e2829ac052bcb1047fdb6387de41561490c757246a32fef0.
Protected PXO: 173779784354c7d2decbc87a0c13edfc2928d70aeabc91772e63d950d0b20992.
Protected ORA: d536eae42395ce5765f6b1f4eb201203ef0c77d44a4285568adf3ed6d2e67267.
Manifest: e57f5c93131daffff56bc75a47d9a2c1357f4c337797ea0d07c0c73918692e7e.

## Independently exercised checks

1. Existing Yanke author `check` with ../tooling/venv/bin/python -X utf8 -I: exit0, YANKE_SOUTH_V01_ALL_OK, deterministic rebuild and installed bytes match, hard failures empty. Log outputs/yanke-s96/hermes-author-check.log, raw hash744bdfb14f597f610d907e7f957d673868af8c5a71c4b6d0da5bdd36cf1b27e5.
2. Existing independent checker with --root . --out outputs/yanke-s96/hermes-independent: exit0,31/31, no failures, including corrupt-hash/tampered-pixel controls and native-layer composition. Proof raw hash972bd7c08b2e78c02d57a2c436f3c255f582df3d305d2f3bb913ee4044e00bdb.
3. Actual Pixelorama1.2.3 PXO CLI export, timeout30, headless, Dummy audio, fresh outputs/yanke-s96/hermes-native directory. Exit0. FFmpeg decoded both candidate and exported PNG into RGBA and hashed pixel bytes; diff of the two SHA-256 result files exited0. Source and native pixel-hash files both raw hash932f662d97d16feea82ed080fafdea6aee185e71d68f04fd40700709230f6f0f. PXO hash unchanged after export. Native export equality PASSES; native application cleanliness FAILS: four sampler/shader-compiler ERROR diagnostics retained in hermes-native-export.log. The producer additionally exercised split PXO layers and ORA export; its full receipt and raw diagnostic logs remain separate evidence, not inferred from process success.
4. Existing source-fit GDScript through the bounded checked runner, Xvfb640x360, Dummy audio, opengl3, timeout45, expected JIANG37_SOURCE_FIT_PASS captures=4. Corrected run exit0, CHECKED_RUN PASS, elapsed3.556seconds; four EN/ZH city/ruins captures, scale0.5, runtimeAdopted=false and artApproved=false. Manifest outputs/yanke-s96/hermes-fit-r2/rpg-2-star-ocean-the-second_yanke_source-fit-manifest_test-only-v01_20261024-090000-b96f0002.json, raw hash94f17215f18950e0fd637041323f5ae298b9fbf076e1db28eb8d3b162c7a4754.
5. Normal game M1 smoke through checked runner, headless and Dummy audio, timeout45, res://tests/m1_smoke.gd: M1_SMOKE_OK, CHECKED_RUN PASS, exit0. Log outputs/yanke-s96/hermes-m1.runner.log, raw hash7f5c828437d97aa9f7e616c9603bbf017f9e7bcfac91d86e9a83ee172cffee2d. This is a targeted smoke, not a full release regression.
6. All33 package/tool/QA/evidence hashes from the final producer receipt verified with sha256sum -c; all OK. Exact list and results: hermes-provider-hashes.sha256 and hermes-provider-hashes-check.log under outputs/yanke-s96. The provider transcript is local provenance and is intentionally not a publication target.

## Visual inspection and gates

Hermes loaded the x6 source preview, cityEN and ruinsZH source-fit images. The sturdy silhouette, cream sleeves, olive apron, dark trousers, beard and notched steel tool read without obvious clipping at the test position. Face detail is small at48 logical pixels; the frontal pose and broad square shoulders remain unapproved artistic choices. This is bounded static inspection, not full-set style acceptance, normal gameplay occlusion/motion validation or a creator review. No normal defaults or other direction were changed. Native application diagnostics remain failed, including the producer's additional ORA import/exit diagnostics. GUI SaveAs/reopen is unverified.

## Retained failures and operational limits

- Coordinator source-fit attempt1 could not save PNG because its output directory had not been created. Checked runner correctly returned FAIL diagnostic, exit-9, missing success marker. Exact error retained in outputs/yanke-s96/hermes-fit.runner.log. Creating a fresh output directory fixed the setup error; no source or criterion was changed.
- A read-only aggregation request through execute_code was rejected before execution: arbitrary local Python is blocked in unattended single-query mode. No bypass was used; normal file reads, jq, existing project checkers and native commands supplied the evidence.
- The producer's original draft failures, incorrect tooling paths and missing-script failure remain preserved in its QA notes and local batch93 outputs. No failure was relabelled as a pass.
- The Bible's latestTaskProgress still belongs to the unrelated in-progress Muxiu east task. Do not finish, replace or fabricate that record to record Yanke progress. Task-local before/after meters and the audited ledger transition remain the truthful record until that shared-record conflict is reconciled.
- Starting canonical meters: production62.0% (content691/1881); inspection21.6%; creator approval7.8%. After values must be read from the canonical ledger after any legitimate task transition. No points for reports, screenshots or validation counts.

Only the existing frozen south-static production task is eligible for completion after its verified source commit. All runtime/full-set/native-application/GUI/human gates remain separate. Unrelated staged files and dirty shared records must be preserved.
