extends RefCounted
class_name GrowthRules

const APTITUDE_IDS := ["martial", "adaptive", "scholarly", "spiritual"]
const SERIES := {
	"sword": {"aptitude": "martial", "stage_names": ["剑士", "剑术师"], "stage_names_en": ["Swordsman", "Swordmaster"], "skills": ["sword_slash", "sword_arc"]},
	"firearms": {"aptitude": "adaptive", "stage_names": ["枪手", "精准射手"], "stage_names_en": ["Gunner", "Marksman"], "skills": ["firearms_shot", "firearms_burst"]},
	"tactics": {"aptitude": "scholarly", "stage_names": ["参谋", "战术师"], "stage_names_en": ["Strategist", "Tactician"], "skills": ["tactics_mark", "tactics_rally"]},
	"relics": {"aptitude": "spiritual", "stage_names": ["遗物学徒", "遗物师"], "stage_names_en": ["Relic Adept", "Relic Keeper"], "skills": ["relics_echo", "relics_delay"]},
}
const SKILL_JP_BASE := [20, 35, 55]


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


static func jp_cost(member: Dictionary, series_id: String, next_rank: int) -> int:
	if next_rank < 1 or next_rank > SKILL_JP_BASE.size():
		return -1
	var score: int = clampi(aptitude(member, series_id), 60, 100)
	return ceili(float(SKILL_JP_BASE[next_rank - 1]) * (1.0 - 0.5 * float(score - 60) / 40.0))


static func stage_name(series_id: String, stage: int, language: String) -> String:
	if not SERIES.has(series_id):
		return series_id
	var names: Array = SERIES[series_id]["stage_names_en" if language == "en" else "stage_names"]
	return String(names[clampi(stage, 1, names.size()) - 1])


static func current_skill_id(member: Dictionary) -> String:
	var series_id: String = member.get("job_series", "sword")
	if not SERIES.has(series_id):
		return ""
	var stage: int = mini(2, int(member.get("job_stage", 1)))
	return String(SERIES[series_id]["skills"][stage - 1])


static func skill_rank(member: Dictionary, skill_id: String) -> int:
	var series_id: String = member.get("job_series", "sword")
	var record: Dictionary = member.get("job_records", {}).get(series_id, {})
	return int(record.get("skills", {}).get(skill_id, 0))
