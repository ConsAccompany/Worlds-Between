# Ten-node progression: SCIENCE-MVP rules slice — QA note (Workstream C)

- Date: 2026-10-16 01:30 local
- Worker: Claude Code, signed in to Claude Max (`claude auth status`: `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`). `ANTHROPIC_API_KEY` was not set. No API key, credits or paid fallback was used.
- Status: **technical rules slice, unapproved.** It implements the *shape* of the creator's 2026-10-15 progression rules. It does **not** author any of the 710 approved skill designs (20 × 10 career + 51 × 10 personal). The catalog records `approvedNodeDesignsAuthored: 0`.
- Nothing was staged, committed or pushed. These were not touched: `game/scripts/battle_arena.gd` (its unrelated dirty art hunks), art paths, the Game Bible app and server, `docs/progress.md`, and the completion meter.

## Canon implemented

Source: creator decisions note §2 (`docs/design/…creator-decisions-2026-10-15…39efc292.md`), plus the roster rules in `outputs/…all-jobs_five-tier-proposal…6f2b9c11.json`.

| Rule | Runtime behaviour |
|---|---|
| Each series has 10 nodes, 2 per stage across 5 stages | The catalog has 20 series × 10 nodes. Entering a stage opens both of its nodes at rank 1, with no JP. This happens on a new run, on recruitment, on promotion and on the first switch into a series. |
| JP only upgrades nodes | `GrowthRules.jp_cost` returns −1 for rank 1 and for ranks above 5. JP cannot open a node of a stage the member has not entered. |
| Career and personal skill cap is 5 | `SKILL_RANK_CAP := 5`. This applies to job nodes, the personal signature and other personal nodes. Commerce `FAIR_QUOTE_MAX_RANK` is now 5 (rate 105–125 %). |
| Stages 1–4 advance at the ten-level choice; stage 5 needs the series final quest, cleared once for the whole party | `GrowthRules.can_promote`, `AppState.cleared_final_quests`, `AppState.clear_series_final_quest`. The MVP has **no final-quest content**, so in normal play stage 5 is unreachable. The growth screen says so ("第五阶需先完成系列后期任务"). |
| Changing series preserves records | This already held. It is now also asserted for stage 4/rank 5 through a firearms detour. |
| Personal tree: 10 nodes, all opened by level 100; the initial unique skill is available on recruitment | The catalog has 51 identities × 10 nodes. Node 1 is the signature: `availableOnJoin`, level 1. Its rank remains `personal_skill_rank`, which the battle reads. Nodes 2–10 open at rank 1 at their level gate and are stored in `personal_node_ranks`. A late recruit opens every node at or below its synced level at once. |

## Files

| File | Change | sha256-text-lf-v1 |
|---|---|---|
| `game/data/growth/rpg-2-star-ocean-the-second_progression-ten-node_science-mvp-skeleton_v01_20261016-005300-e36e5d2c.json` | new catalog (123 KB) | `d0ed82e39977dda59083130b288f9a98d9ef154bd6c32f31ec58f578e70fdff7` |
| `game/scripts/growth_rules.gd` | catalog loader, stage/node/personal rules, migration | `9e672e65f1157b1eda2fe5d95307c1e4c2319722a47b672cb84814a3206ddbf3` |
| `game/scripts/app_state.gd` | node grants, final-quest flag, upgrades, save/load/validation, strings | `69e930c6b61d5023c80186f74697e31a2c2f07d1cbdf5874b00779b7b5736f23` |
| `game/scripts/growth_screen.gd` | 5-stage promotion and a "技能节点 / Skill nodes" overlay | `67289a2e8dafbdf255aa6ea40aece66fabb00117ada4fe417746126de6837aff` |
| `game/scripts/commerce_ledger.gd` | `FAIR_QUOTE_MAX_RANK` 3 → 5 and its comment | `2578ee0756d4b7983a85969c839c54a45aee23641eaf40110b6bf794ec4d5158` |
| `game/tests/…progression-ten-node_rules-save-ui-smoke_science-mvp-v01_20261016-005300-e36e5d2c.gd` | new test | `afc1ab12722a34865e509bc9850b58c70464a29c7e01131f265be085476a161a` |
| `game/tests/…merchant-career-city-commerce_playable-path-smoke…4f6e24f2.gd` | 1 assertion: 5 approved stage names, not "only 2" | `c5bd7ce85142dce87345e5bcedfd936a0dfe64161d872102dab6b4aa43d684d3` |
| `game/tests/…merchant-fair-quote_rank-settlement-ui-smoke…b37eb6d9.gd` | rank-3 cap assertions → rank 5 (125 %); the legacy-save fixture now writes the da394c3 record shape explicitly and asserts the migration | `5ab4b6f60f39aba251ddfcebd116b07eee3376c9182dcade0bc01b589d7c00e0` |

## Catalog derivation

A one-off generator, kept outside the repo in `%TEMP%`, read three sources: the approved roster (20 series: ids, Chinese names, English series names, the five stage names, aptitude), the Game Bible `characters` (51 ids, names) and the decision note. It records the `sha256-text-lf-v1` of each source inside the JSON. The new test re-reads the roster and the Game Bible from `outputs/` and checks every series and identity field-for-field.

- **Career node ids.** The five runtime series keep their existing skill ids as stage-1 and stage-2 node "a" (for example `sword_slash`, `sword_arc`, `merchant_fair_quote`). Every other node is `<series>_s<stage><a|b>`, with `effect: "none"` and `status: "skeleton-pending-design"`. **9 of 200** career nodes have a runtime effect: 8 battle actions (sword, firearms, tactics, relics) and Fair Quote (commerce). Supply Pact stays a no-effect placeholder.
- **Personal node ids.** These are `<identity>.p01`–`p10`. **4 of 510** have a runtime effect: the existing battle signatures of the hero, Liang Xu (`character-01`), Zhao Ling (`character-31`) and Ji Cheng (`character-16`). The other 47 identities have structural nodes only. No signature names were invented.
- **Personal unlock gates** are `1, 6, 14, 22, 32, 42, 54, 66, 80, 100` for all 51 identities. The final gate, Lv100, is the creator's decision ("all 10 personal nodes unlock at level 100"). Gates 2–9 are the shared gates from the unapproved hero/c01–c03 proposal and stay labelled provisional in the catalog.
- **JP bases** for ranks 2/3/4/5 are 35/55/80/110. Ranks 2–3 keep the earlier runtime costs; 4–5 are placeholders. The existing aptitude discount and the personal-skill home-series pricing are unchanged.
- **Stage names.** Chinese comes from canon for all 5 stages. The runtime display therefore changes from 剑士/参谋/遗物学徒 to 剑客/分析员/识物者, and so on; Merchant (行商/契约经理) is unchanged. There are no approved English stage names, so the existing runtime English labels are kept for stages 1–2 of the 5 runtime series (for example "Swordmaster" for 连刃士). All other stages fall back to "<Series> · Stage N".
- **Runtime-enterable series** are still only the 5 with existing behaviour (`GrowthRules.SERIES`). The other 15 are catalogued but cannot be entered: they have no battle behaviour, and `battle_arena.gd` was out of scope.

## Save migration (additive; `SaveStore.SCHEMA_VERSION` unchanged)

- New optional fields: snapshot `growthFinalQuests` (series → true), and `personal_node_ranks` per member.
- On load, `GrowthRules.normalize_member` does four things:
  1. Opens every node that a saved record's stage or a member's level already earns.
  2. Clamps ranks to 1–5 and stages to 1–5.
  3. Converts JSON floats to ints.
  4. Never removes records. Records for unknown series are kept as they are.
- `AppState.growth_state_migrated` reports whether anything was added or clamped.
- Validation rejects these shapes: `job_stage` outside 1–5, a non-dictionary `job_records`/`skills`/`personal_node_ranks`, and `growthFinalQuests` containing unknown series or non-`true` values.

## Test evidence

Godot 4.7.2 (`work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`), run from the repo root as `--headless --path game --script res://tests/<name>.gd`.

**Baseline before the change:** m4, m5, m6, the merchant path test (109 checks), Fair Quote (91) and commerce weekly (149) all passed.

**After the change:**

| Test | Result |
|---|---|
| new `…progression-ten-node_rules-save-ui-smoke…` | `PROGRESSION_TEN_NODE_OK checks=458` (exit 0) after the Lv100 correction below. Before it: `checks=455`, and a windowed run with `-- --capture=<dir>` gave `checks=457` (the two extra checks are the capture writes). |
| m1, m2, m3, m4, m5, m6, m6_restart, m7 smoke | all `*_OK`, exit 0 |
| m8 city integration / navigation / re-entry | OK, exit 0 |
| merchant city-commerce path | `checks=109` OK |
| merchant Fair Quote rank/settlement/UI | `checks=92` OK (was 91; one migration assertion added) |
| commerce weekly settlement | `checks=149` OK |
| global earth map / travel core / export-data inclusion / route figures v06 / US migration | OK |
| canopy silhouette, field NPC visual, character gallery | OK |

**Mutation check.** Setting `LEVEL_CHOICE_STAGE_CAP` to 5 made the new test fail 3 checks (stage-5 gate, last-stage limit, screen text). The file was restored.

## Correction 2026-10-16: final personal gate Lv95 → Lv100

The first pass ended the personal gates at Lv95. The creator decision is that all 10 personal nodes unlock at level 100, so node 10 of every identity (51 × `.p10`) and `rules.personalUnlockLevels[9]` are now 100. `personalUnlockLevelsStatus` now marks Lv100 as the creator decision and gates 2–9 as provisional. No script changed. The only changes are to the catalog, the test and this note.

- The test now asserts that `rules.personalUnlockLevels` runs from Lv1 to Lv100. It also asserts that every identity's node gates equal those shared gates, with node 10 at exactly 100. It reaches level 99 and checks that `.p10` is still closed, then opens it at level 100. That gives 3 more checks, for 458 in total.
- Mutation: one identity's node 10 was set back to 95, and 2 checks failed (the hero's gate check and the Lv99 boundary). The catalog was restored from a byte copy, and 51 nodes are at 100.
- Rerun, headless, all exit 0: the new test (`checks=458`); m1–m7, m6_restart and m8 city integration/navigation/re-entry; merchant path (`checks=109`); Fair Quote (`checks=92`); commerce weekly (`checks=149`). The windowed capture run was not repeated, because the overlay text and layout did not change.
- Self-review of save migration and growth UI found no regression that needed a code change. `normalize_member` runs only after `_valid_snapshot`. A float/int difference from JSON alone does not set `growth_state_migrated`. Records are only added to, and old saves (stage ≤ 2, ranks ≤ 3) gain exactly the nodes they earn. The main-screen stage buttons, the promote button and the overlay all read the same rules. One known gap remains, and it is not new: for a stationed Contract Manager, the overlay's Fair Quote button looks upgradable, but the press is refused. The main-screen button has always behaved the same way, so it was left unchanged.

**Not passing in this headless sweep, judged unrelated:**
- Two `global-map-*_readability-check` tests and `protagonist-male_high-fidelity-city-scale-check` timed out (exit 124). The readability checks state in their headers that they need a display renderer and must not be run with `--headless`.
- Five `*_sideview-combat-smoke_m8-prototype` tests exited 1 with "Capture viewport missing or wrong size". That is a dummy-renderer texture capture failure.
- `quantized-south-idle…report-check` exited 1 because it expects a report-file argument.
- `scifi-world-map_background-visual-check` exited 1 on hard-coded marker geometry. It has no growth references; the map changed in `cb6ca33`.

None of these failures were re-run on an isolated HEAD copy.

**Overlay captures** (zh/en, 1280×720 window) were written to `%TEMP%\wsc-growth\capture\` and are **not** in the repo. Everything fits on screen. Skeleton nodes are greyed as "Lv1 · 待设计 / pending design" and locked nodes show their gate. The summary line states "职业 2/10 · 个人 1/10" nodes with an effect.

## Follow-up 2026-10-16: stationed Fair Quote UI and recruit stage seeding

This follow-up came after the root inspected the zh/en 1280×720 overlay captures and this note. It used the same worker and account (Claude Max, `firstParty`, no API key or paid fallback). Nothing was committed. Art, `battle_arena.gd`, the Game Bible app and server, `docs/progress.md` and the meter were not touched.

**1. Fair Quote while stationed (fixes the known gap above).** The new `AppState.fair_quote_frozen(member_id, skill_id)` is now the single rule. Three places read it:
- `upgrade_job_skill`, which refuses the press as before;
- the main-screen stage-2 button, which is disabled and reads "公平报价 · 驻守冻结 / Fair Quote · stationed";
- the overlay node, which is disabled and reads "Lv1 · 驻守冻结 / Lv1 · stationed".

The localized reason "驻守商会中：公平报价已冻结，召回后才能升级。 / Stationed at a company: Fair Quote is frozen; recall to upgrade." replaces the Merchant note on the main screen. It is also added as the last line of the overlay summary. Supply Pact, the personal signature and personal nodes are not frozen. After recall, both buttons can be pressed again. In normal play a stationed companion is not in the active party, so its member button is hidden. The test reaches this state by selecting the member directly.

**2. Recruit stage seeding. PROVISIONAL: this policy needs creator review.** `GrowthRules.recruit_stage(level, series, cleared_final_quests)` treats a level-synced recruit as having promoted in its home series at every ten-level choice it has passed. The stage is `1 + level / 10` (Lv1–9 → 1, Lv10 → 2, Lv20 → 3, Lv30+ → 4). Stage 5 needs level ≥ 40 **and** that series' party-wide final quest; another series' quest does not count.

The recruit's record holds that stage, and `new_job_record` opens every node of stages 1..stage at **rank 1 only**. JP stays 0, no pending choice is created, and no rank 2–5 is seeded. Each recruit keeps its home series and aptitudes. The battle action set is unchanged: stages past 2 keep the stage-2 action.

The older personal-signature catch-up (`mini(3, 1 + (level − 1) / 20)`) predates this slice and is still in place. It is the only JP-priced rank a recruit gets free. I left it unchanged rather than silently removing it; whether to keep it is a creator decision.

Save compatibility: there is no schema change, and loading never re-seeds a stage. An old save with a stage-2 level-23 recruit loads at stage 2 and only gains its stage-2 nodes. A stage-5 recruit round-trips without migration.

**Tests.**
- The progression smoke now reports `checks=494` headless (was 458).
  - New recruit checks: a level table for the stage formula, a level-45 recruit held at stage 4 with 8 rank-1 nodes and no JP, the other-series quest refused, stage 5 with 10 nodes after its own quest, and the round trip and old-save cases above.
  - New stationed-UI checks: both buttons, the reason line and on-screen fit in zh and en, the presses spending nothing, and recall restoring the upgrade.
- I also fixed a vacuous assertion: the "invalid growth save is rejected" cases wrote to manual slot 4, but `MANUAL_SLOTS` is 3. The write returned "" and the check passed without testing anything. They now use slot 3 and assert that the write succeeded.
- `m4_smoke` and `m5_smoke` asserted the old cap (a level-23 recruit at stage 2). They now expect stage 3, and m5 also checks `tactics_s3a` at rank 1.
- Mutation checks:
  - Restoring `mini(2, …)` failed 5 checks.
  - Disabling the screen's frozen branches failed 4 checks (both buttons × zh/en).
  - Both files were restored and confirmed by byte compare.
- Reruns, headless, all exit 0:
  - m1, m2, m3, m4, m5, m6, m6_restart and m7 smokes;
  - m8 city integration, navigation and re-entry;
  - merchant path (`checks=109`), Fair Quote (`checks=92`) and commerce weekly (`checks=149`).
- A windowed run at `--resolution 1280x720` with `--capture` gave `checks=498`. The captures are in `%TEMP%\wsc-growth\capture2\`, not in the repo: overlay-zh/en and stationed-zh/en. I viewed both stationed captures: the Fair Quote node is greyed with the reason, and all text fits.

| File | sha256-text-lf-v1 after follow-up |
|---|---|
| `game/scripts/growth_rules.gd` | `05f2c0147f9cfc9f8a24398e5c1a6a59a589dda2de4606d268b0fab239c89b71` |
| `game/scripts/app_state.gd` | `2df470f5f40128f8a128e8a3efb331bfb9dff88e0ce38c0ec31311ae8db61cc1` |
| `game/scripts/growth_screen.gd` | `640bd3971a39b76dba6fcdb6afb0c754657fdbe73357d8720c014b63fbb85b76` |
| `game/tests/…progression-ten-node_rules-save-ui-smoke…e36e5d2c.gd` | `a1cd10836f59aff3b8a4c7df85c8fbe1028a73b8afd345ed02d15fe8a3a9ee9f` |
| `game/tests/m4_smoke.gd` | `ff4100fb27790386b516e5f62f2f27701ddfbf6b14965a26176dfd3ffc1d0d0d` |
| `game/tests/m5_smoke.gd` | `053717a4bf503a22fe1194aab16cdf646ad814c20c4d7b22d8ea26a8fec955fb` |

The hashes in the Files table above are from the first pass. They are now superseded for these files.

## Limitations (do not overstate)

1. **No skill designs.** 191 career nodes and 506 personal nodes are skeletons. They open and are saved, but they have no name, number or effect, and they take no JP (following the earlier Supply Pact precedent). The 50 研学 proposal nodes and the 40 hero/c01–c03 proposal nodes are unapproved and were **not** imported.
2. **Stages 3–5 add no new battle action.** The battle keeps the stage-2 action skill (`current_skill_id`), because `battle_arena.gd` was out of scope.
3. **Rank 4–5 balance is unreviewed.** The existing battle formulas scale linearly with rank. For example, Ji Cheng's signature delays the enemy by 3.25 s at rank 5. Fair Quote at rank 5 pays 125 %.
4. **No final-quest content.** Stage 5 is reachable only through `clear_series_final_quest` (tests).
5. **Recruit seeding is provisional** (follow-up 2 below). A recruit enters at stage `1 + level / 10`, held at 4 until the party clears that series' final quest. Only rank-1 stage nodes come with it. The older free personal-signature catch-up (up to rank 3 by level) is kept as it was. It is the one JP-priced rank that recruits still get without paying, and it is flagged for creator review.
6. **15 series are catalogued but cannot be entered.** The growth screen still offers 5 series buttons.
7. **Unapproved placeholders.** The English stage labels, personal unlock gates 2–9 (the final Lv100 gate is canon), rank 4–5 JP costs, the recruit stage formula and the kept recruit signature catch-up are placeholders pending creator review.
8. **No human review or playtest.** Counters are unchanged: sprites 0/52, science scene visuals 0/11, human playtests 0/2.
