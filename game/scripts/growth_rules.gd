extends RefCounted
class_name GrowthRules

# Ten-node progression rules (creator decisions 2026-10-15). The catalog holds the 20 approved series with
# their five canonical stage names and 10 skeletal nodes each (2 per stage), and the 51 identities with 10
# personal nodes each. Only nodes that map to an effect the runtime already executes carry an effect; the
# rest are structural skeletons with no design, so JP is never spent on them (like Supply Pact before).
const CATALOG_PATH := "res://data/growth/rpg-2-star-ocean-the-second_progression-ten-node_science-mvp-skeleton_v01_20261016-005300-e36e5d2c.json"
const APTITUDE_IDS := ["martial", "adaptive", "scholarly", "spiritual"]
const STAGE_COUNT := 5
# Stages 1-4 advance at the ten-level choices; stage 5 also needs the series final quest, which clears it
# for the whole party once done.
const LEVEL_CHOICE_STAGE_CAP := 4
const SKILL_RANK_CAP := 5
# The series the runtime can enter. "skills" is the stage-ordered action list battle_arena.gd reads (index
# = stage - 1); every entry is also that stage's "a" node in the catalog.
const SERIES := {
	"sword": {"aptitude": "martial", "skills": ["sword_slash", "sword_arc"]},
	"firearms": {"aptitude": "adaptive", "skills": ["firearms_shot", "firearms_burst"]},
	"tactics": {"aptitude": "scholarly", "skills": ["tactics_mark", "tactics_rally"]},
	"relics": {"aptitude": "spiritual", "skills": ["relics_echo", "relics_delay"]},
	# Merchant (行商). Its id must match CommerceLedger.MERCHANT_SERIES_ID. "placeholder_skills": its job
	# skills have no battle effect, so they are never battle actions. Stage-2 Fair Quote (公平报价) is a
	# commerce passive read by the provisional ledger at settlement; stage-1 Supply Pact has no effect.
	"merchant": {"aptitude": "adaptive", "skills": ["merchant_supply_pact", "merchant_fair_quote"], "placeholder_skills": true},
}
# JP base per target rank (index = rank - 1). Rank 1 is granted when a node opens and is never bought.
# Ranks 2-3 keep the earlier runtime costs; 4-5 are provisional.
const SKILL_JP_BASE := [0, 35, 55, 80, 110]
const FAIR_QUOTE_SKILL_ID := "merchant_fair_quote"

static var _catalog: Dictionary = {}
static var _series_by_id: Dictionary = {}
static var _identity_by_member: Dictionary = {}


static func catalog() -> Dictionary:
	if _catalog.is_empty():
		var file := FileAccess.open(CATALOG_PATH, FileAccess.READ)
		if file == null:
			push_error("growth catalog missing: " + CATALOG_PATH)
			return _catalog
		var parsed: Variant = JSON.parse_string(file.get_as_text())
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("growth catalog is not a JSON object: " + CATALOG_PATH)
			return _catalog
		_catalog = parsed
		for entry in _catalog.get("series", []):
			_series_by_id[String(entry["id"])] = entry
		for identity in _catalog.get("identities", []):
			if identity.has("runtimeMemberId"):
				_identity_by_member[String(identity["runtimeMemberId"])] = identity
	return _catalog


static func series_entry(series_id: String) -> Dictionary:
	catalog()
	return _series_by_id.get(series_id, {})


static func catalog_series_ids() -> Array[String]:
	catalog()
	var ids: Array[String] = []
	for series_id in _series_by_id:
		ids.append(String(series_id))
	return ids


static func career_nodes(series_id: String) -> Array:
	return series_entry(series_id).get("nodes", [])


static func career_node(series_id: String, node_id: String) -> Dictionary:
	for node in career_nodes(series_id):
		if String(node["id"]) == node_id:
			return node
	return {}


static func stage_node_ids(series_id: String, stage: int) -> Array[String]:
	var ids: Array[String] = []
	for node in career_nodes(series_id):
		if int(node["stage"]) == stage:
			ids.append(String(node["id"]))
	return ids


static func xp_to_next(level: int) -> int:
	return 30 + 10 * maxi(0, level - 1)


static func aptitude(member: Dictionary, series_id: String) -> int:
	if not SERIES.has(series_id):
		return 0
	var index: int = APTITUDE_IDS.find(SERIES[series_id]["aptitude"])
	var values: Array = member.get("aptitudes", [60, 60, 60, 60])
	return int(values[index]) if index >= 0 and index < values.size() else 0


static func can_enter(member: Dictionary, series_id: String) -> bool:
	return aptitude(member, series_id) >= 60


# JP for raising a skill to next_rank. -1 outside ranks 2..SKILL_RANK_CAP: JP never opens a node.
static func jp_cost(member: Dictionary, series_id: String, next_rank: int) -> int:
	if next_rank < 2 or next_rank > SKILL_RANK_CAP:
		return -1
	var score: int = clampi(aptitude(member, series_id), 60, 100)
	return ceili(float(SKILL_JP_BASE[next_rank - 1]) * (1.0 - 0.5 * float(score - 60) / 40.0))


static func stage_count(series_id: String) -> int:
	return series_entry(series_id).get("stageNamesZh", []).size()


# Chinese names are the approved canon. English has labels only where the runtime already had them
# (stages 1-2 of the five runtime series); other stages fall back to "<series> · Stage N".
static func stage_name(series_id: String, stage: int, language: String) -> String:
	var entry := series_entry(series_id)
	if entry.is_empty():
		return series_id
	var names: Array = entry["stageNamesZh"]
	var index := clampi(stage, 1, names.size()) - 1
	if language != "en":
		return String(names[index])
	var english: Variant = entry.get("stageNamesEn", [])[index]
	return String(english) if english != null else "%s · Stage %d" % [String(entry["nameEn"]), index + 1]


# Whether a promotion is open for the member's current series: stages 1-4 at a level choice, stage 5
# only after the series final quest (cleared_final_quests: series id -> true).
static func can_promote(member: Dictionary, cleared_final_quests: Dictionary) -> bool:
	var stage := int(member.get("job_stage", 1))
	if stage < LEVEL_CHOICE_STAGE_CAP:
		return true
	return stage == LEVEL_CHOICE_STAGE_CAP and cleared_final_quests.get(String(member.get("job_series", "")), false) == true


# Opens every node of stages 1..through_stage at rank 1 if it is not open yet. Returns how many opened.
static func grant_stage_nodes(record: Dictionary, series_id: String, through_stage: int) -> int:
	if not record.has("skills") or typeof(record["skills"]) != TYPE_DICTIONARY:
		record["skills"] = {}
	var skills: Dictionary = record["skills"]
	var opened := 0
	for node in career_nodes(series_id):
		if int(node["stage"]) <= through_stage and int(skills.get(String(node["id"]), 0)) < 1:
			skills[String(node["id"])] = 1
			opened += 1
	return opened


# Provisional (pending creator review): a level-synced recruit counts as having promoted at every
# ten-level choice its level has passed, so stage = 1 + level / 10. It stays at the level-choice cap (4)
# unless the party has cleared that series' final quest. Only stage nodes at rank 1 come with it; the
# JP-paid ranks 2-5 are never seeded.
static func recruit_stage(level: int, series_id: String, cleared_final_quests: Dictionary) -> int:
	var cap := STAGE_COUNT if cleared_final_quests.get(series_id, false) == true else LEVEL_CHOICE_STAGE_CAP
	return clampi(1 + maxi(1, level) / 10, 1, mini(cap, maxi(1, stage_count(series_id))))


static func new_job_record(series_id: String, stage: int) -> Dictionary:
	var record := {"stage": stage, "skills": {}}
	grant_stage_nodes(record, series_id, stage)
	return record


# Battle effect only. False for unknown series and for series whose job skills are placeholders in
# battle (Merchant), so the battle never shows or runs them.
static func job_skills_have_effect(series_id: String) -> bool:
	return SERIES.has(series_id) and not bool(SERIES[series_id].get("placeholder_skills", false))


# Whether JP may be spent on this node: it belongs to an enterable series and has a runtime effect
# (battle skills, plus the Fair Quote commerce passive). Skeleton nodes and Supply Pact take no JP.
static func job_skill_upgradable(series_id: String, skill_id: String) -> bool:
	return SERIES.has(series_id) and String(career_node(series_id, skill_id).get("effect", "none")) != "none"


static func job_node_open(member: Dictionary, series_id: String, node_id: String) -> bool:
	var node := career_node(series_id, node_id)
	var record: Dictionary = member.get("job_records", {}).get(series_id, {})
	return not node.is_empty() and int(node["stage"]) <= int(record.get("stage", 0)) and int(record.get("skills", {}).get(node_id, 0)) >= 1


# Fair Quote rank that counts for commerce: 0 unless the member is currently a stage-2+ Merchant,
# clamped to the rank cap so a tampered save cannot inflate it.
static func fair_quote_rank(member: Dictionary) -> int:
	if String(member.get("job_series", "")) != "merchant" or int(member.get("job_stage", 1)) < 2:
		return 0
	return clampi(skill_rank(member, FAIR_QUOTE_SKILL_ID), 0, SKILL_RANK_CAP)


# The latest battle action the member's stage has opened (stages past the action list keep the last one).
static func current_skill_id(member: Dictionary) -> String:
	var series_id: String = member.get("job_series", "sword")
	if not SERIES.has(series_id):
		return ""
	var skills: Array = SERIES[series_id]["skills"]
	var stage: int = clampi(int(member.get("job_stage", 1)), 1, skills.size())
	return String(skills[stage - 1])


static func skill_rank(member: Dictionary, skill_id: String) -> int:
	var series_id: String = member.get("job_series", "sword")
	var record: Dictionary = member.get("job_records", {}).get(series_id, {})
	return int(record.get("skills", {}).get(skill_id, 0))


# --- Personal trees -------------------------------------------------------------------------------
# Node 1 is the signature skill, open on joining; its rank stays in "personal_skill_rank" (read by the
# battle). Nodes 2-10 open at rank 1 when the member's level reaches their gate and live in
# "personal_node_ranks" (node id -> rank).

static func identity_for_member(member_id: String) -> Dictionary:
	catalog()
	return _identity_by_member.get(member_id, {})


static func personal_nodes(member_id: String) -> Array:
	return identity_for_member(member_id).get("nodes", [])


static func personal_node(member_id: String, node_id: String) -> Dictionary:
	for node in personal_nodes(member_id):
		if String(node["id"]) == node_id:
			return node
	return {}


static func signature_node_id(member_id: String) -> String:
	var nodes := personal_nodes(member_id)
	return String(nodes[0]["id"]) if not nodes.is_empty() else ""


static func personal_node_rank(member: Dictionary, member_id: String, node_id: String) -> int:
	if node_id != "" and node_id == signature_node_id(member_id):
		return int(member.get("personal_skill_rank", 1))
	return int(member.get("personal_node_ranks", {}).get(node_id, 0))


static func personal_node_upgradable(member_id: String, node_id: String) -> bool:
	return String(personal_node(member_id, node_id).get("effect", "none")) != "none"


# Opens the personal nodes whose gate the member's level has reached. Returns how many opened.
static func unlock_personal_nodes(member: Dictionary, member_id: String) -> int:
	if not member.has("personal_node_ranks") or typeof(member["personal_node_ranks"]) != TYPE_DICTIONARY:
		member["personal_node_ranks"] = {}
	if int(member.get("personal_skill_rank", 0)) < 1:
		member["personal_skill_rank"] = 1
	var ranks: Dictionary = member["personal_node_ranks"]
	var level := int(member.get("level", 1))
	var opened := 0
	for node in personal_nodes(member_id):
		if bool(node.get("signature", false)) or int(node["unlockLevel"]) > level:
			continue
		if int(ranks.get(String(node["id"]), 0)) < 1:
			ranks[String(node["id"])] = 1
			opened += 1
	return opened


# Additive save migration and tamper guard. Opens every node a saved stage or level already earns,
# clamps ranks to 1..SKILL_RANK_CAP and stages to 1..STAGE_COUNT, and never removes a record (records of
# series this build cannot enter are kept as they are). JSON floats become ints. Returns true when a
# node opened or a value had to be clamped.
static func normalize_member(member: Dictionary, member_id: String) -> bool:
	var changed := false
	if typeof(member.get("job_records")) != TYPE_DICTIONARY:
		member["job_records"] = {}
		changed = true
	var records: Dictionary = member["job_records"]
	var current := String(member.get("job_series", "sword"))
	changed = _clamp_key(member, "job_stage", 1, STAGE_COUNT) or changed
	if not records.has(current) and not series_entry(current).is_empty():
		records[current] = {"stage": member["job_stage"], "skills": {}}
		changed = true
	for series_id in records:
		var record: Variant = records[series_id]
		if typeof(record) != TYPE_DICTIONARY or series_entry(String(series_id)).is_empty():
			continue
		changed = _clamp_key(record, "stage", 1, STAGE_COUNT) or changed
		changed = grant_stage_nodes(record, String(series_id), int(record["stage"])) > 0 or changed
		for node_id in record["skills"]:
			changed = _clamp_key(record["skills"], node_id, 1, SKILL_RANK_CAP) or changed
	changed = _clamp_key(member, "personal_skill_rank", 1, SKILL_RANK_CAP) or changed
	if typeof(member.get("personal_node_ranks")) != TYPE_DICTIONARY:
		member["personal_node_ranks"] = {}
		changed = true
	changed = unlock_personal_nodes(member, member_id) > 0 or changed
	var ranks: Dictionary = member["personal_node_ranks"]
	for node_id in ranks:
		changed = _clamp_key(ranks, node_id, 1, SKILL_RANK_CAP) or changed
	return changed


static func _clamp_key(target: Dictionary, key: Variant, low: int, high: int) -> bool:
	var value := clampi(int(target.get(key, low)), low, high)
	var changed := not target.has(key) or float(target[key]) != float(value)
	target[key] = value
	return changed
