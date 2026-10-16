# MVP completion meter: agent closeout routine / MVP 完成度：任务收尾流程

The progress state `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json` carries `completionMeter`. This is a **weighted delivery estimate, not formal approval**. Formal approval exists only in `approvalLedger` (creator acceptance) and the two M9 human playtests. The Game Bible cloud tracker reads GitHub `main`, so the meter only shows there after a push.

进度状态文件中的 `completionMeter` 是**加权交付估算，不是正式批准**。正式批准只看 `approvalLedger` 中的创作者验收和 M9 两轮真人试玩。Game Bible 云端读取 GitHub `main`，推送后才会显示。

Fixed baseline: core gameplay 20 (M1, M3–M6), global world/travel 10 (12 `m2Expansion.gates`), science playable content 10 (four M7 gates kept in the meter), character art 25 (0/52 accepted runtime sprites), science environment art 20 (0/11 scene gates), final integrated validation 15 (0/2 post-art human playtests). Baseline on 2026-10-15: **35.0%**.

CLI: `tools/rpg-2-star-ocean-the-second_mvp-completion-meter_recompute-and-task-closeout-cli_v01_20261015-233032-d296a2cb.js`

## After every completed task / 每完成一项任务

1. If the task really changed a gate, first update the authoritative field. Use `steps[].status`, `m2Expansion.gates[].status`, or `approvalLedger` (a counter **and** an item with `status: "accepted"`, `acceptanceKind: "runtime-sprite" | "scene-visual" | "post-art-playtest"`, and evidence). The meter's own M7 gates change only through `--set-gate`.
2. Record the closeout. This step is mandatory, even when nothing changed:
   ```
   node tools/<cli> record --title-en "<what was done>" --title-zh "<中文>" \
     [--gate <category>/<gate> | --gate <counter-category>]... [--set-gate science-playable-content/<gate>=done] \
     [--evidence <repo-relative path>]...
   ```
   - If no gate changed, omit `--gate`. The CLI writes a zero-change receipt (`changed: false`, delta 0).
   - Every changed count must be claimed with `--gate` and backed by at least one existing `--evidence` file.
   - The CLI refuses unclaimed changes, claims for unchanged gates, and unknown categories, gates or statuses. Fix the input. Do not work around the refusal.
   - Concepts, unapproved static frames, direction approvals and smoke tests never count as visual acceptance. Post-art playtests are held at 0 until both art categories are 52/52 and 11/11.
3. Verify: `node tools/<cli> check` must print `CHECK OK`. Then run `node tests/mvp-completion-meter/rpg-2-star-ocean-the-second_mvp-completion-meter_recompute-and-closeout_check_v01_20261015-233032-af0786b1.js` and any tests for the task itself.
4. Push the verified change through the existing workflow:
   - Stage explicit paths only: the state JSON plus your task files. Never use `git add -A`, and never sweep in other workstreams' dirty files. Use the selective-index or clean-clone method when files are mixed.
   - Commit, then push to GitHub `origin` on the branch your dispatch names (`main` unless told otherwise).
   - Report the commit ID, the closeout ID, and the before → after percentage.
   - If a test fails, do not push. Report the failure.

Use `--dry-run` to preview. Changing weights, denominators or gate sets is a baseline revision for the creator, not task progress.
