# Ten-node personal skills for the hero and companions 01–03: design and QA note

- Date: 2026-10-15 23:21 local (2026-10-16T03:21Z)
- Status: **PROPOSAL, pending creator review.** All 40 nodes are unapproved. Nothing here is in the runtime.
- Authoring: a signed-in Claude Max first-party session (Claude Code). No API key, credits or paid fallback were used.
- Proposal file: `outputs/rpg-2-star-ocean-the-second_core-cast_personal-skills-ten-node-proposal_hero-c01-c03-v01_20261015-232129-dfc60394.json`
  - LF-normalised SHA-256: `24144b39930a197d484fa0b8fe4592bc66e2c60fe1d7b1583313eb3fe237c341`

## Sources

- The core-cast character bible (`…_character-bible_v01_20261012-234158-cc7e91a4.md`).
- The superseded 5-node draft (`…_personal-skill-trees-proposal_v01_20261013-230015-4ce1a8d2.json`).
- The 2026-10-15 creator decisions note (`…_creator-decisions-2026-10-15_…_39efc292.md`).
- Design brief §3:
  - Flat side-view battlefield with no jumping. Terrain and obstacles have no effect.
  - Energy does not regenerate in battle.

None of these files was modified. The proposal also leaves the Game Bible, `docs/progress.md`, the runtime, the app/server and Git untouched. Nothing was committed or pushed. The Game Bible's `approvedAuthored` personal-node count stays **0**.

## Rules applied

| Rule | How the proposal meets it |
|---|---|
| Exactly 10 distinct nodes per identity | 4 trees × 10 = 40 nodes. Every ID and Chinese name is unique, both within a tree and across all 40. |
| All unlocked by personal level 100 | Shared gates are `1, 6, 14, 22, 32, 42, 54, 66, 80, 95`. The last node opens at 95, leaving a 5-level margin. |
| Signature skill immediately on joining | Node 1 is the bible's skill, with its name unchanged: **临场理解 / 战术校准 / 二次装配 / 折线路径**. It opens at level 1 with `availableOnJoin: true`. |
| No JP unlock | Each node opens automatically at rank 1 when its level is reached. A companion who joins later opens every node at or below the synced level at once. |
| JP only for ranks 2–5 | Placeholder costs: 40 / 70 / 110 / 160. That is 380 JP per node and 3,800 per tree. |
| Usable in any job | `usableInAnyJob: true` on every node. |
| No terrain or elevation | No node uses terrain, elevation, cover or scene geometry. Devices have no collision. Rounds turn only between enemies. Lin's stance checks only whether she is moving, not where she stands. |
| No overpowered infinite scaling | Every scaling stat has exactly 5 rank values. Every node has explicit limits. The global caps are in the next section. |

**Global caps (`rules.globalLimits`):**

- Personal bonuses on one action add together, up to **+30%**.
- Energy discounts cannot take a skill below **50%** of its base cost.
- Refunds and transfers never create net energy. Jiang's device refunds are capped per battle at **20–30%** of her max energy.
- Bosses get delays or halved effects, not hard control.
- Everything resets at the end of a battle. Nothing grows from kill or battle counts.
- The creator rule "revive downed allies first, then urgent heals" always outranks the AI bias a node adds.
- Combos still charge every participant.

## Node summary

Each cell shows level, node, type and energy cost. A = active, P = passive (always 0 energy).

| Lv | Hero | Liang Xu (01) | Jiang Lan (02) | Lin Que (03) |
|---|---|---|---|---|
| 1 | **临场理解** A16 | **战术校准** A18 | **二次装配** A20 | **折线路径** A18 |
| 6 | 共享笔记 P | 节奏稳定 P | 易修结构 P | 先看后动 P |
| 14 | 修正假设 P | 预备方案 P | 模块外壳 P | 标记锁定 P |
| 22 | 分灯 A12 | 现场复盘 P | 护持装置 A22 | 净角射击 P |
| 32 | 直面 A20 | 倾听例外 P | 备用零件 P | 标记接力 P |
| 42 | 交汇洞见 P | 稳住阵脚 A28 | 改装切换 A8→4 | 最少动作 A14 |
| 54 | 换个角度 P | 共同判断 P | 维护清单 P | 三点成线 P |
| 66 | 旧笔记 P | 板上推演 A24 | 共享工具 P | 侧镜标定 A12 |
| 80 | 理解之桥 A36 | 双轨指令 P | 超频装配 A34 | 挺直站姿 P |
| 95 | 同行共学 P | 自主判断 P | 双件联动 P | 一线贯通 A40 |

Totals: 15 active and 25 passive nodes. The hero, Jiang and Lin each have 4 actives; Liang has 3. Active costs run from 8 to 40. That fits the runtime's starting max energy of 60–80, which rises by 2 per level.

**Identity hooks.** Each node's `identityLink` ties it to the bible.

- **Hero:** curiosity, admitting misunderstandings, the underground community's habit of sharing (分灯), and a sense of justice (直面).
- **Liang Xu:** concise orders, evidence over guesswork, and listening to experience that contradicts the data (倾听例外). His capstone is a mentor's goal: the team learns to judge without him (自主判断).
- **Jiang Lan:** repairable tools, the two different folding devices at her waist (护持装置, 双件联动), and her habit of underestimating maintenance cost. That habit is written into the rules as a refund cap (维护清单) and an overclock that gives no refund (超频装配).
- **Lin Que:** she observes first and acts with minimal motion. Her punctuality shows in 标记接力, her side-mounted goggles in 侧镜标定, and her upright stance in 挺直站姿.

**Lineage.** Each node's `lineage` field records where it came from. Of the 20 nodes in the superseded 5-node draft:

- The 4 signature skills carry over.
- 12 of the 16 enhancement nodes carry over in revised form.
- 3 enhancement nodes were folded into the signature skills' rank scaling: 快速归纳, 清晰口令 and 轨迹记忆.
- `jiang_reuse_loop` was dropped. The capped refund system replaces its cheaper-third-device loop.

The other 24 nodes are new.

## Schema (per node)

`id`, `order` (1–10), `unlockLevel`, `nameZh`, `nameEn`, `status` (`PROPOSAL`), `reviewState` (`pending-creator-review`), `type` (`active` | `passive`), `energyCost` (int; 0 for passive), `usableInAnyJob`, `tags`, `effectZh`, `summaryEn`, `rankScaling[]` (`{stat, unit, values[5]}`), `limits[]`, `identityLink`, `lineage`.

Some nodes add optional fields:

- `signature` and `availableOnJoin` (node 1 only).
- `modifies[]`, which lists the IDs of the nodes it changes.

Tree-level fields are `characterId`, `signatureSkill`, `identitySummary` and `treeTheme`. Jiang's tree also has `deviceRules`.

## Validation run (Python 3.12, read-only, run inline with no script file added)

| Check | Result |
|---|---|
| Trees / total nodes / unique IDs | 4 / **40** / 40 |
| Nodes per tree | 10, 10, 10, 10 |
| `order` = 1…10; `unlockLevel` = the shared gates; max ≤ 100 | pass (max 95) |
| Node 1 name = bible signature (verbatim), level 1, exactly one signature per tree | pass ×4 |
| Required fields present on every node | pass |
| Active → energy > 0; passive → energy = 0 | pass (15 / 25) |
| Every `rankScaling` has 5 numeric, monotonic, non-flat values | pass |
| Every node has ≥ 1 limit; all `modifies` IDs resolve | pass |
| Every node `status = PROPOSAL` | pass (40/40) |
| Duplicate Chinese names across all 40 | none |
| Forbidden-term scan of node text (地形, 高低, 高差, 地势, 障碍, 掩体, 高处, 跳, 墙, 反弹, 无限, 永久提升) | none found |
| Source files (bible, old draft, Game Bible JSON, decisions note) | `git status` clean |

## Open questions for the creator

1. Should personal-skill JP get the aptitude discount that job skills get? The proposal assumes **no**.
2. Should the shared gates apply to all 51 identities, or may each identity have its own?
3. All numbers are placeholders until combat terms are defined in the runtime: skill power, cooldown, stagger, wind-up and warning.
4. 临场理解 needs a weakness-tag field in enemy data. 旧笔记 needs saves to record which enemy kinds have been defeated.
