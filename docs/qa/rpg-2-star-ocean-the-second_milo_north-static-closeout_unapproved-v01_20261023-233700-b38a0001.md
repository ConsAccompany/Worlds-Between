# Milo north static: Hermes independent source-production verdict (UNAPPROVED)

Canonical task: `content.char.milo.static-north`. Creator batch 38. Tested base: `9c2fc393399db331f15799eea3be5e4e4e9c96b2`. Coordinator and accountable integration owner: Hermes; source authoring: existing Claude adapter production, including the earlier interrupted hand repair. No source art was reauthored in batch 38. The source below is ready for scoped commit; production credit is conditional on that commit. Creator acceptance, normal runtime integration, full character set and motion are not claimed.

## Independent verdict

PASS for the existing production criterion: a north-facing native static at 48 logical pixels, with editable PXO/ORA, deterministic PNG export and this QA record. Source canvas 80x112; opaque body rows 8..103, density 2/display scale 0.5; pivot (40,104). Eleven genuine visible role layers plus hidden guides. The old 32x48 placeholder is not used. The source retains Milo's white-grey short medical coat, navy clothes, silver hair accent, green wristband and square medicine case.

Hermes visually inspected the actual north PNG, x6 source preview, English City Hall Park and Chinese ruins Godot captures. Back-facing head has no face; case/silver accent are screen-right and wristband screen-left. The repaired left hand is slightly inward from the wristband, but remains joined and readable as a relaxed hand against the coat; no severed limb or lost identity was observed. This is a bounded technical source judgment, not creator art acceptance or a claim of final style quality. Static-overlay captures are explicitly test-only; they are not normal actor integration, motion or dark-scene evidence.

## Source hashes

All hashes are SHA-256 of exact raw file bytes, with no text or line-ending normalization. Prefix: `game/assets/characters/milo-native-v01/north/`.

| Filename | SHA-256 |
| --- | --- |
| rpg-2-star-ocean-the-second_milo_north-static_unapproved-v01_20261023-225642-5968ba0c.png | cf1e559885f2a87c31a3c6cf9feee953d95c8c1ca138ecd9bd8d6838bee8da61 |
| rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-7f054cac.pxo | 9d9004e65b032f68e06a0b064cf623c7996cdd7c679ef36d7c8a37ab0108baee |
| rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-af5a9058.ora | a7a691f63f3c776293cc6fede97b1895c7f48a961c3825a9d6368a1a426895cf |
| rpg-2-star-ocean-the-second_milo_north-palette_unapproved-v01_20261023-225642-a3a9c89f.json | e837c5f76ad17caa7d2b9c269cec261c4813dc2238d6297514ae3d3aaf02554d |
| rpg-2-star-ocean-the-second_milo_north-manifest_unapproved-v01_20261023-225642-163cf811.json | 0cb2b25f115117795dbc2788e9a2f448218c0899b8f2fc9929154ddb324402b1 |

Author: `tools/rpg-2-star-ocean-the-second_milo_north-static-author_unapproved-v01_20261023-225642-1b612f93.py`, hash `8453d78278e10accaff3b9a13a72203f87d58562d6d00b82dde502a4dd93dff4`.
Independent checker: matching `milo_north-static-source-check` tool, hash `96d7aac23180bf5d1627bd2c02af050a32a134cbb69c5008ef427c0a1b88e2bf`. This is byte-identical to the checker from the failed run; no threshold was weakened.

## Hermes reruns

From repository root, `O=outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-qa-orchestrate_v01_20261023-225642-1b612f93.py`.

- `python3 -I $O check hermes38-check`: inner rc0, `MILO_NORTH_V01_ALL_OK`; deterministic rebuild, disk matches all five files; no hard failures.
- `python3 -I $O source hermes38-source`: inner rc0, `MILO_N01_INDEPENDENT 41 / 41`, `FAILURES []`. Negative controls reject south, mirrored south, mirrored north, corrupt hashes, tampered PNG, visible guides and tampered south manifest.
- `python3 -I $O pixelorama hermes38-pxl`: both exports rc0, source files unchanged. Application diagnostics FAIL separately below.
- `python3 -I $O compare hermes38-compare hermes38-pxl`: inner rc0, `MILO_NORTH_PXL_EXPORT_PIXEL_EXACT`; zero differing texels for PXO and ORA. Both emitted PNG raw hashes `6b48418d2a0bb3a612018287093165ac77aa585b8b432d273ca173575902a985`.
- `python3 -I $O fit hermes38-fit`: bounded checked Godot runner with Dummy audio, Xvfb and OpenGL3; `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS`, exit0. No SCRIPT_ERROR, Parse Error or ERROR marker; one V-Sync warning.
- `python3 -I outputs/milo-n01/scratch/milo_north_batch34_repair_diag.py`: rc0; all nine original backup entries match exact size/hash. Retained log: `outputs/milo-n01/logs/hermes38-repair/repair.log`.

Logs and source-bound summaries: `outputs/milo-n01/logs/hermes38-{check,source,pxl,compare,fit}/`. Hermes parsed all five summaries, verified every inner result is zero, sourceRevision is the tested base, and every pinsBefore/pinsAfter entry remains equal to the actual file hash. North, south, unfinished west and reused tools remain unchanged by all checks. The orchestrator's process exit alone was not used as evidence.

## Retained failures and limitations

Original `outputs/milo-n01/logs/source1/independent/` proof remains false with only `north_case_screen_right` failing (40/41). Exact proof hash: `fedc94d589bb6529d36155252d4a07717e3d4d0ad40737051fef5074f39edd6c`. Original checkpoint and package are retained in `outputs/milo-n01/backup-pre-hand-repair_v01_20261023-repair1/`. The repair moves the screen-left hand inward without changing checker thresholds. Actual final composed-image change is 43 texels, x21..27, rows62..69 (including outline effects); not merely the seven hand rows. Off-side opaque texels in the case region change 14 to 0; the right-side case remains 140. The original failing artifact was not overwritten in the backup.

Pixelorama application-clean gate remains FAILED despite exact exports: PXO has four shader-compiler errors; ORA has eleven ERROR lines and one warning (four shader errors, three get_child errors, null rp_node, ancestor-control error, twelve leaked Dummy texture RIDs, sixteen resources still in use and 160 leaked ObjectDB instances). Exact source production is distinct from application diagnostic/GUI reliability. No new GUI SaveAs/reopen check was performed for this north source. No diagnostics were suppressed or thresholds relaxed.

Adapter invocation `provider-1.result.json` reports Claude firstParty execution with `classification: permission_denied` and confirmed scope cleanup, despite provider exit0. Its denied shell commands are not treated as successful checks. The provider retried allowed forms for its check/source/export/fit steps, and Hermes separately reran all required checks and the previously denied read-only backup diagnostic. No provider/account policy was modified and no DeepSeek fallback was used. The adapter receipt is operational evidence only, never game completion proof.

Routine CLI discovery also returned `unknown command --help` for the ledger tool and a usage error for the progress recorder; both were read-only. Their source was read to obtain supported commands. No build or test failure is hidden by those later successful commands.

## Boundaries and next action

Only north source production is eligible for existing two-point credit after source commit. No default, runtime, animation, south/west art or creator gate change. Inspection and approval meters remain unchanged. Batch-start canonical meters were production 61.1%, inspection 21.6%, approval 7.8%; final measured values are recorded through the canonical ledger and Bible CLIs at integration.

The pre-existing west progress record is preserved as paused, not falsely completed; west remains canonical todo and all unfinished files remain protected. Next useful existing task after north closeout: resume `content.char.milo.static-west`. Do not reopen cosmetic north refinements or mark a full sprite set accepted.
