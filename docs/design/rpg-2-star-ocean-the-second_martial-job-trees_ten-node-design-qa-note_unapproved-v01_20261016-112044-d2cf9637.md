# 武艺 job trees: ten-node redesign (PROPOSAL) — design and QA note

- Date: 2026-10-16 11:20 local (EDT)
- Status: **PROPOSAL. All 50 nodes are pending balance and creator review.** Nothing here is approved or implemented.
- Data: [`outputs/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112044-4e3b550a.json`](../../outputs/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112044-4e3b550a.json). It holds:
  - the 50 nodes, the rules and the shared mechanics
  - a provisional JP table
  - an embedded JSON Schema
  - the embedded validation results and metrics

  Its `sha256-text-lf-v1` is `8cf65b63c0d1ae376ca0ea3b796f2f9083cc7a26c0261bd87fa464bb347ebd3d`.
- Companion validator (deterministic, read-only, no dependencies): [`tools/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-validate_unapproved-v01_20261016-112044-706c17da.js`](../../tools/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-validate_unapproved-v01_20261016-112044-706c17da.js). Run it from the repo root with `node tools/…706c17da.js`.
- Scope: the five 武艺 series (守护, 剑术, 重武, 武道, 长兵), with 10 nodes each, 50 in total. This is 50 of the 200 job nodes asked for in creator decision note §2 and §8.2.
- Not touched: runtime, Game Bible, progress meter and progress docs, other job-tree proposals, and art. Nothing was staged, committed or pushed.

## Sources read

- Global `~/.codex/AGENTS.md`, for the file naming pattern.
- The approved roster: `outputs/…_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json`.
  - Copied **verbatim** for each series: name, English name, role, the five stage names and `finalQuest`.
  - A check compares them with this file **and** with Game Bible `jobProposal.series`.
- The creator decision note `…_creator-decisions-2026-10-15_…-39efc292.md`. It sets the skill rules, the AI and combo rules, no missed content, and the US science MVP places.
- The 研学 ten-node JSON and QA note, used as the schema and constraint template:
  - energy bands per stage
  - linear or shrinking rank steps, r5 ≤ 2 × r1
  - the shared stacking caps
  - the banned-term list (extended here)
  - optional-only science utility
- The superseded drafts, for lineage only:
  - `…_martial-job-trees_skill-node-proposal_v01_…-1c9e73ab.json` (剑术, 重武, 武道, 长兵)
  - the 守护 tree in `…_four-job-trees_…-5a72d0be.json`
- Game Bible chapters 3 and 4, read only:
  - flat side-view battlefield
  - energy does not regenerate in battle
  - after a battle, survivors recover 20% and downed characters return at 10%
  - **no level cap**
- Runtime, read only:
  - `battle_arena.gd`:
    - guard cuts a hit to 30% and costs 6 energy per guarded hit
    - dodge costs 12 energy and gives 0.27 s of invulnerability
    - enemy windups last 0.48–0.65 s
    - melee reach is 69 px
    - job skill cost is 10 + 3 × stage
  - `growth_rules.gd` and `app_state.gd`: the two existing 剑术 MVP skills, 破锋斩 / Edge Break and 回旋剑势 / Sword Arc.

## Rules applied

- The 2 nodes of a stage open **at rank 1** as soon as the character enters that stage. They cost 0 JP and have no extra level gate.
- Stage 5 also needs the series final quest. Completing it once opens stage 5 for the whole party.
- JP only raises ranks 2–5, and the maximum rank is 5. There are **no exclusive branches**: every character can eventually learn all 10 nodes to rank 5.
- Proposed JP base cost per rank is 30 / 45 / 60 / 75, the same as the 研学 proposal. This conflicts with the runtime skeleton's provisional 35 / 55 / 80 / 110; see the open points.
- Every node has:
  - Chinese and English names
  - a concrete first-rank effect (horizontal px, seconds, % of attack or % of max HP)
  - five-rank scaling
  - energy cost and cooldown (actives), or trigger rules (passives)
  - AI use and avoid conditions
  - a stacking rule with declared cap categories
- Banned in all node text (32 terms): terrain, elevation, obstacles, cover, jumping, launch/airborne, walls, slopes, pits, ground cracks, stealth, ambush.
  - Dashes, backsteps and knockback are horizontal only and stop at the arena edge.
  - Area effects only trigger attacks. They never block movement and leave no lasting zone on the field.
- AI:
  - AI reads the same windup cues as the player, with no early knowledge.
  - It uses no consumables, and combo AI stays off.
  - The two passives that move a character (同袍代受, 天衡步) can be switched off in the character's strategy.
  - 稳息 heals only its user, so it never enters the party heal order (downed allies first, then urgent healing).

## Role identity: five distinct ways to fight

| Series | Identity | It never… |
|---|---|---|
| 守护 | **Where the damage lands.** Redirects a share of an ally's or objective's damage (护线), forces enemies to target it (挑衅号令), steps in to take big hits (同袍代受), party damage reduction (DR) and shields | knocks back or slows (长兵), deals counter damage (武道), pre-empts windups (剑术) |
| 剑术 | **Before the hit lands.** Strikes during an enemy windup: non-boss attacks are interrupted, boss windups are delayed. 剑势 stacks drive the combo | needs a successful guard or dodge, shields others, knocks back |
| 重武 | **Charge and armour.** Super armour while charging, 裂甲 stacks, damage to armour gauges and protective plates, circular impacts, in-place stagger only | redirects damage, pre-empts windups, counters after impact, pushes or pierces in lines |
| 武道 | **After the hit lands.** Counters only once a guard succeeds or a dodge makes an attack miss. Builds 劲 and sustains itself with 调息 (self only) | protects others, pre-empts windups, pushes |
| 长兵 | **How far away the enemy is.** Full power in the 70–160 px reach band and weaker up close; horizontal line pierce, knockback, approach slow, intercepts fast enemies | redirects damage, relies on guard success, charges armour breaks |

Stage pairs (stage 1 → 5):

| Series | Nodes |
|---|---|
| 守护 | 护线·挑衅号令 / 壁垒架势·同袍代受 / 阵线庇护·守护回响 / 不屈界限·坚阵鼓舞 / 守誓穹幕·万界誓约 |
| 剑术 | 破锋斩·连刃 / 回旋剑势·看破 / 破势斩·观锋 / 无隙锋线·流刃追击 / 界线一闪·界域剑心 |
| 重武 | 裂甲重击·山岳定锚 / 破甲楔·震击 / 震岳重砸·持重蓄势 / 崩甲连携·裂隙追击 / 地脉震响·撼岳之势 |
| 武道 | 调息击·借力回击 / 沾衣反打·稳息 / 连环身法·吐纳归元 / 化劲掌·静心守势 / 无形连环·无相守意 |
| 长兵 | 直线突刺·枪距本能 / 拦截扫·驻枪拒止 / 贯阵·枪线压制 / 牵制旋·天衡步 / 星轨贯穿·天枢枪阵 |

- Totals: 35 active and 15 passive nodes. 守护 has 6A/4P; the other four have 7A/3P. Every stage has at least one active.
- The distinction is enforced by checks, not just described:
  - **Signature-mechanic tags** must be present (守护 7/10, the other four 10/10). No node may carry another series' signature tag.
  - **Exclusive vocabulary** in effect text:
    - 击退/枪尖区 → 长兵 only
    - 分担/代受/护线 → 守护 only
    - 反击/反打/反震/劲 → 武道 only
    - 蓄力/裂甲/护甲值/防护板/霸体 → 重武 only
    - 剑势/看破 → 剑术 only
- Tactical roles do not repeat within a series. The highest cross-series role Jaccard is 0.11 (剑术/武道, which share only `energy_economy` and `finisher`).
- The sword/martial split is about timing:
  - 剑术 acts during the windup, before impact (看破, 破势斩, 界域剑心).
  - 武道 acts on impact or on a miss (沾衣反打, 连环身法, 化劲掌, 无相守意).

## Final-quest fit (quest text unchanged)

These nodes suit each quest. Ordinary attacks, guard and allies stay valid too.

| Series | Fit |
|---|---|
| 守护 | Beacons can be targets of 护线, 阵线庇护 and 守誓穹幕. 挑衅号令 pulls attackers off a beacon. 同袍代受 can take a heavy hit meant for a beacon |
| 剑术 | Quick windup → 看破 (stage 2). Heavy windup → 破势斩 (stage 3). Feint → 无隙锋线 (stage 4) |
| 重武 | Plates → 破甲楔 (stage 2) and 裂甲重击. Exposed core → 裂隙追击 (stage 4) |
| 武道 | Four methods: 沾衣反打 (catch and counter), 连环身法 (dodge counter), 化劲掌 (redirect force), 借力回击 (guard counter). 稳息 between rounds |
| 长兵 | 驻枪拒止 and 拦截扫 intercept fast enemies. 枪线压制 slows line crossers. 天枢枪阵 covers the zone. 贯阵 and 天衡步 keep the assault boss in the reach band |

## Numbers for an endgame with no level cap

- No value grows with character level:
  - damage, healing and shields are % of attack or % of max HP
  - control is in seconds, distance in px
  - energy returns are flat points with a per-battle trigger cap
- The validator restricts scaling units to these types and rejects level-scaling wording.
- Rank curves are linear or shrinking. The maximum r5/r1 is 2.00, reached by four nodes: the three energy-return passives (4 → 8) and 枪距本能 (8% → 16%).
- Energy cost, cooldown and trigger counts never change with rank.
- Proposed all-source stacking caps. They do not loosen with level or difficulty tier:

| Cap | Limit |
|---|---|
| Enemy damage taken | +25% |
| Enemy defense down (incl. defense ignore) | 30% |
| Skill DR (separate from guard's base 30%) | 50% |
| Minimum damage taken | ≥ 10% of raw |
| Shield per character | 30% max HP |
| Status resistance | 60% |
| Self damage bonus | 40% |
| Enemy slow | 40% |
| Redirected share of one hit | 50% |
| Windup delay per attack cycle | 0.6 s |
| Energy returned per node per battle | 32 |
| 武道 self-heal per battle | 60% max HP |
| Charge-time reduction | 60% (floor 0.24 s per charge step) |
| Reflected damage | ≤ 200% of attack per reflect |

- Control diminishing: a second interrupt, stagger or knockback within 3 s is halved, and a third is ignored until the window ends. Bosses are never interrupted or staggered: interrupts become windup delays, and knockback is halved. Forced targeting has a 6 s lockout (10 s for bosses).
- At rank 5, the largest single-node contributions are:

| Category | Largest single node at rank 5 |
|---|---|
| Damage DR | 40 (破势斩, one hit) |
| Self damage bonus | 40 (界线一闪 with 5 剑势) |
| Self-heal | 60 (稳息 × 3) |
| Energy return | 32 |

  All are within their caps.
- The embedded metrics model a 120 s battle with an energy pool of 60 + 2 × (level − 1). Casting every active on cooldown would need:

| Series | Energy | Low pool covers it at level |
|---|---|---|
| 守护 | 866 | ~404 |
| 剑术 | 1575 | ~759 |
| 重武 | 1294 | ~618 |
| 武道 | 1222 | ~582 |
| 长兵 | 1338 | ~640 |

  Below those levels, energy is the limit. Above them, cooldowns and per-battle caps are. Throughput is therefore bounded at any level.

## Science-region MVP utility (optional, only where plausible)

| Node | Utility | MVP places |
|---|---|---|
| 重武 裂甲重击 (stage 1) | 强力开启: force open marked jammed lockers and supply crates for ordinary supplies that are also sold in shops and dropped in battle | 扬克斯郊外, 华盛顿特区 · 国会大厦遗址（科技勘察前哨）, 芝加哥 · 卢普区 |

- The utility contains no story items or records and changes no route.
- Jammed lockers stay in place, so anyone who later switches to 重武 can open them.
- It needs the user's current series to be 重武. `storyMandatory` is `false`.
- The other 49 nodes have no believable non-combat use, so none was forced on them. The validator rejects utility text that opens shortcuts, paths or archive entries.

## Validation (actual results)

The embedded run happened before the file was written: 22/22 pass. The standalone companion run adds `embedded-results-match`. Command and output on the written file:

```
node tools/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-validate_unapproved-v01_20261016-112044-706c17da.js
PASS file-proposal-status — PROPOSAL / pending balance and creator review
PASS series-set — guardian, sword, heavy, martial, polearm
PASS approved-text-verbatim — 5 系列 × (名称/定位/5 阶/终阶任务) 与两处来源逐字一致；50 个 stageName 一致
PASS ten-nodes-two-per-stage — 5 × 10 = 50；每阶 2 个
PASS node-schema — 文件通过；50/50 节点通过
PASS distinct-nodes — 50 个 id / 50 个中文名 / 50 个英文名；与研学提案重名 0 个
PASS unlock-and-rank-rules — 50/50；JP 表只含第 2–5 级；无互斥分支
PASS active-passive-energy — guardian 6A/4P; sword 7A/3P; heavy 7A/3P; martial 7A/3P; polearm 7A/3P
PASS non-exponential-ranks — 全部为固定或递减加法步长；最大 r5/r1 = 2.00
PASS unlimited-level-safe — 50/50；单位限于 % 攻击力、% 生命上限、% 原始伤害、%、秒、px、点能量
PASS capped-stacking — 50/50；各类别第 5 级单节点最大贡献：damage_redirect 37/≤50；ally_damage_reduction 40/≤50；energy_return 32/≤32；status_resistance 32/≤60；shield_total 18/≤30；windup_delay 0.4/≤0.6；self_damage_bonus 40/≤40；enemy_defense_down 20/≤30；charge_time_reduction 50/≤60；enemy_damage_taken_up 18/≤25；damage_floor 15/≥10；self_heal_per_battle 60/≤60；enemy_slow 23/≤40
PASS energy-return-capped — guardian_n06_guardians_echo 单次 ≤8（本系列最低主动 10）× 4 次 = 32；sword_n06_edge_reading 单次 ≤8（本系列最低主动 13）× 3 次 = 24；martial_n06_breath_return 单次 ≤8（本系列最低主动 10）× 4 次 = 32
PASS no-terrain-elevation-obstacle-jump-stealth — 32 个禁用词，50 个节点与 5 段系列说明 0 命中
PASS distinct-roles — 系列内 10/10 不同；最大跨系列 Jaccard 0.11（sword/martial）
PASS series-signature-mechanics — guardian 7/10; sword 10/10; heavy 10/10; martial 10/10; polearm 10/10
PASS exclusive-vocabulary — 50 个节点 0 越界
PASS ai-use — 50/50
PASS science-mvp-utility-optional — 1 个：heavy_n01_armor_cracking_blow(强力开启)；其余 49 个节点为 null
PASS proposal-marking — 50/50
PASS superseded-lineage — 32/35 个草案节点有继承关系；舍弃 3 个：guardian_counter_window, polearm_shared_line, sword_parry_focus
PASS runtime-lineage — sword_n01_edge_break=sword_slash, sword_n03_sword_arc=sword_arc
PASS source-hashes — 10 个来源一致
PASS embedded-results-match — 22 项一致
proposal sha256-text-lf-v1 8cf65b63c0d1ae376ca0ea3b796f2f9083cc7a26c0261bd87fa464bb347ebd3d
23/23 pass, 0 warn, 0 fail
```

- **The first build failed 3 checks and was not written:**
  - 剑术 had only 2 signature tags, but the schema floor was 3. The floor was lowered to 2; 剑术 still has 10/10 signature nodes.
  - Two passive AI notes were under 8 characters. They were expanded.
  - 护线 said "减伤" without declaring that cap. The wording was changed.
- **Mutation test: 23/23 caught.** A throwaway script outside the repo injected 23 defects into in-memory copies, and each one failed its target check:
  - a stage name or final quest edited
  - an accelerating rank curve
  - JP used for unlock
  - a stage-5 node without the final-quest gate
  - a terrain word, and the English word "jump"
  - knockback on 守护
  - the DR cap exceeded
  - an undeclared slow
  - an oversized energy return
  - energy outside its stage band
  - level-based scaling
  - a foreign signature tag
  - a duplicate role, a duplicate name
  - a utility that opens a shortcut, a non-MVP location
  - status other than PROPOSAL
  - reused lineage
  - runtime cost drift
  - AI using a consumable
  - a tampered embedded result
- **Line endings:** a CRLF copy validates 23/23 and gives the same `sha256-text-lf-v1`. The written file has 0 CR bytes.
- **Untouched files:** 498 protected text files were hashed before and after (`outputs`, `docs`, `docs/design`, `docs/qa`, `game/scripts`, `game/data/growth`, `tools`). The only content change was in `outputs/…_mvp-progress_state_…json`, made by another session's commit `4bf778f` (it also moved HEAD from `15c9b73`). The only files this pass added are this note, the JSON and the validator. Other new files that appeared (an adaptive-job-trees proposal and checker, a static-pilot QA note, tmp prompts) belong to parallel sessions. The index is empty: nothing was staged.
- The generator, hash-snapshot and mutation scripts stay in `%TEMP%\wb-martial-ten-node` and were not added to the repo.

## Lineage

32 of the 35 superseded draft nodes carry forward. The rest were redirected or dropped so the series stay distinct:

- **Changed:**
  - 震退 → 震击: in-place stagger, no push.
  - 破阵横扫 → 震岳重砸: circular, not a line.
  - 持重蓄势: triggers on a full-charge hit, not on a guard.
  - 化劲掌: stagger instead of push.
  - 无形连环: spends 劲 instead of reading windups.
  - 支点守势 → 驻枪拒止: an active stop-thrust, not tied to guarding.
  - 逆隙反斩 → 看破.
- **Dropped:**
  - 守护·反击窗口: counters belong to 武道.
  - 剑术·听锋: post-guard bonus belongs to 武道.
  - 长兵·枪线协防: relied on allies guarding.
- **Runtime:** 破锋斩 and 回旋剑势 keep their stage, name and current energy cost (13, 16). Only their designed numbers are new. The runtime was not changed.

## Open points for balance and creator review

1. All numbers are placeholders calibrated to today's runtime (see Sources).
2. Several nodes depend on systems the runtime does not have yet:
   - windup types (quick, heavy, feint)
   - a boss flag
   - armour gauges and protective plates
   - an enemy "fast approach" state
   - protected-objective units (beacons, escorts)
   - forced targeting
   - super armour and interrupt rules for party members
   - ailments and resistance
   - marks from other series
   - battles with several enemies: today's arena has 1 enemy, so area, line, intercept and redirect effects are worth less there
3. The JP table conflicts with the runtime skeleton (30/45/60/75 vs 35/55/80/110). Both are unapproved, and creator note §8.2 is still open.
4. Only one science utility is proposed (重武). Please confirm whether more are wanted.
5. 守护回响 and 吐纳归元 can return up to 32 energy per battle each. That is within the shared cap, but it is generous for a 60–80 pool at level 1, so it is a balance-review candidate.
6. Not done here: the remaining 10 series (100 nodes) and the 510 personal nodes. *(Updated 13:52: the 应变 proposal now exists, so 灵觉 (50 nodes) is the only job tree left.)*
7. **Cross-proposal caps, provisional (found by the independent check below):**
   - **Redirect.** This file caps all-source redirect of one hit at 50% (`damage_redirect`). The 应变 proposal caps beast-companion redirect at 40% (`allyDamageRedirect`). Neither file says how the two combine. With a 守护 and a 驯兽 in the party, rank-5 values on one hit sum to 77%: 护线 37 + 护伴哨 32 + 万灵同路 8. The suggested reading is that the beast's 40% counts inside this file's 50% all-source cap. This is not decided; balance review and the creator should settle it.
   - **Energy return.** This file allows up to 32 energy returned per node per battle. The 研学 proposal's largest is 24 (紧急回收), and the 应变 proposal has no refund nodes. This is a balance difference, not a rule conflict.

## Independent verification (2026-10-16 13:52 EDT, separate session)

The earlier session hit its quota limit before an independent result. This pass ran that verification. **No defect was found in the JSON, so the proposal, its hash and its embedded results are unchanged.** Nothing was staged, committed or pushed.

- **Companion validator:** `node tools/…706c17da.js` gives **23/23 pass, 0 warn, 0 fail** and `sha256-text-lf-v1 8cf65b63…7ebd3d`. Running it from `%TEMP%` (outside the repo) gives the same result.
- **Independent cross-check:** [`tools/rpg-2-star-ocean-the-second_martial-adaptive-job-trees_ten-node-independent-crosscheck_unapproved-v01_20261016-135211-122bcb8b.js`](../../tools/rpg-2-star-ocean-the-second_martial-adaptive-job-trees_ten-node-independent-crosscheck_unapproved-v01_20261016-135211-122bcb8b.js) (`sha256-text-lf-v1 82ad5b4b…cf7ae`). It is written separately from both companion validators and covers 武艺 and 应变 together. Result: **13/15 pass, 2 warn, 0 fail**; the two warnings are open point 7.
  - Approved text: all 10 series' aptitude, name, English name, role, five stage names and `finalQuest` equal both the roster (`…6f2b9c11.json`) and Game Bible `jobProposal.series`. All 100 `stageName`s match, and so do the runtime catalog's Chinese names.
  - Rule shape:
    - 100 nodes = 10 series × 5 tiers × 2 (slots 1, 2).
    - `maxRank` 5; every node unlocks at rank 1 for 0 JP on stage entry.
    - The final-quest gate is on exactly tier 5.
    - JP keys are 2–5 only.
    - There are 0 branch/exclusive keys or exclusive-choice phrases.
  - Status: 100/100 nodes and both files are PROPOSAL / pending. 8 words such as "approved" appear in prose; each one is a reference to the approved roster text, a path containing "unapproved", or "XP 曲线尚未定稿". None is an approval claim.
  - Names: across the 150 job nodes (研学 + 武艺 + 应变), every id, Chinese name and English name is unique. There are 0 clashes with 139 personal skill names: the 51 character-card signatures, the superseded 5-node trees and the core-cast 10-node proposal. **The companion validator does not check 武艺 against 应变 or against personal names.** That was shown by a spot mutation: a node renamed to 瞄准射击 passed it. The cross-check covers that gap.
  - Numbers: every rank 2–5 text and every rank-1 `baseEffect` contains its scaling value. Steps are flat or shrinking; the highest r5/r1 is 2.00.
  - Energy: the energy bands are identical in 研学, 武艺 and 应变, and every active's cost is inside its band. Ranges are ≤ 584 px.
  - Schema: the file passes its embedded 2020-12 schema under an independently written subset validator.
  - Runtime: 破锋斩/Edge Break (E13) and 回旋剑势/Sword Arc (E16) match the names in `app_state.gd` and the cost formula `10 + 3 × stage` in `battle_arena.gd`. Both match `sword_slash`/`sword_arc` in the catalog. The cited runtime constants were re-read in HEAD and in the working copy: guard 30%, 6 energy per guarded hit, dodge 12 energy / 0.27 s, windup 0.48–0.65 s, melee reach 69 px.
  - Canon scan:
    - 0 superseded place or sphere terms (上海/松江/良渚/星外/奇幻).
    - The utility places are all in the US science MVP set: 扬克斯郊外; 华盛顿特区 · 国会大厦遗址（科技勘察前哨）; 芝加哥 · 卢普区.
    - No AI condition uses items.
    - 稳息 heals only its user.
  - Undeclared caps: a separate text scan for slow, DR, redirect, damage-taken and defence-down effects found nothing that isn't declared. 同袍代受 is an intercept of the whole hit, not a share; 守护回响 only triggers on redirects.
- **Mutation test of the cross-check:** 24/24 injected defects across both files were caught, each by its target check. The harness is outside the repo in `%TEMP%\wb-jobtree-indep\`.
- **Spot mutation of the companion validator:** 5/6 caught. It caught knockback on 守护, a rank-text mismatch, rank 6, 跳跃 and an edited final quest. It missed the cross-proposal name clash, as described above.
