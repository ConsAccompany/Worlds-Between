# Worlds Between: Hermes takeover

Prepared 2026-10-23T03:42:58.071066+00:00. Creator timezone America/New_York.

## Authority and first read

The creator explicitly requested Hermes on their Hostinger VPS to take over this project, with all associated assets, repository access, skills and current context. This supersedes older Codex-coordinator and canceled DeepSeek takeover assignments. Preserve the game and its frozen scoring baseline. Hermes is the incoming coordinator; the creator retains art/canon/scope approval and human playtests.

Read this document, `AGENTS.md`, `docs/workflow.md`, the canonical ledger, Bible, progress and operating registry before changing the game. Read only relevant evidence for the next task, not every historical report. The complete task map is `docs/handoff/rpg-2-star-ocean-the-second_hermes_complete-task-map_v01_20261023-034257-b6c39f27.json`; it includes every task, done criterion, dependency, owner, evidence and status. It is a handoff snapshot; the canonical ledger remains authoritative after work resumes.

## Where everything lives

VPS working repository: `/home/kel/projects/worlds-between/repo` (user kel). Parent project directory contains `tooling`, `vault`, `incoming`, and `handoff`.

- Current game/source/data/documentation: the Git checkout, repository `ConsAccompany/Worlds-Between`.
- Verified pre-handoff main: `1c5793224c2d5b77f2dc9fc19b92cefff15b0ec9`.
- Last ordinary game-content/default revision: `d5f204373c17c62e45e92dea14c3a2e85c525062`. Later commits include source-only candidates.
- Current full canonical records: `outputs/rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json`; `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json`; `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`; `outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json`; operating registry linked by `docs/workflow.md`.
- Complete historical Git asset snapshot: `assets/handoff/` contains 23 packages, index and original origins for 8,815 unique asset/provenance files. Historical versions use frozen gitBlob IDs; a current scene file may legitimately differ. The old archive verifier can reject changed current scenes; use the new project-ops `archive-verify` command instead of modifying scenes to match an old snapshot.
- New full local/worktree snapshot: `../vault/index.json`, with SHA-256, byte size, original path aliases and a storage path relative to the parent project directory for every unique file. Canonical files are reused; unique historical/unfinished bytes are in `../vault/objects`. Read the manifest coverage/exclusions/errors and transfer proof before claiming coverage. Search/restore with the project-ops helper. Never restore a whole old worktree over the current game.
- `../incoming/lexplore59/` preserves the latest uncommitted Lin Que source bank and checker, with a manifest and missing-check contract. These files are NOT completed ledger credit, current defaults, or artistic approval.
- Primary PC migrated to `D:/UserData/Documents/Codex/2026-10-12/rpg-2-star-ocean-the-second`; protected dirty primary is behind. Old C: paths in reports are historical. Do not reset or treat old worktrees as alternate current sources. Their eligible unique assets/source are in the vault.

## Verified progress, including what is NOT complete

Production **60.5% before takeover → 60.5% after setup (+0.0 points)**. Coding111/111 points,23/23 tasks. Content644/1881 points,211/715 tasks. Inspection21.6% →21.6%; creator approval7.8% →7.8%. Frozen task count1183. Final sprite sets0/52; accepted final scene art5/12; human post-art playtests0/2; formal MVP acceptancefalse. The old mixed44.2% is a separate historical metric. Setup/transfers/new versions do not earn game-production points.

The code and playable paths are implemented; most missing production points are character content across the frozen 52-variant roster. Do not promise100% by merely finishing the presently playable party or silently shrinking that roster. Existing game systems, scene assets, enemies, VFX, UI and audio production are largely complete; inspection and creator acceptance remain separate.

## Current canon and creator decisions

- PC single-player bilingual EN/ZH science US+Canada MVP; NYC/Catskills; start2537-05-25. Locations include City Hall Park, Yonkers, Washington Capitol ruins, Chicago Loop.
- 51 identities/52 variants; five Earth civilization spheres, separate final portal planet, Antarctica DLC; no persistent companion followers.
- Fixed simple whole-hour travel. Generic flight information, no named airports or airport/traffic micromanagement. The creator rejected simulation-level travel detail.
- Character direction references Sea of Stars, with original identities. Exploration48 logical pixels; battle display proportion0.65. Smooth, fluid, well-paced motion; more frames or green metrics alone do not establish fluidity.
- Ordinary MVP default use, with polish deferred, was explicitly authorized for heroine, male lead, Zhao Ling, Liang Xu, Ji Cheng; sentry and patrol; Chicago style42; Washington exterior style45 and records room style48; NYC City Hall style46. Consult the Bible for precise files/scope. Default adoption is NOT final art/motion approval.
- Earlier outdoor proposals were rejected for style inconsistency. Creator selected the Chicago material/light/teal-tech unified direction. Do not revive the rejected City Hall v04 or rejected coarse32x48/heroine battlev16/v17r2 baselines.
- Full visual sets and human timed playtests require the creator. Ask only essential creative/scope questions after showing actual accessible gameplay evidence; continue independent tasks while waiting. Do not ask implementation-parameter questions or repeatedly present invisible images. A working direct image/GIF link has been necessary.
- Finish missing useful MVP deliverables and play/release blockers; defer face/material/limb micro-polish and unrelated concepts until after MVP.

## Immediate handoff task: Lin Que exploration bank (lexplore59)

Claude and DeepSeek both exited0 before takeover. No worker remains active. Their source/check outputs exist locally and are transferred under incoming. No independent native-app/Godot/visual acceptance was completed. Five ledger tasks remain TODO: `content.char.lin-que.idle-anim`, `walk-south`, `walk-west`, `walk-north`, `walk-east` under that prefix. Reassign these to actual workers through the audited CLI only when starting; do not claim prior output as your own.

Author: `tools/rpg-2-star-ocean-the-second_lin-que_exploration-source-author_unapproved-lexplore59-v01_20261022-231558-6875dc75.py`. Independent checker: matching `lin-que_exploration-package-check` tool. Inputs: existing Lin four-direction statics and reusable Jiang Lan jexplore39 author. No need to start another generator or concept.

Outputs:4 animatedPXO files (41frames each),4 staticORA,164 individual sourcePNGs and matching runtime copies/data. Contract80x112,density2,pivot40,104,48logical. Idle4frames/direction; walk12 phases40ms; 12 stop-entry bridges/direction with2middle frames and byte-exact neutral endpoint. Author reports341/341 deterministic outputs and52 source checks; independently reproduce before credit. DeepSeek checker pass is technical producer evidence, not independent coordinator approval.

Required next steps: safely materialize incoming only if current files absent/identical; inspect source/hash/foot contracts; run native Pixelorama export equality on Linux with diagnostic capture; run bounded Godot test/actual gameplay-scale bilingual fit and normal-speed capture; separate source-production criteria from runtime/display/stop-host integration. Preserve truthful failures. Award only existing task points if their criteria pass. A full set, normal defaults, motion approval and supplemental stop playback are distinct gates.

Known limitations: front/back in-place walk residual5.6logicalpx; side40ms foot slip≤1source texel but frame-hold60fps excursion remains10.667sourcepx. Cape/scarf follow torso only. Generic loader returns immediately to idle and does not demonstrate supplemental stop bridges. Old static/portrait art is unapproved. Lin Que is NOT selected by normal defaults; changing that needs explicit creator authorization. Do not call this fluid or fully integrated from source checks alone.

## Remaining work and order

1. Finish/reconcile the existing Lin Que source-bank boundary and missing validation; do not open parallel cosmetic candidates.
2. Use the canonical remaining-task list to finish incomplete four-direction/editable exploration, battle action sets and integration for required characters. Reuse the complete heroine/party pipeline; preserve original identities. Finish one useful set before another broad batch.
3. Complete outstanding source-bound character/runtime/normal-input inspection and release checks. Existing code done status does not waive remaining QA. Investigate actual play/data-loss failures immediately.
4. Complete actual audio listening/content QA (currently BLOCKED/unperformed), remaining visual/motion reviews and full-set creator presentations. PCM/RMS and cue wiring are not listening evidence.
5. Stage the current playable Windows bundle for the creator's two timed integrated playtests, record real results and fix blockers. Automated/scripted runs cannot count as human playtests.
6. Remaining canon choices and artistic acceptance stay creator-owned; use exact canonical task IDs. Do not count ordinary default use as final acceptance.
7. Keep Game Bible/progress and GitHub verified and consistent. Hosted private Site publishing requires the creator's authenticated Codex/Sites bridge, which is not present on this VPS; preserve source/data/fallback, report this boundary instead of claiming a deployment.

## Tools, commands and Git access

Project Python: `../tooling/venv/bin/python` (NumPy/Pillow/PyYAML). Godot: `../tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64`. Pixelorama: `../tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64`. Node22,Git,FFmpeg,Xvfb,Mesa and CJKfonts are installed. Use `source ../tooling/worlds-between-env.sh` for session-local aliases/environment; do not replace global settings.

Game import: `"$GODOT" --headless --path game --editor --import --quit`. Smoke: `"$WB_PYTHON" tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 60 --expect M1_SMOKE_OK --log work/<unique-log> -- "$GODOT" --headless --path game --script res://tests/m1_smoke.gd`. Actual rendered capture needs `xvfb-run -a` and the existing game capture scripts; headless alone is not visual evidence.

Ledger CLI: `node tools/rpg-2-star-ocean-the-second_production-completion_ledger-cli_v01_20261018-140533-3b436630.js summary|check|set|reassign`. Hermes is an audited non-creator owner. Transfer only current work, preserving task IDs/points/criteria/status/evidence. Creator-task transfers are refused. A separate checker reviews delegated output; the producer never supplies creator approval. Owner transitions add no progress.

Git uses a VPS-generated read/write deploy key scoped only to this repository, configured in this clone's core.sshCommand. Private key remains outside the project in kel's SSH directory. No personal GitHub token or PC private key was copied. Clone/fetch and a push dry-run were verified. This grants Git push; GitHub issue/PR/release REST writes are NOT authenticated by that SSH key. Public reads work; broader API access needs a separately scoped token later, not a copied personal credential. The `gh` CLI is installed but is not broadly logged in.

Commit only explicit reviewed files; inspect staged raw bytes, required tests and remote HEAD before pushing. Never git add dot, blanket reset, force-push or overwrite unrelated dirty files. Avoid hooks copied from unknown old worktrees. Keep historical asset hashes raw; do not silently normalize old CRLF. Preserve .gitattributes bytes and add narrow rules only. Do not publish incoming/vault or private account records to GitHub wholesale.

To revoke this project access, delete deploy key ID167381824 in this repository's GitHub Deploy Keys settings; remove the dedicated key on the VPS only after access is no longer needed. No new public service/firewall was opened. Hermes itself was not upgraded or restarted.

## Skills and capability boundaries

Trusted repo-local `.hermes/skills/` contains production, Godot/native assets, and evidence/integration procedures; load these in the project session. Existing Hermes debugging/GitHub skills remain installed. Read their scope instead of assuming gh API authentication.

Native Pixelorama exact export, application diagnostics and GUI SaveAs/reopen are separate checks. Known shader/resource diagnostics exist on the old PC setup; compare the actual Linux run and disclose them. GUI SaveAs/reopen has not been established by CLI output. The VPS can run native Linux Godot and offscreen rendering; Windows EXE execution, listening and creator playtests need the appropriate host/human. Existing Windows playtest bundle is preserved in the vault: `work/n56-8ef48084/rpg-2-star-ocean-the-second_mvp_native-playtest-bundle_unsigned_20261022-211046-8ef48084.zip`, SHA2563c9f0bf25270b7b3e90a5c3552e0b06d87ad6a4409a0b5f4c89e4708790d7a53; verify rather than assume latest source build.

No provider/account tokens, private keys, cloud-credit controls, browser profiles or personal account/budget logs were transferred. Hermes currently uses the VPS's existing openai-codex subscription configuration (gpt-6.1-sol); preserve it. Do not use Claude API/cloud/extra paid usage, buy/top-up, enable auto-reload or paid fallback. Local Claude/DeepSeek desktop harnesses are not installed/authenticated on the VPS and must not be claimed available. If delegated providers are later connected, verify exact authorized account/model and limits first; DeepSeek insufficient credit means stop project production, preserve handoff and do not top up. No new recurring schedules are created by this transfer.

## Finish each real task

Capture before/after production, inspection and approval from the canonical ledger; report percentage-point change. Retain task IDs, actual worker, base/tested/integrated revisions, source/editable files and hashes, command results, failed checks, independent verdict and next task. Do not add points for screenshots/reports/another version or fill time with repeated audits. Update existing ledger/Bible through their CLIs. When a required human decision blocks one item, record it and continue another useful task. Full completion requires the existing acceptance gates, not merely a100% production display.
