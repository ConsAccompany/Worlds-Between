# 研学 job trees: ten-node redesign (PROPOSAL) — design and QA note

- Date: 2026-10-15 23:21 local
- Status: **PROPOSAL. All 50 nodes are pending balance and creator review.** Nothing here is approved or implemented.
- Data: [`outputs/rpg-2-star-ocean-the-second_research-job-trees_ten-node-skill-proposal_unapproved-v01_20261015-232143-842e0540.json`](../../outputs/rpg-2-star-ocean-the-second_research-job-trees_ten-node-skill-proposal_unapproved-v01_20261015-232143-842e0540.json). The file holds the nodes, the rules, a provisional JP table, an embedded JSON Schema and the validation results. Its `sha256-text-lf-v1` is `d7f9b2917702d420afa3bc9d64b4ad8379ed244a1c227c5b38168ac142c67b50`.
- Authored in a Claude Code session signed in to Claude Max (firstParty). No API key, credits or paid fallback was used.
- Scope: the five 研学 series (工程, 机偶, 医疗, 药剂, 战术). Each gets 10 nodes, 50 in total. This is 50 of the 200 job nodes asked for in the creator decision note, §2 and §8.2.

## Sources read

- The approved roster: `outputs/…_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json`. Each series' name, English name, role, five stage names and `finalQuest` are copied **verbatim**, and a check confirms it.
- The superseded 7-node drafts, used for lineage only:
  - `outputs/…_scholarly-job-trees_skill-node-proposal_v01_20261013-225251-3e6a19d8.json` (engineering, automata, medicine, alchemy)
  - the tactics tree in `outputs/…_four-job-trees_skill-node-proposal_v01_20261013-224554-5a72d0be.json`
- The creator decision note: `docs/design/…_creator-decisions-2026-10-15_world-skills-ai-endgame_reconciliation-note_v01_20261015-174559-39efc292.md`. It sets the skill, AI and combo rules and the US science MVP places.
- Game Bible chapters 1, 3 and 4 (read only), for the battle rules:
  - The battlefield is flat with no terrain effects.
  - Energy does not regenerate in battle.
  - After a battle, survivors recover 20% and downed characters return at 10%.

## Rules applied

- The 2 nodes of a stage open at rank 1 as soon as the character enters that stage. They cost no JP and have no extra level gate. Stage 5 still needs the series final quest. JP only raises ranks 2–5, and the maximum rank is 5. There are no exclusive branches.
- Proposed JP base cost per rank: 30 / 45 / 60 / 75. This is linear, 210 JP per skill. The existing aptitude discount still applies (100% of base at 60, down to 50% at 100).
- Rank curves use fixed or shrinking additive steps. At rank 5 each value is at most 2× its rank 1 value. Energy cost, cooldown and trigger counts stay the same at every rank. The file states proposed stacking caps.
- No node touches terrain, elevation, obstacles, cover or jumping. Devices and automata have no collision, and range is horizontal pixels only. No stealth.
- Heal and revive AI handles downed allies first. Combo energy is still paid by every participant. Tactics can lower combo cost but never bypasses combo conditions.

## Role identity (distinct per series)

| Series | Identity | Stage 1 → 5 node pairs |
|---|---|---|
| 工程 | Static short-lived devices; armor break on mechanical targets; repairs anyone's devices and automata | 护板架设·弱点拆解 / 现场维保·脉冲桩 / 安全覆写·能源旁路 / 联锁护阵·过载释放 / 构件冗余·创构矩阵 |
| 机偶 | Mobile units with modes (attack, escort, decoy, repair); 1 → 3 units | 随行机偶·护航模式 / 牵制模式·修复模式 / 双机编组·同步协议 / 三机编队·紧急回收 / 自律重构·共生机魂 |
| 医疗 | HP economy: heals, regen, revive, lethal save, aftercare; single-target cleanse | 急救包扎·生命监测 / 净创处理·持续点滴 / 战地复苏·战后护理 / 群体分诊·生命线 / 余量转护·生命共振 |
| 药剂 | Status and reaction economy: marks and detonation, debuffs, buff strip, party-wide prevention and type cleanse | 反应瓶·样本辨识 / 中和剂·催化滴剂 / 连锁反应·抑制剂 / 应急溶剂·缓释配方 / 复合抗剂·万象配方 |
| 战术 | Command: marks, AI orders, formation bonus, read and counter, combo support; no direct damage or heal | 优先目标·敌情研判 / 稳阵指令·集火口令 / 阵形学·后备轮换 / 逆向预判·协同调度 / 双重指令·万局同调 |

- Totals: 35 active and 15 passive nodes. Every stage has at least one active.
- Each node has a tactical role, and no role repeats inside a series.
- The two most similar series by role set are engineering and automata, with a Jaccard overlap of 0.33. What separates them: engineering devices are stationary, while automata move, have their own HP and switch modes.

## Science-region MVP utility (optional advantages only)

| Node | Utility | MVP places |
|---|---|---|
| 工程 现场维保 (stage 2) | Repair marked broken public devices for optional shortcuts, caches or archive entries | City Hall Park, Capitol ruins outpost, Chicago Loop |
| 机偶 随行机偶 (stage 1) | Scout ahead: map outline, interactables, patrol routes of visible enemies; log outpost patrol automata | Yonkers, Capitol ruins, Loop |
| 医疗 急救包扎 (stage 1) / 战后护理 (stage 3) | Treat injured NPCs (共情 behaviour record); +HP after battles between rests | Yonkers, Capitol ruins, City Hall Park |
| 药剂 样本辨识 (stage 1) | Analyze regional samples into archive formula notes, which seed the final quest; preview local ailments | All four MVP places |
| 战术 敌情研判 (stage 1) | Show a visible enemy's composition, level band and weaknesses before contact | All four MVP places |

None of these is ever the only way to finish content. They need the user's **current** series to be the one that owns the node. They create no inventory items and have no effect on market prices.

## Validation (embedded in the JSON; 14/14 pass)

The checks were run when the file was built and again on the written file:

- series set
- approved text verbatim
- 10 nodes, 2 per stage
- node schema (custom validator that mirrors `$defs.node`; no external library)
- unique ids and names
- unlock and rank rules
- active/passive and per-stage energy bands
- non-exponential ranks (max r5/r1 = 2.00)
- capped energy returns
- banned terrain, elevation and stealth terms: 0 hits
- distinct roles
- science MVP utility
- PROPOSAL marking (50/50)
- superseded-draft lineage (31 of 35 draft nodes carried forward; dropped: 模块重组, 稳态照护, 批次记忆, 机会评估)

The first build caught 能源旁路 at 3 → 7 (2.33×). It was changed to 4 → 8.

There are 12 protected files: the source JSONs, the decision note, the Game Bible state and app, the server, `docs/progress.md`, the MVP progress JSON, and `app_state.gd`, `battle_arena.gd` and `battle_rules.gd`. All 12 have the same `sha256-text-lf-v1` hash before and after this pass. The generator and validator script was kept outside the repo, in `%TEMP%`, and was not committed.

## Open points for balance and creator review

1. All numbers are placeholders. They are calibrated against the runtime as it is today:
   - 60–80 energy at level 1, +2 per level
   - job skill cost 13–25
   - dodge 12, guard hit 6
2. 战后护理 changes the post-battle recovery rule (20% / 10%). It needs the creator to opt in.
3. Several nodes rely on tags or systems the runtime does not have yet:
   - a "mechanical enemy" tag
   - removable buffs and debuffs
   - ailment types and resistance
   - multiple enemies per battle (today's arena has one enemy, so splash and all-enemy effects are worth less there)
4. The JP table is provisional. Creator note §8.2 still lists it as open.
5. Not done here: the other 15 series (150 nodes) and the 510 personal nodes.
