# Science-sphere career series: MVP audit and stage-1 "b" passive candidates (QA note, UNAPPROVED)

- Date: 2026-10-16, 17:45–17:55 local (EDT).
- Agent: Claude Code (Opus 5.5), signed-in Claude Max (claude.ai first-party). `ANTHROPIC_API_KEY` was checked and is **absent**. No API billing or paid fallback was used, and quota was not exhausted.
- Status: **CANDIDATE / UNAPPROVED / OFF BY DEFAULT.** Nothing in this note is a creator approval. No proposed skill tree is treated as approved.
- Not touched: the completion meter, the Game Bible (state JSON, app, server), `approvalLedger`, the MVP progress JSON, `docs/progress.md`, art, map and travel files, and Git (no stage, commit or push). Codex decides integration and sync.

## 1. Sources read

- Approved canon: `docs/design/…creator-decisions-2026-10-15…39efc292.md` §2, and Game Bible `jobProposal` + `creatorDecisions.skillRules` / `skillRuntime` in `outputs/…game-bible_state_v01_…b8c16d42.json`. The approved items are the 20-series roster, every five-stage name and `finalQuest` text, 10 nodes per series (2 per stage, opened on stage entry), rank cap 5 via JP, 51 × 10 personal nodes by Lv100, and a signature skill on joining. `role` and `rules` are **not** separately confirmed (`approvalScope`).
- Job rules (Game Bible `jobProposal.rules`): an aptitude of 60 enters the series; a forced choice every 10 levels (stay, promote or switch), and switching back restores progress; stages 1–4 come from level choices and stage 5 also needs the series final quest, which clears it for the whole party; job skills work only in the current series and personal skills always work.
- Runtime: `game/scripts/growth_rules.gd`, `app_state.gd` (growth / JP / choice / recruit / save), `battle_arena.gd` (`_use_job_skill`, `_try_attack`, AI), `growth_screen.gd`, and the catalog `game/data/growth/…science-mvp-skeleton_v01_…e36e5d2c.json` (`approvedNodeDesignsAuthored: 0`).
- Unapproved ten-node proposals, used **only** for context and adopted nowhere: 武艺 `…4e3b550a`, 应变 `…ec58fa23`, 研学 `…842e0540`, 灵觉 `…d70bdf84` (all `PROPOSAL pending balance and creator review`).
- Ledger context: the latest `outputs/…mvp-completion-ledger_…closeout-evidence-index…` files. They were read only.
- "Science region" here means the active MVP science sphere (US + Canada). Its five career series are the five that the runtime can enter: **sword, firearms, tactics, relics, merchant**.

## 2. Gap table — BEFORE this pass (HEAD 3841241 + the existing working tree)

Node ids are `<series>_s<stage><slot>`. s1a and s2a are the two runtime skills; every other node is a catalog skeleton (`effect: "none"`, no name, takes no JP).

| Series (aptitude) | Nodes with a real runtime effect | Exact effect (rank r, stage s) | Empty placeholders | Stages 3–5 | Behaviour tests of the effect | Talent gate (MVP members who qualify) | Item gate |
|---|---|---|---|---|---|---|---|
| 剑术 sword (martial) | 2/10: `sword_slash` s1a, `sword_arc` s2a | damage 8+4r+3s (15 / 18 at r1), range ≤105 px, energy 10+3s (13 / 16), 2.2 s cooldown | 8: s1b, s2b, s3a–s5b | no new action; battle keeps `sword_arc` | **yes**: m5 (15 / 18 damage, win), merchant smoke, progression rules | martial ≥ 60: hero only (Liang 48, Zhao 51, Ji 41) | none |
| 枪械 firearms (adaptive) | 2/10: `firearms_shot`, `firearms_burst` | **same formula as sword**, range ≤175 px | 8 | same | **none** (catalog/rules only) | adaptive ≥ 60: hero, Liang 67, Zhao 84, Ji 67 | none |
| 战术 tactics (scholarly) | 2/10: `tactics_mark`, `tactics_rally` | +(2+2r+2(s−1)) boost to each standing ally (4 / 6), spent on the next basic hit | 8 | same | **none** (rules only) | scholarly ≥ 60: hero, Liang 94, Zhao 68, Ji 79 | none |
| 遗物 relics (spiritual) | 2/10: `relics_echo`, `relics_delay` | enemy recovery +(0.25+0.2r+0.2(s−1)) s (0.45 / 0.65), and the same added to a wind-up in progress | 8 | same | **none** | spiritual ≥ 60: hero, Ji 83 | none |
| 行商 merchant (adaptive) | 1/10: `merchant_fair_quote` s2a (commerce, not battle) | companion weekly rate +5 %/rank at stage ≥ 2; frozen while stationed | 9: Supply Pact s1a is a **named placeholder**, plus 8 skeletons | same | **yes** (two merchant smokes + progression) | adaptive ≥ 60: as firearms | none |

Shared facts (all five series):

- **Totals:** 9/50 nodes have an effect: 8 battle and 1 commerce. In the MVP-reachable stages 1–2, 9/20 nodes have an effect.
- **When nodes open:** stage nodes open at rank 1 with no JP. JP raises ranks 2–5 at base 35/55/80/110 × (1 − 0.5·(apt−60)/40), rounded up. There is **no level cap** (`xp_to_next` = 30+10(L−1)). There is a **forced choice every 10 levels.**
- **Stage 5:** only the `clear_series_final_quest` hook exists. The MVP has **no final-quest content.**
- **AI:** AI uses job skills only from **Lv10**, and only with the `skill` command or the `aggressive` policy.
- **Reachability:** Lv10 needs 630 XP, about 25 patrol wins (26 XP each) or 15 sentry wins (44 XP), so stage 3+ is effectively out of MVP reach.
- **English stage names:** these exist only for stages 1–2 of the runtime series. Later stages fall back to "<Series> · Stage N".
- **Item gates:** none. No inventory or item requirement exists in the runtime, and the approved rules contain none. (The superseded relics draft even says "不要求持有特定剧情遗物".)
- **Mechanical overlap:** within each series, s1a and s2a share one mechanic (+3 damage / +2 boost / +0.2 s per stage). Sword and firearms differ only in range.

## 3. What was implemented (highest-value reversible subset)

**Choice and rationale.** The four **stage-1 slot-b** nodes of the battle series (`sword_s1b`, `firearms_s1b`, `tactics_s1b`, `relics_s1b`) were filled first, for three reasons:

- These nodes are open from Lv1 for every party member in those series, so every MVP battle can show them. Stage 3+ is out of MVP reach.
- Each is a **passive on landed basic attacks**. That makes them useful below Lv10, where AI-controlled allies never use job skills.
- All four hook into a single battle function, which keeps the hunk small.

Merchant was **left unchanged**, because its placeholder status is pinned by about 10 checks in three tests (see §6).

**Candidate data:** `game/data/growth/rpg-2-star-ocean-the-second_science-career-series_stage1-b-passive-candidates_unapproved-v01_20261016-174537-19222a66.json` (`status: CANDIDATE-UNAPPROVED`, `enabledByDefault: false`). All labels and numbers are Claude candidates. They avoid the names in the unapproved proposals (no name collision was found in `outputs/`, `game/` or `docs/`).

| Node | Candidate label (zh / en) | Passive (rank r) | Basis (role text, not separately confirmed) |
|---|---|---|---|
| `sword_s1b` | 候选·起手破绽 / Cand. Wind-up Gap | a basic hit that lands while the enemy winds up deals +2r | 连续斩击与看破敌方起手 |
| `firearms_s1b` | 候选·远距稳射 / Cand. Long Steady | a basic hit from ≥120 px deals +2r | 射程管理与弹道切换 |
| `tactics_s1b` | 候选·编队协同 / Cand. Formation Sync | while this member is standing, every ally's basic hit deals +r; the party's highest Tactics rank counts and ranks do not stack | 队友指令、目标标记与编队收益 |
| `relics_s1b` | 候选·余波滞时 / Cand. Echo Linger | a basic hit during enemy recovery adds 0.1r s, once per enemy attack per member | 古物解读与特殊效果调用 |

**Runtime changes:**

- **`growth_rules.gd` (+96/−1).** Adds `CANDIDATE_PATH`, a switch (`candidate_effects_enabled()` / `set_candidate_effects()`, or the user argument `--career-candidates`), `candidate_node`, `candidate_rank` (current series only, open node only), `candidate_basic_hit` and `candidate_text`. `job_skill_upgradable` also accepts a candidate node, but only while the switch is on. The catalog is **unchanged**, so `careerNodesWithRuntimeEffect` stays 9 and saves are unchanged.
- **`growth_screen.gd` (+11/−1).** The overlay names candidate nodes from their data. It keeps the catalog count line ("职业 2/10 · 个人 1/10") and adds a separate line: "候选效果（未批准，可关闭，可用 JP 升级）：<label> Lv r: <value>".
- **`battle_arena.gd`.** Two hunks, nowhere near the other workstream's uncommitted M8 art hunks: one call in `_try_attack` and a 6-line helper `_standing_member_states()`. Removing exactly these two hunks reproduces the pre-edit working file byte for byte (sha256 `be8859a8…acae`). The patch also applies cleanly to the HEAD version (offset −149):

```diff
@@ -443,6 +443,12 @@ func _try_attack(index: int = -1) -> bool:
 	var damage := int(definition["attack_damage"]) + int(fighter["boost"]) + next_attack_bonus
+	# Unapproved career candidate passives (GrowthRules; off unless enabled, then all zero).
+	var candidate := GrowthRules.candidate_basic_hit(AppState.member_state(String(fighter["id"])), _standing_member_states(), {"enemy_winding_up": enemy_windup > 0.0, "distance": absf(enemy_x - float(fighter["x"])), "enemy_recovering": enemy_windup == 0.0 and enemy_cooldown > 0.0 and int(fighter.get("candidate_delay_cycle", -1)) != enemy_attack_count})
+	damage += int(candidate["damage"])
+	if float(candidate["enemy_delay"]) > 0.0:
+		enemy_cooldown += float(candidate["enemy_delay"])
+		fighter["candidate_delay_cycle"] = enemy_attack_count
 	fighter["boost"] = 0
@@ -453,6 +459,14 @@
+func _standing_member_states() -> Array:
+	var states := []
+	for index in fighters.size():
+		if _is_alive(index):
+			states.append(AppState.member_state(String(fighters[index]["id"])))
+	return states
+
+
 func _try_dodge(index: int = -1) -> bool:
```

`app_state.gd`, the catalog JSON, the save format and every other test file are **unchanged**.

**How to switch it on for playtesting:** `Godot_v4.7.2-stable_win64_console.exe --path game -- --career-candidates`.

**How to reverse it:**

1. Leave it off, which is the default.
2. To remove it: delete the candidate JSON, the new test and the two PNGs. Revert the GrowthRules/growth-screen additions and the two battle hunks.

Caveat: JP spent on candidate ranks **while the switch is on** is not refunded. The rank stays in the save but is inert and takes no JP when off (tested).

## 4. Rule preservation (checked with candidates ON)

| Rule | Evidence |
|---|---|
| Forced job choice every 10 levels | new test: Lv10 sets `pending_job_choices` = 1 |
| No level cap | new test: reaches Lv105 |
| Current-tree usability | the sword passive is inactive after switching to Firearms (19, not 25) |
| Retained history | switching back restores rank 3 and +6 |
| JP upgrades | ranks 2–5 cost 35+55+80+110 at aptitude 60; rank 5 is the cap; the overlay button spends JP |
| 60 talent gate | Liang (martial 48) still cannot enter sword |
| Unique personal skills | Liang's signature still upgrades to rank 4 beside the candidates; all personal paths are untouched |
| Merchant placeholder and Fair Quote | Supply Pact is still not upgradable; all merchant tests pass with candidates on and off |
| Saves | a candidate rank round-trips with no migration; switching off afterwards keeps the rank but makes it inert |

## 5. Tests and exact before/after coverage

New test: `game/tests/rpg-2-star-ocean-the-second_science-career-candidates_stage1-b-passive-smoke_unapproved-v01_20261016-174537-581a982e.gd`.

- It has **52 checks** headless. Windowed with `-- --capture=<dir>` it runs 54 checks (the extra two are the capture writes).
- Every check drives the real battle scene (`_try_attack` / `_use_job_skill` on a paused `battle_arena.tscn`), the real JP/choice/save paths or the real growth screen. None of them only re-reads data.
- It also adds the **missing baseline coverage** for the existing firearms, tactics and relics job skills, with candidates off.

| Coverage item | Before | After |
|---|---|---|
| Nodes with any runtime effect, five series (default runtime) | 9/50 | 9/50 (unchanged while off) |
| … with `--career-candidates` | — | 13/50 (+4 candidate) |
| MVP-reachable stages 1–2 with an effect (off / on) | 9/20 | 9/20 / 13/20 |
| Battle-behaviour tests of existing job skills: sword / firearms / tactics / relics | 2/2 · 0/2 · 0/2 · 0/2 | 2/2 · 2/2 · 2/2 · 2/2 |
| Behaviour tests of stage-1 "b" nodes (passives) | 0/4 (only "skeleton takes no JP" for `sword_s1b`) | 4/4 (on), plus "off = exact old value" for sword, firearms and relics |

**Mutation checks (all restored afterwards):**

- Caught by the new test:
  - sword `perRank` 2→3: 7 failures
  - formation ranks stack: 1
  - relic delay not limited to once per enemy attack: 2
  - switch stuck on: 9
  - (baseline section, run in an isolated HEAD copy) tactics boost base 2→3: 3
  - firearms range 175→185: 2
  - relic delay base 0.25→0.30: 2
- Not caught: removing the series test in `candidate_rank`. This is an **equivalent mutant**: `job_node_open` already looks nodes up inside the current series only.

**Regression runs** (Godot 4.7.2 console; "--headless" unless noted; all exit 0 and 0 `SCRIPT ERROR` unless stated):

| Suite | Before edit | After, switch OFF | After, `--career-candidates` | HEAD + only these changes (isolated copy, imported) |
|---|---|---|---|---|
| progression ten-node smoke | OK 494 | OK 494 | **FAILED 5/494** (see §6) | OK 494 |
| m5_smoke / m6_smoke | OK / OK | OK / OK | OK / OK | OK / OK |
| merchant city-commerce path | OK 110 | OK 110 | OK 110 | OK 110 |
| merchant Fair Quote rank/settlement UI | OK 92 | OK 92 | OK 92 | OK 92 |
| m3 / m4 smoke | — | OK / OK | OK / OK | OK / OK |
| m6_restart / m7 smoke | — | OK / OK | OK / OK | — |
| five sideview combat smokes (`-- --no-capture`) | — | all OK | — | — |
| new candidates smoke | — | OK 52 | (sets the switch itself) | OK 52 |

Visual evidence (windowed run, byte-identical across two runs; logical 640×360, captured at 1280×720):

- `outputs/rpg-2-star-ocean-the-second_science-career-candidates_growth-overlay-zh_unapproved-v01_20261016-174537-b5d8c65a.png` — sha256-bytes `de19d74283823ba55e72cf9378d25013c33aa7571747fd5bdce4c8d256438e0b`
- `outputs/rpg-2-star-ocean-the-second_science-career-candidates_growth-overlay-en_unapproved-v01_20261016-174537-9248fecd.png` — sha256-bytes `c9ccdfad0a5fcdd09947c89acd8d43197facb5fbedf17c6a9297a87731522458`

Both were inspected: the candidate node, the separate candidate line and the unchanged count line are readable, and nothing is clipped or off-screen in zh or en.

**Final file hashes (`sha256-text-lf-v1`):**

| File | Hash |
|---|---|
| `growth_rules.gd` | `e4f45c3769d98a9aa03eaeb66e9e2caf341543d9453674ae581842c298546875` |
| `growth_screen.gd` | `41d17e4519fea0c4428a0b01f3ca181c78e7b6c1625a432df2f7af1deb949fde` |
| `battle_arena.gd` (includes the other workstream's uncommitted art hunks) | `0c47a2742381192841a666be99510fbe9e8baafd124405e359fc2c79c6b37aa7` |
| candidate JSON | `3c394db067568cb7e3a4a6b55cb4c03e20e8d35f9628db8b4bf53082725c6b73` |
| new test | `d94cf6016ebe04a4fad289b2870a6565f753877f1a7ecb65b53a379a8d4c2da8` |

**Git status:** compared before and after this pass, the only new or modified paths are the five files above plus the two PNGs and this note. `battle_arena.gd` was already `M`. The other new untracked items that appeared (NYC v04, map-art v02) belong to parallel sessions. No `.uid` file and no other artifacts were created.

## 6. Test-contract conflicts if the switch is turned ON permanently

With `--career-candidates`, the progression ten-node smoke fails 5 checks:

- "a skeleton node takes no JP"
- "JP cannot open a node of an unentered stage"
- "rank 5 is the cap; ranks 2-5 cost 35+55+80+110"
- "promotion opens both stage-2 nodes with no JP"
- "skeleton and unopened career nodes are shown but disabled"

The root cause is one choice: the test uses **`sword_s1b` as its example skeleton**, in both the rules section and the UI section. The other four failures are knock-on exact-JP-total checks. All other suites pass with the switch on.

Making the candidates default would need the test owner to move that example to a node that is still a skeleton (e.g. `sword_s2b`, after promotion). That is why the switch ships OFF.

## 7. Creator decisions needed

1. **The four candidate passives:** accept, rename or reject each one, and set its numbers (+2r / +2r at 120 px / +r party / 0.1r s). The labels currently carry the "候选 / Cand." prefix.
2. **Default state:** keep the candidates switchable, or make them the default. Making them the default needs the §6 test-contract change.
3. **Passive vs active for slot b.** The unapproved proposals put a mix of passives and actives in s1b/s2b, while this pass uses passives only. Decide whether the "b" slot should be the passive slot.
4. **Firearms vs sword:** s1a/s2a currently share one damage formula and differ only in range. Should firearms get its own mechanic?
5. **Merchant in battle:** Supply Pact (s1a) stays a placeholder with no effect, and Merchant has no battle use. Is a battle role wanted for the MVP?
6. **Remaining gaps:**
   - s2b in all five series is still empty.
   - Stages 3–5 have no new effects, and no final-quest content exists.
   - JP costs for ranks 4–5 (80/110) are still provisional, and three proposals use 30/45/60/75 instead.
   - Whether JP spent on rejected candidates should be refunded.
7. **Item gates:** none exist and none are approved. Confirm that careers stay free of item gates.

## 8. Not done (out of scope)

- No plot, romance, sphere expansion, the other 15 series, personal-node design, AI changes or new battle buttons.
- No change to the Game Bible, completion meter, approval ledger, progress docs, art, map or travel.
- No Git operation.

## Zero-change closeout (2026-10-16, ledger only)

- Recorded as a **zero-change** meter closeout: 35.8% → 35.8%, no gate, counter or category change. M7 stays **3/4**; no playable gate moved.
- Evidence is the recorded runs in §5: the existing suites pass with the switch **off**, and the new candidates smoke passes 52/52. With `--career-candidates`, the progression ten-node smoke has the **five known failures** of §6, because that test uses `sword_s1b` as its empty example node. These runs were not repeated for the closeout. The seven hashes in §5 were re-checked and match the working tree.
- The four effects, their labels and numbers are **unapproved**, and the switch stays **off by default**. The creator decisions in §7 remain open.
- Only this note is tracked. `growth_rules.gd`, `growth_screen.gd`, `battle_arena.gd` (which also holds another workstream's uncommitted hunks), the candidate JSON, the new test and the two captures stay local and are hash-pinned in `outputs/rpg-2-star-ocean-the-second_mvp-completion-ledger_map-art-v02-nyc-v04-career-s1b-closeout-evidence-index_v01_20261016-220533-2f06d687.json`.
