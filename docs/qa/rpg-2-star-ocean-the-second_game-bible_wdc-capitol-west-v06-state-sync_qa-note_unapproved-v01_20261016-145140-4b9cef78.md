# Game Bible: Washington Capitol West walkable v06 state sync (QA note, Task H, UNAPPROVED content)

- **Date:** 2026-10-16 14:51 UTC. **Stamp:** `20261016-145140`. **Id:** `4b9cef78`.
- **Author:** Claude (Claude Code, Opus 5.5), signed-in claude.ai Max, firstParty only. No API key, API billing, credits, auto-reload or paid fallback.
- **Scope:** documentation and tracked-state integration only. The Game Bible state and its builder assertions now describe the Capitol West walkable v06 candidate that was synced in `b12576a`. **No runtime data, scene, script, test, art or acceptance counter changed.** Visual approvals stay at zero: sprites 0/52, science scenes 0/11, human playtests 0/2. M2 stays 9/12.
- **Not touched:** the dirty Game Bible app (`outputs/…game-bible_app_v01_…90e7bc24.js`) and server (`tools/…game-bible_server_v05_…3d5b8a9f.js`), `docs/progress.md`, `game/scripts/battle_arena.gd`, and the character-readiness checklist files.

## Files changed

| path | change |
|---|---|
| `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json` | Washington v06 entry, art-route wording, M2 route-evidence citation; `updatedAt` refreshed by the builder |
| `tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js` | canon checks 25 → 27 (Washington check tightened, two checks added) |
| `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json` | one zero-change meter closeout citing this note: `closeout-20261016-145217-9e4c6562` (35.0% → 35.0%) |
| this note | new |

## Source paths cited

- v06 QA note (with the Task E erratum: 47/47, not 48/48): `docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_qa-note_unapproved-v06_20261016-071733-18b9cea3.md`
- v06 Codex visual audit: `docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-v06-codex-visual-audit_unapproved-v01_20261016-134646-35af3a0d.md`
- M2 route-evidence draft: `docs/qa/rpg-2-star-ocean-the-second_m2-door-to-door-route-figures_public-source-evidence-proposed-calculations_qa-note_m2-v08_20261016-112319-834f6532.md`
- M2 independent audit supplement: `docs/qa/rpg-2-star-ocean-the-second_m2-door-to-door-route-figures_independent-source-audit_qa-supplement_m2-v08a_20261016-085803-b91a5a30.md`
- Sync commit: `b12576a`.

## Exact Bible wording diff

### 1. Visible open question "MVP 美术技术路线" (`openQuestions[].detail`, shown on the site)

Before:

> 华盛顿特区已定为高精度 Pixelorama 场景试点：已有未批准候选（可步行西侧园区 v01–v05、独立的穹顶定场远景 v01–v02），均未接入运行时、未验收；

After:

> 华盛顿特区已定为高精度 Pixelorama 场景试点：已有未批准候选（可步行西侧园区 v01–v06、独立的穹顶定场远景 v01–v02），均未接入运行时、未验收；最新的可步行 v06 为未批准、非运行时候选，技术检查 47/47 通过（勘误后），不是场景验收；

The rest of the paragraph (the Godot 2D plan and the Liangzhu sentence) is unchanged.

### 2. `environmentVisualReview.washingtonDC.unapprovedCandidates`

- `walkable`: `["v01"…"v05"]` → `["v01"…"v06"]`. `cinematic` is unchanged (`v01`, `v02`).
- `status`: `可步行西侧园区 v01–v05` → `可步行西侧园区 v01–v06`. The rest is unchanged, including "highPrecisionPixelSceneAuthored 仍为 false，指尚无可接入或已验收的场景".
- `evidence`: the v06 QA note and the v06 Codex audit are appended after the four existing paths.
- New `latestWalkable` object:
  - `version` `v06`, `runId` `18b9cea3`, `status` `UNAPPROVED / NONRUNTIME`, `technicalGates` `47/47`.
  - `runtimeIntegrated`, `artAccepted` and `sceneApproved` are all `false`.
  - `technicalGatesNote`: 技术检查 47/47 通过（整合复核勘误：原 QA 笔记中的 48/48 为误计，报告与重跑均为 47 项）；技术检查通过不是画面验收
  - `zh` / `en` summary of the Codex audit: the dome is larger and easier to recognize. The West Lawn is compressed, facade and ground patterns repeat, and the patrol machine has no ground contact, so the scene is not yet the requested finished quality. The `.pxo` layers were generated from tables, so this is not a completed hand-painted Pixelorama scene.
  - `qa` and `codexVisualAudit` hold the two paths above.
- Unchanged and still `false`: `washingtonDC.highPrecisionPixelSceneAuthored`, `sceneBriefAuthored`, `runtimeIntegrated`, `artAccepted`.

### 3. `environmentVisualReview.runtimeGeographyMap.routeFigureEvidence` (new)

- `status` `research-only`; `doorToDoorImplemented` `false`; `evidence` holds the m2-v08 and m2-v08a paths.
- `zh`: 门到门路线时长：已有公开来源证据与拟议算法草稿（m2-v08）及独立核对补充（m2-v08a），但尚未写入运行时；运行时仍用 v02 旅行数据中的初步估算。M2 路线数据门仍为"仅初步估算"，M2 仍为 9/12。
- `en`: Door-to-door route times: a public-source evidence and proposed-calculation draft (m2-v08) and an independent audit supplement (m2-v08a) exist, but nothing is implemented in the runtime; the runtime still uses the preliminary estimates in the v02 travel data. The M2 route-data gate stays estimate-only and M2 stays 9/12.

No M2 gate, route figure or travel data file was changed. `m2Expansion` lives in the progress state and was not edited.

## Builder assertions

The guarded reconciliation rules were read first: curated sections are carried from the tracked state, and `checkCanon` must pass before any write. The edits stay inside that model:

- **Washington check (tightened):**
  - walkable must be exactly v01–v06;
  - `status` and the art-route text must say `v01–v06` and must no longer contain `v01–v05`;
  - `washingtonDC.highPrecisionPixelSceneAuthored === false`.
- **New: Washington walkable v06.**
  - `latestWalkable` must be v06, run `18b9cea3`, `UNAPPROVED / NONRUNTIME`, `47/47`, with every acceptance flag false.
  - The gate note must mention 47/47, the 48/48 miscount and "不是画面验收". The art route must mention v06, 47/47 and "不是场景验收".
  - The QA and audit paths must match their exact names, be listed in `evidence` and exist on disk.
- **New: M2 route-figure evidence.**
  - Status must be `research-only` and `doorToDoorImplemented` false.
  - Both evidence files must exist.
  - The zh/en text must say "not implemented" and 9/12.

**Negative probes** (in memory, nothing written):
- The `HEAD` (b12576a) state, which still says v01–v05, is rejected by the Washington check.
- Setting `highPrecisionPixelSceneAuthored` to true is rejected.
- Setting `technicalGates` to `48/48` is rejected by the v06 check.

## Tests (all run 2026-10-16 from the repository root)

| command | result |
|---|---|
| builder `--check` before the edit | contentEqual/bytesEqual true, 25 canon checks |
| builder (write) then `--check` | contentEqual true, bytesEqual true, **27** canon checks, exit 0 |
| `tests/game-bible-builder/…canon-reconciliation_check_m2-v01_…5c2d9e71.js` | RESULT PASS (5 checks) |
| `tests/game-bible-m2-global-travel/…m2-global-travel-gates_check_m2-v01_…06efaa9b.js` | RESULT PASS (5 checks); 9/12 gates, door-to-door 0 |
| `tests/game-bible-environment-candidates/…environment-candidate-cards_check_m8-v01_…c9369925.js` | all PASS, exit 0 |
| `tests/game-bible-environment-candidates/…paving-ab-selout-v8-card_check_m8-v02_…4e7a1c2d.js` | all PASS, exit 0 |
| `tests/mvp-completion-meter/…recompute-and-closeout_check_v01_…af0786b1.js` | RESULT PASS (6 checks) |
| meter `check` | CHECK OK 35.0%; sprites 0/52, scenes 0/11, playtests 0/2 |

The two panel tests that start a server launch the working-tree `game-bible_server_v05`, which carries another session's uncommitted edits. That file was not modified here.

## Not claimed

- No scene approval, no art acceptance, no runtime wiring, and no change to the meter or counters (zero-change closeout).
- `highPrecisionPixelSceneAuthored` stays false.
- Door-to-door figures are not implemented.
- The private cloud tracker was not checked here; root verifies it live.
