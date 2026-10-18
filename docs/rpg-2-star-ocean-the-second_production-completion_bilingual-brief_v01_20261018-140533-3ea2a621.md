# 制作完成度 / Production completion — brief (v01, owner-authorized baseline 2026-10-18T18:10:59Z)

- Ledger (data + derived numbers): `outputs/rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json`
- The one updater and checker: `tools/rpg-2-star-ocean-the-second_production-completion_ledger-cli_v01_20261018-140533-3b436630.js`
- Invariant tests: `tests/production-completion/rpg-2-star-ocean-the-second_production-completion_invariants_check_v01_20261018-140533-2978305e.js`
- Local Game Bible: server v05 serves `/production`; the production view shows a compact panel that only displays the ledger's `computed` block.

## 1. 这是什么 / What it measures

**中文：** 新的主指标「制作完成度」衡量**已完成的工作量**，不是验收。它与旧的 40.8%（验收加权估算）是**不同指标**，不能相减，也不能说成“从 40.8% 增长”。旧的 40.8% 原样保留为历史与验收视图（在界面中折叠并标为旧版），此前全部 139 条收尾记录、批准值和正典不变。正式验收（final accepted）仍为 false，直到 approvalLedger 与 M9 两轮试玩等现有门全部通过。

**English:** The new primary label "Production completion / 制作完成度" measures **work done**, not acceptance. It is a **different metric** from the legacy 40.8% acceptance-weighted estimate; the two are never subtracted or presented as a gain. The 40.8% meter is kept unchanged as the legacy / acceptance view (collapsed and labelled legacy in the UI); all 139 earlier closeouts, approval values and canon are untouched. Final acceptance stays false until the existing gates (approvalLedger, the two M9 playthroughs) pass.

## 2. 公式 / Formulas (one derivation, rounded once)

```
production  = round1( 40 × codingDone/codingTotal + 60 × contentDone/contentTotal )
coding%     = round1( 100 × codingDone/codingTotal )          (shown separately)
content%    = round1( 100 × contentDone/contentTotal )        (shown separately)
inspection  = (technical-inspection + visual-review points credited) / their total     separate meter
approval    = creator-approval points done / total                                      separate meter
```

Credited statuses are `done`, and `not_required` for a review that a done creator approval made unnecessary (`waivedBy`). Review and approval tasks never carry production points, so a pending review, a requested change, or an approval toggle cannot add or remove production credit (tests 3–4).

## 3. 阶段与负责方 / Stages and owners (one owner per task)

| Stage | Owner | Meter |
| --- | --- | --- |
| `coding` | `claude` | production (40%) |
| `content` (native pixel content, scene passes, integration) | `claude` | production (60%) |
| `technical-inspection` (automated Godot checks) | `claude` | inspection |
| `visual-review` (in-game visual / browser review) | `codex` | inspection |
| `creator-approval` (art acceptance, canon choices, the 2 human playthroughs) | `creator` | approval |

Work that needs two parties is two tasks (e.g. `content.scene.city.native-pass` → `review.scene.city` → `creator.scene.city.accept`). Cloud/Site publication is Codex's and is not an MVP game task.

## 4. 冻结的任务点 / Frozen milestone points

| Deliverable (count) | Production milestones (points) | Inspection / approval tasks (1 point each unless noted) |
| --- | --- | --- |
| Character variant (52, registry) | portrait 1, static-south 3, static-west/north/east 2 each, idle-anim 2, walk-south/west/north/east 3 each, display 2, runtime-integration 2 = **28** | runtime-set check, static-south review, runtime-set review, approve portrait, approve south static, accept runtime sprite, accept display |
| Combat set (5 playable) | combat-static 3, combat-actions 8, combat-integration 2 = **13** | set check, static review, set review, accept set |
| Enemy (sentry, patrol) | static 2, battle-animation 6, runtime-default 2 = **10** | check, review, accept art (+ sentry direction approval) |
| Science scene gate (12, inventory scene-quality) | plate 4, wiring 3, native-pass 12, native-default 2 = **21** | check, review, scene-quality acceptance |
| Fixed revision milestone (changes requested before baseline: map, City Hall Park, Yonkers room 1, female battle static) | scene 6, combat 3 | — |
| Coding (23 tasks, 111 points) | M1 8, M3 12, M4 10, M5 10, M6 8; M2 travel 31; M7 route 6 + endpoint 3; settings 3; runtime pipelines 20 | M2 acceptance tests 3 |
| Other content | M7 investigations/companions 10; VFX 12; audio 15; UI final visuals 13 | review + creator acceptance per group |
| Validation | — | pre-playtest regression 3; playthrough 1 and 2 (3 each); final MVP acceptance 2; canon choices 1 each |

Totals: 1176 tasks; coding 111, content 1864, technical inspection 77, visual review 131, creator approval 244 points. Baseline task-set hash `1a04b791a658266b…`. New versions (v01–v14), receipts or test-assertion counts are never tasks; adding one fails the baseline check (test 8). Only `add-rework` (a fixed revision milestone, 1–8 points, adds to the denominator only) or an owner-authorized baseline revision can change the task set, and each leaves a `baseline.revisions` record.

## 5. 证据对账规则 / Evidence reconciliation

- A task is done only with **git-tracked** evidence that exists (QA note, manifest, test, acceptance record). Unknown or uncommitted work = not done; no guessed partial percent.
- **Credited even though unapproved:** delivered static frames (female south v8 approved; female north; male v8pair, Liang Xu, Ji Cheng, Zhao Ling south), female battle static v14 + its revision, sentry static + v2 21-frame strip, scene plates in the runtime, committed native scene passes (opt-in counts for `native-pass`, not for `native-default`), map v03r2 (runtime), the four ambient loops and the discovery cue, all M1–M7 coding gates.
- **Not credited:** the rejected 32×48 placeholders (the checker refuses their paths for production tasks), generated concept images (battle arena), uncommitted work (Yonkers outskirts clue fixtures, City Hall Park v07, Chicago v04/v05 beyond test-harness opt-in, WDC room 2 as default), all movement (female south run v07 is `in_progress`: the creator asked for more run/stop polish), every other direction, idle animations, displays, combat action sets, runtime-default integrations, VFX, themed music, UI/combat SFX, settings UI.
- **Reviews:** Codex/root verdicts recorded in tracked notes or closeouts count as done reviews with an `outcome` (`technical-pass` for root's technical-only acceptances, `changes_requested` for the Liang Xu audit). The three creator-accepted rooms and the approved female south still have `not_required` reviews (waived by that approval; withdrawing the approval reopens the review).

## 6. 当前数字 / Current numbers (baseline)

| Meter | Numerator / denominator | Percent |
| --- | --- | --- |
| **Production completion / 制作完成度** | 40 × 91/111 + 60 × 324/1864 | **43.2%** |
| Coding / 编码 | 91 / 111 | 82.0% |
| Content / 内容 | 324 / 1864 | 17.4% |
| Inspection / 检查与审查 | 23 / 208 (technical 14/77, visual 9/131) | 11.1% |
| Creator approval / 创作者批准 | 17 / 244 | 7.0% |
| Final accepted / 正式验收 | — | false |
| Legacy acceptance estimate (different metric) | unchanged | 40.8% |

By area (content): characters 69/1456, combat 6/68, enemies 8/20, scenes 227/270, VFX 0/12, audio 4/15, UI visuals 0/13, M7 content 10/10. Scenes are high because nine native passes are delivered; most await review, and only 3/12 are accepted.

By owner: Claude 806 tasks, 429/2052 points (135 done, 1 in progress, 670 todo). Codex 131 tasks, 9/131 (5 done, 4 not required, 122 todo; **8 ready**). Creator 239 tasks, 17/244 (17 done, 222 todo; **56 ready**: 43 concept portraits, 4 south statics, 7 scene acceptances, 2 canon choices).

## 7. 更新方法 / How to update

```
node tools/<cli> set --task review.scene.city --status done --outcome changes_requested --evidence docs/qa/<note>.md
node tools/<cli> add-rework --for creator.scene.city.accept --points 6 --title-en ".." --title-zh ".." --reason-en ".."
node tools/<cli> check        # schema, owners, evidence, dependencies, frozen baseline, byte-identical recompute
node tools/<cli> queue | summary | list --owner codex --stage visual-review --status todo
```

## 8. 仍未知 / Open unknowns

- Whether the old in-game display images and the 32×48-era combat pipeline can carry high-density sets (the runtime pipeline tasks are `todo` until proven).
- Whether Codex reviewed the current WDC room 1 v02, Yonkers room 1 v06, Chicago v03r1/v05 and map v03r2 (no tracked verdict found → `todo`, listed in the ready queue).
- Point weights are a frozen owner-authorized judgment of relative effort; they are not measured hours.
