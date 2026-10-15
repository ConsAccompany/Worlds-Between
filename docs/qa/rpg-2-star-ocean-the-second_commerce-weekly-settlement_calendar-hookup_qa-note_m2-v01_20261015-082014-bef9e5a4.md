# Commerce weekly settlement ↔ calendar week hookup — QA note (M2, v01)

- Date: 2026-10-15
- Engine: Godot 4.7.2.stable.official.ed1daf0bf (`work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`)
- Status: **implemented and automated-tested; not reviewed by a person.** M2 is not complete.
- Revised: 2026-10-15 after review. Settlement now runs before `calendar_advanced`, and a saved `travel.calendarWeekIndex` must match its clock. See [Review follow-up](#review-follow-up-2026-10-15).
- Revised again: 2026-10-15 after a second review. A saved commerce cursor must now **equal** the saved clock's week. A cursor behind it is rejected instead of being moved up on load. See [Review follow-up 2](#review-follow-up-2-2026-10-15-strict-cursor).

## What this adds

Each Monday 00:00 crossing in `AppState.advance_calendar` now settles a small, independent commerce ledger. It settles before any calendar signal is emitted. `calendar_week_transition` is still emitted, but only as a notification.

- `game/scripts/commerce_ledger.gd` (`CommerceLedger`, new): state and rules only. It holds companies (one per city), the cursor (`settledWeekIndex`), the balance, the per-week income rule, and save validation and loading.
- `game/scripts/app_state.gd`:
  - settles the ledger inside `advance_calendar`, after the clock and week are updated and before `calendar_advanced` is emitted;
  - adds a `commerce_weeks_settled(result)` signal;
  - adds eligibility checks and `open_commerce_company`, `assign_commerce_manager`, `recall_commerce_manager` and `commerce_ledger_state`;
  - writes and reads a `commerce` snapshot block;
  - validates that block;
  - clears the ledger in `begin_new_run`.

There is no UI and no marketplace. Robber events, prices and stationed-companion skill effects are not implemented.

## Rules as implemented (provisional where marked)

| Rule (user / Game Bible) | Implementation |
|---|---|
| One company per major city | Any **discovered** location with `type: "city"` can host one company. The data has no major/minor split yet, so every city counts. *Provisional.* |
| Only a recruited companion in the merchant job may be stationed | `commerce_manager_block_reason` refuses `hero`, unknown, unrecruited and non-`merchant` members, and members already stationed. |
| One site per manager | `CommerceLedger.open_company` / `assign_manager` refuse a manager who already runs a company. Save validation rejects duplicate managers. |
| Stationed companion leaves the active party | Removed from `active_party_ids`, but stays in `recruited_members` and `member_states`. |
| On recall an ordinary NPC runs it at 80% | The company stays open with `managerId: ""`. NPC weeks pay `base × 80 / 100`. The recalled companion rejoins the party if there is room; otherwise they stay recruited as a reserve. |
| Stable income every game week | Each week that ends pays one amount per company. `PROVISIONAL_BASE_WEEKLY_INCOME = 100`; `base_weekly_income` can be changed and is not saved. **Not a final economy.** |
| Stationed companion gets 25% XP/JP | Already true through the existing reserve rule: `award_battle_rewards` gives 25% to members outside the active party, and `award_survey_jp` gives 2 of 8. The test checks this for battle JP. There is no separate commerce-specific hookup. |
| No coin/account system exists | The balance is `ledgerUnits` with `ledgerUnitKind: "provisional-ledger-unit"`. It is a separate ledger, **not usable currency**. Nothing spends it. |
| No permanently missed companions | Recall always works, including for a company whose city ID is later removed from the data: unknown IDs are kept, as the travel block does. |

Design choices the user had not specified (all provisional):

- **Opening week:** the partial week a company opens in pays 0. Income starts with the first full week.
- **Full-week rule:** a week pays the companion rate only if the same merchant companion was stationed for the entire week. A recall, assignment or job change during the week gives the NPC rate for that week. This stops a player from earning the full rate by stationing a companion just before Monday.
- **Job change:** a stationed companion who leaves the merchant job earns only the NPC rate until they are a merchant again. They are not recalled automatically.
- **Opening needs a companion:** a company can't be opened with an NPC manager. NPCs take over only after a recall.

## How double settlement is prevented

1. **Cursor.** `settledWeekIndex` is the calendar week the ledger has caught up to. Crossing into week N settles weeks from `max(cursor, previous_week_index)` up to N − 1, then sets the cursor to N. A repeated, overlapping or late `settle_to_week` call with N ≤ cursor does nothing. Emitting `calendar_week_transition` from outside settles nothing.
2. **`max(…, previous_week_index)`.** If the clock is set directly, with no transition, the skipped weeks are never paid. Only the weeks of the real crossing are.
3. **Loading emits nothing.** `load_save` restores the clock and ledger without emitting `calendar_advanced` or `calendar_week_transition`, so loading can't settle anything. The cursor is saved, so replaying a crossing after loading pays that week once from the saved balance, never on top of the later balance.
4. **Settled before any handler runs.** `advance_calendar` updates the clock, week and ledger before it emits `calendar_advanced`, so an autosave in any calendar handler stores a cursor that is already current.
5. **Strict cursor invariant on load.** A saved block is valid only if `settledWeekIndex == TravelCalendar.week_index(saved calendarMinutes)`. For a save with no travel block, the saved week is the calendar start week that the travel migration restores. A cursor **behind** the clock (ended weeks never settled) or **ahead** of it (weeks settled that have not ended) makes the whole load fail, and live state is left unchanged. Nothing is clamped, so a load can neither drop owed weeks nor produce back pay.
6. **Saves without a commerce block** (legacy, or travel-only) start an empty ledger with the cursor at the restored week. There is no retroactive windfall. This is the only case where load sets the cursor from the clock, because there is no saved cursor to check.
7. Cancelled or stale travel previews and same-place travel don't advance the clock, so they can't settle anything.

## Save format

The snapshot gains an optional `commerce` block. `SaveStore.SCHEMA_VERSION` stays **1**, and older saves load unchanged.

```json
"commerce": {"version": 1, "ledgerUnitKind": "provisional-ledger-unit", "settledWeekIndex": 2967, "ledgerUnits": 300,
  "companies": {"earth.cn.shanghai": {"managerId": "zhao-ling", "managerSinceWeekIndex": 2963, "openedWeekIndex": 2963, "weeksSettled": 3, "unitsEarned": 300}}}
```

A malformed block makes the whole load fail, and state (clock, balance, cursor, companies) is left unchanged. The test covers 19 malformed cases:

- not an object;
- future version;
- wrong unit kind;
- cursor ahead of the clock;
- cursor one week behind the clock;
- cursor far behind the clock (week 0);
- fractional cursor;
- negative or text balance;
- `companies` not an object;
- company opened in the future;
- manager assigned before opening;
- fractional count;
- missing manager;
- manager in the active party;
- unrecruited manager;
- protagonist as manager;
- one companion at two companies;
- commerce cursor not at the week of a migrated pre-travel clock (travel block removed).

A commerce block on a save with no travel block is checked against the calendar start week, which is the week the travel migration restores.

**Travel week index.** When `travel.calendarWeekIndex` is present, it must equal `TravelCalendar.week_index(travel.calendarMinutes)`, or the load is rejected. A whole-number float is accepted, because JSON reads numbers back as floats. The field is optional. Saves without it load, and the week comes from the clock. Load and the commerce cursor checks always use the week derived from the clock. The test covers 7 inconsistent cases:

- index ahead of the clock;
- index behind the clock;
- index and commerce cursor both ahead of the clock (old validation accepted this);
- clock moved without its index;
- fractional index;
- text index;
- null index.

## Commands and results (repository root, 2026-10-15)

```
G=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
$G --headless --path game --import        # needed once for the new class_name
$G --headless --path game --script res://tests/<file>.gd
```

| Test | Result |
|---|---|
| `rpg-2-star-ocean-the-second_commerce-weekly-settlement_calendar-hookup-smoke_m2-v01_20261015-082014-a9d18fda.gd` (new) | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` (104 originally, 134 after the first review follow-up) |
| `…global-earth-travel_calendar-route-core-smoke_m2-v01_20261015-024215-a19d5ae7.gd` | `GLOBAL_TRAVEL_CORE_OK` |
| `m2_smoke` | `M2_SMOKE_OK` |
| `…global-earth-map_smoke_m2-v01_20261015-024300-7b4550d6.gd` | `GLOBAL_EARTH_MAP_SMOKE_OK checks=201` |
| `…global-map-travel_integration-regression_m2-v02_20261015-031232-786a054d.gd` | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=104` |
| `…global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_20261015-033441-6e5c07b5.gd` (source mode) | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| `m1_smoke`, `m2_smoke`, `m3_smoke`, `m4_smoke`, `m5_smoke`, `m6_smoke`, `m6_restart_smoke`, `m7_smoke`, `m8_city_integration_smoke`, `m8_city_navigation_smoke`, `m8_city_reentry_smoke` | all `*_OK`, exit 0 |

All rows above were rerun for Review follow-up 2 and show those results.

What the new test covers:

- **Sunday→Monday by real travel.** A trip from Shanghai to Liangzhu leaves Sunday evening and arrives Monday. The minute edges are checked: Sunday 23:58 and 23:59 settle nothing; Monday 00:00 settles.
- **Multi-week rest.** A 4-week rest is one transition: four weeks settle once each and the partial opening week pays 0.
- **Duplicate delivery.** An externally emitted `calendar_week_transition` pays nothing. Repeated and overlapping `settle_to_week` calls pay nothing.
- **Autosave on `calendar_advanced`.** On a Sunday→Monday trip, a `calendar_advanced` handler writes an autosave. The test checks four things:
  - the handler already sees the week settled (balance +100, cursor at the new week);
  - the autosave stores that balance and cursor;
  - loading the autosave later restores them, with `weeksSettled` up by exactly one;
  - the next Monday pays only the following week.

  It also checks the order `calendar_advanced` → `calendar_week_transition` → `commerce_weeks_settled`.
- **Travel week index.** The 7 inconsistent `calendarWeekIndex` cases are rejected, and state is left unchanged. Saves without the index, or with a whole-float index, still load.
- **Clock changes.** A negative advance is refused. A clock set directly never pays for skipped weeks.
- **NPC rate and full-week rule.** A mid-week recall pays 80%. A mid-week re-station is not paid at the full rate. A job change gives the NPC rate. A configurable base keeps the 80% ratio.
- **No-advance actions.** Cancelled, stale and same-place trips and entering the local scene settle nothing.
- **Save and load.** Saving and loading twice emits nothing and restores the exact balance and cursor. Replaying a crossing after loading pays once. A re-save made after settling doesn't pay again.
- **Legacy and behind-cursor saves.**
  - A travel-only save, a pre-travel save, and an empty block on a pre-travel save all load.
  - After a travel-only save migrates, later Mondays pay nothing: the company that existed before the load does not come back. A company opened afterwards is paid for its first full week, once.
  - Three behind-cursor blocks are rejected: clock ten weeks ahead with a matching index, cursor one week behind, and clock ahead with no index. Each rejected load leaves the clock, week, whole ledger and active party unchanged, and emits no signal. The live ledger then settles the next week exactly once.
- **Eligibility.**
  - Non-merchant, hero, unrecruited and unknown members are refused, as are an occupied company and a second company for the same manager.
  - Non-city, unknown and undiscovered places are refused, and so is a second company in one city.
  - Recall, NPC takeover and re-assignment work.
  - A stationed companion gets 25% battle JP.
- **Retired places and new runs.** A company in a retired city still loads and its companion can be recalled. A new run clears the ledger.

**Mutation check.** Eight deliberate one-line breaks in the ledger or AppState were each caught by the new test, with 1–13 failed checks each. The breaks were:

- remove the cursor guard;
- pay the partial opening week;
- drop the clamp on load (historical: the clamp was removed in Review follow-up 2);
- pay NPCs the full rate;
- accept a cursor ahead of the clock;
- keep commerce across a new run;
- skip the merchant check;
- pay weeks skipped by setting the clock directly.

The files were restored byte-for-byte afterwards.

Review follow-up mutations were run in a temporary copy under `AppData\Local\Temp`, which was then deleted:

- emit `calendar_advanced` before settling: 6 failed checks, all in the autosave test;
- restore the integer-only `calendarWeekIndex` check and use the saved index again: 10 failed checks.

## Known limitations

- **No in-game way to reach the merchant job.** `GrowthRules.SERIES` has no `merchant` series yet, so no companion can be stationed in normal play. The tests set `job_series = "merchant"` directly to stand in for that future job change.
- **No UI or gameplay entry point.** Nothing calls the open, assign or recall APIs yet.
- **Placeholder data.** The only `type: "city"` location is the provisional Shanghai entry, and the geography and dates are still provisional. The second-city rules are tested at ledger level and through save validation, using a test-only ID.
- **Not implemented:** robber events, the profit formula, price effects, stationed-companion skill bonuses (Zhou He and others) and any balance tuning.
- **Lost-week edge case: fixed.** See the review follow-up below.
- **`calendar_week_transition` no longer drives settlement.** Emitting it from outside `advance_calendar` settles nothing. No game code emits it; the old test that did was rewritten.
- **Docs.** Review follow-up 2 updated the stale `docs/progress.md` bullet in the M2 status entry's "still open" list. The unchecked M2 checklist item and the M2 design doc were not edited.
- **Stray `.uid` files.** `--import` created `.uid` files next to other workstreams' untracked scripts and tests. They were left local and unstaged.

## Review follow-up (2026-10-15)

**Problem 1: an autosave could drop a week.** `advance_calendar` emitted `calendar_advanced` before `calendar_week_transition`, and the ledger settled only in the second signal's handler. An autosave in a `calendar_advanced` handler stored the new clock with the cursor one week behind. On load, the clamp moved the cursor up to the clock, so one owed week was never paid.

**Fix.** `advance_calendar` now does all state changes before any signal:

1. Update the clock and week.
2. Call `commerce.settle_to_week(previous_week, new_week, …)` directly.
3. Emit `calendar_advanced`, then `calendar_week_transition`, then `commerce_weeks_settled` (only if weeks settled while a company existed).

The order of the three signals is unchanged. What changed is that the ledger is already settled when the first one fires. The `_ready` connection and `_on_calendar_week_transition` were removed, so settlement has one path.

Travel semantics are unchanged:

- arguments and values of `calendar_advanced` are the same;
- `calendar_week_transition` still fires once per advance that crosses a Monday;
- loading still emits nothing;
- negative and zero advances are unchanged.

The emitted values now come from locals, so a handler that advances the calendar again cannot change what the outer call reports. Under the old code, such a nested advance would have skipped the outer call's weeks. That case is not covered by a test.

**Problem 2: week index could disagree with the clock.** `_valid_travel_block` checked only that `calendarWeekIndex` was a whole number, while restore and the commerce cursor checks used it as given. A save could pair a clock in week W with an index and cursor of W+3. It passed validation, and the clock and week then disagreed after load.

**Fix.** A present index must equal `TravelCalendar.week_index(calendarMinutes)`. `_restore_travel_state` and `_saved_week_index` now always derive the week from the clock. Saves without the index are unaffected.

**Files changed:**

- `game/scripts/app_state.gd`;
- the commerce smoke test;
- this note.

`commerce_ledger.gd` was not changed.

**Signal-order dependencies checked.** No game script connects to `calendar_advanced`, `calendar_week_transition` or `commerce_weeks_settled`. The travel-core and map-travel integration tests record the two calendar signals in separate arrays and do not assert their relative order. Both still pass.

**Remaining limitations:**

- Handlers on `calendar_advanced` now see the ledger already settled, but `commerce_weeks_settled` still fires last. A UI that shows the new balance on `calendar_advanced` will show it before the settlement notice.
- An index-less legacy save cannot be checked for a clock/index mismatch, because it has no index. Its week is simply derived from the clock.
- The other limitations listed above still apply.

## Review follow-up 2 (2026-10-15, strict cursor)

**Problem.** `is_valid_save_block` accepted a `settledWeekIndex` behind the saved clock's week, and `load_save` moved it up with `maxi(cursor, saved_week)`. A block like that means weeks ended without being settled, and moving the cursor up dropped those weeks silently. The commerce block is new (v1), and `advance_calendar` now settles before any handler can autosave, so this version never writes a lagging cursor. A lagging cursor on disk can only be corrupt or hand-edited.

**Fix.**

- `CommerceLedger.is_valid_save_block`: the cursor must equal `saved_week_index` exactly (`!=` instead of `>`). `saved_week_index` comes from the unchanged `_saved_week_index`: `TravelCalendar.week_index(travel.calendarMinutes)`, or the calendar start week for a save with no travel block. The other checks are unchanged.
- `CommerceLedger.load_save`: the clamp and its `saved_week_index` parameter are removed, and the cursor is restored as saved. `AppState._restore_commerce_state` uses the new signature. Comments in both files now state the invariant.
- `AppState`: no behaviour change in this pass. Since the first follow-up, a present `travel.calendarWeekIndex` must equal the clock's week, and the restored week always comes from the clock.
- Saves **without** a commerce block are unchanged. They migrate to an empty ledger at the restored week (`commerce_state_migrated = true`).

**Test changes (commerce smoke).**

- The old "lagging cursor is moved up on load" check is replaced by:
  - the three rejection cases listed above under "Legacy and behind-cursor saves";
  - a positive control: the same save with a matching cursor still loads.
- The malformed list gains "cursor behind clock" and "cursor far behind clock". The pre-travel case is relabelled. The state-unchanged check now also compares the cursor.
- The migration test now also checks that a travel-only save gives no windfall or double settlement in the following weeks.

**Older M2 fixtures.** Two tests built a "pre-travel legacy" save by removing only `travel` from a new-format snapshot:

- `…global-earth-travel_calendar-route-core-smoke_m2-v01_20261015-024215-a19d5ae7.gd` (`_test_legacy_and_unknown_id_migration`);
- `…global-map-travel_integration-regression_m2-v02_20261015-031232-786a054d.gd` (`_legacy_save_on_map`).

A real pre-travel save has no commerce block either. Both fixtures now also remove `commerce` (one line plus a comment each). Their travel migration assertions are unchanged. **Neither failed without this edit**: both snapshots are taken right after `begin_new_run`, so the cursor already equals the start week. The edit makes the fixtures realistic; it does not fix a failure.

**Results (repository root, 2026-10-15, Godot 4.7.2 headless; all exit 0).**

| Test | Result |
|---|---|
| commerce smoke | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` |
| travel calendar/route core | `GLOBAL_TRAVEL_CORE_OK` |
| map ↔ travel integration | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=104` |
| `m2_smoke` | `M2_SMOKE_OK` |
| global Earth map smoke | `GLOBAL_EARTH_MAP_SMOKE_OK checks=201` |
| export data inclusion (source mode) | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| `m1_smoke`, `m3_smoke` … `m7_smoke`, `m6_restart_smoke`, the three `m8_city_*` smokes | all `*_OK` |
| Game Bible M2 global-travel gates check (Node) | RESULT PASS (5 checks); reads the M2 gate state, which this pass did not change |

**Mutation check.** `commerce_ledger.gd` was backed up under `AppData\Local\Temp`, edited in place, and then restored. Its SHA-256 matched the original after the restore.

- Putting back `>` (accepting a behind cursor) caused 24 failed checks.
- Shifting the cursor by +1 in `load_save` caused 8 failed checks.

**Limitations.**

- A save from an earlier local build of this unreleased work that has a lagging cursor now fails to load instead of being repaired. The current code cannot write such a save, and the block has never shipped.
- A bad commerce block fails the whole load, not just the block. There is no partial recovery and no player-facing message beyond the existing load failure.
- Code that sets `calendar_minutes` directly, without `advance_calendar`, leaves the cursor behind the clock, and a save made in that state would be rejected. No game code does this; only test helpers set the clock directly. The travel core smoke's `_test_save_load_without_recharge` calls `_set_clock` (which does not touch the cursor) and then saves. It passes because its Sunday 23:00 trip crosses a Monday, and `settle_to_week` then sets the cursor to the new week. If that trip were changed so it no longer crosses a Monday, its save would be rejected. The commerce smoke's `_fresh_run_at` resets the cursor and so has no such dependency.
- The earlier limitations still apply: no merchant job in play, no UI, no profit formula or balance, and the ledger units are not currency.
