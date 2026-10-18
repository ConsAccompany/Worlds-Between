# 制作完成度 / Production completion — brief (v01, owner-authorized baseline 2026-10-18T18:54:14Z)

- Ledger (data + derived numbers): `outputs/rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json`
- The one updater and checker: `tools/rpg-2-star-ocean-the-second_production-completion_ledger-cli_v01_20261018-140533-3b436630.js`
- Invariant tests: `tests/production-completion/rpg-2-star-ocean-the-second_production-completion_invariants_check_v01_20261018-140533-2978305e.js`
- Local Game Bible: server v05 serves `/production`; the production view shows a compact panel that only displays the ledger's `computed` block.
- The baseline was corrected before its first publication after two root reviews (movement credit, owners by task type, waivers, one revision bucket per deliverable, review reconciliation; then capability-based coding criteria and a stronger freeze). Root authorized this correction. Baseline task-set hash `06164cec29168879…`.

## 1. 这是什么 / What it measures

**中文：** 新的主指标「制作完成度」衡量**已完成的工作量**，不是验收。旧的 40.8% 是**混合了交付与验收的旧版估算**，不表示 40.8% 已被正式验收；它原样保留（界面中折叠并标为旧版）。两者是不同指标，不能相减，也不能说成“增长”。此前 139 条收尾记录、批准值和正典不变；正式验收仍为 false。

**English:** The new primary label "Production completion / 制作完成度" measures **work done**, not acceptance. The old 40.8% is a **legacy mixed delivery/acceptance estimate**; it does not mean 40.8% is formally accepted. It stays unchanged, collapsed and labelled legacy in the UI. The two are different metrics, never subtracted or presented as a gain. The 139 earlier closeouts, approval values and canon are untouched; final acceptance stays false.

## 2. 公式 / Formulas (one derivation, rounded once)

```
production  = round1( 40 × codingDonePoints/codingTotalPoints + 60 × contentDonePoints/contentTotalPoints )
inspection  = performed (done) points / active points of technical-inspection + visual-review + content-qa
              (waived reviews are excluded from BOTH numerator and denominator)
approval    = creator-approval done points / total
operations  = Codex dashboard inspection and publication: listed with owners, in no percentage
```

Points are frozen effort weights; task counts are shown separately and are a different number.

**What is frozen:** each task's id, type, stage, owner, points, subject, target, dependencies **and done criterion** (so a criterion cannot be weakened silently). Status, evidence, outcome, notes and timestamps stay mutable.

**Coding = normal runtime capability, not art adoption.** A coding task is done when the capability works in the normal runtime, verified through an opt-in flag or a test fixture with targeted tests (e.g. the character / combat sprite pipelines and the battle backdrop loader). Adopting a set or backdrop for the shipped game is a separate content task (`runtime-integration`, `native-default`, `runtime-default`) plus a creator acceptance. The checker refuses a coding task that depends on an approval or a default-adoption task, or whose criterion requires default adoption (test 8b). The three pipeline/backdrop tasks stay `todo` until real implementation evidence exists (the backdrop loader is being built in another worktree). Review, approval and operations tasks never carry production points, so a pending review, a requested change, a waiver or an approval toggle cannot change production (tests 4–5).

## 3. 负责方按任务类型 / Owners by task type

| Task type | Stage | Owner |
| --- | --- | --- |
| `feature-code`, `pipeline-code` | coding | claude |
| `native-pixel` (Pixelorama statics, walks, scenes, VFX, UI visuals), `integration`, `content-writing`, `audio-production` | content | claude |
| `concept-generation` (the 52 image-generated source portraits) | content | **codex** |
| `revision` (one per deliverable) | same as the deliverable | same as the deliverable |
| `technical-check` | technical-inspection | claude |
| `visual-review` | visual-review | codex |
| `audio-qa` (content / audio QA, not "visual review") | content-qa | codex |
| `creator-acceptance`, `canon-choice`, `playtest` | creator-approval | creator |
| `ops-inspection`, `ops-publication` (new dashboard browser check, Site publication) | operations (no %) | codex |

Work needing two parties is two tasks (deliverable → review → acceptance).

## 4. 冻结的任务点 / Frozen milestone points

| Deliverable (count) | Production milestones (points) |
| --- | --- |
| Character variant (52) | portrait 1 (Codex), static-south 3, static-west/north/east 2 each, idle-anim 2, walk/run south/west/north/east 3 each, display 2, runtime-integration 2 = **28** |
| Combat set (5 playable) | combat-static 3, combat-actions 8, combat-integration 2 = **13** |
| Enemy (sentry, patrol) | static 2, battle-animation 6, runtime-default 2 = **10** |
| Science scene gate (12) | plate 4, wiring 3, native-pass 12, native-default 2 = **21** |
| Coding (23 tasks, 111 points) | M1 8, M3 12, M4 10, M5 10, M6 8; M2 travel 31; M7 route 6 + endpoint 3; settings 3; runtime pipelines 20 |
| Other content | M7 investigations/companions 10; VFX 12; audio 15; UI final visuals 13 |
| **Revision bucket** | exactly one per deliverable, fixed at ceil(points / 2) |

Each review / acceptance / check is 1 point; playthroughs 3 each; final MVP acceptance 2; pre-playtest regression 3. Totals: 1181 tasks; coding 111, content 1873, technical inspection 77, visual review 130 (4 waived), content QA 1, creator approval 244, operations 2 (no %).

**No version farming:** `revise --for <deliverable>` creates that deliverable's one bucket the first time (recorded in `baseline.revisions`, denominator only); every later candidate version reopens the same bucket with no new task or points. A second bucket, a re-pointed bucket or a version-as-task fails the frozen-baseline check (tests 6, 10). When a bucket is delivered, the review that asked for the change reopens for a new verdict (history kept).

## 5. 证据对账 / Evidence reconciliation

- Done only with **git-tracked** evidence. Unknown or uncommitted = not done; no guessed partial percent.
- **Initial work keeps its credit; requested changes are a separate bucket:**
  - female south walk/run: v07 delivered (1942e31, closeout 20587ab6) = **done**; run/stop polish = its one revision bucket, **done** as a produced technical revision (v10 + r1, 364d47a: focused check 16/16, each boot down within 88.9 ms at mixed frame times, release to stop up to 272.2 ms; root: slower cadence clear, leading leg still diagonal — gait and fluidity unapproved). Other directions not started.
  - map (v03r2 after Codex's v03r1 judgment), City Hall Park (v06 after the v04 rejection), Yonkers room 1 (v03–v06 after the v02 rejection), female battle static (v12–v14 after v11 feedback), WDC Capitol west (v13 after root's v12r2 critique): buckets **done**.
  - Liang Xu south static: Codex audit asked for changes → bucket **todo**.
- **Reviews recorded as performed:** Yonkers room 1 v06 root verdict (closeout 5597d7f5) = changes_requested; WDC v13 root verdict (QA 075675cf: dome clear, localized collapse improves; ground grainy, foliage blocky; art unapproved) = changes_requested; Liang audit = changes_requested; male, Ji Cheng, female battle v14 and sentry = technical-pass.
- **WDC v13 proven only as far as it goes:** revision delivered (QA 075675cf, opt-in flag 9071882); native-default **todo** (off by default); technical inspection **done** from the deterministic fixed-60 fps check that root accepted at 22/22 (0636b40: 20 fixed frames, 8 accepted rooms 0 px) — technical only, not art acceptance.
- **Waived, not performed:** 4 reviews made unnecessary by direct creator approvals (3 accepted rooms, female south still) are listed separately and excluded from the inspection meter. Withdrawing such an approval reopens its review.
- **Approval queue:** an acceptance whose latest review asked for changes, with no revision delivered after that verdict, is listed under "needs Claude revision", never as ready (Yonkers room 1, WDC exterior, Liang Xu). No approval completes automatically.
- **Not credited:** rejected 32×48 placeholders (refused by the checker), concept-only art (battle arena), uncommitted work, other directions, idle animations, displays, combat action sets, default integrations, VFX, themed music, UI/combat SFX, settings UI. Existing runtime-sprite acceptance stays 0/52.

## 6. 当前数字 / Current numbers (baseline)

| Meter | Numerator / denominator (points) | Percent |
| --- | --- | --- |
| **Production completion / 制作完成度** | 40 × 91/111 + 60 × 334/1873 | **43.5%** |
| Coding / 编码 | 91 / 111 (17 / 23 tasks) | 82.0% |
| Content / 内容 | 334 / 1873 | 17.8% |
| Inspection performed / 已执行的检查 | 21 / 204 (technical 14/77, visual 7/126, content QA 0/1; 4 waived excluded) | 10.3% |
| Creator approval / 创作者批准 | 17 / 244 | 7.0% |
| Operations (no %) | 0 / 2 tasks | — |
| Final accepted | — | false |
| Legacy mixed delivery/acceptance estimate | unchanged | 40.8% |

Content by area: characters 74/1460, combat 5/67, enemies 8/20, scenes 233/276, VFX 0/12, audio 4/15, UI visuals 0/13, M7 content 10/10. Scenes are high because the native passes are delivered; only 3/12 are accepted.

By owner (tasks; points exclude operations and waivers):
- Claude 757 tasks, 387/2009 points (86 done, 671 todo); 0 inspection tasks ready, plus 3 revisions blocking acceptances (Yonkers room 1, WDC exterior, Liang Xu).
- Codex 185 tasks incl. 2 operations, 59/179 points (59 done — 52 portraits + 7 performed reviews; 4 waived; 122 todo); 7 ready (6 reviews + dashboard browser inspection).
- Creator 239 tasks, 17/244 points (17 done, 222 todo); 53 ready (43 concept portraits, 3 south statics, 5 scenes, 2 canon choices).

## 7. 更新方法 / How to update

```
node tools/<cli> set --task review.scene.city --status done --outcome changes_requested --evidence docs/qa/<note>.md
node tools/<cli> revise --for content.scene.city.native-pass --reason-en ".."     # one bucket; later calls reopen it
node tools/<cli> check        # owners by type, evidence, dependencies, one-bucket rule, frozen baseline, byte-identical recompute
node tools/<cli> queue | summary | list --owner codex --stage visual-review --status todo
```

## 8. 画廊 / Current gallery (Game Bible)

Still 11 current cards. The Washington exterior slot is now v13 in the normal game behind `--wdc-capitol-west-v13` (9071882, actual 640×360 runtime capture, off by default, technical only, art unapproved); the two run cards are now the v10r1 1× showreels (364d47a, 1280×720 window of the 640×360 canvas, heroine 48 px, not native 640; produced technical revision, gait/fluidity unapproved). v12r2 and the two v07 reels stay as pinned history. The gallery narrative calls 40.8% the legacy mixed delivery/acceptance estimate. No other card changed.

## 9. 仍未知 / Open unknowns

- Whether the old in-game display images and the 32×48-era combat pipeline can carry high-density sets (pipeline tasks `todo`).
- No tracked Codex verdict yet for WDC room 1 v02, City Hall Park v06, Chicago v03r1/v05, map v03r2 or Zhao Ling (ready in the Codex queue).
- Who generated the m8 scene plates is not recorded; plate/wiring tasks stay Claude-owned integration work.
- Point weights are a frozen owner-authorized judgment of relative effort, not measured hours.
