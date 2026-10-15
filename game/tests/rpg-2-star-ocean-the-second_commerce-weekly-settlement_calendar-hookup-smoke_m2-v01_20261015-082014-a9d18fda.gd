extends SceneTree

# Weekly commerce settlement run by AppState.advance_calendar at each Monday 00:00 crossing, before
# calendar_advanced / calendar_week_transition are emitted.
# Amounts are the provisional base (100 per full week, NPC 80%); they are checked as rule outcomes,
# not as economic balance. No game path puts a companion in the merchant job yet, so tests set
# job_series = "merchant" directly to stand in for that future job change.
# Run: Godot --headless --path game --script res://tests/<this file>
const SHANGHAI := "earth.cn.shanghai"
const SONGJIANG := "earth.cn.shanghai.songjiang-outskirts"
const LIANGZHU := "earth.cn.liangzhu-ruins"
const OTHER_CITY := "earth.test.second-city"
const SAVE_ROOT := "user://test-saves/m2-commerce-weekly-settlement"

var app: Node
var failures := 0
var checks := 0
var week_events: Array = []
var settled_events: Array = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	SaveStore.root_path = SAVE_ROOT
	_clear_saves()
	app.calendar_week_transition.connect(func(previous: int, current: int) -> void: week_events.append([previous, current]))
	app.commerce_weeks_settled.connect(func(result: Dictionary) -> void: settled_events.append(result.duplicate(true)))
	_test_manager_and_city_eligibility()
	_test_sunday_to_monday_by_travel()
	_test_multiweek_and_duplicate_delivery()
	_test_npc_efficiency_and_full_week_rule()
	_test_cancel_and_free_actions_settle_nothing()
	_test_save_load_never_double_settles()
	_test_autosave_on_calendar_advanced_sees_settled_week()
	_test_legacy_migration_and_behind_cursor_rejected()
	_test_malformed_commerce_blocks_rejected()
	_test_travel_week_index_must_match_clock()
	_test_retired_city_keeps_companion_recallable()
	_test_new_run_clears_commerce()
	_clear_saves()
	if failures > 0:
		push_error("COMMERCE_WEEKLY_SETTLEMENT failed checks: %d of %d" % [failures, checks])
		quit(1)
		return
	print("COMMERCE_WEEKLY_SETTLEMENT_OK checks=%d" % checks)
	quit(0)


# Test setup: a fresh run whose clock starts at the given date (as if the run began there).
func _fresh_run_at(year: int, month: int, day: int, hour: int, minute: int) -> void:
	app.begin_new_run()
	app.calendar_minutes = TravelCalendar.to_minutes(year, month, day, hour, minute)
	app.calendar_week_index = TravelCalendar.week_index(app.calendar_minutes)
	app._reset_commerce_state()
	app.commerce.base_weekly_income = CommerceLedger.PROVISIONAL_BASE_WEEKLY_INCOME
	week_events.clear()
	settled_events.clear()


func _recruit_merchant(member_id: String) -> void:
	if member_id == "ji-cheng":
		app.ji_records_checked = true
	app.recruit_member(member_id)
	app.member_states[member_id]["job_series"] = "merchant"


func _advance_to(target_minutes: int) -> void:
	app.advance_calendar(target_minutes - app.calendar_minutes, "rest")


func _travel(destination: String) -> Dictionary:
	var preview: Dictionary = app.preview_travel(destination)
	if not preview.get("ok", false):
		return preview
	return app.settle_travel()


func _leg_minutes(from_id: String, to_id: String) -> int:
	return int(app.travel_registry().routes_between(from_id, to_id)[0]["total_minutes"])


func _units() -> int:
	return int(app.commerce_ledger_state()["ledgerUnits"])


func _test_manager_and_city_eligibility() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	_check(app.open_commerce_company(SHANGHAI, "liang-xu")["reason"] == "not-merchant" and app.commerce_ledger_state()["companies"].is_empty() and app.active_party_ids.has("liang-xu"), "a recruited non-merchant cannot open or run a company and stays in the party")
	_check(app.open_commerce_company(SHANGHAI, "hero")["reason"] == "hero-cannot-station", "the protagonist cannot be stationed")
	_check(app.open_commerce_company(SHANGHAI, "ji-cheng")["reason"] == "not-recruited", "an unrecruited companion cannot be stationed")
	_check(app.open_commerce_company(SHANGHAI, "nobody")["reason"] == "unknown-member", "an unknown member id is refused")
	app.member_states["zhao-ling"]["job_series"] = "merchant"
	_check(app.open_commerce_company(LIANGZHU, "zhao-ling")["reason"] == "not-a-city" and app.open_commerce_company(SONGJIANG, "zhao-ling")["reason"] == "not-a-city", "ruins and outskirts cannot host a company")
	_check(app.open_commerce_company("earth.xx.nowhere", "zhao-ling")["reason"] == "unknown-city", "an unknown place cannot host a company")
	app.discovered_locations.erase(SHANGHAI)
	_check(app.open_commerce_company(SHANGHAI, "zhao-ling")["reason"] == "city-not-discovered", "an undiscovered city cannot host a company")
	app.discovered_locations[SHANGHAI] = true
	_check(app.active_party_ids.has("zhao-ling") and app.commerce_ledger_state()["companies"].is_empty(), "refused attempts change nothing")
	var opened: Dictionary = app.open_commerce_company(SHANGHAI, "zhao-ling")
	_check(opened["ok"] and opened["city_id"] == SHANGHAI, "a recruited merchant companion opens a company in a discovered city")
	_check(not app.active_party_ids.has("zhao-ling") and app.recruited_members.has("zhao-ling") and app.member_states.has("zhao-ling"), "the stationed companion leaves the active party but stays recruited")
	app.member_states["liang-xu"]["job_series"] = "merchant"
	_check(app.open_commerce_company(SHANGHAI, "liang-xu")["reason"] == "company-exists" and app.active_party_ids.has("liang-xu"), "one company per city")
	_check(app.assign_commerce_manager(SHANGHAI, "liang-xu")["reason"] == "manager-present", "a company with a stationed companion takes no second one")
	_check(app.commerce_manager_block_reason("zhao-ling") == "already-stationed" and not app.commerce.open_company(OTHER_CITY, "zhao-ling", app.calendar_week_index) and not app.commerce.has_company(OTHER_CITY), "the same companion cannot run a second company")
	_check(app.recall_commerce_manager(SONGJIANG)["reason"] == "no-company" and app.assign_commerce_manager(LIANGZHU, "liang-xu")["reason"] == "no-company", "recall/assign need an existing company")
	var liang_jp := int(app.member_states["liang-xu"]["jp"])
	var zhao_jp := int(app.member_states["zhao-ling"]["jp"])
	var reward: Dictionary = app.award_battle_rewards("patrol")
	_check(int(app.member_states["liang-xu"]["jp"]) - liang_jp == int(reward["jp"]) and int(app.member_states["zhao-ling"]["jp"]) - zhao_jp == ceili(float(reward["jp"]) * 0.25), "a stationed companion receives the 25% reserve share of battle JP")
	var recall: Dictionary = app.recall_commerce_manager(SHANGHAI)
	_check(recall["ok"] and recall["member_id"] == "zhao-ling" and recall["rejoined_active_party"] and app.active_party_ids.has("zhao-ling"), "recall returns the companion to the party")
	_check(app.commerce.has_company(SHANGHAI) and app.commerce_ledger_state()["companies"][SHANGHAI]["managerId"] == "", "after recall an ordinary NPC keeps the company")
	_check(app.recall_commerce_manager(SHANGHAI)["reason"] == "no-companion-manager", "an NPC-run company has nobody to recall")
	app.member_states["liang-xu"]["job_series"] = "tactics"
	_check(app.assign_commerce_manager(SHANGHAI, "liang-xu")["reason"] == "not-merchant", "assigning also requires the merchant job")
	_check(app.assign_commerce_manager(SHANGHAI, "zhao-ling")["ok"] and not app.active_party_ids.has("zhao-ling"), "a merchant can be stationed again at an NPC-run company")


func _test_sunday_to_monday_by_travel() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	var opened_week: int = app.calendar_week_index
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	var monday := TravelCalendar.to_minutes(2026, 10, 19)
	var leg := _leg_minutes(SHANGHAI, LIANGZHU)
	_advance_to(monday - leg + 30)
	_check(TravelCalendar.from_minutes(app.calendar_minutes)["weekday"] == 7 and settled_events.is_empty() and _units() == 0, "resting to Sunday evening settles nothing")
	var trip := _travel(LIANGZHU)
	_check(trip.get("departed", false) and app.calendar_week_index == opened_week + 1, "Sunday-evening trip arrives in the next week")
	_check(settled_events.size() == 1 and settled_events[0]["settled_week_indices"] == [opened_week] and int(settled_events[0]["units"]) == 0, "the opening week settles once and pays nothing for a partial week")
	var second_monday := monday + TravelCalendar.MINUTES_PER_WEEK
	_advance_to(second_monday - 2)
	_check(settled_events.size() == 1, "Sunday 23:58 is still the same week")
	app.advance_calendar(1, "rest")
	_check(settled_events.size() == 1 and TravelCalendar.from_minutes(app.calendar_minutes)["hour"] == 23, "Sunday 23:59 is still the same week")
	app.advance_calendar(1, "rest")
	_check(settled_events.size() == 2 and settled_events[1]["settled_week_indices"] == [opened_week + 1] and int(settled_events[1]["units"]) == 100 and _units() == 100, "the first full week pays the companion rate at Monday 00:00")
	_check(int(app.commerce_ledger_state()["settledWeekIndex"]) == app.calendar_week_index, "cursor equals the current week after settling")
	_travel(SHANGHAI)
	_check(settled_events.size() == 2 and _units() == 100, "a trip inside the week settles nothing more")


func _test_multiweek_and_duplicate_delivery() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	var week: int = app.calendar_week_index
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 4, "rest")
	_check(week_events == [[week, week + 4]] and settled_events.size() == 1, "a four-week rest is one transition and one settlement")
	_check(settled_events[0]["settled_week_indices"] == [week, week + 1, week + 2, week + 3] and _units() == 300, "each crossed week settles once: partial opening week 0 + three full weeks")
	_check(int(app.commerce_ledger_state()["companies"][SHANGHAI]["weeksSettled"]) == 3, "the company counts three settled weeks")
	app.calendar_week_transition.emit(week, week + 4)
	_check(_units() == 300 and settled_events.size() == 1, "an externally emitted transition signal is a notification only and pays nothing")
	var companions: Dictionary = app._commerce_companion_ids()
	var repeat: Dictionary = app.commerce.settle_to_week(week, week + 4, companions)
	var overlap: Dictionary = app.commerce.settle_to_week(week + 2, week + 4, companions)
	_check(_units() == 300 and repeat["settled_week_indices"].is_empty() and overlap["settled_week_indices"].is_empty(), "repeated or overlapping settlement of the same weeks pays nothing again")
	_check(not app.advance_calendar(-TravelCalendar.MINUTES_PER_WEEK, "rest") and _units() == 300 and app.calendar_week_index == week + 4, "a negative advance is refused and settles nothing")
	app.calendar_minutes += TravelCalendar.MINUTES_PER_WEEK * 10
	app.calendar_week_index = TravelCalendar.week_index(app.calendar_minutes)
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() == 400 and settled_events[-1]["settled_week_indices"] == [week + 14], "weeks skipped by setting the clock directly are never paid; only the crossed week is")


func _test_npc_efficiency_and_full_week_rule() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	var week: int = app.calendar_week_index
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	var before := _units()
	app.recall_commerce_manager(SHANGHAI)
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() - before == 80, "the week of a mid-week recall pays the NPC 80% rate")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() - before == 160, "a full NPC week pays 80%")
	app.assign_commerce_manager(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() - before == 240, "a companion stationed mid-week does not earn the full rate for that week")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() - before == 340, "the next full stationed week pays the full rate again")
	app.member_states["zhao-ling"]["job_series"] = "firearms"
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() - before == 420, "a stationed companion who left the merchant job earns only the NPC rate")
	app.member_states["zhao-ling"]["job_series"] = "merchant"
	app.commerce.base_weekly_income = 250
	app.recall_commerce_manager(SHANGHAI)
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	_check(_units() - before == 420 + 200 + 200, "the provisional base is configurable and NPC weeks stay at 80% of it")
	_check(app.calendar_week_index == week + 9 and int(app.commerce_ledger_state()["companies"][SHANGHAI]["weeksSettled"]) == 8, "eight full weeks settled after the opening week")


func _test_cancel_and_free_actions_settle_nothing() -> void:
	_fresh_run_at(2026, 10, 18, 22, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	settled_events.clear()
	var units := _units()
	var minutes: int = app.calendar_minutes
	var preview: Dictionary = app.preview_travel(LIANGZHU)
	_check(int(preview["weeks_crossed"]) == 1 and settled_events.is_empty(), "previewing a Monday-crossing trip settles nothing")
	app.cancel_travel_preview()
	_check(not app.confirm_travel() and app.calendar_minutes == minutes and settled_events.is_empty() and _units() == units, "cancelled trip charges no time and settles nothing")
	app.preview_travel(LIANGZHU)
	app.advance_calendar(5, "rest")
	settled_events.clear()
	_check(not app.confirm_travel() and settled_events.is_empty(), "a stale preview cannot settle a week")
	var same: Dictionary = app.settle_travel(SHANGHAI)
	_check(not same["departed"] and settled_events.is_empty() and _units() == units, "travelling to the current place settles nothing")
	app.enter_current_location_scene()
	_check(settled_events.is_empty() and _units() == units, "entering the local scene settles nothing")


func _test_save_load_never_double_settles() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	var monday := TravelCalendar.to_minutes(2026, 11, 2)
	_advance_to(monday - _leg_minutes(SHANGHAI, LIANGZHU) + 30)
	var saved_units := _units()
	var saved_week: int = app.calendar_week_index
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	var id: String = app.write_manual_save(1)
	var entry := SaveStore.read_entry(id)
	var block: Dictionary = entry["snapshot"].get("commerce", {})
	_check(id != "" and int(entry["schemaVersion"]) == 1 and SaveStore.SCHEMA_VERSION == 1, "save keeps SaveStore schema version 1")
	_check(block.get("ledgerUnitKind") == "provisional-ledger-unit" and int(block["ledgerUnits"]) == saved_units and int(block["settledWeekIndex"]) == saved_week and block["companies"][SHANGHAI]["managerId"] == "zhao-ling", "save carries the provisional ledger, cursor and company")
	_travel(LIANGZHU)
	_check(_units() == saved_units + 100, "crossing Monday after saving pays one week")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	week_events.clear()
	settled_events.clear()
	_check(app.load_save(id), "save loads")
	_check(week_events.is_empty() and settled_events.is_empty(), "loading emits no week transition and no settlement")
	_check(_units() == saved_units and int(app.commerce_ledger_state()["settledWeekIndex"]) == saved_week and app.calendar_week_index == saved_week, "loading restores the saved balance and cursor exactly")
	_check(not app.active_party_ids.has("zhao-ling") and app.commerce.company_for_manager("zhao-ling") == SHANGHAI, "the stationed companion stays stationed and out of the party")
	app.load_save(id)
	_check(_units() == saved_units and settled_events.is_empty(), "loading twice changes nothing")
	_travel(LIANGZHU)
	_check(_units() == saved_units + 100 and settled_events.size() == 1, "replaying the same crossing after load pays that week once, not twice")
	var resaved: String = app.write_manual_save(2)
	settled_events.clear()
	app.load_save(resaved)
	_travel(SHANGHAI)
	_check(_units() == saved_units + 100 and settled_events.is_empty(), "a save made after settlement does not settle that week again")


# Review regression: calendar_advanced used to fire before settlement, so an autosave there captured the
# new clock with the crossed week unsettled; loading moved the cursor up to the clock and the week was lost.
func _test_autosave_on_calendar_advanced_sees_settled_week() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	var monday := TravelCalendar.to_minutes(2026, 10, 26)
	_advance_to(monday - _leg_minutes(SHANGHAI, LIANGZHU) + 30)
	var sunday_week: int = app.calendar_week_index
	var units_before := _units()
	var weeks_before := int(app.commerce_ledger_state()["companies"][SHANGHAI]["weeksSettled"])
	_check(TravelCalendar.from_minutes(app.calendar_minutes)["weekday"] == 7 and int(app.commerce_ledger_state()["settledWeekIndex"]) == sunday_week, "setup: Sunday evening, cursor at the current week")
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	var order: Array = []
	var seen := {}
	var autosave := func(_previous: int, _current: int, _reason: String) -> void:
		order.append("calendar_advanced")
		seen["units"] = _units()
		seen["cursor"] = int(app.commerce_ledger_state()["settledWeekIndex"])
		seen["id"] = app.write_auto_save("map", Vector2.ZERO, "calendar_autosave")
	var log_week := func(_previous: int, _current: int) -> void: order.append("calendar_week_transition")
	var log_settled := func(_result: Dictionary) -> void: order.append("commerce_weeks_settled")
	app.calendar_advanced.connect(autosave)
	app.calendar_week_transition.connect(log_week)
	app.commerce_weeks_settled.connect(log_settled)
	var trip := _travel(LIANGZHU)
	app.calendar_advanced.disconnect(autosave)
	app.calendar_week_transition.disconnect(log_week)
	app.commerce_weeks_settled.disconnect(log_settled)
	var new_week := sunday_week + 1
	_check(trip.get("departed", false) and app.calendar_week_index == new_week and TravelCalendar.from_minutes(app.calendar_minutes)["weekday"] == 1, "Sunday-evening trip arrives on Monday")
	_check(order == ["calendar_advanced", "calendar_week_transition", "commerce_weeks_settled"], "signal order is calendar_advanced, calendar_week_transition, commerce_weeks_settled (got %s)" % [order])
	_check(int(seen.get("units", -1)) == units_before + 100 and int(seen.get("cursor", -1)) == new_week, "the calendar_advanced handler already sees the crossed week settled")
	var entry := SaveStore.read_entry(String(seen.get("id", "")))
	_check(not entry.is_empty() and entry["kind"] == "auto", "the handler wrote an autosave")
	if entry.is_empty():
		return
	var saved: Dictionary = entry["snapshot"]
	_check(int(saved["commerce"]["ledgerUnits"]) == units_before + 100 and int(saved["commerce"]["settledWeekIndex"]) == new_week and int(saved["travel"]["calendarWeekIndex"]) == new_week, "the autosave holds the new clock with that week already settled")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	week_events.clear()
	settled_events.clear()
	_check(app.load_save(String(seen["id"])) and week_events.is_empty() and settled_events.is_empty(), "the autosave loads and settles nothing on load")
	_check(app.calendar_week_index == new_week and _units() == units_before + 100 and int(app.commerce_ledger_state()["settledWeekIndex"]) == new_week, "after load the ledger balance and cursor include the crossed week")
	_check(int(app.commerce_ledger_state()["companies"][SHANGHAI]["weeksSettled"]) == weeks_before + 1, "the crossed week was settled exactly once")
	_advance_to(monday + TravelCalendar.MINUTES_PER_WEEK - 1)
	_check(_units() == units_before + 100 and settled_events.is_empty(), "the rest of the loaded week pays nothing more")
	app.advance_calendar(1, "rest")
	_check(_units() == units_before + 200 and settled_events.size() == 1 and settled_events[0]["settled_week_indices"] == [new_week], "the next Monday pays only the following week: the autosaved week is neither lost nor paid twice")


func _test_legacy_migration_and_behind_cursor_rejected() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	var no_commerce: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	no_commerce.erase("commerce")
	var no_commerce_id := SaveStore.write_entry("manual", 2, no_commerce)
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 3, "rest")
	settled_events.clear()
	_check(app.load_save(no_commerce_id), "save with travel but no commerce block loads")
	_check(app.commerce_state_migrated and app.commerce_ledger_state()["companies"].is_empty() and _units() == 0 and int(app.commerce_ledger_state()["settledWeekIndex"]) == app.calendar_week_index, "missing commerce starts an empty ledger at the saved week")
	_check(app.active_party_ids.has("zhao-ling") and settled_events.is_empty(), "migration leaves the companion in the party and settles nothing")
	var migrated_week: int = app.calendar_week_index
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	_check(settled_events.is_empty() and _units() == 0 and int(app.commerce_ledger_state()["settledWeekIndex"]) == migrated_week + 2, "after migration, later Mondays pay nothing: the live company from before the load does not come back")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() == 100 and int(app.commerce_ledger_state()["companies"][SHANGHAI]["weeksSettled"]) == 1, "a company opened after migration earns from its first full week only, once")
	var legacy: Dictionary = no_commerce.duplicate(true)
	legacy.erase("travel")
	var legacy_id := SaveStore.write_entry("manual", 3, legacy)
	_check(app.load_save(legacy_id) and app.commerce_state_migrated and int(app.commerce_ledger_state()["settledWeekIndex"]) == app.calendar_week_index and app.calendar_minutes == app.travel_registry().calendar_start_minutes, "pre-travel legacy save gets a cursor at the migrated calendar week")
	var empty_without_travel: Dictionary = legacy.duplicate(true)
	empty_without_travel["commerce"] = {"version": 1, "settledWeekIndex": TravelCalendar.week_index(app.travel_registry().calendar_start_minutes), "ledgerUnits": 0, "companies": {}}
	_check(app.load_save(SaveStore.write_entry("manual", 3, empty_without_travel)) and not app.commerce_state_migrated and _units() == 0, "an empty commerce block on a pre-travel save is checked against the migrated week and loads")
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	app.load_save(app.write_manual_save(3))
	_check(not app.commerce_state_migrated and app.commerce_ledger_state()["companies"].is_empty(), "migrated save re-saves with a commerce block")
	# Review regression: a commerce cursor behind its saved clock used to load and be moved up to the
	# clock, silently dropping the ended-but-unsettled weeks. advance_calendar settles before any handler
	# can save, so this version never writes such a block: it is corrupt and the whole load is refused.
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	var base: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	var lagging_ten: Dictionary = base.duplicate(true)
	lagging_ten["travel"]["calendarMinutes"] = app.calendar_minutes + TravelCalendar.MINUTES_PER_WEEK * 10
	lagging_ten["travel"]["calendarWeekIndex"] = app.calendar_week_index + 10
	var lagging_one: Dictionary = base.duplicate(true)
	lagging_one["commerce"]["settledWeekIndex"] = int(base["commerce"]["settledWeekIndex"]) - 1
	var lagging_no_index: Dictionary = lagging_ten.duplicate(true)
	lagging_no_index["travel"].erase("calendarWeekIndex")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	var live_minutes: int = app.calendar_minutes
	var live_week: int = app.calendar_week_index
	var live_ledger: Dictionary = app.commerce_ledger_state()
	var live_party: Array = app.active_party_ids.duplicate()
	var behind_cases := {"clock ten weeks ahead of the cursor": lagging_ten, "cursor one week behind its clock": lagging_one, "clock ahead of the cursor, no week index": lagging_no_index}
	for label in behind_cases:
		var behind_id := SaveStore.write_entry("manual", 3, behind_cases[label])
		settled_events.clear()
		week_events.clear()
		_check(behind_id != "" and not app.load_save(behind_id), "behind-cursor commerce block rejected: " + label)
		_check(app.calendar_minutes == live_minutes and app.calendar_week_index == live_week and app.commerce_ledger_state() == live_ledger and app.active_party_ids == live_party and not app.commerce_state_migrated, "rejected behind-cursor load leaves clock, ledger and party unchanged: " + label)
		_check(settled_events.is_empty() and week_events.is_empty(), "rejected behind-cursor load emits nothing: " + label)
	var live_units := _units()
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() == live_units + 100 and settled_events.size() == 1 and settled_events[0]["settled_week_indices"] == [live_week], "after the refused loads the live ledger settles the next week exactly once")
	_check(app.load_save(SaveStore.write_entry("manual", 3, base)) and int(app.commerce_ledger_state()["settledWeekIndex"]) == app.calendar_week_index, "the same save with a cursor equal to its clock week still loads")


func _test_malformed_commerce_blocks_rejected() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.recruit_member("liang-xu")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	var good: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	var week := int(good["travel"]["calendarWeekIndex"])
	var cases := {
		"not a dictionary": func(s: Dictionary) -> void: s["commerce"] = "rich",
		"future version": func(s: Dictionary) -> void: s["commerce"]["version"] = 99,
		"currency kind": func(s: Dictionary) -> void: s["commerce"]["ledgerUnitKind"] = "coins",
		"cursor ahead of clock": func(s: Dictionary) -> void: s["commerce"]["settledWeekIndex"] = week + 1,
		"cursor behind clock": func(s: Dictionary) -> void: s["commerce"]["settledWeekIndex"] = week - 1,
		"cursor far behind clock": func(s: Dictionary) -> void: s["commerce"]["settledWeekIndex"] = 0,
		"fractional cursor": func(s: Dictionary) -> void: s["commerce"]["settledWeekIndex"] = week - 0.5,
		"negative balance": func(s: Dictionary) -> void: s["commerce"]["ledgerUnits"] = -5,
		"text balance": func(s: Dictionary) -> void: s["commerce"]["ledgerUnits"] = "lots",
		"companies not a dictionary": func(s: Dictionary) -> void: s["commerce"]["companies"] = [],
		"company opened in the future": func(s: Dictionary) -> void: s["commerce"]["companies"][SHANGHAI]["openedWeekIndex"] = week + 3,
		"manager since before opening": func(s: Dictionary) -> void: s["commerce"]["companies"][SHANGHAI]["managerSinceWeekIndex"] = week - 30,
		"fractional weeks settled": func(s: Dictionary) -> void: s["commerce"]["companies"][SHANGHAI]["weeksSettled"] = 1.5,
		"missing manager": func(s: Dictionary) -> void: s["commerce"]["companies"][SHANGHAI].erase("managerId"),
		"manager in active party": func(s: Dictionary) -> void: s["activeParty"].append("zhao-ling"),
		"manager not recruited": func(s: Dictionary) -> void: s["commerce"]["companies"][SHANGHAI]["managerId"] = "ji-cheng",
		"protagonist as manager": func(s: Dictionary) -> void: s["commerce"]["companies"][SHANGHAI]["managerId"] = "hero",
		"one companion at two companies": func(s: Dictionary) -> void: s["commerce"]["companies"][OTHER_CITY] = s["commerce"]["companies"][SHANGHAI].duplicate(),
		"commerce cursor not at a migrated pre-travel clock's week": func(s: Dictionary) -> void: s.erase("travel"),
	}
	var units_before := _units()
	var minutes_before: int = app.calendar_minutes
	var cursor_before := int(app.commerce_ledger_state()["settledWeekIndex"])
	for label in cases:
		var broken: Dictionary = good.duplicate(true)
		cases[label].call(broken)
		var broken_id := SaveStore.write_entry("manual", 3, broken)
		settled_events.clear()
		_check(broken_id != "" and not app.load_save(broken_id), "malformed commerce rejected: " + label)
		_check(_units() == units_before and app.calendar_minutes == minutes_before and int(app.commerce_ledger_state()["settledWeekIndex"]) == cursor_before and app.commerce.company_for_manager("zhao-ling") == SHANGHAI and settled_events.is_empty(), "rejected load leaves state unchanged: " + label)
	var good_id := SaveStore.write_entry("manual", 3, good)
	_check(app.load_save(good_id), "the unmodified block still loads")


# travel.calendarWeekIndex is derived data. When present it must be the week of travel.calendarMinutes;
# otherwise the commerce cursor checks would compare against a week the clock does not match.
func _test_travel_week_index_must_match_clock() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	var good: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	var week := int(good["travel"]["calendarWeekIndex"])
	var minutes := int(good["travel"]["calendarMinutes"])
	_check(week == TravelCalendar.week_index(minutes), "setup: a fresh save's week index matches its clock")
	# Old validation accepted this: the cursor check ran against the saved index, not the clock's week.
	var index_and_cursor_ahead := func(s: Dictionary) -> void:
		s["travel"]["calendarWeekIndex"] = week + 3
		s["commerce"]["settledWeekIndex"] = week + 3
	var cases := {
		"week index ahead of the clock": func(s: Dictionary) -> void: s["travel"]["calendarWeekIndex"] = week + 1,
		"week index behind the clock": func(s: Dictionary) -> void: s["travel"]["calendarWeekIndex"] = week - 1,
		"week index and commerce cursor both ahead of the clock": index_and_cursor_ahead,
		"clock moved without its week index": func(s: Dictionary) -> void: s["travel"]["calendarMinutes"] = minutes + TravelCalendar.MINUTES_PER_WEEK * 3,
		"fractional week index": func(s: Dictionary) -> void: s["travel"]["calendarWeekIndex"] = week + 0.5,
		"text week index": func(s: Dictionary) -> void: s["travel"]["calendarWeekIndex"] = str(week),
		"null week index": func(s: Dictionary) -> void: s["travel"]["calendarWeekIndex"] = null,
	}
	var units_before := _units()
	for label in cases:
		var broken: Dictionary = good.duplicate(true)
		cases[label].call(broken)
		var broken_id := SaveStore.write_entry("manual", 3, broken)
		settled_events.clear()
		_check(broken_id != "" and not app.load_save(broken_id), "inconsistent travel week rejected: " + label)
		_check(app.calendar_minutes == minutes and app.calendar_week_index == week and _units() == units_before and int(app.commerce_ledger_state()["settledWeekIndex"]) == week and settled_events.is_empty(), "rejected load leaves clock and ledger unchanged: " + label)
	var legacy: Dictionary = good.duplicate(true)
	legacy["travel"].erase("calendarWeekIndex")
	_check(app.load_save(SaveStore.write_entry("manual", 3, legacy)) and app.calendar_minutes == minutes and app.calendar_week_index == week and int(app.commerce_ledger_state()["settledWeekIndex"]) == week and _units() == units_before, "a save without the optional week index still loads, with the week derived from its clock")
	var float_index: Dictionary = good.duplicate(true)
	float_index["travel"]["calendarWeekIndex"] = float(week)
	_check(app.load_save(SaveStore.write_entry("manual", 3, float_index)) and app.calendar_week_index == week, "a matching week index stored as a whole float loads")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK, "rest")
	_check(_units() == units_before + 100, "after loading a consistent save the next crossing pays exactly one week")


func _test_retired_city_keeps_companion_recallable() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	var snapshot: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	snapshot["commerce"]["companies"]["earth.xx.retired-city"] = snapshot["commerce"]["companies"][SHANGHAI]
	snapshot["commerce"]["companies"].erase(SHANGHAI)
	var id := SaveStore.write_entry("manual", 3, snapshot)
	_check(app.load_save(id) and app.commerce.company_for_manager("zhao-ling") == "earth.xx.retired-city", "a company in a place later removed from data still loads")
	var recall: Dictionary = app.recall_commerce_manager("earth.xx.retired-city")
	_check(recall["ok"] and app.active_party_ids.has("zhao-ling"), "its companion can still be recalled, so nobody is lost")


func _test_new_run_clears_commerce() -> void:
	_fresh_run_at(2026, 10, 14, 10, 0)
	_recruit_merchant("zhao-ling")
	app.open_commerce_company(SHANGHAI, "zhao-ling")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 3, "rest")
	_check(_units() > 0, "setup earned some units")
	app.begin_new_run()
	var state: Dictionary = app.commerce_ledger_state()
	_check(state["companies"].is_empty() and int(state["ledgerUnits"]) == 0 and int(state["settledWeekIndex"]) == app.calendar_week_index and not app.commerce_state_migrated, "begin_new_run clears companies, balance and cursor")
	settled_events.clear()
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 2, "rest")
	_check(settled_events.is_empty() and _units() == 0, "a new run earns nothing from the previous run's company")


func _clear_saves() -> void:
	var directory := DirAccess.open(SAVE_ROOT)
	if directory == null:
		return
	for name in directory.get_files():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_ROOT.path_join(name)))


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if condition:
		return true
	failures += 1
	push_error("Commerce weekly settlement check failed: " + label)
	return false
