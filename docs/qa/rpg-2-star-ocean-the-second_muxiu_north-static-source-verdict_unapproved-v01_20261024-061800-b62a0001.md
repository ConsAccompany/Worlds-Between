# Muxiu north static — independently verified source, UNAPPROVED

Canonical task: `content.char.muxiu.static-north`. Claude authored through durable adapter job `d70f6325eefe402fb61ac0634832c36f`; Hermes independently checked and integrates. Tested base `322f88f37d16f737c57d42be2c3ae5c6a69239c5`. Recorded 2026-10-24 UTC. SHA-256 means raw bytes with no normalization. Filename stamp `080000` is the producer's label, not the actual execution time.

## Production boundary

New north/back static, not the old32x48 placeholder:80x112 source, opaque rows8..103, pivot40,104, scale0.5 =48 logical pixels. Editable layered PXO/ORA plus PNG, palette and manifest.27 colours,13 contributing visible roles and hidden guides. Existing Muxiu south/west identity and palette are pinned and unchanged. Native serializers and gates reuse the established Lin/Jiang/male/Muxiu pipeline; this is not a new pipeline. Source-only production credit requires this package and QA to be committed. No motion, east source, UI/default wiring, GUI reliability, human playtest or art approval is delivered.

Final author: `tools/rpg-2-star-ocean-the-second_muxiu_north-static-author_unapproved-v01r2_20261024-080000-4e7d2c19.py`.
Checker: `tools/rpg-2-star-ocean-the-second_muxiu_north-static-source-check_v01_20261024-080000-4e7d2c19.py`.
Producer QA: `docs/qa/rpg-2-star-ocean-the-second_muxiu_north-static-source-qa_unapproved-v01_20261024-080000-4e7d2c19.md`. Its source pass is not an application-clean verdict; the application failures below qualify the producer's summary.

## Independent checks

Commands ran from repo with parent tooling Python and UTF-8. Exact argv, exit statuses and logs: `outputs/muxiu-n01/hermes62-source/commands.json`.

- Final author `check`: rc0, `MUXIU_NORTH_V01R2_ALL_OK`, empty hard failures, two deterministic in-memory builds and all five installed files exact.
- Separate north checker `--root . --out outputs/muxiu-n01/hermes62-source/proof`: rc0,28/28. North/back predicates pass; south, mirrored south, squashed south, west, mirrored west and mirrored north are rejected. This checker imports no author. Its limited package checks were supplemented independently rather than treated as exhaustive.
- Coordinator structure verification:14/14, including actual ORA layer composition (not merely mergedimage), PXO layer composition,13 genuine role contributions, north anchors, hidden guides, corrupted-hash and modified-pixel negative controls. All5187 protected baseline files remain byte-exact. Four bilingual640x360 logical capture files exist. Proof: `outputs/muxiu-n01/hermes62-source/rpg-2-star-ocean-the-second_muxiu_north-coordinator-structure-proof_v01_20261024-061800-b62a0001.json`, SHA256 `a0b1aec5b641d232683e08326051d59d122149da475fc1488f776658215ca723`.
- Existing v03 orchestration `pixelorama hermes62-pxl`, then `compare hermes62-compare hermes62-pxl`: inner native processes rc0, source unchanged; both exports80x112 and exact authored RGBA. Encoded PNG bytes differ; equality is pixels, not raw PNG hashes. Application-clean FAIL separately below.
- Same orchestration `fit hermes62-fit`: existing generic test-only fit script, Xvfb, Dummy audio, checked runner110s deadline. Inner rc0, `JIANG37_SOURCE_FIT_PASS captures=4`, checked PASS, no script/parser/runtime ERROR markers. EN/ZH city and ruins captures are four separate images. They are overlays, not normal Muxiu actor adoption or night/low-light proof.
- Checked Godot runner with60s deadline, Dummy audio, `res://tests/m1_smoke.gd`: rc0, `M1_SMOKE_OK`, checked PASS. Log: `outputs/muxiu-n01/hermes62-source/m1-smoke.runner.log`.

The existing south eye gate becomes the reused north no-eyes/no-mouth rule. North anchor checks retain12 visible texels for appropriate roles; front-worn whistle body is intentionally invisible, with only its cord visible behind. The all-role-nonempty and isolated-texel<=24 gates remain unchanged; final18 isolated texels. These orientation rules do not supply artistic acceptance.

## Visual observation, not approval

Hermes loaded the original identity sheet, final enlarged source and actual EN city/ZH ruins captures through native image input. The static is recognizably back-facing, with brown hair mass, broad green capelet, cream motifs, left wrist band and boot backs. The pose is rigid and symmetric. Enlarged, the braid crossing the right shoulder is a stepped dark stripe rather than clearly readable plait; the cape's central cream motif is very geometric. At actual48px the green cape and back-facing head read, but braid/bracelet detail does not remain independently clear, and the colours blend with foliage/stone. The test sprite is distinct from the normal heroine. The portrait's rear braid hangs centrally down the back; this source instead takes the braid forward over the right shoulder to match existing south/west. That documented deviation is not creator-approved. No visual-review task closes.

## Retained failures and operational concerns

- Draft failed all-role-nonempty (empty whistle layer) and isolated-texel limit28>24. Revision1 failed25>24. Both source tools/previews/logs remain. Revision2 fixes the pixels without changing the24 limit.
- Preinstall revision2 preview/stage rc1 and FAIL markers are preserved: hard failures empty, but its result calculation also required not-yet-installed game files. Installation/check subsequently pass; earlier failures are not erased.
- Pixelorama application-clean FAIL: four shader compiler diagnostics per native format. ORA also reports child-index/null/control errors, ObjectDB/resource and RID leaks on shutdown. Exact native export remains PASS. GUI SaveAs/reopen is unverified for this package. No claim that all native checks passed.
- Adapter finished rc0, outcome `exited`, classification `permission_denied`, scope confirmed. The terminal provider record says success/completed; neither aggregate result proves game-task completion. Exact result and raw local transcript hashes are retained in the checkpoint below.
- Exact denied Bash commands and actual error responses are preserved in the checkpoint: variable/compound discovery and orchestration commands, direct diagnostic invocation and `cp` with/without flags. These were technical gates, not absent creator replacement consent. The provider retried the denied diagnostic under system `python3`; it failed missing NumPy. That different-interpreter retry is an operational compliance concern, not proof of honoring the no-workaround rule. The coordinator did not repeat it or change permissions/settings. Originals remained intact; new separately named revisions were retained. No existing asset bytes were replaced, so no safe-replace receipt was needed.
- Coordinator's initial unsupported `progress-task_record --help` and begin missing Chinese title failed; corrected begin succeeded. No failed command is counted as verification.

Checkpoint: `outputs/muxiu-n01/rpg-2-star-ocean-the-second_muxiu_north-provider-checkpoint_unapproved-v01_20261024-061800-b62a0001.json`, SHA256 `338708f66ed96d0c63c46df1f6cde09552fdaf5d40c6209047c9f58cd2fe8601`.

## Source hashes

Under `game/assets/characters/muxiu-native-v01/north/`:

- PNG ending `f1f63759.png`: `03062ace22b7e83aacf8d02b6b0d715e6ff0d4ef74c71770ff7fb8aeb96e5bbe`
- PXO ending `4b1f2dd1.pxo`: `e3152eee03091ec05b4114446a3a6a05fb75c3c65e45783d6f87c58a2ad3f95c`
- ORA ending `bbe8ce6f.ora`: `8c9c990eb80151597e51249ff70560bbfa11d2cd839b64502bcd310f3a09d4e4`
- Palette ending `b950d628.json`: `834805c28e3d19f45ee7d60d6ea645290d0f6d8f8006d48b6d2e68d6b823be34`
- Manifest ending `d1f8693c.json`: `089c18947c03eea607a3213fb326fdc97abe46555175546622e124ec1878b542`

## Closure

Starting canonical production61.7%, inspection21.6%, creator approval7.8%. Final measured before/after values are recorded by the existing Bible CLI after the verified source commit and audited north-only ledger transition. Frozen scoring and all human/default gates remain unchanged. Operational verdict is partial because genuine permission-gate concerns and native application failures remain; this does not erase a separately committed source-production boundary. Next only the next explicitly assigned unpaused task; no automatic east/motion work or resumption of paused work.
