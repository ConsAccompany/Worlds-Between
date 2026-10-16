# 应变 job trees: ten-node redesign (PROPOSAL) — design and QA note

- Date: 2026-10-16 11:21 local (EDT, −04:00)
- Status: **PROPOSAL. All 50 nodes are pending balance and creator review.** Nothing here is approved or implemented.
- Data: [`outputs/rpg-2-star-ocean-the-second_adaptive-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112114-ec58fa23.json`](../../outputs/rpg-2-star-ocean-the-second_adaptive-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112114-ec58fa23.json) (168 KB). It holds the nodes, rules, JP table and aptitude economics, an embedded JSON Schema and the validation results. Its `sha256-text-lf-v1` is `f3b287d6b180bb479aac76c79e39fd0222623a9dfcb3159b6fa2faddaa814797`.
- Validator (companion, deterministic, read-only): [`tools/rpg-2-star-ocean-the-second_adaptive-job-trees_ten-node-proposal-check_unapproved-v01_20261016-112114-e0ce1cbc.js`](../../tools/rpg-2-star-ocean-the-second_adaptive-job-trees_ten-node-proposal-check_unapproved-v01_20261016-112114-e0ce1cbc.js), `sha256-text-lf-v1` `0e9c742ece0a46074087b5f4086df50b6ad5abd01b4cebf082900726db576bec`. Run `node tools/<that file>` from any directory. It uses the shared content-hash helper.
- Scope: the five 应变 series (弓猎, 枪械, 游击, 驯兽, 行商). Each gets 10 nodes, 50 in total. Together with the 研学 proposal (2026-10-15), this makes 100 of the 200 job nodes asked for in creator decision note §2 and §8.2.
- Nothing was staged, committed or pushed. No runtime, catalog, Game Bible, meter, old draft or art file was edited.

## Sources read

- `C:\Users\hkzha\.codex\AGENTS.md`: file-naming rules, followed for all three new files.
- **The approved roster** `outputs/…_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json`. For each series these are copied verbatim, and a check confirms it: name, English name, role, the five stage names and `finalQuest`.
- **Creator decision note** `docs/design/…_creator-decisions-2026-10-15_…39efc292.md`, §2–§3 and §5:
  - 10 nodes per series, 2 per stage, max rank 5, all branches learnable.
  - AI rules: no consumables by default, downed allies first, combo AI off.
  - Every combo participant pays energy.
  - Price effects propagate along trade routes.
- **Template**: the 研学 ten-node JSON (`…842e0540.json`) and its QA note (`…540056b9.md`). They supply the structure, energy bands, the r5/r1 ≤ 2 rule, the banned-term scan and the stacking-cap style.
- **Superseded drafts, for lineage only**:
  - `outputs/…_adaptive-job-trees_skill-node-proposal_v01_20261013-225032-9b7e26c4.json` (弓猎, 枪械, 驯兽, 行商)
  - the 游击 tree in `outputs/…_four-job-trees_skill-node-proposal_v01_20261013-224554-5a72d0be.json`
- **Game Bible state, read only**:
  - chapter 1: flat, fixed-size horizontal field; no jumping; terrain has no effect
  - chapter 3: energy does not regenerate; post-battle recovery 20% / 10%
  - chapter 4: aptitude discount, 50% spread
  - chapter 6: the party never carries goods; NPC stand-in runs at 80%
  - character cards: personal skill names and adaptive aptitudes
- **Runtime, read only**:
  - the ten-node skeleton catalog `game/data/growth/…_science-mvp-skeleton_…e36e5d2c.json`: node ids and the current 35/55/80/110 JP table
  - `growth_rules.gd`: `jp_cost`
  - `battle_arena.gd`: field x 28–612, firearms range 175 px, job skill cost `10 + 3 × stage`, dodge 12
  - `app_state.gd`: JP rewards
  - `commerce_ledger.gd`: base 100, NPC 80%, Fair Quote +5%/rank

## Rules applied

- **Unlock and JP.** Entering a stage opens its 2 nodes at rank 1, with no JP and no level gate. Stage 5 also needs the series final quest. JP raises ranks 2–5 only. There are no `branch` fields and no exclusive choices.
- **Rank curves.** Fixed or shrinking additive steps; rank 5 ≤ 2× rank 1. Energy, cooldown and trigger counts are the same at every rank. `rankProgression` text is generated from the values, and `baseEffect` states the rank-1 value. The validator checks both.
- **Battlefield.**
  - All ranges are horizontal pixels, ≤ 584 px.
  - Dashes, backsteps and beast following are ground movement with no collision.
  - No terrain, elevation, obstacle, cover or jump effect. The scan covers 22 terms in Chinese and English.
- **No stealth.** Every node keeps the user visible and targetable. Dodge invulnerability stays the generic rule. 游击 "无迹" is defined as "leaves no opening".
- **Passives are never permanent unconditional combat buffs.** Each of the 18 passives has a trigger and one of these limits:
  - not a combat effect: 4 commerce/trade passives
  - a per-battle cap of ≤ 10: 10 passives
  - a window of ≤ 10 s with an internal cooldown at least as long as the window: 3 passives
  - stacks that are spent on use: 1 passive (积势)
- **Energy.** No node refunds energy from nothing. The four 行商 routing nodes always cost the merchant more than the allies gain or save:
  - 补给协议: ≤ 8 saved for a cost of 10
  - 应急调拨: ≤ 24 saved for 32
  - 万路协约: ≤ 30 saved for 46
  - 万路兜底: the merchant pays 1.5× the shortfall
- **Stacking caps (proposal).**
  - Limits: enemy damage taken ≤ 25%, enemy defence down ≤ 30%, enemy slow ≤ 40%, ally damage reduction ≤ 50%, beast redirect ≤ 40%, ally first-hit bonus ≤ 30%.
  - The validator sums each series' rank-5 values as if they were all active at once.
  - Tightest: 驯兽 redirect 40/40 and 驯兽 slow 37/40.
- **AI.**
  - Every node has `aiBehavior`: default on/off, a use condition and an avoid condition, written in px and HP%.
  - No condition uses items.
  - 万灵同路 is the only heal. It cannot revive, and its AI waits for revive-capable skills when an ally is down.
  - 万路协约 touches combos, so it is **off by default**, like combo AI.

## Series identity (distinct per series)

| Series | Identity | Stage 1 → 5 node pairs |
|---|---|---|
| 弓猎 | Observe → mark → precision. Long single-target shots; the party sees marked enemies' wind-ups early; weak-point windows; reveals decoys and copies (final quest: find the true body). | 瞄准射击·猎迹标记 / 掩护箭·弱点辨识 / 退步连射·长线追矢 / 真身辨识·双向警戒 / 天际追猎·承迹 |
| 枪械 | Range bands (near ≤ 120, mid 120–260, far > 260 px) and switchable rounds (precision / suppression / breaker); shield breaking (final quest: three modes, shield targets) | 精准射击·射程校准 / 连发压制·破盾弹 / 弹种切换·移动换匣 / 弹道贯穿·反位火线 / 极域弹道·三模同调 |
| 游击 | Pass-through repositioning, bait-then-dodge, punishing whiffed attacks, short focus-switch signals (final quest: lead chasers, then switch fire). Always visible. | 换位突袭·诱导步 / 转火讯号·积势 / 破绽追击·折返双击 / 拆队讯号·引敌回旋 / 百步无迹·流转不息 |
| 驯兽 | Living beast companion(s) with stamina, battle-only trust, whistle cues and withdrawal; second companion of the other temperament from stage 3 (final quest: two companions with different abilities) | 兽伴呼应·信任纽带 / 护伴哨·追迹哨 / 兽群协律·双声协猎 / 群生护圈·信任节奏 / 万灵同路·归队本能 |
| 行商 | Reallocates the party's own energy, cooldowns and damage taken; commerce income, price edge and price intel. Never uses items or goods. | 补给协议·公道议价 / 公平报价·调期协议 / 需求洞察·风险共担 / 应急调拨·交接章程 / 万路协约·万路兜底 |

- Totals: 32 active and 18 passive nodes. Every stage has at least one active.
- The two most similar series by role set are 弓猎 and 枪械, with a Jaccard overlap of 0.11 (they share `precision_damage` and `burst`). Against the five 研学 series the highest overlap is 0.18 (驯兽/工程).
- **弓猎 vs 枪械.** Archery earns damage by observing (draw time, staying 200–480 px from a target, marks) and gives the party information. Firearms earns it by staying in the right range band and choosing the right round, and it has no marks.
- **游击 vs 战术.** 游击 signals last 6–10 s and reward switching. In 拆队讯号 the skirmisher personally keeps the "held" enemy busy. Long-term AI orders and formations stay with 战术.

### Beast companions vs automata

The series JSON carries a `companionModel`. The validator checks it, and it also confirms that no 驯兽 node uses machine words (机偶, 维修, 修复, 部署, 模式, 零件, 程序, 回收, 充能, repair, deploy, mode, robot).

| | 兽伴 (驯兽) | 机偶 (研学) |
|---|---|---|
| Nature | Living animal partner | Machine unit |
| Damage pool | Stamina (50% of the handler's max HP; second companion 30–50%) | Durability |
| At zero | Withdraws to the field edge to rest; it is never destroyed. It returns via 兽伴呼应 (40%, 2×/battle) or 归队本能 (once each) | Destroyed or recalled |
| Control | Whistle/gesture cues, 0.3 s reaction. Instinctively returns to the handler when the handler is below 30% HP | Switchable modes, exact execution |
| Upkeep | Cannot be repaired, recalled for energy or targeted by engineering/automata. Living-target heals may apply | Repaired by engineering, recalled for energy |
| Growth in battle | Trust stacks (信任纽带) | None |
| Field | Calms scared or hurt non-hostile animals only; no forced taming; no effect on patrol automata | Scouting |

### Merchant: commerce without carrying goods

- No 行商 node reads, consumes or creates an item. The validator scans 13 terms (货物, 背包, 携带, 道具, 消耗品, goods, carry, …) and finds 0 hits.
- Battle nodes move the party's own resources between members: energy (补给协议, 应急调拨, 万路协约, 万路兜底), cooldowns (调期协议) and damage taken (风险共担).
- Commerce nodes state where they apply in `commerceContext`:
  - 公平报价: `stationed`
  - 公道议价: `activeParty`, an edge on the protagonist's deal price that does not change the market baseline
  - 需求洞察: `stationedOrActiveParty`, 24–48 h earlier notice of long-term price changes and their route propagation path, information only
  - 交接章程: `recall`
- The protagonist only brokers. Logistics stays with NPC staff, per Game Bible chapter 6.
- The draft node 风险准备金 was dropped because it duplicated 周赫's personal skill 「履约储备」. No 行商 node repeats the commerce personal skills of 周赫, 安索, 韩泽, 雀枝 or 零饼.

## Science-region MVP utility (optional advantages only)

| Node | Utility | MVP places |
|---|---|---|
| 弓猎 猎迹标记 (stage 1) | 足迹判读: points to optional camps, stranded animals or supplies; logs practice for the final quest | Yonkers, Capitol ruins outpost |
| 枪械 射程校准 (stage 1) | 校准委托: optional calibration drills for small rewards and a 求知 record | Capitol ruins outpost, Chicago Loop |
| 游击 转火讯号 (stage 2) | 开战标记: a battle opens with a chosen enemy already signalled. Does not hide the party or change whether the encounter happens | Yonkers, Capitol ruins, Loop |
| 驯兽 信任纽带 (stage 1) | 动物照护: treat stray or hurt animals and find lost pets (共情 record); the companion sniffs out optional supplies | Yonkers, City Hall Park |
| 行商 补给协议 (stage 1) | 供需报价: read-only supply/demand gaps on the company panel | City Hall Park, Loop |
| 行商 公道议价 (stage 1) | 城市议价: small deal-price edge in shops | City Hall Park, Loop |

None of these is ever the only way to finish content, and every utility text says so. They need the member's **current** series to be the one that owns the node. Running a company still needs a stationed merchant companion; that is the existing Game Bible rule, not a new gate.

## Progression economics

- **Proposed JP table: 30 / 45 / 60 / 75.** This is the same table as the 研学 proposal, so all 200 job nodes can share it.
  - Linear (+15 per rank). The ratios from one rank to the next fall: 1.50 / 1.33 / 1.25.
  - Rank 5 costs 2.5× rank 2.
  - 210 JP per skill, 2100 per series.
- **Runtime catalog table, unchanged: 35 / 55 / 80 / 110.**
  - Increments 20 / 25 / 30. The ratios also fall (1.57 / 1.45 / 1.38), so it is **not exponential**, but it is steeper.
  - 280 per skill, 2800 per series.
  - Which table to adopt is a creator decision.
- **Aptitude discount.** The existing `GrowthRules.jp_cost` formula is recomputed by the validator:

| 应变 aptitude | Example | Rank 2/3/4/5 JP | Per skill | Per series |
|---|---|---|---|---|
| 60 | protagonist | 30/45/60/75 | 210 | 2100 |
| 83 | character-06 (驯兽) | 22/33/43/54 | 152 | 1520 |
| 88 | character-03 (枪械), 韩泽 | 20/30/39/49 | 138 | 1380 |
| 91 | character-10 (弓猎), 周赫 | 19/28/37/46 | 130 | 1300 |
| 94 | 零饼 (行商) | 18/26/35/44 | 123 | 1230 |
| 100 | — | 15/23/30/38 | 106 | 1060 |

- **Spread.** Aptitude 100 pays 50.5% of the aptitude-60 cost, which stays inside the Game Bible's 50% spread (rounding up keeps it at or above 50%). Cost never rises with aptitude.
- **Battle counts.** Current runtime rewards are 20 JP per sentry win and 12 per patrol win (active members only).
  - Maxing one stage's two nodes at aptitude 60 takes 21 sentry or 35 patrol wins, and a whole series takes 105 or 175. At aptitude 100 these drop to 11/18 and 53/89.
  - Each stage also sits behind a 10-level job choice. The XP curve is not final, so these numbers are not converted to levels.
- The discount changes only JP. Effect caps are the same for every member.

## Validation (embedded in the JSON; 23/23 pass)

The validator has 23 checks. It ran when the file was built, and then five more times on the written file: four from the repo root (the last one after the other sessions' commits below) and one from `/tmp`. Every run gives the same results digest, `82c06355056fc681…`.

1. `source-locks`: 6 enforced locks match: roster, both drafts, the 研学 proposal, the decision note and the runtime catalog. The Game Bible hash is only recorded (see below).
2. `series-set`
3. `approved-text-verbatim`
4. `ten-nodes-two-per-stage`
5. `node-schema`: the whole file against the embedded schema, using a built-in subset validator with no external library.
6. `distinct-nodes`: no clash with the 50 研学 node names or the 51 personal skill names in the Game Bible.
7. `unlock-and-rank-rules`
8. `active-passive-energy`: energy bands by stage are 6–16 / 6–20 / 6–30 / 6–34 / 24–50.
9. `non-exponential-ranks`: max r5/r1 = 2.00.
10. `passive-bounds`
11. `energy-transfer-capped`
12. `stacking-caps`
13. `battlefield-range`: max 560 px.
14. `no-terrain-elevation-jump-stealth`: 0 hits.
15. `merchant-no-goods`
16. `beast-living-companion`
17. `distinct-roles`
18. `ai-descriptions`
19. `science-mvp-utility`
20. `runtime-catalog-mapping`: 50/50 unique. Four nodes link to existing runtime nodes, and each carries a `runtimeNote` with the current numbers: `firearms_shot`, `firearms_burst`, `merchant_supply_pact`, `merchant_fair_quote`.
21. `progression-economics`
22. `proposal-marking`: 50/50.
23. `superseded-lineage`: 33 of 35 draft nodes are carried forward. Dropped: `merchant_risk_reserve`, `merchant_mutual_turnover`.

**Mutation test: 25 of 25 caught.** Each mutated copy was written to `%TEMP%\wbad\mut\` and run with `--proposal <copy>`. Every one exited 1 on the check it targeted, and every one also flagged the stale embedded results. The mutations were:

- a stage name and a final quest edited
- accelerating rank steps; r5/r1 = 2.2
- 跳跃 and 潜行 added to node text
- 背包中的货物 added to a 行商 node; 维修 added to a 驯兽 node
- a passive left unbounded
- an energy transfer that gains more than it costs
- stage 5 without the final quest; JP charged to unlock a node
- an exponential JP table (30/60/120/240)
- MVP text made mandatory; an MVP place outside the four
- a heal AI without the downed-ally rule
- energy outside the stage band
- a duplicate role
- a missing runtime id; a reused lineage id
- a node marked APPROVED
- a range beyond the field
- a cap sum exceeded
- a `branch` field
- an edited embedded result

**Determinism.** Rebuilding to a temp path gives a file identical to the delivered one except for `validation.ranAt`.

**Protected files.** I recorded `sha256-text-lf-v1` for 17 files before and after this pass:

- the roster and both drafts
- the 研学 JSON and QA note, and the decision note
- the Game Bible state, app, server and builder
- `docs/progress.md` and the MVP progress JSON
- the skeleton catalog
- `growth_rules.gd`, `app_state.gd`, `battle_arena.gd` and `commerce_ledger.gd`

14 are unchanged. Three changed during the session: the Game Bible state, the builder and the MVP progress JSON. Other sessions committed them (`15c9b73` at 11:15 and `4bf778f` at 11:24), and the working copy of each now equals `HEAD`; I did not edit them. That is why the Game Bible is recorded but not lock-enforced. The validator re-run after those commits still passes 23/23.

The generator `gen.js` and the mutation script are in `%TEMP%\wbad\`, outside the repo, and are not committed. The JSON is the source of truth.

## Open points for balance and creator review

1. **All numbers are placeholders.** They are calibrated against today's runtime:
   - 60–80 energy at level 1, +2 per level
   - job skill cost 13 / 16
   - dodge 12
   - enemy wind-up 0.48–0.65 s
   - field 584 px
2. **Fair Quote curve divergence.** The runtime pays +5%/rank (105–125%). This proposal uses 8/10/12/14/16% (108–116%, r5/r1 = 2.0): slightly more at rank 1 and less at rank 5. The runtime was not changed.
3. **The JP table** is 30/45/60/75 here and 35/55/80/110 in the runtime catalog; this was already open (creator note §8.2).
4. **Rule changes that need creator opt-in.**
   - 交接章程 temporarily raises the approved NPC stand-in rate (80% → 83–85% for 2 weeks).
   - 公道议价 depends on the undecided price formula.
5. **Strong nodes to watch.**
   - 兽群协律: a second companion for the whole battle.
   - 弹种切换: a battle-long toggle, at most +18% or −18% move speed.
   - 掩护箭: wind-up +0.45 s at rank 5, almost doubling today's 0.48 s sentry wind-up.
   - 风险共担 + 群生护圈 together.
6. **Tags and systems the runtime does not have yet.**
   - decoy, projection and copy tags (真身辨识)
   - enemy shields (破盾弹, 极域弹道)
   - facing/back (换位突袭)
   - melee/ranged enemy type (折返双击)
   - ailments
   - a second companion slot
   - multiple enemies: today's arena has one, so 拆队讯号, 引敌回旋, 弹道贯穿, 天际追猎, 承迹 and 流转不息 are worth little or nothing there
   - robber events, which are still not implemented
7. **Content gaps.**
   - No companion starts in 游击.
   - Beast species for the science MVP are not chosen.
   - Beast-vs-automaton visual distinction is an art follow-up; this pass touched no art.
8. **Not done here:** the remaining 10 series (武艺 and 灵觉, 100 nodes) and the 510 personal nodes. *(Updated 13:52: the 武艺 proposal now exists, so 灵觉 (50 nodes) is the only job tree left.)*
9. **Cross-proposal caps, provisional (found by the independent check below):**
   - **Redirect.** This file caps beast-companion redirect at 40% (`allyDamageRedirect`). The 武艺 proposal caps all-source redirect of one hit at 50% (`damage_redirect`). Neither file says how the two combine. With a 驯兽 and a 守护 in the party, rank-5 values on one hit sum to 77%: 护伴哨 32 + 万灵同路 8 + 护线 37. The suggested reading is that the beast's 40% counts inside the 武艺 50% all-source cap. This is not decided.
   - **Energy return.** This file has no energy-refund nodes. 研学 allows up to 24 per node per battle and 武艺 up to 32. This is a balance difference, not a rule conflict.

## Independent verification (2026-10-16 13:52 EDT, separate session)

This pass checked the file separately from its companion validator. **No real error was found, so the JSON, its hash, the validator and the embedded results are unchanged.** Nothing was staged, committed or pushed.

- **Companion validator:** `node tools/…e0ce1cbc.js` gives **23/23 pass**, the embedded results match (digest `82c06355056fc681`), and the hash is `sha256-text-lf-v1 f3b287d6…814797`. Running it from `%TEMP%` gives the same result.
- **Independent cross-check:** [`tools/rpg-2-star-ocean-the-second_martial-adaptive-job-trees_ten-node-independent-crosscheck_unapproved-v01_20261016-135211-122bcb8b.js`](../../tools/rpg-2-star-ocean-the-second_martial-adaptive-job-trees_ten-node-independent-crosscheck_unapproved-v01_20261016-135211-122bcb8b.js) (`sha256-text-lf-v1 82ad5b4b…cf7ae`). It covers 应变 and 武艺 together. Result: **13/15 pass, 2 warn, 0 fail**; the two warnings are open point 9.
  - Approved text: all 10 series' text equals both the roster and Game Bible `jobProposal.series`, all 100 `stageName`s match, and the runtime catalog's Chinese names agree.
  - Rule shape: 100 nodes = 10 × 5 × 2; `maxRank` 5; every node opens at rank 1 for 0 JP; the final-quest gate is on exactly tier 5; JP keys are 2–5 only; there are 0 exclusive-branch keys or phrases.
  - Status: 100/100 nodes are PROPOSAL / pending, and the prose contains no approval claims.
  - Names: across 150 job nodes, every id and every Chinese and English name is unique. There are 0 clashes with 139 personal names.
  - Numbers: every rank text and every rank-1 `baseEffect` matches its values. Steps are flat or shrinking, with r5/r1 ≤ 2.
  - Energy and range: energy bands are identical in all three proposals, and every range is ≤ 584 px.
  - Schema: the file passes its embedded schema under an independently written validator.
  - Runtime catalog: `runtimeCatalogNodeId` matches series, stage and slot for all 50 nodes. Every catalog node that has runtime behaviour is claimed. 精准射击, 连发压制, 补给协议 and 公平报价 equal the zh/en names in `app_state.gd`. The firearms costs (E13, E16) equal `10 + 3 × stage`. Fair Quote's +5%/rank was confirmed in `commerce_ledger.gd`; this proposal's 8–16% differs, as open point 2 already says.
  - Canon:
    - The reputation words used are only 求知 and 共情.
    - The utility places are all in the US science MVP set.
    - No AI condition uses items.
    - 万灵同路, the only party heal, defers to revive-capable skills when an ally is down.
  - Undeclared caps: the cap-declaration text scan raised only one hit for this file, 信任纽带's damage reduction. That reduction protects the beast's own stamina, not party members, so it is outside `allyDamageReduction`.
- **Mutation test of the cross-check:** 24/24 injected defects were caught, each by its target check. The harness is in `%TEMP%\wb-jobtree-indep\`.
