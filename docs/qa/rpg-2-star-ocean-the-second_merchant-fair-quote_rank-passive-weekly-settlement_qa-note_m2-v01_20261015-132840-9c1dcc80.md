# Merchant Fair Quote (公平报价) rank passive and weekly settlement — QA note (M2, v01)

- Date: 2026-10-15. Base commit: `da394c3`. Engine: Godot 4.7.2 (`work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`).
- Run id: `9c1dcc80` (note). The smoke test has its own id, `b37eb6d9`.
- Status: **unapproved engineering slice.** M2 stays `in_progress`, with 6/12 gates implemented and none `done`. No art, scene or playtest counter changed (sprites 0/52, scenes 0/11, human playtests 0/2).
- Revision (2026-10-15, caveat fixes): the company panel now separates the full-week rate from the running week's rate, a narrow old-save regression was added, and the earlier "no screenshots" statement is corrected. See [Caveat fixes](#caveat-fixes-2026-10-15).

## Canon used (proposal status)

`adaptive-job-trees_skill-node-proposal_v01` and the Game Bible state list `merchant_fair_quote` as tier 2, branch 互惠, type 被动 (passive), energy 0. Its effect: "驻守商会时提高供需互补协议的稳定收益；只在当前职业为行商时生效" (raises a stationed company's stable income; only active while the current job is Merchant). This slice builds that effect in its smallest form.

The size of the bonus is an engineering placeholder, not canon. No currency, prices, geography, character or market system was added.

## Rule as implemented

| Item | Rule |
|---|---|
| Where it applies | Only to a week paid at the **companion rate**: the same Merchant companion was stationed for the whole week and is still a recruited Merchant. |
| Size | `CommerceLedger.FAIR_QUOTE_PERCENT_PER_RANK = 5` % of `base_weekly_income` per rank. With the provisional base of 100 units: rank 0 = 100, rank 1 = 105, rank 2 = 110, rank 3 = 115. |
| NPC weeks | 80 % (`NPC_EFFICIENCY_PERCENT`) with **no** bonus at any rank. This covers weeks after a recall, the partial week after stationing or re-stationing, and a manager who has left the Merchant job. |
| Opening week | Still 0, unchanged. |
| Staged promotion | Fair Quote counts only at stage 2 (契约经理), using `GrowthRules.fair_quote_rank()`. Promoting to stage 2 gives rank 1 at no JP cost, as every series' stage-2 skill does. A stage-1 Merchant gets no bonus and cannot buy Fair Quote, because the existing stage gate in `upgrade_job_skill` refuses it. |
| JP costs | `GrowthRules.jp_cost(member, "merchant", rank)`, which is the existing Adaptive-aptitude path with `SKILL_JP_BASE` 20/35/55. For Liang Xu (Adaptive 67), rank 2 = 32 JP and rank 3 = 51 JP. Rank 3 is the maximum. |
| When the rank is read | At settlement (`advance_calendar` → `settle_to_week`), from the manager's current member state, clamped to 0–3. It is not stored in the ledger. Settled weeks keep their stored `unitsEarned` and are never re-priced. |
| Station/recall | A stationed manager **cannot** upgrade Fair Quote (`upgrade_job_skill` refuses it) and **cannot** promote or switch series (`choose_job` refuses `promote` and `switch`; `stay` still works), so the rank is fixed while they earn the companion rate. In play, a stationed companion is also out of the party and does not appear on the growth screen. To raise the rank: recall (NPC week) → upgrade in the party → station again (partial NPC week) → full weeks at the new rank. |
| Save/load | Rank and JP (member state) and the ledger (cursor, units, companies) come from the same snapshot. A rank bought after saving is gone after loading. The existing cursor rule (the saved cursor must equal the saved clock's week) still prevents re-settling. A tampered rank such as 99 is clamped to 3, in both `GrowthRules.fair_quote_rank` and `CommerceLedger.companion_rate_percent`. No save-format change was needed. |
| Supply Pact (补给协议) | Still a placeholder: no effect, no JP, and the growth button shows "· 仅经营 / · commerce" and stays disabled. |
| Battle | Unchanged. `GrowthRules.job_skills_have_effect("merchant")` is still `false`, so the existing `battle_arena.gd` guard hides and refuses both Merchant skills. `battle_arena.gd` was **not** edited. |
| Personal skills | Unchanged and still upgradable. |

## Changed files

| File | Change |
|---|---|
| `game/scripts/growth_rules.gd` | Adds `commerce_passive_skills: ["merchant_fair_quote"]` to the Merchant series, plus `FAIR_QUOTE_SKILL_ID`, `job_skill_upgradable()` and `fair_quote_rank()`. Rewords the comment on `job_skills_have_effect` (battle effect only). |
| `game/scripts/commerce_ledger.gd` | Adds `FAIR_QUOTE_PERCENT_PER_RANK`, `FAIR_QUOTE_MAX_RANK` and static `companion_rate_percent()`. `week_income` and `settle_to_week` take an optional `fair_quote_ranks` dictionary; without it they pay what they paid before. Header comment documents the rule. |
| `game/scripts/app_state.gd` | `advance_calendar` passes `_commerce_fair_quote_ranks()`. Adds `commerce_companion_rate_percent()`. `upgrade_job_skill` now uses `job_skill_upgradable()` and refuses Fair Quote while the member is stationed. `choose_job` refuses `promote` and `switch` while the member is stationed. Adds a `growth_fair_quote_note` string in zh and en. |
| `game/scripts/growth_screen.gd` | The placeholder check is now per skill, so Fair Quote is upgradable and Supply Pact is not. A stage-2 Merchant's hint line shows the rank and bonus. |
| `game/scripts/scifi_world_map.gd` | The company line shows the manager's current rate instead of a hard-coded 100. |
| `game/tests/…merchant-fair-quote_rank-settlement-ui-smoke_m2-v01_20261015-132840-b37eb6d9.gd` | New smoke test (63 checks). |
| `docs/progress.md` | Notes the change on the previous entry's limit line and appends a new entry. The file's other uncommitted hunks are untouched. |
| `outputs/…mvp-progress_state…json` | Updates the M2 `remaining` and `details` text, adds one evidence line and bumps the top-level `updatedAt`. Gates are untouched (6/12). |
| `outputs/…game-bible_app…js` | Replaces one sentence in the rule card. The file's other uncommitted hunks are untouched. |

## What the new smoke test covers

Liang Xu goes through the real growth screen buttons (XP is granted directly, not by battles):

1. Stage-1 Merchant: no Fair Quote button, the Supply Pact placeholder is disabled, and no JP is spent.
2. Promotion at level 20 gives rank 1 at no JP cost. The button shows the exact cost, Supply Pact presses spend nothing, and an upgrade spends exactly 32 JP. The hint shows Lv1 +5 %, then Lv2 +10 % in zh and en, and fits on the 640 px screen.
3. The personal skill still upgrades.
4. A real battle scene: neither Merchant skill is shown in the pause menu, and neither runs or spends energy at stage 2.
5. Stationed: the upgrade is refused. Weekly results are opening week 0, then 110.
6. Save, then rest one week, recall and buy rank 3, then load: rank 2, JP, ledger and post come back, and the next week pays 110 once.
7. NPC week 80 at rank 2. Rank 3 is bought in the party, then the post is re-stationed: the partial week pays 80, then the full week 115.
8. Tamper and guard cases: rank 99 still pays 115, a stage-1 record pays 100, and leaving Merchant pays 80. The company panel shows 115 % and its text still fits.
9. Direct API: a stationed manager is set to a stage-1 Merchant with a pending choice. `choose_job` returns `false` for both `promote` and `switch` (to a series Liang Xu can enter). Series, stage, Fair Quote record, pending choice and post are unchanged, and that week pays 100. After recall, the pending promotion goes through.

## Results (repository root, headless; all exit 0)

| Test | Result |
|---|---|
| new Fair Quote smoke | `MERCHANT_FAIR_QUOTE_OK checks=63` (58 before the `choose_job` follow-up) |
| Merchant / company path smoke | `MERCHANT_CITY_COMMERCE_PATH_OK checks=109` |
| commerce weekly settlement smoke | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` |
| travel core / map–travel integration | `GLOBAL_TRAVEL_CORE_OK` / `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=104` |
| Earth map / export data inclusion | `GLOBAL_EARTH_MAP_SMOKE_OK checks=201` / `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| `m1`–`m7`, `m6_restart`, `m8_city_integration` / `navigation` / `reentry` | all `*_OK` |
| Game Bible M2 gates check (Node) | `RESULT PASS (5 checks)` |

`git status --porcelain` was compared before and after the Godot runs. The only new entries were the new test file and two sentry p5 files from another session. No `.uid` file was created, and `--import` was not run in the shared tree.

**Mutation check.** Run in a copy of `game/` under `%TEMP%\fq-mut-b37eb6d9`; the shared files were never touched. Each mutation was applied alone, and the copy was restored after each one.

**Follow-up (`choose_job` guard).** Only the new Fair Quote smoke (63 checks) and the Merchant / company path smoke (109 checks) were re-run; the other rows above are from the original slice. The guard mutation was applied to the shared `game/scripts/app_state.gd` for one run and restored from a byte copy straight after.

| Mutation | Result |
|---|---|
| bonus percent set to 0 | FAILED (3) |
| bonus also added to NPC weeks | FAILED (1) |
| stage-2 gate removed | FAILED (1) |
| Supply Pact made upgradable | FAILED (1) |
| stationed-upgrade freeze removed | FAILED (8) |
| ranks not passed to settlement | FAILED (7) |
| panel rate hard-coded to 100 | FAILED (1) |
| Merchant skills given a battle effect | FAILED (2) |
| ledger clamp removed | FAILED (1) |
| both clamps removed | FAILED (1) |
| stationed `choose_job` guard removed (follow-up) | FAILED (4) |
| `GrowthRules.fair_quote_rank` clamp removed alone | **passed**: expected, because the ledger clamp still caps the rate |

## Limitations

- **Placeholder size.** +5 % per rank is an engineering placeholder. No profit formula or balance has been decided, and ledger points are still not currency.
- **Rank read at settlement.** The rank cannot change mid-week through the UI or the `AppState` API: a stationed manager is out of the party, off the growth screen, and refused by both `upgrade_job_skill` (Fair Quote) and `choose_job` (`promote`/`switch`). Only direct edits to member state (as the tamper checks do) can still change it; those are clamped but not blocked.
- **Legacy saves.** A save from `da394c3` with a stage-2 Merchant already has Fair Quote rank 1 in its record. That manager now earns 105 per full week from the next settlement on; past weeks are not re-priced. This is now covered by a regression check (see [Caveat fixes](#caveat-fixes-2026-10-15)). The check builds a save with the `da394c3` shape in the current build; it does not load a file written by the `da394c3` binary.
- **Supply Pact.** It has no effect, and its proposal effect (battle consumables and a supply/demand readout) is not built.
- **Merchant R key.** Pressing R as a Merchant in battle still does nothing and shows no message (unchanged from `da394c3`).
- **Test shortcut.** XP is granted directly rather than through repeat battles. The `da394c3` path smoke still covers that route.
- **UI review.** UI fit is checked by layout assertions (hint label width, company-panel text height) and by real 1280×720 zh/en captures (listed below). No human review has been done. *Correction:* an earlier version of this line said no screenshots were taken. That stopped being true once the `140030` set was captured (2026-10-15 14:00 local), and the line was not updated then.

## Caveat fixes (2026-10-15)

Only Fair Quote code, its test and capture harness, and Fair Quote tracking text changed. Battle, art and Liangzhu files are untouched. M2 stays `in_progress` (6/12 implemented, none `done`), and all counters are unchanged.

### 1. Company panel: full-week rate vs. the running week

**Problem.** The panel's companion line showed the Fair Quote rate (for example 115 %) as "收益 / rate", even in the partial week after stationing or re-stationing. That week actually settles at the NPC 80 %, with no bonus.

**Fix.**

- The companion line now says **满周收益 / full-week rate** X %.
- When the running week settles differently, a second, indented line follows it:
  - Partial week after (re-)stationing: "本周：派驻未满一周，按普通 NPC 80% 结算；下周起按满周 X%。" / "This week: not stationed for the full week, so it settles at the NPC rate (80%); X% from next week."
  - Opening week: "本周：开业当周不计收益；下周起按满周 X%。" / "This week: opening week, earns nothing; X% from next week."
- The running week's rate comes from the ledger rule, not a copy of it:
  - New `CommerceLedger.week_rate_percent()`; `week_income` now returns `base × week_rate_percent / 100`, so payouts are unchanged.
  - New `AppState.commerce_current_week_rate_percent(city_id)` reads it for the current calendar week.
- NPC-run company lines are unchanged.

| File | Change |
|---|---|
| `game/scripts/commerce_ledger.gd` | Adds `week_rate_percent()`; `week_income` delegates to it. |
| `game/scripts/app_state.gd` | Adds `commerce_current_week_rate_percent()`. `commerce_company_companion` now reads 满周收益 / full-week rate. Adds `commerce_week_partial` and `commerce_week_opening` in zh and en. |
| `game/scripts/scifi_world_map.gd` | `_refresh_commerce` adds the this-week line when the running week's rate differs from the full-week rate. |
| `game/tests/…rank-settlement-ui-smoke…b37eb6d9.gd` | Panel checks in zh and en for the opening week, a full week at rank 2, the re-stationed partial week at rank 3 and a full week at rank 3. The re-stationed case also checks the literal zh/en wording. Adds the old-save regression. |
| `game/tests/…ui-visual-capture…495b6ff0.gd` | After the full-week shots, Liang Xu is recalled, one NPC week passes (80), and Liang Xu is stationed again through the panel buttons. Then the zh/en partial-week shots are taken. 6 captures instead of 4. |

### 2. Old-save regression

`_test_legacy_save()` in the smoke test:

1. Liang Xu becomes a Merchant and is promoted through `choose_job`.
2. The Merchant record must equal the `da394c3` shape exactly: `{"stage": 2, "skills": {supply_pact: 1, fair_quote: 1}}`.
3. Liang Xu opens the company, and the opening week and one full week pass.
4. The snapshot's commerce block must keep its version-1 keys, with no Fair Quote field.
5. That week's amounts are set to the 100 that `da394c3` paid (`ledgerUnits` and `unitsEarned`). The snapshot is written with `SaveStore.write_entry`, the run is reset, and the save is loaded through `load_save`.

Results:

- Rank 1, the post and the 100 come back unchanged.
- The running week is at 105 %.
- The next rest settles one week at **105**. The ledger becomes 205, and the earlier week stays at 100.

### Results (repository root, headless unless noted; all exit 0)

| Test | Result |
|---|---|
| Fair Quote smoke | `MERCHANT_FAIR_QUOTE_OK checks=91` (was 63) |
| Merchant / company path smoke | `MERCHANT_CITY_COMMERCE_PATH_OK checks=109` |
| commerce weekly settlement smoke | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` |
| map–travel integration / Earth map | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=104` / `GLOBAL_EARTH_MAP_SMOKE_OK checks=201` |
| `m2_smoke`, `m6_smoke`, `m6_restart_smoke` | `M2_SMOKE_OK`, `M6_SMOKE_OK`, `M6_RESTART_OK` |
| capture harness (windowed, `--resolution 1280x720`, gl_compatibility) | `FAIR_QUOTE_CAPTURE_OK captures=6` |

The Fair Quote, path and commerce smokes were run again after a final en wording change. The other rows come from the run just before that change, which only touched one English string.

`git status --porcelain` was compared before and after. The new entries are this run's capture PNGs and manifest, plus one Liangzhu tool file from another session. No `.uid` file was created.

**Mutations** (in a copy under `%TEMP%\fq-caveat-mut-7c41e2a9`; shared files untouched):

| Mutation | Result |
|---|---|
| opening-week line never shown | FAILED (2) |
| partial-week line never shown | FAILED (3) |
| running week read as the next week | FAILED (7) |
| zh label back to 收益 | FAILED (1) |
| en label back to "X% rate" | FAILED (1) |
| zh partial-week line reworded | FAILED (1) |
| Fair Quote ignored (always 100) | FAILED (1, in the rule checks before the old-save case runs) |
| rank 1 counted as 0 | FAILED (24) |

## Visual captures

Harness: [`game/tests/rpg-2-star-ocean-the-second_merchant-fair-quote_ui-visual-capture_m2-v01_20261015-135951-495b6ff0.gd`](../../game/tests/rpg-2-star-ocean-the-second_merchant-fair-quote_ui-visual-capture_m2-v01_20261015-135951-495b6ff0.gd). It runs windowed at `--resolution 1280x720` (640×360 logical). All PNGs are 1280×720 and reloaded from disk. The captures are test-only and not approved.

**Set `140030` (original slice, before the caveat fix).** Its panel still shows the old "收益 110% / 110% rate" label.

- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_growth-ui_fair-quote-rank2-zh_20261015-140030-d937c96a.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_growth-ui_fair-quote-rank2-en_20261015-140030-3b5f6db9.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_full-week-110-zh_20261015-140030-0db6eabc.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_full-week-110-en_20261015-140030-ecf41a06.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_ui-visual-capture-manifest_m2-v01_20261015-140030-79db5206.json`

**Set `142808` (after the caveat fix; superseded by `143253`, kept as history).** Its en partial-week shot has the mixed-language feedback line described below.

- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_growth-ui_fair-quote-rank2-zh_20261015-142808-1b3e706d.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_growth-ui_fair-quote-rank2-en_20261015-142808-a533c855.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_full-week-110-zh_20261015-142808-ffb753a9.png`: 满周收益 110%, no this-week line.
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_full-week-110-en_20261015-142808-b4354a93.png`: full-week rate 110%, no this-week line.
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_restationed-partial-week-npc80-zh_20261015-142808-18dff252.png`: 满周收益 110%, plus "本周：派驻未满一周，按普通 NPC 80% 结算；下周起按满周 110%。"
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_restationed-partial-week-npc80-en_20261015-142808-7886ddb4.png`: full-week rate 110%, plus the English partial-week line (it wraps to two lines and fits).
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_ui-visual-capture-manifest_m2-v01_20261015-142808-8d8934b2.json`

**Stale feedback in `142808` (harness artifact, fixed in the harness only).** In the `142808` en partial-week shot, the first line reads "梁序 is now stationed at the company." `_commerce_station` stores the feedback as a text key plus the member name resolved at press time (`scifi_world_map.gd:1009`). The harness stationed Liang Xu in zh, then switched language with the panel open and re-rendered it, so the zh name ended up in the en template. Players cannot do this. The panel is modal, the map has no language control, and `open_commerce()` clears the feedback whenever the panel opens. So production UI was not changed. The harness now clears `commerce_feedback` after switching to en, before the en partial-week capture, and records `en_stale_station_feedback_cleared: true` in the manifest. It also fails if either en panel capture (full-week or partial-week) has any CJK character in the body or title. The full-week en shot keeps its "Rested 7 days…" line, because those arguments are numbers and re-render correctly.

**Set `143253` (current; harness stale-feedback fix, no game code changed).** Smoke rerun first: `MERCHANT_FAIR_QUOTE_OK checks=91`, exit 0. Then the capture: `FAIR_QUOTE_CAPTURE_OK captures=6`, exit 0, `failures: []`, windowed, gl_compatibility, Godot 4.7.2. The before/after `git status --porcelain` diff lists only the seven files below. No `.uid` file was created.

- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_growth-ui_fair-quote-rank2-zh_20261015-143253-df306c23.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_growth-ui_fair-quote-rank2-en_20261015-143253-4fa1695b.png`
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_full-week-110-zh_20261015-143253-e6175ba1.png`: 满周收益 110%, no this-week line.
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_full-week-110-en_20261015-143253-ded28c0d.png`: full-week rate 110%, no this-week line, fully English.
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_restationed-partial-week-npc80-zh_20261015-143253-18749dc7.png`: "梁序 已派驻商会。", 满周收益 110%, plus the zh partial-week line.
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_company-panel_restationed-partial-week-npc80-en_20261015-143253-c11173f6.png`: no transient feedback line, full-week rate 110%, plus the English partial-week line. Fully English.
- `outputs/rpg-2-star-ocean-the-second_merchant-fair-quote_ui-visual-capture-manifest_m2-v01_20261015-143253-d81d9a0b.json`
