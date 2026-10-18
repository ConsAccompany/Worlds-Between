#!/usr/bin/env node
// Worlds Between production-completion task ledger: the one updater and checker for the work-done metric.
// "Production completion / 制作完成度" = CODING 40% + CONTENT 60%, from frozen task points. Inspection (technical checks,
// Codex visual review, content/audio QA) and creator approval are separate meters with their own queues; neither one can add
// or remove production credit. Waived reviews are shown separately and are neither performed work nor part of a denominator.
// Operations (dashboard inspection and publication) are listed with owners but excluded from every percentage.
// Release / final MVP acceptance stays false until the existing gates (approvalLedger + M9) pass.
// The legacy 40.8% meter in the progress state is read only and shown as a separate, legacy mixed delivery/acceptance estimate.
// Run from the repository root:
//   node tools/<this file> init --now <ISO>          build the frozen baseline once (refuses to overwrite)
//   node tools/<this file> check                     validate, recompute in memory, compare with the stored ledger
//   node tools/<this file> recompute                 rewrite the derived meters (idempotent)
//   node tools/<this file> set --task <id> --status <s> [--evidence <repo path>]... [--outcome <o>] [--waived-by <id>]
//        [--note-en ".."] [--note-zh ".."] [--now <ISO>]
//   node tools/<this file> revise --for <production task id> --reason-en ".." [--reason-zh ".."] [--now <ISO>]
//        opens (or reopens) the ONE fixed revision bucket of a deliverable; points are fixed, never chosen
//   node tools/<this file> summary | queue | list [--owner o] [--stage s] [--status s] [--area a]
// Options for every command: --ledger <path> (tests work on a copy), --dry-run.
'use strict';
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

const ROOT = path.resolve(__dirname, '..');
const LEDGER_REL = 'outputs/rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json';
const PROGRESS_REL = 'outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json';
const INVENTORY_REL = 'outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json';
const REGISTRY_REL = 'game/data/character-visuals/rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json';
const CHECKLIST_REL = 'game/data/character-visuals/rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json';
const BRIEF_REL = 'docs/rpg-2-star-ocean-the-second_production-completion_bilingual-brief_v01_20261018-140533-3ea2a621.md';
const LEDGER_ID = 'rpg-2-star-ocean-the-second_production-completion_v01';

const STAGES = {
  'coding': {kind: 'production', zh: '编码', en: 'Coding'},
  'content': {kind: 'production', zh: '内容制作', en: 'Content'},
  'technical-inspection': {kind: 'inspection', zh: '技术检查', en: 'Technical inspection'},
  'visual-review': {kind: 'inspection', zh: '视觉审查', en: 'Visual review'},
  'content-qa': {kind: 'inspection', zh: '内容／音频质量检查', en: 'Content / audio QA'},
  'creator-approval': {kind: 'approval', zh: '创作者批准', en: 'Creator approval'},
  'operations': {kind: 'operations', zh: '运营（看板检查与发布，不计入百分比）', en: 'Operations (dashboard inspection and publication; no percentage)'},
};
// Owners follow the task type, not the stage: Codex generated the source portraits with image generation, Claude authors
// native Pixelorama content and code, Codex reviews in the browser and publishes, the creator accepts and decides canon.
const TASK_TYPES = {
  'feature-code': {stage: 'coding', owner: 'claude'},
  'pipeline-code': {stage: 'coding', owner: 'claude'},
  'concept-generation': {stage: 'content', owner: 'codex'},
  'native-pixel': {stage: 'content', owner: 'claude'},
  'integration': {stage: 'content', owner: 'claude'},
  'content-writing': {stage: 'content', owner: 'claude'},
  'audio-production': {stage: 'content', owner: 'claude'},
  'revision': {stage: null, owner: null}, // same stage and owner as the deliverable it revises
  'technical-check': {stage: 'technical-inspection', owner: 'claude'},
  'visual-review': {stage: 'visual-review', owner: 'codex'},
  'audio-qa': {stage: 'content-qa', owner: 'codex'},
  'creator-acceptance': {stage: 'creator-approval', owner: 'creator'},
  'canon-choice': {stage: 'creator-approval', owner: 'creator'},
  'playtest': {stage: 'creator-approval', owner: 'creator'},
  'ops-inspection': {stage: 'operations', owner: 'codex'},
  'ops-publication': {stage: 'operations', owner: 'codex'},
};
const DEFAULT_TYPE = {coding: 'feature-code', content: 'native-pixel', 'technical-inspection': 'technical-check', 'visual-review': 'visual-review', 'creator-approval': 'creator-acceptance'};
const OWNERS = {claude: {zh: 'Claude（原生 Pixelorama 内容、编码、测试、技术文档、整合）', en: 'Claude (native Pixelorama content, coding, tests, technical writing, integration)'},
  codex: {zh: 'Codex（图像生成的设定图、视觉／浏览器检查、内容质量检查、云端发布）', en: 'Codex (image-generated source portraits, visual / browser inspection, content QA, cloud publication)'},
  creator: {zh: '创作者（美术验收、正典选择、两轮真人试玩）', en: 'Creator (art acceptance, canon choices, the two human playthroughs)'}};
const STATUSES = {
  production: ['todo', 'in_progress', 'done', 'blocked'],
  inspection: ['todo', 'in_progress', 'done', 'not_required', 'blocked'],
  approval: ['todo', 'done', 'changes_requested', 'blocked'],
  operations: ['todo', 'in_progress', 'done', 'blocked'],
};
const OUTCOMES = ['passed', 'technical-pass', 'changes_requested'];
const WEIGHTS = {coding: 40, content: 60};
const ID_PATTERN = /^(code|content|qa|review|creator|ops)\.[a-z0-9]+(?:[.-][a-z0-9]+)*$/;
const POINT_RANGE = [1, 21];
const revisionPoints = points => Math.ceil(points / 2);
// Old 32x48 placeholders were rejected; their files can never be evidence for a production milestone.
const REJECTED_BASELINE_PATTERN = /\/(native-prototypes|native-animation|combat-prototypes)\/|_m8-prototype_|native-idle-(south|west|north|east)_m8-v01_/;
const isProduction = t => STAGES[t.stage]?.kind === 'production';
const isInspection = t => STAGES[t.stage]?.kind === 'inspection';

const QA = name => 'docs/qa/rpg-2-star-ocean-the-second_' + name;
const EV = {
  sentryV2: QA('scifi-sentry-automaton_v2-optin-portability_qa-note_unapproved-v01_20261018-103500-7d2e91b4.md'),
  sentryPilot: QA('scifi-sentry-automaton_battle-sprite-pilot_qa-note_m8-v01_20261014-221953-96ac4035.md'),
  sentryAnimV2: QA('scifi-sentry-automaton_battle-animation-pilot_qa-note_m8-anim-v02_20261014-231549-748c6de8.md'),
  femaleV8: 'docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md',
  femaleV8Qa: QA('protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md'),
  femaleNorth: QA('protagonist-female_north-idle-static-pilot_qa-note_unapproved-nonruntime-v01_20261018-090713-4bcb9cdb.md'),
  femaleRunV07: QA('protagonist-female_south-run-v07_repress-rise-lock-control-correction_qa-note_unapproved-nonruntime_20261018-085800-a589f0f3.md'),
  femaleBattleV14: QA('protagonist-female_battle-static-v14-cloth-volume-leg-anatomy_qa-note_unapproved-v01_20261018-084553-dda2c05f.md'),
  femaleBattleV11Feedback: QA('protagonist-female_battle-static-v11-creator-feedback-and-v12-visual-target_unapproved-v01_20261017-193755-c7a93e12.md'),
  maleV8pair: QA('protagonist-male_south-idle-v8pair-static-pilot_qa-note_unapproved-v01_20261018-130225-3fad02c7.md'),
  liang: QA('liang-xu_south-idle-static-pilot_48px-identity-qa-note_unapproved-v01_20261016-140940-d01e679f.md'),
  liangCodex: QA('liang-xu_south-idle-static-pilot-codex-visual-audit_unapproved-v01_20261016-145125-76c4ab13.md'),
  ji: QA('ji-cheng_south-idle-static-pilot_qa-note_unapproved-v01_20261018-132812-23499262.md'),
  zhao: QA('zhao-ling_south-idle-static-pilot_48px-identity-qa-note_unapproved-v01_20261018-052006-27b43b74.md'),
  mapV03: QA('global-map_native-art-pass_qa-note_unapproved-v03_20261017-175314-e8b8f8af.md'),
  mapV01: QA('global-map-art_northeast-and-globe-candidate_qa-note_candidate-unapproved-v01_20261016-164615-f9e453b0.md'),
  mapInset: QA('global-map_route-inset-runtime-integration_qa-note_unapproved-v01_20261016-205301-5a17c3e9.md'),
  mapV03r1Codex: QA('global-map_v03r1-codex-native-visual-judgment_unapproved-v01_20261017-194711-66d8a7b4.md'),
  mapV03r2: QA('global-map_v03r2-bounded-visual-gate_qa-note_unapproved-v03r2_20261017-224631-9875b9e2.md'),
  sceneAudit: QA('scifi-region-eleven-scene_visual-gate-audit_m8-v01_20261014-201003-6b73e7a4.md'),
  cityRuntime: 'outputs/rpg-2-star-ocean-the-second_scifi-city_navigation-manifest_m8-boundaries_20261014-063728-a19da10f.json',
  chpV04: QA('nyc-city-hall-park_walkable-pilot-640x360_qa-note_unapproved-v04_20261016-172144-eb092a52.md'),
  chpV04Reject: QA('nyc-city-hall-park_style-alignment-visual-direction_unapproved-v01_20261016-225800-2a4e7c91.md'),
  chpV06: QA('nyc-city-hall-park_scene-candidate-640x360_qa-note_unapproved-v06_20261017-165253-4519dffe.md'),
  wdcV12: QA('wdc-capitol-west_actual-viewport-integration_qa-note_unapproved-v12_20261017-235608-66d00477.md'),
  wdcV12r2: QA('wdc-capitol-west_sentry-encounter-viewport_qa-note_unapproved-v12r2_20261018-042200-7c1e5b39.md'),
  wdcV13: QA('wdc-capitol-west_ruin-material-collapse_qa-note_unapproved-v13_20261018-100938-075675cf.md'),
  wdcV13Flag: QA('wdc-capitol-west_v13-flag-integration_qa-note_unapproved-v13_20261018-135539-63201688.md'),
  femaleRunV10r1: QA('female-south-run-v10r1_reach-landing-amendment_qa-note_unapproved-nonruntime_20261018-142136-249dbf66.md'),
  femaleRunV10r1Receipt: 'outputs/rpg-2-star-ocean-the-second_city-annex_female-south-run-v10r1-capture-receipt-h48_unapproved_20261018-182800-9ee66cb8.json',
  wdcV13Det: QA('wdc-capitol-west_v13-flag-deterministic-check_qa-note_unapproved-v13_20261018-141558-22d034ba.md'),
  wdcV13DetReport: 'outputs/wdc-cw-v13flagdet_20261018-141558-22d034ba/rpg-2-star-ocean-the-second_wdc-capitol-west_deterministic-check-report_unapproved-v13_20261018-141558-22d034ba.json',
  nycR1: QA('nyc-public-facilities-room1_three-fixture-native-scene-visual-qa_unapproved-v01_20261017-011800-43d5b92f.md'),
  nycR1Accept: QA('nyc-public-facilities-room1_scene-visual-acceptance_v01_20261017-013027-3e7d91c4.md'),
  nycR2: QA('nyc-public-facilities-room2_three-fixture-native-scene-visual-qa_unapproved-v01_20261017-010600-4a81e9d2.md'),
  nycR2Accept: QA('nyc-public-facilities-room2_scene-visual-acceptance_v01_20261017-010900-8f4a2c6e.md'),
  yR1V01: QA('yonkers-antenna-corridor-room1_three-antenna-fixture-native-scene-visual-qa_unapproved-v01_20261017-025000-8e41c7b2.md'),
  yR1V03: QA('yonkers-antenna-corridor-room1_v03-outdoor-refinement-candidate_qa-note_unapproved-v03_20261017-224447-15709be4.md'),
  yR1V06: QA('yonkers-antenna-corridor-room1_v06-outdoor-readability-refinement_qa-note_unapproved-v06_20261018-084726-c8f0d900.md'),
  yR1Default: 'game/scripts/survey_annex.gd',
  yR2: QA('yonkers-maintenance-room2_four-fixture-native-scene-visual-qa_unapproved-v01_20261017-012000-14f2b0c9.md'),
  yR2Accept: QA('yonkers-maintenance-room2_scene-visual-acceptance_v01_20261017-013504-6a0c92d1.md'),
  wdcR1: QA('wdc-annex-room1_capitol-interior-v02-quality-pass_qa-note_unapproved-v02_20261017-160235-f1e4f2a0.md'),
  wdcR1Manifest: 'outputs/wdc-sr1-v02_71300729/rpg-2-star-ocean-the-second_wdc-annex-room1_scene-and-fixtures-manifest_unapproved-v02_20261017-160235-71300729.json',
  wdcR2: QA('wdc-annex-room2_records-chamber-playable-integration_qa-note_unapproved-v01_20261018-035908-3a34d132.md'),
  wdcR2Fix: QA('wdc-annex-rooms_default-layout-collision-fix_qa-note_unapproved-v01_20261018-041322-c3ff819c.md'),
  chiV02: QA('chicago-loop_state-lake-arrival-block-native-scene_qa-note_unapproved-v02_20261017-160959-6bcff07f.md'),
  chiV03r1: QA('chicago-loop_state-lake-arrival-block-native-scene_qa-note_unapproved-v03r1_20261017-184340-49dde4dd.md'),
  m7Smoke: 'game/tests/m7_smoke.gd',
  audioLoopCity: 'game/assets/audio/rpg-2-star-ocean-the-second_scifi-city_ambient-loop_m7_20261013-211230-c8e1159a.wav',
  audioLoopBattle: 'game/assets/audio/rpg-2-star-ocean-the-second_scifi-battle_ambient-loop_m7_20261013-211230-37fcaa02.wav',
  audioCue: 'game/assets/audio/rpg-2-star-ocean-the-second_discovery_interaction-cue_m7_20261013-211230-ad781e52.wav',
  progress: PROGRESS_REL,
  inventory: INVENTORY_REL,
};

// Baseline credits (2026-10-18). Only tracked evidence may complete a task; anything not listed here starts as todo.
// `at` records when the verdict or delivery happened (used to decide whether a requested change is still unanswered).
// Statuses that came from the progress state's own fields (steps, m2 gates, M7 meter gates, ledger items, inventory checks)
// are derived in buildTasks; this table holds the per-asset milestones that those fields do not record.
const CREDITS = {
  'code.runtime.enemy-sprite-pipeline': {status: 'done', evidence: [EV.sentryV2, 'game/scripts/battle_arena.gd']},
  'content.char.protagonist-female.static-south': {status: 'done', evidence: [EV.femaleV8, EV.femaleV8Qa]},
  'content.char.protagonist-female.static-north': {status: 'done', evidence: [EV.femaleNorth]},
  // The delivered, committed v07 south run (1942e31, closeout 20587ab6) is the initial south locomotion milestone; the
  // creator's run/stop polish request is its fixed revision bucket below, not a reason to withhold the initial credit.
  'content.char.protagonist-female.walk-south': {status: 'done', at: '2026-10-18T10:00:57Z', evidence: [EV.femaleRunV07, EV.progress],
    note: {zh: 'v07 南向跑动已提交（1942e31，closeout 20587ab6），单一方向、未接入、未批准。', en: 'v07 south run committed (1942e31, closeout 20587ab6): single direction, nonruntime, unapproved.'}},
  'content.char.protagonist-male.static-south': {status: 'done', evidence: [EV.maleV8pair]},
  'content.char.liang-xu.static-south': {status: 'done', evidence: [EV.liang]},
  'content.char.ji-cheng.static-south': {status: 'done', evidence: [EV.ji]},
  'content.char.zhao-ling.static-south': {status: 'done', evidence: [EV.zhao]},
  'review.char.liang-xu.static-south': {status: 'done', outcome: 'changes_requested', at: '2026-10-16T14:51:25Z', evidence: [EV.liangCodex]},
  'review.char.protagonist-male.static-south': {status: 'done', outcome: 'technical-pass', at: '2026-10-18T13:02:25Z', evidence: [EV.maleV8pair, EV.progress],
    note: {zh: 'root 仅接受为技术静止候选（closeout 6406bb8 记录的视觉判断）；美术未批准。', en: 'Root accepted a technical static candidate only (visual findings in the 6406bb8 closeout); art unapproved.'}},
  'review.char.ji-cheng.static-south': {status: 'done', outcome: 'technical-pass', at: '2026-10-18T14:45:00Z', evidence: [EV.ji, EV.progress],
    note: {zh: 'root 仅接受为技术静止候选：姿势正面僵硬、靴子厚重、发梢含糊、米色对比弱（closeout c6755462）。', en: 'Root accepted a technical static candidate only: stiff frontal pose, heavy boots, ambiguous hair tips, weak cream contrast (closeout c6755462).'}},
  'review.char.protagonist-female.static-south': {status: 'not_required', waivedBy: 'creator.char.protagonist-female.approve-static-south', evidence: [EV.femaleV8]},
  'content.combat.protagonist-female.combat-static': {status: 'done', evidence: [EV.femaleBattleV14]},
  'review.combat.protagonist-female.static': {status: 'done', outcome: 'technical-pass', at: '2026-10-18T13:47:00Z', evidence: [EV.femaleBattleV14, EV.progress],
    note: {zh: 'v14 技术静止收尾（50c179c）；美术未批准。', en: 'v14 technical static closeout (50c179c); art unapproved.'}},
  'content.enemy.sentry.static': {status: 'done', evidence: [EV.sentryPilot]},
  'content.enemy.sentry.battle-animation': {status: 'done', evidence: [EV.sentryAnimV2, EV.sentryV2]},
  'qa.enemy.sentry.check': {status: 'done', outcome: 'passed', evidence: [EV.sentryV2]},
  'review.enemy.sentry': {status: 'done', outcome: 'technical-pass', at: '2026-10-18T17:55:49Z', evidence: [EV.sentryV2, EV.progress],
    note: {zh: 'root 看过实机 en640/zh640：只接受技术代码移植；眼部部分遮挡与几何占位背景仍在（closeout fa4c8600）。', en: 'Root viewed actual en640/zh640 captures: technical code port only; partly occluded eye and geometric backdrop remain (closeout fa4c8600).'}},
  // Scenes. plate = a candidate plate playable in the runtime; native-pass = a committed native pixel quality pass.
  'content.scene.map.plate': {status: 'done', evidence: [EV.mapV01]},
  'content.scene.map.wiring': {status: 'done', evidence: [EV.mapInset]},
  'content.scene.map.native-pass': {status: 'done', evidence: [EV.mapV03]},
  'content.scene.map.native-default': {status: 'done', evidence: [EV.mapV03r2, EV.progress]},
  'qa.scene.map.check': {status: 'done', outcome: 'passed', evidence: [EV.mapV03r2]},
  'content.scene.city.plate': {status: 'done', evidence: [EV.sceneAudit, EV.cityRuntime]},
  'content.scene.city.wiring': {status: 'done', evidence: [EV.cityRuntime, EV.m7Smoke]},
  'content.scene.city.native-pass': {status: 'done', evidence: [EV.chpV04]},
  'qa.scene.city.check': {status: 'done', outcome: 'passed', evidence: [EV.chpV06]},
  'content.scene.outskirts.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.outskirts.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.ruins.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.ruins.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.ruins.native-pass': {status: 'done', evidence: [EV.wdcV12, EV.wdcV12r2]},
  // The published v13 flag checker was red (18/21, variable-fps F13); 0636b40 replaced it with a deterministic fixed-60fps
  // check that root accepted at 22/22. Technical inspection only; the art stays unapproved.
  'qa.scene.ruins.check': {status: 'done', outcome: 'passed', at: '2026-10-18T18:25:12Z', evidence: [EV.wdcV13Det, EV.wdcV13DetReport],
    note: {zh: 'root 接受 v13 开关的确定性检查 22/22（固定 60 fps，20 个固定帧，8 个已验收房间 0 像素差异；0636b40）；仅技术检查，美术未批准。', en: 'Root accepted the deterministic v13 flag check at 22/22 (fixed 60 fps, 20 fixed frames, 8 accepted rooms 0 px; 0636b40); technical inspection only, art unapproved.'}},
  'review.scene.ruins': {status: 'done', outcome: 'changes_requested', at: 'INIT', evidence: [EV.wdcV13, EV.wdcV13Flag],
    note: {zh: 'root 看过 v13 开关的实机入口与战后返回画面：穹顶清楚、局部坍塌改善了废墟观感；地面颗粒感重、植被块状。美术未批准。', en: 'Root viewed the actual v13 flag entry and battle-return frames: the dome stays clear and the localized collapse improves the ruin read; the ground is grainy and the foliage blocky. Art unapproved.'}},
  'content.scene.city-survey-outer.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.city-survey-outer.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.city-survey-outer.native-pass': {status: 'done', evidence: [EV.nycR1]},
  'content.scene.city-survey-outer.native-default': {status: 'done', evidence: [EV.nycR1, EV.nycR1Accept]},
  'qa.scene.city-survey-outer.check': {status: 'done', outcome: 'passed', evidence: [EV.nycR1]},
  'review.scene.city-survey-outer': {status: 'not_required', waivedBy: 'creator.scene.city-survey-outer.accept', evidence: [EV.nycR1Accept]},
  'content.scene.city-survey-inner.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.city-survey-inner.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.city-survey-inner.native-pass': {status: 'done', evidence: [EV.nycR2]},
  'content.scene.city-survey-inner.native-default': {status: 'done', evidence: [EV.nycR2, EV.nycR2Accept]},
  'qa.scene.city-survey-inner.check': {status: 'done', outcome: 'passed', evidence: [EV.nycR2]},
  'review.scene.city-survey-inner': {status: 'not_required', waivedBy: 'creator.scene.city-survey-inner.accept', evidence: [EV.nycR2Accept]},
  'content.scene.outskirts-survey-outer.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.outskirts-survey-outer.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.outskirts-survey-outer.native-pass': {status: 'done', evidence: [EV.yR1V01]},
  'content.scene.outskirts-survey-outer.native-default': {status: 'done', evidence: [EV.yR1V03, EV.yR1Default]},
  'qa.scene.outskirts-survey-outer.check': {status: 'done', outcome: 'passed', evidence: [EV.yR1V06]},
  'review.scene.outskirts-survey-outer': {status: 'done', outcome: 'changes_requested', at: '2026-10-18T13:12:00Z', evidence: [EV.yR1V06, EV.progress],
    note: {zh: 'root 对 v06 的视觉判断（closeout 5597d7f5）：墙面更平静、设备更清楚，但大面积平墙、底座发白、三块平台布局呆板；美术未批准。', en: 'Root visual judgment of v06 (closeout 5597d7f5): calmer wall and clearer fixtures, but large flat wall areas, pale bases and a rigid three-pad layout; art unapproved.'}},
  'content.scene.outskirts-survey-inner.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.outskirts-survey-inner.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.outskirts-survey-inner.native-pass': {status: 'done', evidence: [EV.yR2]},
  'content.scene.outskirts-survey-inner.native-default': {status: 'done', evidence: [EV.yR2, EV.yR2Accept]},
  'qa.scene.outskirts-survey-inner.check': {status: 'done', outcome: 'passed', evidence: [EV.yR2]},
  'review.scene.outskirts-survey-inner': {status: 'not_required', waivedBy: 'creator.scene.outskirts-survey-inner.accept', evidence: [EV.yR2Accept]},
  'content.scene.ruins-survey-outer.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.ruins-survey-outer.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.ruins-survey-outer.native-pass': {status: 'done', evidence: [EV.wdcR1, EV.wdcR1Manifest]},
  'content.scene.ruins-survey-outer.native-default': {status: 'done', evidence: [EV.wdcR1, EV.wdcR2Fix]},
  'qa.scene.ruins-survey-outer.check': {status: 'done', outcome: 'passed', evidence: [EV.wdcR1]},
  'content.scene.ruins-survey-inner.plate': {status: 'done', evidence: [EV.sceneAudit]},
  'content.scene.ruins-survey-inner.wiring': {status: 'done', evidence: [EV.sceneAudit, EV.m7Smoke]},
  'content.scene.ruins-survey-inner.native-pass': {status: 'done', evidence: [EV.wdcR2]},
  'qa.scene.ruins-survey-inner.check': {status: 'done', outcome: 'passed', evidence: [EV.wdcR2, EV.wdcR2Fix]},
  'content.scene.chicago-loop.plate': {status: 'done', evidence: [EV.chiV02]},
  'content.scene.chicago-loop.wiring': {status: 'done', evidence: [EV.chiV02]},
  'content.scene.chicago-loop.native-pass': {status: 'done', evidence: [EV.chiV03r1]},
  'qa.scene.chicago-loop.check': {status: 'done', outcome: 'passed', evidence: [EV.chiV03r1]},
  'content.audio.ambient-loops': {status: 'done', evidence: [EV.audioLoopCity, EV.audioLoopBattle, EV.m7Smoke]},
  'content.audio.discovery-cue': {status: 'done', evidence: [EV.audioCue, EV.m7Smoke]},
};
// The one fixed revision bucket per deliverable that already had a requested change at the baseline (initial credit kept).
const BASELINE_REVISIONS = {
  'content.scene.map.native-pass': {status: 'done', at: '2026-10-18T02:46:31Z', evidence: [EV.mapV03r1Codex, EV.mapV03r2], zh: 'Codex 对 v03r1 视觉判断后的修订（v03r2）', en: 'Revision after the Codex v03r1 visual judgment (v03r2)'},
  'content.scene.city.native-pass': {status: 'done', at: '2026-10-17T20:52:53Z', evidence: [EV.chpV04Reject, EV.chpV06], zh: '创作者否决 v04 后的修订（v06）', en: 'Revision after the creator rejected v04 (v06)'},
  'content.scene.outskirts-survey-outer.native-pass': {status: 'done', at: '2026-10-18T12:47:26Z', evidence: [EV.yR1V03, EV.yR1V06], zh: '创作者否决 v02 室外观感后的修订（v03 起，最新 v06）', en: 'Revision after the creator rejected the v02 outdoor look (v03 onward, latest v06)'},
  'content.scene.ruins.native-pass': {status: 'done', at: '2026-10-18T18:06:24Z', evidence: [EV.wdcV13, EV.wdcV13Flag], zh: 'root 对 v12r2 外观意见后的修订（v13 局部坍塌，可选启用）', en: 'Revision after root\'s v12r2 critique (v13 localized collapse, opt-in flag)'},
  'content.combat.protagonist-female.combat-static': {status: 'done', at: '2026-10-18T12:45:53Z', evidence: [EV.femaleBattleV11Feedback, EV.femaleBattleV14], zh: '按创作者对 v11 的意见修订（v12–v14）', en: 'Revision after the creator feedback on v11 (v12-v14)'},
  // v10 + r1 (364d47a): root accepted the PRODUCED technical revision only (slower cadence clear; leading leg still diagonal, minor
  // improvement); focused check 16/16, mixed-frame boot down <= 88.9 ms, release-to-stop <= 272.2 ms. Gait and fluidity unapproved.
  'content.char.protagonist-female.walk-south': {status: 'done', at: '2026-10-18T18:36:18Z', evidence: [EV.femaleRunV10r1, EV.femaleRunV10r1Receipt], zh: '跑动／停步打磨（v10 + r1，已制作的技术修订；步态与流畅度未批准）', en: 'Run/stop polish (v10 + r1, produced technical revision; gait and fluidity unapproved)'},
  'content.char.liang-xu.static-south': {status: 'todo', evidence: [], zh: '按 Codex 视觉审查意见修订南向静止帧', en: 'South static revision after the Codex visual audit'},
};

// The twelve science scene-quality gates (inventory world/scene-quality), keyed by a short stable id.
const SCENES = [
  ['map', 'visual-scene.map', '科技区世界地图', 'Science-sphere world map'],
  ['city', 'visual-scene.city', '纽约市政厅公园（城市）', 'NYC City Hall Park (city)'],
  ['outskirts', 'visual-scene.outskirts', '扬克斯城外', 'Yonkers outskirts'],
  ['ruins', 'visual-scene.ruins', '华盛顿国会大厦西侧废墟', 'Washington Capitol west ruins'],
  ['city-survey-outer', 'visual-scene.city-survey-outer', '纽约公共设施 1 号房', 'NYC public facilities room 1'],
  ['city-survey-inner', 'visual-scene.city-survey-inner', '纽约公共设施 2 号房', 'NYC public facilities room 2'],
  ['outskirts-survey-outer', 'visual-scene.outskirts-survey-outer', '扬克斯天线走廊 1 号房', 'Yonkers antenna corridor room 1'],
  ['outskirts-survey-inner', 'visual-scene.outskirts-survey-inner', '扬克斯信号维修 2 号房', 'Yonkers signal maintenance room 2'],
  ['ruins-survey-outer', 'visual-scene.ruins-survey-outer', '华盛顿勘察附楼 1 号房', 'Washington survey annex room 1'],
  ['ruins-survey-inner', 'visual-scene.ruins-survey-inner', '华盛顿勘察附楼 2 号房（档案室）', 'Washington survey annex room 2 (records)'],
  ['battle-arena', 'visual-scene.battle-arena', '科技区横向战场', 'Science side-view battle arena'],
  ['chicago-loop', 'visual-scene.chicago-loop-outdoor', '芝加哥卢普区街区', 'Chicago Loop block'],
];
const COMBAT_VARIANTS = ['protagonist-male', 'protagonist-female', 'liang-xu', 'ji-cheng', 'zhao-ling'];
const DIRS = [['south', '南'], ['west', '西'], ['north', '北'], ['east', '东']];

function rel(root, file) { return path.join(root, file); }
function readJson(root, file) { return JSON.parse(fs.readFileSync(rel(root, file), 'utf8')); }
function sha256(text) { return crypto.createHash('sha256').update(text).digest('hex'); }
function enName(id) {
  if (id === 'protagonist-male') return 'Male protagonist';
  if (id === 'protagonist-female') return 'Female protagonist';
  return id.split('-').map(w => /^\d+$/.test(w) ? w : w[0].toUpperCase() + w.slice(1)).join(' ');
}
function tracked(root, files) {
  if (!files.length) return new Set();
  const out = spawnSync('git', ['ls-files', '--', ...files], {cwd: root, encoding: 'utf8'});
  if (out.status !== 0) throw new Error('git ls-files failed: ' + out.stderr);
  return new Set(out.stdout.split(/\r?\n/).filter(Boolean));
}
function revisionTask(target, extra = {}) {
  return {id: target.id + '.revision', type: 'revision', title: {zh: target.title.zh + ' · 修订', en: target.title.en + ' · revision'}, area: target.area, stage: target.stage, owner: target.owner,
    status: 'todo', points: revisionPoints(target.points), doneCriterion: {zh: '针对最近一次审查／创作者意见的修订版已提交并有 QA；后续版本只更新本条，不新增分值', en: 'A revision answering the latest review / creator request is committed with QA; later versions update this bucket and add no points'},
    dependsOn: [target.id], evidence: [], subject: target.subject, target: target.id, ...extra};
}

// ---------- baseline builder (init only) ----------
function buildTasks(root, now) {
  const progress = readJson(root, PROGRESS_REL);
  const inventory = readJson(root, INVENTORY_REL);
  const registry = readJson(root, REGISTRY_REL);
  const invItems = new Map();
  for (const c of inventory.categories) for (const s of c.subcategories) for (const i of s.items) invItems.set(i.id, i);
  const tasks = [];
  const t = (id, stage, points, title, criterion, extra = {}) => {
    const type = extra.type || DEFAULT_TYPE[stage];
    const rule = TASK_TYPES[type];
    const task = {id, type, title, area: extra.area, stage: rule.stage, owner: rule.owner, status: 'todo', points, doneCriterion: criterion,
      dependsOn: extra.dependsOn || [], evidence: [], subject: extra.subject};
    if (extra.target) task.target = extra.target;
    tasks.push(task);
  };
  const C = (zh, en) => ({zh, en});
  const credit = (id, status, evidence, more = {}) => {
    const task = tasks.find(x => x.id === id);
    if (!task) throw new Error('credit for unknown task ' + id);
    Object.assign(task, {status, evidence}, more);
  };

  // Core gameplay coding (steps M1, M3-M6).
  const core = [['m1', 'M1', 8, '项目基础（启动、像素显示、语言、数据 ID）', 'Project foundation (launch, pixel display, language, data IDs)'],
    ['m3', 'M3', 12, '战斗核心（横向平地、动作、能量、敌人、恢复）', 'Combat core (side-view arena, actions, energy, enemies, recovery)'],
    ['m4', 'M4', 10, '伙伴与 AI（五人位、三种招募、切换、指令）', 'Companions and AI (five slots, three recruit routes, switching, commands)'],
    ['m5', 'M5', 10, '等级与职业（XP/JP、天分、职业与技能）', 'Levels and jobs (XP/JP, aptitudes, jobs and skills)'],
    ['m6', 'M6', 8, '存档与恢复（手动、自动、检查点、迁移）', 'Saves and recovery (manual, autosave, checkpoints, versions)']];
  for (const [key, step, pts, zh, en] of core) {
    const id = 'code.core.' + key;
    t(id, 'coding', pts, C(zh, en), C(`${step} 冒烟测试通过且步骤状态为 done`, `${step} smoke test passes and the step status is done`), {area: 'core-gameplay', subject: {kind: 'feature', id: step}});
    const s = progress.steps.find(x => x.id === step);
    if (s.status === 'done') credit(id, 'done', ['game/tests/' + step.toLowerCase() + '_smoke.gd']);
  }
  // Global travel coding (M2 gates other than art and human review). Anchor and start-year were creator canon choices that
  // Claude implemented: split into a coding task and a creator task.
  const travel = {'map-ui': 6, 'place-registry': 4, 'route-preview': 4, 'calendar': 4, 'save-migration': 4, 'route-data': 3, 'air-route': 3, 'anchor': 2, 'start-year': 1};
  for (const gate of progress.m2Expansion.gates) {
    const ev = (gate.evidence || []).filter(e => typeof e === 'string' && !/\s/.test(e));
    if (travel[gate.id]) {
      const id = 'code.travel.' + gate.id;
      t(id, 'coding', travel[gate.id], C(gate.zh, gate.en), C(`m2Expansion 门 ${gate.id} 为 implemented 且有 QA 证据`, `m2Expansion gate ${gate.id} is implemented with QA evidence`), {area: 'global-travel', subject: {kind: 'feature', id: 'm2.' + gate.id}});
      if (gate.status === 'implemented' || gate.status === 'done') credit(id, 'done', ev);
    }
    if (gate.id === 'acceptance-test') {
      t('qa.travel.acceptance-tests', 'technical-inspection', 3, C(gate.zh, gate.en), C('M2 Godot 自动测试全部通过', 'The M2 Godot automated tests all pass'), {area: 'global-travel', subject: {kind: 'feature', id: 'm2.acceptance-test'}});
      if (gate.status === 'implemented') credit('qa.travel.acceptance-tests', 'done', ev, {outcome: 'passed'});
    }
    if (gate.id === 'anchor' || gate.id === 'start-year') {
      const id = 'creator.canon.' + gate.id;
      t(id, 'creator-approval', 1, C('正典决定：' + gate.zh, 'Canon choice: ' + gate.en), C('创作者已作决定并记录', 'The creator made and recorded the decision'), {type: 'canon-choice', area: 'canon', subject: {kind: 'decision', id: 'm2.' + gate.id}});
      credit(id, 'done', ev);
    }
  }
  // Science playable content (M7 meter gates). Pacing is the creator's human playthroughs below.
  const m7 = progress.completionMeter.categories.find(c => c.id === 'science-playable-content').gates;
  const m7Map = {'three-area-route': ['code.m7.free-order-route', 'coding', 6, 'feature-code'], 'report-endpoint': ['code.m7.report-endpoint', 'coding', 3, 'feature-code'],
    'investigations-companions': ['content.m7.investigations-companions', 'content', 10, 'content-writing']};
  for (const g of m7) {
    if (!m7Map[g.id]) continue;
    const [id, stage, pts, type] = m7Map[g.id];
    t(id, stage, pts, C(g.zh, g.en), C(`M7 内容门 ${g.id} 为 done 且有测试或清单证据`, `M7 content gate ${g.id} is done with test or manifest evidence`), {type, area: 'science-content', subject: {kind: 'feature', id: 'm7.' + g.id}});
    if (g.status === 'done') credit(id, 'done', g.evidence);
  }
  // Remaining MVP coding (inventory MVP items that are planned, plus the runtime pipelines the art needs).
  const P = {type: 'pipeline-code', area: 'runtime'};
  t('code.ui.settings', 'coding', 3, C('语言、声音与输入设置界面', 'Language, sound and input settings'), C('设置界面可用并有中英文自动测试', 'Settings screen works with zh/en automated tests'), {area: 'ui', subject: {kind: 'asset', id: 'ui.settings'}});
  t('code.runtime.enemy-sprite-pipeline', 'coding', 3, C('敌人精灵运行时（载入、状态、绘制顺序）', 'Enemy sprite runtime (loaders, states, draw order)'), C('运行时可载入敌人动画条并有自动检查', 'The runtime loads an enemy animation strip with automated checks'), {...P, subject: {kind: 'feature', id: 'battle.enemy-sprites'}});
  t('code.runtime.character-sprite-pipeline', 'coding', 6, C('高密度四方向角色精灵运行时', 'High-density four-direction character sprite runtime'), C('运行时具备载入高密度四方向待机与行走精灵组的正常能力：在正常运行时经可选开关或测试夹具验证，并有针对性测试；是否默认采用属于内容与批准任务', 'Normal runtime capability to load a high-density four-direction idle+walk set, verified in the normal runtime through an opt-in flag or test fixture with targeted tests; adopting a set for the shipped game belongs to the content and approval tasks'), {...P, subject: {kind: 'feature', id: 'exploration.character-sprites'}});
  t('code.runtime.combat-sprite-pipeline', 'coding', 4, C('高密度横向战斗精灵运行时', 'High-density side-view combat sprite runtime'), C('运行时具备载入高密度横向战斗动作组的正常能力：在正常运行时经可选开关或测试夹具验证，并有针对性测试；是否默认采用属于内容与批准任务', 'Normal runtime capability to load a high-density side-view combat action set, verified in the normal runtime through an opt-in flag or test fixture with targeted tests; adopting a set for the shipped game belongs to the content and approval tasks'), {...P, subject: {kind: 'feature', id: 'battle.character-sprites'}});
  t('code.runtime.battle-arena-backdrop', 'coding', 2, C('战场背景载入', 'Battle arena backdrop loader'), C('战斗具备绘制美术背景的正常运行时能力：经可选开关或测试夹具验证，并有针对性测试；采用哪张背景属于场景内容与批准任务', 'Normal runtime capability for battles to draw an art backdrop, verified through an opt-in flag or test fixture with targeted tests; adopting a backdrop belongs to the scene content and approval tasks'), {...P, subject: {kind: 'feature', id: 'battle.arena-backdrop'}});
  t('code.runtime.vfx-system', 'coding', 3, C('战斗特效系统', 'Combat VFX system'), C('攻击、闪避、防御、受击、治疗可触发特效并有测试', 'Attack, dodge, guard, hit and heal can trigger effects, with tests'), {...P, subject: {kind: 'asset', id: 'vfx.common'}});
  t('code.runtime.audio-cues', 'coding', 2, C('界面与战斗音效触发', 'UI and combat sound cues'), C('界面与战斗事件触发音效并有测试', 'UI and combat events trigger sounds, with tests'), {...P, subject: {kind: 'asset', id: 'sfx.combat'}});

  // Character variants (all 52 registry entries; MVP needs four-direction idle + walk and a display image for each).
  const pipeline = 'code.runtime.character-sprite-pipeline';
  for (const entry of registry.entries) {
    const v = entry.visual_id, zhName = entry.display_name_zh, en = enName(v), subject = {kind: 'character-variant', id: v};
    const base = 'content.char.' + v, area = 'characters';
    t(base + '.portrait', 'content', 1, C(zhName + ' · 人物设定图（图像生成）', en + ' · source portrait (image generation)'), C('设定图文件已入库', 'The source portrait file is committed'), {type: 'concept-generation', area, subject});
    for (const [d, dz] of DIRS) {
      t(`${base}.static-${d}`, 'content', d === 'south' ? 3 : 2, C(`${zhName} · ${dz}向高密度静止帧`, `${en} · ${d} high-density static`),
        C(`${dz}向原生像素静止帧（48 逻辑像素）已提交，带 QA 记录；旧 32×48 占位不算`, `${d} native pixel static (48 logical px) committed with a QA note; the old 32x48 placeholder does not count`),
        {area, subject, dependsOn: d === 'south' ? [] : [base + '.static-south']});
    }
    t(base + '.idle-anim', 'content', 2, C(zhName + ' · 四方向待机动画', en + ' · four-direction idle animation'), C('四个方向的待机循环已提交并有 QA', 'Idle loops for all four directions committed with QA'), {area, subject, dependsOn: DIRS.map(([d]) => `${base}.static-${d}`)});
    for (const [d, dz] of DIRS) {
      t(`${base}.walk-${d}`, 'content', 3, C(`${zhName} · ${dz}向行走／跑动`, `${en} · ${d} walk/run`), C(`${dz}向行走或跑动循环与停步已提交，并有触地／滑步检查`, `${d} walk or run cycle and stop committed with contact / slip checks`), {area, subject, dependsOn: [`${base}.static-${d}`]});
    }
    t(base + '.display', 'content', 2, C(zhName + ' · 游戏内展示图', en + ' · in-game display image'), C('游戏内展示图已提交并在界面中显示', 'The in-game display image is committed and shown in the UI'), {area, subject, dependsOn: [base + '.static-south']});
    t(base + '.runtime-integration', 'content', 2, C(zhName + ' · 运行时默认接入', en + ' · runtime default integration'), C('整套四方向待机与行走默认在游戏中使用', 'The full four-direction idle+walk set is used in the game by default'), {type: 'integration', area, subject, dependsOn: [base + '.idle-anim', ...DIRS.map(([d]) => `${base}.walk-${d}`), pipeline]});
    t(`qa.char.${v}.runtime-set-check`, 'technical-inspection', 1, C(zhName + ' · 运行时整套技术检查', en + ' · runtime set technical check'), C('Godot 实机检查（帧、锚点、方向、滑步）全部通过', 'Godot checks (frames, anchors, directions, slip) all pass'), {area, subject, target: base + '.runtime-integration', dependsOn: [base + '.runtime-integration']});
    t(`review.char.${v}.static-south`, 'visual-review', 1, C(zhName + ' · 南向静止帧视觉审查', en + ' · south static visual review'), C('Codex 在 640×360 实机画面中审查并记录结论', 'Codex reviews it in actual 640x360 captures and records a verdict'), {area, subject, target: base + '.static-south', dependsOn: [base + '.static-south']});
    t(`review.char.${v}.runtime-set`, 'visual-review', 1, C(zhName + ' · 运行时整套视觉审查', en + ' · runtime set visual review'), C('Codex 审查实机动作并记录结论', 'Codex reviews the in-game motion and records a verdict'), {area, subject, target: base + '.runtime-integration', dependsOn: [`qa.char.${v}.runtime-set-check`]});
    t(`creator.char.${v}.approve-portrait`, 'creator-approval', 1, C(zhName + ' · 批准设定图', en + ' · approve source portrait'), C('创作者批准设定图（清单勾选）', 'The creator approves the portrait (inventory check)'), {area, subject, target: base + '.portrait', dependsOn: [base + '.portrait']});
    t(`creator.char.${v}.approve-static-south`, 'creator-approval', 1, C(zhName + ' · 批准南向静止基准', en + ' · approve south static baseline'), C('创作者批准南向静止帧（台账条目）', 'The creator approves the south static (ledger item)'), {area, subject, target: base + '.static-south', dependsOn: [base + '.static-south']});
    t(`creator.char.${v}.accept-runtime-sprite`, 'creator-approval', 1, C(zhName + ' · 验收运行时精灵', en + ' · accept runtime sprite'), C('approvalLedger 记有 acceptanceKind runtime-sprite 的验收条目', 'approvalLedger records an acceptanceKind runtime-sprite item'), {area, subject, target: base + '.runtime-integration', dependsOn: [base + '.runtime-integration']});
    t(`creator.char.${v}.accept-display`, 'creator-approval', 1, C(zhName + ' · 验收展示图', en + ' · accept display image'), C('清单 display 项被创作者勾选', 'The creator checks the inventory display item'), {area, subject, target: base + '.display', dependsOn: [base + '.display']});
    const portrait = entry.source_portrait || {};
    if (portrait.exists && portrait.path) credit(base + '.portrait', 'done', [portrait.path]);
    if (portrait.approval === 'approved' && invItems.get('portrait.' + v)?.checked) credit(`creator.char.${v}.approve-portrait`, 'done', [INVENTORY_REL]);
  }
  const femaleApproval = progress.approvalLedger.items.find(i => i.id === 'female-v8-south-idle-static' && i.status === 'approved');
  if (femaleApproval) credit('creator.char.protagonist-female.approve-static-south', 'done', femaleApproval.evidence);
  // Combat sets for the five playable science characters.
  for (const v of COMBAT_VARIANTS) {
    const zhName = registry.entries.find(e => e.visual_id === v).display_name_zh, en = enName(v), subject = {kind: 'character-variant', id: v}, area = 'combat', base = 'content.combat.' + v;
    t(base + '.combat-static', 'content', 3, C(zhName + ' · 横向战斗静止帧', en + ' · side-view combat static'), C('高密度横向战斗待机帧已提交并有 QA；旧 32×48 原型不算', 'High-density side-view battle idle committed with QA; the old 32x48 prototype does not count'), {area, subject, dependsOn: ['content.char.' + v + '.static-south']});
    t(base + '.combat-actions', 'content', 8, C(zhName + ' · 八个战斗动作', en + ' · eight combat actions'), C('八个战斗动作全部提交并有 QA', 'All eight combat actions committed with QA'), {area, subject, dependsOn: [base + '.combat-static']});
    t(base + '.combat-integration', 'content', 2, C(zhName + ' · 战斗运行时默认接入', en + ' · combat runtime default integration'), C('整套战斗动作默认在战斗中使用', 'The combat set is used in battle by default'), {type: 'integration', area, subject, dependsOn: [base + '.combat-actions', 'code.runtime.combat-sprite-pipeline']});
    t(`qa.combat.${v}.set-check`, 'technical-inspection', 1, C(zhName + ' · 战斗整套技术检查', en + ' · combat set technical check'), C('战斗动作 Godot 检查全部通过', 'Godot combat checks all pass'), {area, subject, target: base + '.combat-integration', dependsOn: [base + '.combat-integration']});
    t(`review.combat.${v}.static`, 'visual-review', 1, C(zhName + ' · 战斗静止帧视觉审查', en + ' · combat static visual review'), C('Codex 审查并记录结论', 'Codex reviews it and records a verdict'), {area, subject, target: base + '.combat-static', dependsOn: [base + '.combat-static']});
    t(`review.combat.${v}.set`, 'visual-review', 1, C(zhName + ' · 战斗整套视觉审查', en + ' · combat set visual review'), C('Codex 审查实机战斗动作并记录结论', 'Codex reviews the in-game combat motion and records a verdict'), {area, subject, target: base + '.combat-integration', dependsOn: [`qa.combat.${v}.set-check`]});
    t(`creator.combat.${v}.accept-set`, 'creator-approval', 1, C(zhName + ' · 验收战斗形象', en + ' · accept combat set'), C('清单 playable-combat 项被创作者勾选', 'The creator checks the inventory playable-combat item'), {area, subject, target: base + '.combat-integration', dependsOn: [base + '.combat-integration']});
  }
  // Enemies (inventory enemy.mvp: two science enemy animation sets).
  for (const [e, zh, en] of [['sentry', '防卫机（哨卫）', 'Sentry automaton'], ['patrol', '巡逻机', 'Patrol drone']]) {
    const subject = {kind: 'enemy', id: e}, area = 'enemies', base = 'content.enemy.' + e;
    t(base + '.static', 'content', 2, C(zh + ' · 战斗静止精灵', en + ' · battle static sprite'), C('原生像素静止精灵已提交并有 QA', 'Native pixel static committed with QA'), {area, subject});
    t(base + '.battle-animation', 'content', 6, C(zh + ' · 战斗动画条', en + ' · battle animation strip'), C('全部战斗状态的动画条已提交并有帧检查', 'A strip covering every battle state committed with frame checks'), {area, subject, dependsOn: [base + '.static']});
    t(base + '.runtime-default', 'content', 2, C(zh + ' · 运行时默认使用', en + ' · runtime default'), C('不加参数时战斗默认绘制该动画', 'Battles draw the animation by default, without a flag'), {type: 'integration', area, subject, dependsOn: [base + '.battle-animation', 'code.runtime.enemy-sprite-pipeline']});
    t(`qa.enemy.${e}.check`, 'technical-inspection', 1, C(zh + ' · 技术检查', en + ' · technical check'), C('动画与战斗一致性检查通过', 'Animation and combat-parity checks pass'), {area, subject, target: base + '.battle-animation', dependsOn: [base + '.battle-animation']});
    t(`review.enemy.${e}`, 'visual-review', 1, C(zh + ' · 视觉审查', en + ' · visual review'), C('Codex／root 审查实机画面并记录结论', 'Codex / root reviews actual captures and records a verdict'), {area, subject, target: base + '.battle-animation', dependsOn: [`qa.enemy.${e}.check`]});
    t(`creator.enemy.${e}.accept-art`, 'creator-approval', 1, C(zh + ' · 验收美术', en + ' · accept art'), C('创作者验收该敌人美术', 'The creator accepts the enemy art'), {area, subject, target: base + '.runtime-default', dependsOn: [base + '.runtime-default']});
  }
  t('creator.enemy.sentry.approve-direction', 'creator-approval', 1, C('防卫机 · 批准动作方向', 'Sentry · approve action direction'), C('创作者批准动作方向（不含美术）', 'The creator approves the action direction (not the art)'), {area: 'enemies', subject: {kind: 'enemy', id: 'sentry'}, target: 'content.enemy.sentry.battle-animation', dependsOn: ['content.enemy.sentry.battle-animation']});
  const sentryDirection = progress.approvalLedger.items.find(i => i.id === 'sentry-direction' && i.status === 'direction_accepted');
  if (sentryDirection) credit('creator.enemy.sentry.approve-direction', 'done', sentryDirection.evidence.filter(e => !/\s/.test(e)));
  // Scenes: the twelve science scene-quality gates.
  for (const [key, invId, zh, en] of SCENES) {
    if (!invItems.has(invId)) throw new Error('inventory scene gate missing: ' + invId);
    const subject = {kind: 'scene-gate', id: invId}, area = 'scenes', base = 'content.scene.' + key;
    t(base + '.plate', 'content', 4, C(zh + ' · 场景底板', en + ' · scene plate'), C('可玩场景底板已提交并在运行时可进入（概念图不算）', 'A playable scene plate is committed and enterable in the runtime (a concept image does not count)'), {type: 'integration', area, subject});
    t(base + '.wiring', 'content', 3, C(zh + ' · 碰撞、热点与出入口', en + ' · collision, hotspots and exits'), C('碰撞、热点、出入口与存档有自动检查', 'Collision, hotspots, exits and saves have automated checks'), {type: 'integration', area, subject, dependsOn: [base + '.plate']});
    t(base + '.native-pass', 'content', 12, C(zh + ' · 原生像素画质版', en + ' · native pixel quality pass'), C('原生像素画质版（道具／分层）已提交并有 QA，可为可选启用', 'A native pixel quality pass (fixtures / layers) is committed with QA; opt-in is allowed'), {area, subject, dependsOn: [base + '.plate']});
    t(base + '.native-default', 'content', 2, C(zh + ' · 画质版默认接入', en + ' · quality pass on by default'), C('画质版默认在游戏中使用', 'The quality pass is used in the game by default'), {type: 'integration', area, subject, dependsOn: [base + '.native-pass', base + '.wiring']});
    t(`qa.scene.${key}.check`, 'technical-inspection', 1, C(zh + ' · 技术检查', en + ' · technical check'), C('当前画质版的 Godot 检查全部通过', 'Godot checks of the current quality pass all pass'), {area, subject, target: base + '.native-pass', dependsOn: [base + '.native-pass']});
    t(`review.scene.${key}`, 'visual-review', 1, C(zh + ' · 视觉审查', en + ' · visual review'), C('Codex 审查 640×360 实机画面并记录结论', 'Codex reviews actual 640x360 captures and records a verdict'), {area, subject, target: base + '.native-pass', dependsOn: [`qa.scene.${key}.check`]});
    t(`creator.scene.${key}.accept`, 'creator-approval', 1, C(zh + ' · 场景画质验收', en + ' · scene-quality acceptance'), C('approvalLedger 记有 acceptanceKind scene-visual 的验收条目', 'approvalLedger records an acceptanceKind scene-visual item'), {area, subject, target: base + '.native-pass', dependsOn: [base + '.native-pass']});
  }
  const sceneAccept = {'nyc-public-facilities-room1-scene-visual-accepted': 'city-survey-outer', 'nyc-public-facilities-room2-scene-visual-accepted': 'city-survey-inner', 'yonkers-maintenance-room2-scene-visual-accepted': 'outskirts-survey-inner'};
  for (const item of progress.approvalLedger.items) {
    if (item.status === 'accepted' && item.acceptanceKind === 'scene-visual' && sceneAccept[item.id]) credit(`creator.scene.${sceneAccept[item.id]}.accept`, 'done', item.evidence.filter(e => !/\s/.test(e)));
  }
  // VFX, audio and UI visuals (inventory MVP items).
  const contentItem = (id, pts, zh, en, crit, subjectId, area, deps = [], type = 'native-pixel') => t(id, 'content', pts, C(zh, en), crit, {type, area, subject: {kind: 'asset', id: subjectId}, dependsOn: deps});
  contentItem('content.vfx.common', 5, '通用战斗特效（攻击、闪避、防御、受击、治疗）', 'Common combat effects (attack, dodge, guard, hit, heal)', C('五类特效已提交并接入', 'Five effect sets committed and wired'), 'vfx.common', 'vfx', ['code.runtime.vfx-system']);
  contentItem('content.vfx.mvp-skills', 4, 'MVP 个人与职业技能特效', 'MVP personal and job skill effects', C('MVP 技能特效已提交并接入', 'MVP skill effects committed and wired'), 'vfx.mvp-skills', 'vfx', ['code.runtime.vfx-system']);
  contentItem('content.vfx.encounter', 3, '接敌、胜利、战败与恢复特效', 'Encounter, victory, defeat and recovery effects', C('四类反馈特效已提交并接入', 'Four feedback effects committed and wired'), 'vfx.encounter', 'vfx');
  contentItem('content.audio.ambient-loops', 3, '四段原创环境循环', 'Four original ambient loops', C('城镇、野外、遗址、战斗循环已接入', 'Town, field, ruin and battle loops are wired'), 'music.mvp', 'audio', [], 'audio-production');
  contentItem('content.audio.themed-music', 6, 'MVP 主题配乐', 'MVP themed music', C('四段主题配乐已提交并接入', 'Four themed tracks committed and wired'), 'music.mvp', 'audio', ['content.audio.ambient-loops'], 'audio-production');
  contentItem('content.audio.discovery-cue', 1, '调查发现提示音', 'Discovery cue', C('调查发现时播放提示音', 'Discovery plays the cue'), 'sfx.discovery', 'audio', [], 'audio-production');
  contentItem('content.audio.ui-sfx', 2, '按钮、菜单、提示音', 'Button, menu and prompt sounds', C('界面音效已提交并接入', 'UI sounds committed and wired'), 'sfx.ui', 'audio', ['code.runtime.audio-cues'], 'audio-production');
  contentItem('content.audio.combat-sfx', 3, '攻击、防御、技能、胜败音效', 'Attack, guard, skill, win/lose sounds', C('战斗音效已提交并接入', 'Combat sounds committed and wired'), 'sfx.combat', 'audio', ['code.runtime.audio-cues'], 'audio-production');
  contentItem('content.ui-visual.navigation', 4, '探索界面正式视觉', 'Exploration UI final visuals', C('导航与探索界面正式视觉已接入', 'Final navigation / exploration UI visuals wired'), 'ui.explore', 'ui-visual');
  contentItem('content.ui-visual.battle', 3, '战斗界面正式视觉', 'Battle UI final visuals', C('战斗 HUD、技能、结算正式视觉已接入', 'Final battle HUD, skills and results visuals wired'), 'ui.battle-hud', 'ui-visual');
  contentItem('content.ui-visual.management', 3, '队伍、职业、存档界面正式视觉', 'Party, jobs and saves UI final visuals', C('管理界面正式视觉已接入', 'Final management UI visuals wired'), 'ui.party', 'ui-visual');
  contentItem('content.ui-visual.character-portraits', 3, '队伍头像与对话立绘裁切', 'Party icons and dialogue portrait crops', C('头像与立绘裁切已提交并接入', 'Icons and portrait crops committed and wired'), 'character-ui.portraits', 'ui-visual');
  t('review.content.vfx', 'visual-review', 1, C('特效 · 视觉审查', 'VFX · visual review'), C('Codex 审查实机特效并记录结论', 'Codex reviews the effects in game and records a verdict'), {area: 'vfx', subject: {kind: 'feature', id: 'content.vfx'}, dependsOn: ['content.vfx.common', 'content.vfx.mvp-skills', 'content.vfx.encounter']});
  t('review.content.audio', 'visual-review', 1, C('音频 · 内容／音频质量检查', 'Audio · content / audio QA'), C('Codex 在游戏中试听音乐与音效并记录结论', 'Codex listens to the music and sounds in game and records a verdict'), {type: 'audio-qa', area: 'audio', subject: {kind: 'feature', id: 'content.audio'}, dependsOn: ['content.audio.themed-music', 'content.audio.ui-sfx', 'content.audio.combat-sfx']});
  t('review.content.ui-visuals', 'visual-review', 1, C('界面正式视觉 · 视觉审查', 'UI final visuals · visual review'), C('Codex 审查实机界面并记录结论', 'Codex reviews the in-game UI and records a verdict'), {area: 'ui-visual', subject: {kind: 'feature', id: 'content.ui-visuals'}, dependsOn: ['content.ui-visual.navigation', 'content.ui-visual.battle', 'content.ui-visual.management', 'content.ui-visual.character-portraits']});
  for (const [key, zh, en, area, deps] of [['vfx', '特效', 'VFX', 'vfx', ['content.vfx.common', 'content.vfx.mvp-skills', 'content.vfx.encounter']],
    ['audio', '音频', 'Audio', 'audio', ['content.audio.themed-music', 'content.audio.ui-sfx', 'content.audio.combat-sfx']],
    ['ui-visuals', '界面正式视觉', 'UI final visuals', 'ui-visual', ['content.ui-visual.navigation', 'content.ui-visual.battle', 'content.ui-visual.management', 'content.ui-visual.character-portraits']]]) {
    t('creator.content.' + key + '.accept', 'creator-approval', 1, C(zh + ' · 创作者验收', en + ' · creator acceptance'), C('创作者在清单中勾选相应条目', 'The creator checks the matching inventory items'), {area, subject: {kind: 'feature', id: 'content.' + key}, dependsOn: deps});
  }
  // Canon choices and the final validation that only the creator can do.
  t('creator.canon.display-scale', 'creator-approval', 1, C('正典决定：48 逻辑像素显示比例', 'Canon choice: 48-logical-pixel display scale'), C('创作者批准显示比例', 'The creator approves the display scale'), {type: 'canon-choice', area: 'canon', subject: {kind: 'decision', id: 'display-scale-48'}});
  const scale = progress.approvalLedger.items.find(i => i.id === 'display-scale-48' && i.status === 'approved');
  if (scale) credit('creator.canon.display-scale', 'done', scale.evidence);
  for (const d of progress.decisions.filter(x => x.kind === 'blocked' && ['prologue-start-date', 'old-save-dates'].includes(x.id))) {
    t('creator.canon.' + d.id, 'creator-approval', 1, C('正典决定：' + d.zh, 'Canon choice: ' + d.en), C('创作者作出决定并记录在进度状态', 'The creator decides and it is recorded in the progress state'), {type: 'canon-choice', area: 'canon', subject: {kind: 'decision', id: d.id}});
  }
  const acceptIds = tasks.filter(x => /^creator\.(char\..*\.accept-runtime-sprite|scene\..*\.accept|combat\..*\.accept-set)$/.test(x.id)).map(x => x.id);
  t('qa.validation.pre-playtest-regression', 'technical-inspection', 3, C('整体试玩前回归检查', 'Pre-playtest integrated regression'), C('全部 Godot 测试与中英文实机截图在最终整合版本上通过', 'All Godot tests and zh/en captures pass on the final integrated build'), {area: 'validation', subject: {kind: 'feature', id: 'M9'}, dependsOn: acceptIds});
  for (const n of [1, 2]) t('creator.playtest.' + n, 'creator-approval', 3, C(`第 ${n} 轮真人整合试玩`, `Human integrated playthrough ${n}`), C('新档按不同路线顺序 25–35 分钟通关，并记录试玩回执', 'A fresh save finishes a different route order in 25-35 minutes, with a playtest receipt'), {type: 'playtest', area: 'validation', subject: {kind: 'feature', id: 'M9'}, dependsOn: ['qa.validation.pre-playtest-regression']});
  t('creator.mvp.final-acceptance', 'creator-approval', 2, C('MVP 正式验收', 'Formal MVP acceptance'), C('创作者正式验收 MVP（现有门全部通过）', 'The creator formally accepts the MVP (all existing gates pass)'), {area: 'validation', subject: {kind: 'feature', id: 'M9'}, dependsOn: ['creator.playtest.1', 'creator.playtest.2']});
  // Operations: Codex's remaining dashboard work (listed with owners, excluded from every percentage).
  t('ops.codex.dashboard-browser-inspection', 'operations', 1, C('新制作完成度看板 · 浏览器视觉检查（本地面板与 Site）', 'New production dashboard · browser visual inspection (local panel and Site)'), C('Codex 在浏览器中检查卡片、筛选、分页与旧版折叠并记录结论', 'Codex inspects the cards, filters, pagination and the collapsed legacy meter in a browser and records a verdict'), {type: 'ops-inspection', area: 'operations', subject: {kind: 'feature', id: 'dashboard.production-completion'}});
  t('ops.codex.site-publication', 'operations', 1, C('新制作完成度看板 · Site 正式发布', 'New production dashboard · official Site publication'), C('root 审查后，Codex 发布准备好的 Site 源码并核对线上数字', 'After root review, Codex publishes the prepared Site source and verifies the live numbers'), {type: 'ops-publication', area: 'operations', subject: {kind: 'feature', id: 'dashboard.production-completion'}, dependsOn: ['ops.codex.dashboard-browser-inspection']});

  for (const [id, c] of Object.entries(CREDITS)) {
    const more = {};
    if (c.outcome) more.outcome = c.outcome;
    if (c.waivedBy) more.waivedBy = c.waivedBy;
    if (c.note) more.note = c.note;
    if (c.at) more.statusAt = c.at === 'INIT' ? now : c.at;
    credit(id, c.status, c.evidence, more);
  }
  for (const [targetId, r] of Object.entries(BASELINE_REVISIONS)) {
    const target = tasks.find(x => x.id === targetId);
    const bucket = revisionTask(target, {title: {zh: target.title.zh + ' · ' + r.zh, en: target.title.en + ' · ' + r.en}, status: r.status, evidence: r.evidence});
    if (r.at) bucket.statusAt = r.at;
    tasks.push(bucket);
  }
  // Point of no return: every evidence path used at init must be git-tracked.
  const allEvidence = [...new Set(tasks.flatMap(x => x.evidence))];
  const trackedSet = tracked(root, allEvidence);
  const untracked = allEvidence.filter(e => !trackedSet.has(e));
  if (untracked.length) throw new Error('untracked evidence at init:\n  ' + untracked.join('\n  '));
  return tasks;
}

// ---------- derived values ----------
function taskSetHash(tasks) {
  // Frozen: what a task is and what finishing it means. Status, evidence, outcome, notes and timestamps stay mutable.
  const rows = tasks.map(x => [x.id, x.type, x.stage, x.owner, x.points, x.subject, x.target || null, [...x.dependsOn].sort(), x.doneCriterion]).sort((a, b) => a[0] < b[0] ? -1 : 1);
  return sha256(JSON.stringify(rows));
}
const pct = (num, den) => den ? Math.round(1000 * num / den) / 10 : 0;
// A creator approval is not "ready" while the latest review of its deliverable asked for changes that no later revision answered.
function revisionGate(task, byId) {
  if (task.stage !== 'creator-approval' || !task.target) return null;
  const reviews = [...byId.values()].filter(x => isInspection(x) && x.stage !== 'technical-inspection' && x.target === task.target && x.status === 'done' && x.outcome === 'changes_requested');
  if (!reviews.length) return null;
  const latest = reviews.map(r => r.statusAt || '').sort().pop();
  const bucket = byId.get(task.target + '.revision');
  if (bucket && bucket.status === 'done' && (bucket.statusAt || '') > latest) return null;
  return {review: reviews.find(r => (r.statusAt || '') === latest).id, revision: bucket ? bucket.id : null, revisionStatus: !bucket ? 'missing' : bucket.status === 'done' ? 'delivered-before-latest-review' : bucket.status};
}
function compute(ledger, root) {
  const tasks = ledger.tasks, byId = new Map(tasks.map(x => [x.id, x]));
  const sumPts = list => list.reduce((s, x) => s + x.points, 0);
  const stageTotals = {};
  for (const stage of Object.keys(STAGES)) {
    const all = tasks.filter(x => x.stage === stage), waived = all.filter(x => x.status === 'not_required'), active = all.filter(x => x.status !== 'not_required'), done = active.filter(x => x.status === 'done');
    stageTotals[stage] = {done: sumPts(done), total: sumPts(active), percent: pct(sumPts(done), sumPts(active)), tasks: active.length, tasksDone: done.length, waivedTasks: waived.length, waivedPoints: sumPts(waived)};
  }
  const cod = stageTotals.coding, con = stageTotals.content;
  // Production completion rounds once, from the raw ratios (never from the rounded sub-percents).
  const production = Math.round(10 * (WEIGHTS.coding * cod.done / cod.total + WEIGHTS.content * con.done / con.total)) / 10;
  const insp = ['technical-inspection', 'visual-review', 'content-qa'].map(s => stageTotals[s]);
  const inspDone = insp.reduce((s, x) => s + x.done, 0), inspTotal = insp.reduce((s, x) => s + x.total, 0);
  const ca = stageTotals['creator-approval'], ops = stageTotals.operations;
  const ready = x => x.dependsOn.every(d => ['done', 'not_required'].includes(byId.get(d)?.status));
  const open = tasks.filter(x => !isProduction(x) && !['done', 'not_required', 'blocked'].includes(x.status) && ready(x));
  const queue = [], needsRevision = [];
  for (const x of open) {
    const gate = revisionGate(x, byId);
    if (gate) needsRevision.push({id: x.id, owner: x.owner, stage: x.stage, review: gate.review, revision: gate.revision, revisionStatus: gate.revisionStatus, nextOwner: 'claude'});
    else queue.push({id: x.id, stage: x.stage, owner: x.owner, status: x.status, points: x.points});
  }
  const byOwner = {};
  for (const owner of Object.keys(OWNERS)) {
    const mine = tasks.filter(x => x.owner === owner);
    const counts = {};
    for (const x of mine) counts[x.status] = (counts[x.status] || 0) + 1;
    const counted = mine.filter(x => x.stage !== 'operations' && x.status !== 'not_required');
    byOwner[owner] = {tasks: mine.length, operationsTasks: mine.filter(x => x.stage === 'operations').length, points: sumPts(counted), pointsDone: sumPts(counted.filter(x => x.status === 'done')), byStatus: counts,
      readyInQueue: queue.filter(q => q.owner === owner).length, revisionsBlockingApproval: owner === 'claude' ? needsRevision.length : 0};
  }
  const areas = {};
  for (const x of tasks) {
    if (x.status === 'not_required') continue;
    const a = areas[x.area] || (areas[x.area] = {});
    const s = a[x.stage] || (a[x.stage] = {done: 0, total: 0});
    s.total += x.points; if (x.status === 'done') s.done += x.points;
  }
  const progress = readJson(root, PROGRESS_REL), meter = progress.completionMeter;
  return {
    production: {zh: '制作完成度', en: 'Production completion', percent: production, percentLabel: production.toFixed(1) + '%',
      formula: 'round1(40 * codingDonePoints/codingTotalPoints + 60 * contentDonePoints/contentTotalPoints)',
      coding: {done: cod.done, total: cod.total, percent: cod.percent, weight: WEIGHTS.coding, tasks: cod.tasks, tasksDone: cod.tasksDone},
      content: {done: con.done, total: con.total, percent: con.percent, weight: WEIGHTS.content, tasks: con.tasks, tasksDone: con.tasksDone}},
    inspection: {zh: '检查与审查（已执行的）', en: 'Inspection and review (performed)', done: inspDone, total: inspTotal, percent: pct(inspDone, inspTotal),
      technical: {done: insp[0].done, total: insp[0].total, percent: insp[0].percent}, visual: {done: insp[1].done, total: insp[1].total, percent: insp[1].percent},
      contentQa: {done: insp[2].done, total: insp[2].total, percent: insp[2].percent},
      waived: {tasks: insp.reduce((s, x) => s + x.waivedTasks, 0), points: insp.reduce((s, x) => s + x.waivedPoints, 0),
        zh: '因创作者已直接批准而免除的审查：不是已执行的工作，不计入分子也不计入分母。', en: 'Reviews waived because the creator approved directly: not performed work, excluded from both numerator and denominator.'}},
    approval: {zh: '创作者批准', en: 'Creator approval', done: ca.done, total: ca.total, percent: ca.percent, tasks: ca.tasks, tasksDone: ca.tasksDone},
    operations: {zh: '运营任务（不计入任何百分比）', en: 'Operations tasks (no percentage)', tasks: ops.tasks, tasksDone: ops.tasksDone},
    release: {finalAccepted: meter.formalApproval?.mvpFormallyAccepted === true, source: PROGRESS_REL + '#/completionMeter/formalApproval/mvpFormallyAccepted', rule: {zh: '正式验收仍为 false，直到 approvalLedger 与 M9 两轮试玩等现有门全部通过；本表不能改变它。', en: 'Final acceptance stays false until the existing gates (approvalLedger, the two M9 playthroughs) pass; this ledger cannot change it.'}},
    stageTotals, byOwner, areas,
    queue: {zh: '待处理（依赖已完成）', en: 'Ready (dependencies done)', count: queue.length, items: queue,
      needsRevision: {zh: '需要 Claude 修订后才能验收（最近一次审查要求修改）', en: 'Needs a Claude revision before acceptance (the latest review asked for changes)', count: needsRevision.length, items: needsRevision}},
    legacy: {zh: '旧版混合交付／验收估算（不是正式验收）', en: 'Legacy mixed delivery/acceptance estimate (not formal acceptance)', percent: meter.percent, percentLabel: meter.percentLabel,
      counters: progress.approvalLedger.counters, source: PROGRESS_REL + '#/completionMeter',
      note: {zh: '旧指标混合了交付与验收，不表示 40.8% 已被正式验收；与制作完成度是不同指标，两者不能相减或比较为“增长”。', en: 'The old meter mixes delivery and acceptance; it does not mean 40.8% is formally accepted. A different metric from production completion; the two are never subtracted or presented as a gain.'}},
  };
}

// ---------- validation ----------
function validate(ledger, root, {checkBaseline = true} = {}) {
  const errors = [];
  const ids = new Set();
  const registry = readJson(root, REGISTRY_REL), inventory = readJson(root, INVENTORY_REL);
  const variants = new Set(registry.entries.map(e => e.visual_id));
  const invIds = new Set();
  for (const c of inventory.categories) for (const s of c.subcategories) for (const i of s.items) invIds.add(i.id);
  const byId = new Map(ledger.tasks.map(x => [x.id, x]));
  for (const x of ledger.tasks) {
    const where = 'task ' + x.id + ': ';
    if (ids.has(x.id)) errors.push(where + 'duplicate id'); ids.add(x.id);
    if (!ID_PATTERN.test(x.id)) errors.push(where + 'id does not match the stable pattern');
    const stage = STAGES[x.stage], rule = TASK_TYPES[x.type];
    if (!stage) { errors.push(where + 'unknown stage ' + x.stage); continue; }
    if (!rule) { errors.push(where + 'unknown task type ' + x.type); continue; }
    if (x.type === 'revision') {
      const target = byId.get(x.target);
      if (!target || !isProduction(target) || target.type === 'revision') errors.push(where + 'a revision must target a production deliverable (and never another revision)');
      else {
        if (x.id !== target.id + '.revision') errors.push(where + 'only one fixed revision bucket per deliverable, named <deliverable>.revision');
        if (x.owner !== target.owner || x.stage !== target.stage) errors.push(where + 'revision owner/stage must equal its deliverable');
        if (x.points !== revisionPoints(target.points)) errors.push(where + 'revision points are fixed at ceil(deliverable points / 2)');
      }
    } else {
      if (x.owner !== rule.owner) errors.push(where + `owner ${x.owner} is not the ${x.type} owner ${rule.owner}`);
      if (x.stage !== rule.stage) errors.push(where + `stage ${x.stage} is not the ${x.type} stage ${rule.stage}`);
      if (/\.revision/.test(x.id)) errors.push(where + 'revision ids are reserved for revision buckets');
    }
    if (!STATUSES[stage.kind].includes(x.status)) errors.push(where + `status ${x.status} not allowed for ${x.stage}`);
    if (!Number.isInteger(x.points) || x.points < POINT_RANGE[0] || x.points > POINT_RANGE[1]) errors.push(where + 'points out of range');
    if (!x.title?.zh || !x.title?.en) errors.push(where + 'needs a bilingual title');
    if (!x.doneCriterion?.zh || !x.doneCriterion?.en) errors.push(where + 'needs a bilingual done criterion');
    if (!x.area) errors.push(where + 'needs an area');
    if (!x.subject?.kind || !x.subject?.id) errors.push(where + 'needs a subject');
    else if (x.subject.kind === 'character-variant' && !variants.has(x.subject.id)) errors.push(where + 'unknown character variant ' + x.subject.id);
    else if ((x.subject.kind === 'scene-gate' || x.subject.kind === 'asset') && !invIds.has(x.subject.id)) errors.push(where + 'unknown inventory item ' + x.subject.id);
    if (x.target !== undefined && !byId.has(x.target)) errors.push(where + 'unknown target ' + x.target);
    // Coding measures runtime capability; it may never wait on creator approval or on adopting art as the default.
    if (x.stage === 'coding') {
      for (const d of x.dependsOn) { const dep = byId.get(d); if (dep && (dep.stage === 'creator-approval' || dep.type === 'integration' || /(native|runtime)-default$/.test(dep.id))) errors.push(where + 'a coding task may not depend on approval or default art adoption: ' + d); }
      if (/\bby default\b|默认(载入|绘制|使用)/.test(x.doneCriterion?.en + ' ' + x.doneCriterion?.zh)) errors.push(where + 'a coding criterion may not require default art adoption');
    }
    for (const d of x.dependsOn) if (!byId.has(d)) errors.push(where + 'unknown dependency ' + d);
    if (x.status === 'done' || x.status === 'not_required') {
      if (!x.evidence.length) errors.push(where + x.status + ' without evidence');
      for (const e of x.evidence) {
        if (typeof e !== 'string' || path.isAbsolute(e) || e.includes('..') || e.includes('\\')) errors.push(where + 'evidence must be a repo-relative path: ' + e);
        else if (!fs.existsSync(rel(root, e))) errors.push(where + 'evidence file not found: ' + e);
        if (isProduction(x) && REJECTED_BASELINE_PATTERN.test(e)) errors.push(where + 'the rejected 32x48 baseline cannot complete a production milestone: ' + e);
      }
      // Reviews may be performed out of order (a reviewer can judge a candidate before its check settles); work and approvals may not.
      if (x.status === 'done' && !isInspection(x)) for (const d of x.dependsOn) if (!['done', 'not_required'].includes(byId.get(d)?.status)) errors.push(where + 'done before dependency ' + d);
    }
    if (x.status === 'not_required') {
      const w = byId.get(x.waivedBy);
      if (!w || w.stage !== 'creator-approval' || w.status !== 'done') errors.push(where + 'not_required needs waivedBy = a done creator-approval task');
    } else if (x.waivedBy) errors.push(where + 'waivedBy only allowed with not_required');
    if (x.outcome !== undefined && (!isInspection(x) || x.status !== 'done' || !OUTCOMES.includes(x.outcome))) errors.push(where + 'outcome only on a done inspection task');
    if (isInspection(x) && x.status === 'done' && !x.outcome) errors.push(where + 'done inspection needs an outcome');
    if (x.outcome === 'changes_requested' && !x.statusAt) errors.push(where + 'a changes_requested verdict needs statusAt');
  }
  const required = ['portrait', 'static-south', 'static-west', 'static-north', 'static-east', 'idle-anim', 'walk-south', 'walk-west', 'walk-north', 'walk-east', 'display', 'runtime-integration'];
  for (const v of variants) for (const m of required) if (!byId.has(`content.char.${v}.${m}`)) errors.push(`variant ${v} lacks milestone ${m}`);
  if (variants.size !== 52) errors.push('registry must hold 52 variants, found ' + variants.size);
  for (const [key, invId] of SCENES) if (!byId.has(`content.scene.${key}.native-pass`) || byId.get(`content.scene.${key}.native-pass`).subject.id !== invId) errors.push('scene gate not covered: ' + invId);
  if (checkBaseline) {
    const revisions = ledger.baseline.revisions;
    const expected = revisions.length ? revisions[revisions.length - 1].taskSetSha256 : ledger.baseline.taskSetSha256;
    if (taskSetHash(ledger.tasks) !== expected) errors.push('task set (ids, types, stages, owners, points, subjects, targets, dependencies, done criteria) differs from the frozen baseline; only revise (one fixed bucket per deliverable) or an owner-authorized baseline revision may change it');
    if (ledger.baseline.weights.coding !== WEIGHTS.coding || ledger.baseline.weights.content !== WEIGHTS.content) errors.push('baseline weights changed');
  }
  return errors;
}

// ---------- serialization (one task per line keeps diffs readable) ----------
function serialize(ledger) {
  const {tasks, ...rest} = ledger;
  const head = JSON.stringify(rest, null, 2);
  return head.slice(0, -2) + ',\n  "tasks": [\n' + tasks.map(x => '    ' + JSON.stringify(x)).join(',\n') + '\n  ]\n}\n';
}
function load(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }
function save(file, ledger) { fs.writeFileSync(file, serialize(ledger)); }
function refresh(ledger, root) { ledger.computed = compute(ledger, root); return ledger; }

function init(root, now) {
  const tasks = buildTasks(root, now);
  const ledger = {
    id: LEDGER_ID, schemaVersion: 2, project: 'rpg-2-star-ocean-the-second', updatedAt: now,
    zh: '制作完成度任务台账：衡量已完成的工作量（编码 40% + 内容 60%）；检查／审查与创作者批准分开计量，均不改变制作分；免除的审查不算已执行的工作；运营任务列出负责方但不计百分比。',
    en: 'Production-completion task ledger: measures work done (coding 40% + content 60%); inspection/review and creator approval are separate meters and never change production credit; waived reviews are not performed work; operations tasks list owners but carry no percentage.',
    brief: BRIEF_REL, updater: 'tools/' + path.basename(__filename),
    sources: {progress: PROGRESS_REL, inventory: INVENTORY_REL, registry: REGISTRY_REL, readinessChecklist: CHECKLIST_REL},
    stages: STAGES, taskTypes: TASK_TYPES, owners: OWNERS, statuses: STATUSES,
    baseline: {frozenAt: now, authorizedBy: 'owner', kind: 'owner-authorized-baseline-revision', weights: WEIGHTS,
      rules: {zh: '任务、类型、阶段、负责方与分值冻结；新版本、收据或测试数都不新增任务。每个交付物最多一个固定修订桶（分值固定为原分值的一半向上取整）；之后的版本只更新或重开该桶，不加分。其他任务集变化须经所有者授权的基线修订，并留下记录。',
        en: 'Tasks, types, stages, owners and points are frozen; new versions, receipts or test counts never add tasks. Each deliverable has at most one fixed revision bucket (points fixed at ceil(points/2)); later versions only update or reopen that bucket and add no points. Any other task-set change needs an owner-authorized baseline revision and leaves a record.'},
      taskCount: tasks.length, taskSetSha256: taskSetHash(tasks), revisions: []},
    closeouts: [],
    tasks,
  };
  refresh(ledger, root);
  ledger.baseline.pointsByStage = Object.fromEntries(Object.entries(ledger.computed.stageTotals).map(([k, v]) => [k, v.total + v.waivedPoints]));
  ledger.closeouts.push({id: 'production-baseline-' + now.replace(/[-:]/g, '').replace('T', '-').replace('Z', '') + '-' + crypto.randomBytes(4).toString('hex'), recordedAt: now, kind: 'baseline',
    title: {zh: '所有者授权的制作完成度基线（不是新完成的工作）', en: 'Owner-authorized production-completion baseline (not newly finished work)'},
    production: ledger.computed.production.percent, inspection: ledger.computed.inspection.percent, approval: ledger.computed.approval.percent, legacyPercentUnchanged: ledger.computed.legacy.percent});
  const errors = validate(ledger, root);
  if (errors.length) throw new Error('init produced an invalid ledger:\n  ' + errors.join('\n  '));
  return ledger;
}

function setTask(ledger, root, opts) {
  const task = ledger.tasks.find(x => x.id === opts.task);
  if (!task) throw new Error('unknown task ' + opts.task);
  const kind = STAGES[task.stage].kind;
  if (!STATUSES[kind].includes(opts.status)) throw new Error(`status ${opts.status} not allowed for ${task.stage}`);
  const credited = opts.status === 'done' || opts.status === 'not_required';
  const evidence = opts.evidence.length ? opts.evidence : (credited ? [] : task.evidence);
  if (credited && !evidence.length) throw new Error('a task cannot be completed without evidence');
  const next = {...task, status: opts.status, evidence, statusAt: opts.now};
  delete next.outcome; delete next.waivedBy;
  if (opts.outcome) next.outcome = opts.outcome;
  if (opts.waivedBy) next.waivedBy = opts.waivedBy;
  if (opts.noteEn || opts.noteZh) next.note = {zh: opts.noteZh || task.note?.zh || '', en: opts.noteEn || task.note?.en || ''};
  // A new verdict on a reviewed task keeps the earlier verdict in its history.
  if (isInspection(task) && task.status === 'done' && task.outcome) next.history = [...(task.history || []), {outcome: task.outcome, statusAt: task.statusAt || null, evidence: task.evidence}];
  // Withdrawing an approval voids any review it waived: that review goes back to the queue.
  const voided = x => task.stage === 'creator-approval' && opts.status !== 'done' && x.waivedBy === task.id;
  // A delivered revision answers the requested change: the review that asked for it reopens for a new verdict.
  const answered = x => task.type === 'revision' && opts.status === 'done' && x.target === task.target && isInspection(x) && x.stage !== 'technical-inspection' && x.status === 'done' && x.outcome === 'changes_requested';
  const reopen = x => { const y = {...x, status: 'todo', evidence: [], statusAt: opts.now}; if (x.outcome) y.history = [...(x.history || []), {outcome: x.outcome, statusAt: x.statusAt || null, evidence: x.evidence}]; delete y.waivedBy; delete y.outcome; return y; };
  const trial = {...ledger, tasks: ledger.tasks.map(x => x === task ? next : voided(x) || answered(x) ? reopen(x) : x)};
  const errors = validate(trial, root).filter(e => e.startsWith('task ' + task.id + ':') || e.includes('dependency ' + task.id));
  if (errors.length) throw new Error('refused:\n  ' + errors.join('\n  '));
  ledger.tasks = trial.tasks;
  ledger.updatedAt = opts.now;
  return refresh(ledger, root);
}

// One fixed revision bucket per deliverable. The first call creates it (a recorded baseline revision, fixed points); every
// later call reopens the same bucket with no new points. Initial production credit is never touched.
function revise(ledger, root, opts) {
  const target = ledger.tasks.find(x => x.id === opts.for);
  if (!target) throw new Error('unknown task ' + opts.for);
  if (!isProduction(target) || target.type === 'revision') throw new Error('revise targets a production deliverable (not a review, an approval or another revision)');
  if (!opts.reasonEn) throw new Error('revise needs --reason-en');
  const id = target.id + '.revision';
  const existing = ledger.tasks.find(x => x.id === id);
  if (existing) {
    ledger.tasks = ledger.tasks.map(x => x === existing ? {...x, status: 'in_progress', statusAt: opts.now, note: {zh: opts.reasonZh || '', en: opts.reasonEn}} : x);
  } else {
    ledger.tasks = [...ledger.tasks, revisionTask(target, {status: 'in_progress', statusAt: opts.now, note: {zh: opts.reasonZh || '', en: opts.reasonEn}})];
    ledger.baseline.revisions.push({at: opts.now, kind: 'revision-bucket', addedTaskIds: [id], reason: {zh: opts.reasonZh || '', en: opts.reasonEn},
      effect: {zh: '只增加分母；已完成的原始制作保持计分；本交付物之后的版本只重开此桶。', en: 'Adds to the denominator only; the finished original keeps its credit; later versions of this deliverable only reopen this bucket.'}, taskSetSha256: taskSetHash(ledger.tasks)});
  }
  ledger.updatedAt = opts.now;
  return refresh(ledger, root);
}

function parse(argv) {
  const opts = {command: argv[0], evidence: [], ledger: null, now: new Date().toISOString().replace(/\.\d{3}Z$/, 'Z')};
  const single = {'--ledger': 'ledger', '--now': 'now', '--task': 'task', '--status': 'status', '--outcome': 'outcome', '--waived-by': 'waivedBy',
    '--note-en': 'noteEn', '--note-zh': 'noteZh', '--for': 'for', '--reason-en': 'reasonEn', '--reason-zh': 'reasonZh', '--owner': 'owner', '--stage': 'stage', '--area': 'area', '--root': 'root'};
  for (let i = 1; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === '--dry-run') opts.dryRun = true;
    else if (a === '--evidence') opts.evidence.push(argv[++i]);
    else if (a === '--status' && opts.command === 'list') opts.filterStatus = argv[++i];
    else if (single[a]) opts[single[a]] = argv[++i];
    else throw new Error('unknown argument ' + a);
  }
  return opts;
}

function printSummary(c) {
  const p = c.production;
  console.log(`Production completion / 制作完成度: ${p.percentLabel}  (coding ${p.coding.done}/${p.coding.total} pts = ${p.coding.percent}% x40, content ${p.content.done}/${p.content.total} pts = ${p.content.percent}% x60)`);
  console.log(`Inspection performed: ${c.inspection.done}/${c.inspection.total} pts = ${c.inspection.percent}%  (technical ${c.inspection.technical.done}/${c.inspection.technical.total}, visual ${c.inspection.visual.done}/${c.inspection.visual.total}, content QA ${c.inspection.contentQa.done}/${c.inspection.contentQa.total}; waived ${c.inspection.waived.tasks} excluded)`);
  console.log(`Creator approval: ${c.approval.done}/${c.approval.total} pts = ${c.approval.percent}%   operations ${c.operations.tasksDone}/${c.operations.tasks} tasks (no %)   release finalAccepted=${c.release.finalAccepted}`);
  for (const [o, v] of Object.entries(c.byOwner)) console.log(`  ${o.padEnd(8)} tasks ${v.tasks} (ops ${v.operationsTasks}) points ${v.pointsDone}/${v.points} ready ${v.readyInQueue} ${JSON.stringify(v.byStatus)}`);
  console.log(`Ready queue: ${c.queue.count}; needs Claude revision before acceptance: ${c.queue.needsRevision.count}   Legacy mixed estimate (separate metric): ${c.legacy.percentLabel}`);
}

function main() {
  const opts = parse(process.argv.slice(2));
  const root = opts.root ? path.resolve(opts.root) : ROOT;
  const file = opts.ledger ? path.resolve(opts.ledger) : rel(root, LEDGER_REL);
  if (opts.command === 'init') {
    if (fs.existsSync(file)) throw new Error('ledger already exists; the baseline is frozen: ' + file);
    const ledger = init(root, opts.now);
    if (!opts.dryRun) save(file, ledger);
    printSummary(ledger.computed);
    console.log((opts.dryRun ? 'DRY RUN ' : '') + 'INIT ' + ledger.tasks.length + ' tasks, baseline ' + ledger.baseline.taskSetSha256.slice(0, 16));
    return;
  }
  const ledger = load(file);
  if (opts.command === 'check') {
    const errors = validate(ledger, root);
    const stored = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n'); // autocrlf checkouts compare as LF
    const again = serialize(refresh(load(file), root));
    if (stored !== again) errors.push('stored ledger is not byte-identical to a recompute (run recompute)');
    if (errors.length) { for (const e of errors) console.log('FAIL ' + e); process.exit(1); }
    printSummary(ledger.computed);
    console.log(`CHECK OK ${ledger.tasks.length} tasks; production ${ledger.computed.production.percentLabel}; legacy ${ledger.computed.legacy.percentLabel} unchanged`);
    return;
  }
  if (opts.command === 'recompute') { refresh(ledger, root); if (!opts.dryRun) save(file, ledger); printSummary(ledger.computed); return; }
  if (opts.command === 'set') { setTask(ledger, root, opts); if (!opts.dryRun) save(file, ledger); printSummary(ledger.computed); return; }
  if (opts.command === 'revise') { revise(ledger, root, opts); if (!opts.dryRun) save(file, ledger); printSummary(ledger.computed); return; }
  if (opts.command === 'summary') { printSummary(ledger.computed); return; }
  if (opts.command === 'queue') {
    for (const q of ledger.computed.queue.items) console.log(`READY ${q.owner.padEnd(8)} ${q.stage.padEnd(21)} ${q.status.padEnd(12)} ${q.id}`);
    for (const q of ledger.computed.queue.needsRevision.items) console.log(`NEEDS-REVISION ${q.id} <- ${q.review} (revision ${q.revision || 'missing'}: ${q.revisionStatus})`);
    console.log('READY ' + ledger.computed.queue.count + ' NEEDS-REVISION ' + ledger.computed.queue.needsRevision.count); return;
  }
  if (opts.command === 'list') {
    for (const x of ledger.tasks.filter(x => (!opts.owner || x.owner === opts.owner) && (!opts.stage || x.stage === opts.stage) && (!opts.filterStatus || x.status === opts.filterStatus) && (!opts.area || x.area === opts.area)))
      console.log(`${x.owner.padEnd(8)} ${x.stage.padEnd(21)} ${x.status.padEnd(12)} ${String(x.points).padStart(2)} ${x.id}`);
    return;
  }
  throw new Error('unknown command ' + opts.command);
}

module.exports = {LEDGER_REL, PROGRESS_REL, STAGES, TASK_TYPES, WEIGHTS, compute, validate, serialize, setTask, revise, taskSetHash, refresh, load, init, buildTasks, revisionGate};
if (require.main === module) {
  try { main(); } catch (error) { console.error('ERROR ' + error.message); process.exit(1); }
}
