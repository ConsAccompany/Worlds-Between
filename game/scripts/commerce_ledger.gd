extends RefCounted
class_name CommerceLedger

# Weekly commerce-company settlement. Pure state and rules: AppState decides who is eligible and feeds
# calendar week transitions in. Amounts are a PROVISIONAL separate ledger, not usable currency: the
# game has no coin/account system and the user has not fixed a profit formula, so nothing here is a
# final economic balance. Robber events and price effects are not implemented.
#
# Week w runs from its Monday 00:00 to the next Monday 00:00 (TravelCalendar.week_index). Crossing
# into week N settles every ended week from the cursor up to N - 1, once each, then moves the cursor
# to N. A company earns nothing for the partial week in which it opened; a week pays the companion
# rate only if the same merchant companion was stationed for the whole week, otherwise the NPC rate.
#
# Fair Quote (公平报价, the stage-2 Merchant passive) adds FAIR_QUOTE_PERCENT_PER_RANK of the base per
# rank, only to weeks paid at the companion rate: ranks 1/2/3 pay 105/110/115 % with the provisional
# base of 100. NPC-rate weeks (after a recall, or the partial week after stationing) get no bonus. The
# rank is read when the week is settled; it is never stored here, and settled weeks are never re-priced.

const SAVE_VERSION := 1
const LEDGER_UNIT_KIND := "provisional-ledger-unit"
const PROVISIONAL_BASE_WEEKLY_INCOME := 100
const NPC_EFFICIENCY_PERCENT := 80
const FAIR_QUOTE_PERCENT_PER_RANK := 5
const FAIR_QUOTE_MAX_RANK := 3
const MERCHANT_SERIES_ID := "merchant"

# Tests and later tuning may change this; it is not saved, so saves follow the current rule.
var base_weekly_income := PROVISIONAL_BASE_WEEKLY_INCOME
# Calendar week index the ledger has caught up to. Weeks below it are settled or were never owed.
var settled_week_index := 0
var ledger_units := 0
# city location id -> {"managerId": member id or "" for an ordinary NPC, "managerSinceWeekIndex",
# "openedWeekIndex", "weeksSettled", "unitsEarned"}
var companies: Dictionary = {}


func reset(week_index: int) -> void:
	settled_week_index = week_index
	ledger_units = 0
	companies.clear()


func has_company(city_id: String) -> bool:
	return companies.has(city_id)


func company_for_manager(member_id: String) -> String:
	if member_id == "":
		return ""
	for city_id in companies:
		if companies[city_id]["managerId"] == member_id:
			return String(city_id)
	return ""


func stationed_member_ids() -> Array[String]:
	var result: Array[String] = []
	for city_id in companies:
		if companies[city_id]["managerId"] != "":
			result.append(String(companies[city_id]["managerId"]))
	return result


# Callers check eligibility (recruited merchant, real city) first; these enforce the structural rules.
func open_company(city_id: String, manager_id: String, week_index: int) -> bool:
	if city_id == "" or manager_id == "" or companies.has(city_id) or company_for_manager(manager_id) != "":
		return false
	companies[city_id] = {"managerId": manager_id, "managerSinceWeekIndex": week_index, "openedWeekIndex": week_index, "weeksSettled": 0, "unitsEarned": 0}
	return true


func assign_manager(city_id: String, manager_id: String, week_index: int) -> bool:
	if manager_id == "" or not companies.has(city_id) or companies[city_id]["managerId"] != "" or company_for_manager(manager_id) != "":
		return false
	companies[city_id]["managerId"] = manager_id
	companies[city_id]["managerSinceWeekIndex"] = week_index
	return true


# Returns the recalled member id; an ordinary NPC runs the company from this week on.
func recall_manager(city_id: String, week_index: int) -> String:
	if not companies.has(city_id) or companies[city_id]["managerId"] == "":
		return ""
	var member_id := String(companies[city_id]["managerId"])
	companies[city_id]["managerId"] = ""
	companies[city_id]["managerSinceWeekIndex"] = week_index
	return member_id


# Companion-rate percentage for a Fair Quote rank (clamped to 0..FAIR_QUOTE_MAX_RANK).
static func companion_rate_percent(fair_quote_rank: int) -> int:
	return 100 + FAIR_QUOTE_PERCENT_PER_RANK * clampi(fair_quote_rank, 0, FAIR_QUOTE_MAX_RANK)


# companion_ids: members who may still earn the companion rate (recruited and currently merchants).
# fair_quote_ranks: member id -> current Fair Quote rank; missing members count as rank 0.
# Percentage of the base a week pays: 0 in the opening week, the companion rate (with Fair Quote) for a
# full stationed week, otherwise the NPC rate (including the partial week after stationing).
func week_rate_percent(city_id: String, week: int, companion_ids: Dictionary, fair_quote_ranks: Dictionary = {}) -> int:
	var company: Dictionary = companies.get(city_id, {})
	if company.is_empty() or week <= int(company["openedWeekIndex"]):
		return 0
	var manager := String(company["managerId"])
	if manager != "" and companion_ids.has(manager) and int(company["managerSinceWeekIndex"]) < week:
		return companion_rate_percent(int(fair_quote_ranks.get(manager, 0)))
	return NPC_EFFICIENCY_PERCENT


func week_income(city_id: String, week: int, companion_ids: Dictionary, fair_quote_ranks: Dictionary = {}) -> int:
	return base_weekly_income * week_rate_percent(city_id, week, companion_ids, fair_quote_ranks) / 100


# Settles the weeks that ended between the cursor and new_week_index. The cursor makes repeats and
# out-of-order calls no-ops; starting no earlier than previous_week_index means a clock moved without
# a transition (set directly) never pays for the weeks it skipped.
func settle_to_week(previous_week_index: int, new_week_index: int, companion_ids: Dictionary, fair_quote_ranks: Dictionary = {}) -> Dictionary:
	var first := maxi(settled_week_index, previous_week_index)
	var result := {"settled_week_indices": [], "units": 0, "by_company": {}, "ledger_unit_kind": LEDGER_UNIT_KIND}
	if new_week_index <= settled_week_index:
		return result
	for week in range(first, new_week_index):
		result["settled_week_indices"].append(week)
		for city_id in companies:
			if week <= int(companies[city_id]["openedWeekIndex"]):
				continue
			var units := week_income(city_id, week, companion_ids, fair_quote_ranks)
			companies[city_id]["weeksSettled"] = int(companies[city_id]["weeksSettled"]) + 1
			companies[city_id]["unitsEarned"] = int(companies[city_id]["unitsEarned"]) + units
			result["by_company"][city_id] = int(result["by_company"].get(city_id, 0)) + units
			result["units"] = int(result["units"]) + units
	ledger_units += int(result["units"])
	settled_week_index = new_week_index
	return result


func to_save() -> Dictionary:
	return {
		"version": SAVE_VERSION,
		"ledgerUnitKind": LEDGER_UNIT_KIND,
		"settledWeekIndex": settled_week_index,
		"ledgerUnits": ledger_units,
		"companies": companies.duplicate(true),
	}


# Shape and rule check for a saved block. saved_week_index is the week of the saved clock, and the
# cursor must EQUAL it: advance_calendar settles before any handler can save, so every block this
# version writes is caught up. A cursor behind the clock would mean ended weeks were never settled,
# and a cursor ahead would mean weeks were settled that have not ended; both are rejected as corrupt.
# recruited/members/active_party come from the same snapshot; resolve_city maps legacy aliases to
# current location ids ("" when unknown).
static func is_valid_save_block(block: Variant, saved_week_index: int, recruited: Dictionary, members: Dictionary, active_party: Array, resolve_city: Callable) -> bool:
	if typeof(block) != TYPE_DICTIONARY:
		return false
	if not _is_whole(block.get("version")) or int(block["version"]) < 1 or int(block["version"]) > SAVE_VERSION:
		return false
	if block.get("ledgerUnitKind", LEDGER_UNIT_KIND) != LEDGER_UNIT_KIND:
		return false
	if not _is_whole(block.get("settledWeekIndex")) or int(block["settledWeekIndex"]) != saved_week_index:
		return false
	if not _is_whole(block.get("ledgerUnits")) or int(block["ledgerUnits"]) < 0:
		return false
	if typeof(block.get("companies")) != TYPE_DICTIONARY:
		return false
	var managers: Dictionary = {}
	var cities: Dictionary = {}
	for city_id in block["companies"]:
		var company: Variant = block["companies"][city_id]
		if typeof(city_id) != TYPE_STRING or String(city_id) == "" or typeof(company) != TYPE_DICTIONARY:
			return false
		var city_key := _city_key(String(city_id), resolve_city)
		if cities.has(city_key):
			return false
		cities[city_key] = true
		for key in ["managerSinceWeekIndex", "openedWeekIndex", "weeksSettled", "unitsEarned"]:
			if not _is_whole(company.get(key)) or (key in ["weeksSettled", "unitsEarned"] and int(company[key]) < 0):
				return false
		if int(company["openedWeekIndex"]) > saved_week_index or int(company["managerSinceWeekIndex"]) < int(company["openedWeekIndex"]) or int(company["managerSinceWeekIndex"]) > saved_week_index:
			return false
		var manager: Variant = company.get("managerId")
		if typeof(manager) != TYPE_STRING:
			return false
		if manager != "":
			if manager == "hero" or managers.has(manager) or not recruited.has(manager) or not members.has(manager) or active_party.has(manager):
				return false
			managers[manager] = true
	return true


# Loads a block already passed by is_valid_save_block, so its cursor is already the saved clock's week.
# Emits nothing and settles nothing.
func load_save(block: Dictionary, resolve_city: Callable) -> void:
	var restored: Dictionary = {}
	for city_id in block["companies"]:
		var company: Dictionary = block["companies"][city_id]
		restored[_city_key(String(city_id), resolve_city)] = {
			"managerId": String(company["managerId"]),
			"managerSinceWeekIndex": int(company["managerSinceWeekIndex"]),
			"openedWeekIndex": int(company["openedWeekIndex"]),
			"weeksSettled": int(company["weeksSettled"]),
			"unitsEarned": int(company["unitsEarned"]),
		}
	companies = restored
	ledger_units = int(block["ledgerUnits"])
	settled_week_index = int(block["settledWeekIndex"])


# Unknown IDs are kept as-is, as the travel block does for discovered places.
static func _city_key(city_id: String, resolve_city: Callable) -> String:
	var resolved := String(resolve_city.call(city_id))
	return resolved if resolved != "" else city_id


static func _is_whole(value: Variant) -> bool:
	return typeof(value) in [TYPE_INT, TYPE_FLOAT] and is_finite(float(value)) and float(value) == roundf(float(value))
