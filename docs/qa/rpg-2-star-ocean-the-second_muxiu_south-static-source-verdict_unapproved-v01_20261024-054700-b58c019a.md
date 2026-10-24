# Muxiu south static — independently verified source production, UNAPPROVED

Task: `content.char.muxiu.static-south`. Producer Claude; independent coordinator Hermes. Tested base `2531ad4aa12f1235ada844c273eea8aacea804ba`. Recorded 2026-10-24 UTC. All SHA-256 values are raw bytes, without text normalization. This note accompanies the source commit; the ledger may close only after the committed source is verified.

## Source criterion

The new native static is not the legacy 32x48 placeholder. It has an 80x112 canvas, opaque body rows 8..103 (96 source pixels), pivot (40,104), and display scale 0.5: 48 logical pixels. It includes an authored PNG, editable layered PXO and ORA, palette and manifest. Thirteen visible functional layers plus hidden guides, 33 used colors, binary alpha, clear borders. No other direction, animation, runtime default or creator approval is delivered.

Identity reference is the existing UNAPPROVED Muxiu portrait, SHA-256 `9d80d2d7fc26ea10edd36948e620fbb5a5557db143eacb99fcb202347c22d606`, and Bible character-06: 24-year-old animal carer, moss-green short cloak, knotted rope bracelet, small whistle, braid. Direction is the approved Sea of Stars style contract, not acceptance of this sprite. Original native pixels reuse the existing Lin/Jiang/male serializers and gates, not a rescaled portrait or recolored prior character. Differences from Jiang/Lin/Milo alpha silhouettes are 799/813/629 source texels. The placeholder exclusion check finds no matching Muxiu file in its legacy search directory; that absence is disclosed, not independent evidence of quality.

## Independently exercised checks

From the repository:

1. `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_muxiu_south-static-author_unapproved-v01_20261024-071500-6d3e9a51.py check` — rc0, `MUXIU_SOUTH_V01_ALL_OK`, deterministic in-memory rebuild and all five on-disk files match. Hard failures empty. Exact coordinator stdout retained locally at `/home/kel/projects/worlds-between/autonomy/attempts/58/independent-author-check.log`; producer check logs also retained in `outputs/muxiu-s01/logs/check1/` and `check2/`.
2. `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_muxiu_static-source-check_v01_20261024-071500-6d3e9a51.py --root . --out outputs/muxiu-s01/hermes58-source` — rc0, 31/31, failures empty. Does not import the Muxiu author; verifies PXO/ORA compositing, native sizes, logical height, palette, hashes, visible anchor roles and negative controls. Corrupt manifest hash, visible guides and altered PNG are detected. Whistle/bracelet/braid contributions are nonzero and above their existing thresholds.
3. Existing Muxiu orchestration `pixelorama hermes58-pxl`, then `compare hermes58-compare hermes58-pxl` — inspect inner logs, not wrapper exit. Both native export processes rc0, both RGBA outputs exactly equal the authored PNG, both native sources unchanged. Export file encoding differs from authored PNG, so equality is pixel equality, not PNG raw-byte equality.
4. Same orchestration `fit hermes58-fit` — existing generic scene-fit script, Xvfb, Dummy audio, checked runner deadline110s. Inner rc0, `JIANG37_SOURCE_FIT_PASS captures=4`, checked runner PASS, no script/parser diagnostics. Four separate test-only 640x360 logical captures, EN/ZH city and ruins; no project display/default edits. The ruins plate is daylight, not proof of low-light/night readability.
5. Existing checked runner `--timeout 60 --expect M1_SMOKE_OK --log outputs/muxiu-s01/hermes58-source/m1-smoke.runner.log -- ../tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64 --headless --audio-driver Dummy --path game --script res://tests/m1_smoke.gd` — rc0, `M1_SMOKE_OK`, checked runner PASS. No gameplay scripts or defaults changed.

Independent source proof: `outputs/muxiu-s01/hermes58-source/rpg-2-star-ocean-the-second_muxiu_independent-source-proof_v01_20261024-071500-6d3e9a51.json`, SHA-256 `4dcca0f6a116a96a0e9d3ace84f17470c27090e64e68101258db90d58d491661`.

## Visual observation — not creator approval

Hermes loaded the portrait, enlarged final sprite, actual city EN and actual ruins ZH fit captures through native image input. Muxiu is visible as the labeled test-only figure, not the normal playable actor. Moss cloak, dark long braid at screen left, smile, cream chest whistle and small wrist bracelet are visible in the enlarged source. Cloak silhouette and head read at gameplay size, but tiny rope/whistle detail is not independently legible there. The pose is square and stiff, with straight arms, a broad geometric cape and frontal face. These are retained artistic limitations, not a claim of stylistic or motion approval. Nothing is animated. No visual-review ledger task or human gate is closed.

## Genuine failed checks and limitations

- Draft preview1: rc1, 38 isolated texels exceeds the unchanged limit24. Draft preview2: rc1, opaque row7 violates required rows8..103. Source repairs, not threshold changes, yield final18 isolated texels and correct rows. Both failed logs remain under `outputs/muxiu-s01/logs/preview1/` and `preview2/`.
- EVIDENCE RETENTION INCIDENT: both failed drafts reused preview filename ending `319b5233.png` with different bytes, without a verified backup before replacement. The first original bitmap is not retained or claimed recovered. Failure logs and original source writes/edits survive in the hashed local provider transcript. The surviving reused bitmap and final content-named preview are preserved. This violates the backup-before-replacement rule; source credit does not waive it. No invented reconstruction is substituted for missing original bytes. Future changed-output builds must stage fresh and use the approved replacement helper.
- Pixelorama application-clean FAIL remains: four shader compiler diagnostics for PXO and ORA; ORA also emits child-index/control errors and resource/ObjectDB/RID shutdown leaks. Native exact pixel export passes separately; GUI save/reopen and application cleanliness are not established.
- Provider job `467cdb57e9c545adb4982ee45b974b7b` ended rc1, classification `max_turns`, not normal success. Scope confirmed. Provider attempt59 belongs to coordinator attempt58. Actual stdout/stderr paths, raw log hashes, denial IDs and evidence incident are recorded in `outputs/muxiu-s01/rpg-2-star-ocean-the-second_muxiu_provider-checkpoint_v01_20261024-054700-b58c019a.json`. Exact denied compound Bash commands and responses remain verbatim in that retained stdout. No claim that overwrite consent was missing; these were real tool gates. Independent coordinator checks above establish only the delivered source boundary.
- Coordinator `execute_code` metadata-export attempt was blocked before any tool call in unattended mode. It was not rerun through another interpreter, and no approval configuration was changed. Explicit normal file tools preserve this checkpoint instead.
- Native production defaults, paused Milo west, other dirty work, frozen scores/criteria and creator acceptance remain protected. These files are not an adopted runtime set. Reused raw source hashes refer to this Linux checkout and staged/committed bytes; no guarantee is made for a future checkout with different line-ending filters.

## Raw source hashes

Under `game/assets/characters/muxiu-native-v01/south/`:

- `rpg-2-star-ocean-the-second_muxiu_south-static_unapproved-v01_20261024-071500-ca23fad5.png`: `e14d5c50890d7fcd0c75eb362d2b08fd1d4ac02c9c33e04fc4861b5a7d7a26fe`
- `rpg-2-star-ocean-the-second_muxiu_south-edit_unapproved-v01_20261024-071500-dc8dff45.pxo`: `43e789d80314869a2ef2104057b4ce91b35d558e31c49beef743720bc78b6344`
- `rpg-2-star-ocean-the-second_muxiu_south-edit_unapproved-v01_20261024-071500-21a68f1e.ora`: `62807d582e2de8f79adee3783f9896e0051f4013cc9f7e9741044fa34696e8e2`
- `rpg-2-star-ocean-the-second_muxiu_south-palette_unapproved-v01_20261024-071500-96bc917c.json`: `aaf0a695c43240b8e6ac87b2aee942be1312af761650a3faf19215d843f5c195`
- `rpg-2-star-ocean-the-second_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json`: `24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de`

Author SHA-256 `f329ac7aa595f003ba741ed8de6cf5aade1d912acfa65a1720ce731eb24737f1`; independent checker `fe3da3aa328beb68d70c82700ed8ddb0900923081eeee64ce32004d478e84aa1`.

## Closure

Production before61.6%, inspection21.6%, approval7.8%. Final canonical values are recorded by the existing progress CLI after source commit and audited ledger transition. No approval/inspection score changes are authorized. Operational batch remains partial because of the provider turn limit and lost first draft preview, even if the independently verified, committed source criterion closes. Next action: preserve this evidence incident, use fresh staging for any future replacement, then take only the next explicitly assigned unpaused task; do not automatically start other Muxiu directions or resume Milo west.
