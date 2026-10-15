# Merchant career entry and city company panel — QA note (M2, v01)

- Date: 2026-10-15. Base commit: `192c63b`. Engine: Godot 4.7.2 (`work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`).
- Status: **unapproved engineering slice.** M2 stays `in_progress`. No art, scene or playtest acceptance changes.

## What is now playable

The `CommerceLedger` weekly settlement (commit `192c63b`) can now be reached in normal play:

1. Recruit Liang Xu (city) or Zhao Ling (outskirts).
2. Win repeat battles until the level-10 job choice.
3. On the growth screen, pick **转入 行商 / Switch to Merchant**.
4. At a discovered `city` location, open **世界地图 → 商会 / World map → Company**. The city comes from `AppState.current_location_id` and `commerce_city_block_reason()`; nothing is hard-coded. In the current data this is Shanghai, the provisional city.
5. Open a company with that companion, who then leaves the party. Rest a week, review the ledger, recall the companion (an NPC keeps the company at 80%), and station them again later.

## Canon used (all proposal status, pending the user's confirmation)

- The Adaptive aptitude group includes 行商, and the entry threshold is 60. Sources: the game design brief and the Game Bible `jobProposal`.
- Stage names are 行商 and 契约经理, the first two of five in `all-jobs_five-tier-proposal_v01`.
  - The English names "Merchant" and "Contract Manager" are engineering translations, not canon.
  - Stages 3–5 are **not** implemented. Every MVP series has only two stages.
- Skill nodes are tier 1 补给协议 (Supply Pact) and tier 2 公平报价 (Fair Quote), from `adaptive-job-trees_skill-node-proposal_v01`.
  - They are **placeholders**: they have no battle effect, the ledger does not read their ranks, and JP cannot be spent on them.

## Changed files

| File | Change |
|---|---|
| `game/scripts/growth_rules.gd` | Adds the `merchant` series (two stages, `placeholder_skills: true`) and `job_skills_have_effect()`. |
| `game/scripts/growth_screen.gd` | Shows five series buttons (116×41, wrapped). Merchant skill buttons are disabled with a "仅经营 / commerce" label. Adds a Merchant hint line. |
| `game/scripts/app_state.gd` | Adds bilingual strings and a JP guard in `upgrade_job_skill`. Adds `rest_one_week()` (+7 days through `advance_calendar`, reason `rest`) and `commerce_station_candidates()`. |
| `game/scripts/scifi_world_map.gd` | Adds the 商会 / Company button in the bottom strip (cities only) and a company overlay: open/station, recall, rest a week (writes an autosave with note `commerce_rest`), and status. The field-status label now wraps at 388 px so it stays clear of the button. The open panel is modal (see below). |
| `game/scripts/battle_arena.gd` | **Merchant guard only (4 lines; see below).** The file's existing dirty art hunks are unchanged. |
| `game/tests/…merchant-career-city-commerce_playable-path-smoke_m2-v01_20261015-090550-4f6e24f2.gd` | New smoke test (109 checks). |

### `battle_arena.gd` guard diff (relative to the pre-existing dirty working copy)

```diff
@@ -521,6 +521,9 @@  func _use_job_skill(...)
     var member: Dictionary = AppState.member_state(member_id)
+    # Merchant guard: its job skills are placeholders with no battle effect, so they never run or spend energy.
+    if not GrowthRules.job_skills_have_effect(String(member["job_series"])):
+        return false
     var skill_id := requested_skill_id if requested_skill_id != "" else GrowthRules.current_skill_id(member)
@@ -1103,7 +1106,7 @@  func _refresh_text()
-        button.visible = stage < int(controlled_member["job_stage"])
+        button.visible = stage < int(controlled_member["job_stage"]) and GrowthRules.job_skills_have_effect(String(controlled_member["job_series"]))
```

Removing these 4 lines reproduces the pre-edit working copy byte-for-byte (SHA-256 `0e0c78b8…3bd9579`).

What the guard does:

- When the AI is ordered to use a skill, it falls through to the Merchant's **personal** skill.
- The R key, the pause-menu queue and direct calls all return `false` and spend no energy.

### Company panel is modal (`scifi_world_map.gd`)

- While the panel is open, `_commerce_modal()` makes these do nothing: place selection, departure, route options, globe/region switches, zoom, map mouse input, the field log, party talk, save, growth and menu. No time passes and no travel happens.
- The panel never opens over the field log. Esc closes the panel first.
- Keyboard focus stays inside the panel. Every other control in the map canvas is set to `FOCUS_BEHAVIOR_DISABLED` while the panel is visible and restored when it hides by any path.
- Follow-up fix: pressing Open/Station or Recall hides the button that was pressed, so focus was lost and Tab could not recover it. `_keep_commerce_focus()` now moves focus to Back. A throwaway probe outside the repository confirmed that focus stays on a visible panel button after both actions, and that Tab then moves within the panel.
- The smoke test checks all of the above except the follow-up fix (no new test was added). It also checks that the map controls become focusable again after the panel closes.

## Results (repository root, headless unless noted; all exit 0)

| Test | Result |
|---|---|
| new Merchant / company path smoke | `MERCHANT_CITY_COMMERCE_PATH_OK checks=109` |
| commerce weekly settlement smoke | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` |
| travel core / map–travel integration | `GLOBAL_TRAVEL_CORE_OK` / `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=104` |
| global Earth map smoke / export data inclusion | `GLOBAL_EARTH_MAP_SMOKE_OK checks=201` / `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| `m1`–`m7` smokes, `m6_restart`, three `m8_city_*` smokes | all `*_OK` |
| route card / status backing readability (display renderer; captures sent to `%TEMP%`) | `ROUTE_CARD_READABILITY_OK 99 checks` / `STATUS_BACKING_READABILITY_OK 185 checks` |

**Mutation check.** Run in a throwaway copy of `game/` under `%TEMP%`; the shared file was never touched.

- Removing the `_use_job_skill` guard caused 3 failed checks.
- Removing the pause-menu visibility guard caused 1 failed check.
- Removing the JP guard caused 1 failed check.

## Limitations

- **Battle shortcut in the test.** Battles are won by setting the enemy to 1 HP and attacking once. Recruitment, travel, the growth screen, the map panel and save/load all go through the real scenes and buttons.
- **Silent R key.** Pressing R as a Merchant does nothing and shows no message. The help line still lists "R 职业技 / R job".
- **Rest location.** Rest is offered only inside the company panel, so only in cities. There is no rest action elsewhere yet.
- **Placeholder numbers.** Ledger points remain provisional non-currency units (`CommerceLedger.PROVISIONAL_BASE_WEEKLY_INCOME`). There are no prices, currency, robber events or skill-rank effects.
- **No `.uid` file.** The new test has no `.uid`, because Godot `--import` was not run in the shared tree.
- **Human review.** UI fit was checked by the test's layout assertions and by temporary 640×360 captures (zh and en) kept outside the repository. No human visual review has been done.
