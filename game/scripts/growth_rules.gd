extends RefCounted
class_name GrowthRules

const APTITUDE_IDS := ["martial", "adaptive", "scholarly", "spiritual"]
const SERIES := {
	"sword": {"aptitude": "martial", "stage_names": ["剑士", "剑术师"], "stage_names_en": ["Swordsman", "Swordmaster"], "skills": ["sword_slash", "sword_arc"]},
	"firearms": {"aptitude": "adaptive", "stage_names": ["枪手", "精准射手"], "stage_names_en": ["Gunner", "Marksman"], "skills": ["firearms_shot", "firearms_burst"]},
	"tactics": {"aptitude": "scholarly", "stage_names": ["参谋", "战术师"], "stage_names_en": ["Strategist", "Tactician"], "skills": ["tactics_mark", "tactics_rally"]},
	"relics": {"aptitude": "spiritual", "stage_names": ["遗物学徒", "遗物师"], "stage_names_en": ["Relic Adept", "Relic Keeper"], "skills": ["relics_echo", "relics_delay"]},
	# Merchant (行商): only the first two of the proposal's five stages, like every MVP series. Its id must
	# match CommerceLedger.MERCHANT_SERIES_ID. "placeholder_skills": its job skills have no battle effect,
	# so they are never battle actions. "commerce_passive_skills" lists the ones that are JP-upgradable
	# commerce passives: stage-2 Fair Quote (公平报价), read by the provisional ledger at settlement. The
	# rest (stage-1 Supply Pact) remain placeholders with no effect and take no JP. Personal skills are
	# unaffected.
	"merchant": {"aptitude": "adaptive", "stage_names": ["行商", "契约经理"], "stage_names_en": ["Merchant", "Contract Manager"], "skills": ["merchant_supply_pact", "merchant_fair_quote"], "placeholder_skills": true, "commerce_passive_skills": ["merchant_fair_quote"]},
}
const SKILL_JP_BASE := [20, 35, 55]
const FAIR_QUOTE_SKILL_ID := "merchant_fair_quote"


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


# Battle effect only. False for unknown series and for series whose job skills are placeholders in
# battle (Merchant), so the battle never shows or runs them.
static func job_skills_have_effect(series_id: String) -> bool:
	return SERIES.has(series_id) and not bool(SERIES[series_id].get("placeholder_skills", false))


# Whether JP may be spent on this skill: battle skills, plus listed commerce passives (Fair Quote).
static func job_skill_upgradable(series_id: String, skill_id: String) -> bool:
	if not SERIES.has(series_id) or not SERIES[series_id]["skills"].has(skill_id):
		return false
	return job_skills_have_effect(series_id) or SERIES[series_id].get("commerce_passive_skills", []).has(skill_id)


# Fair Quote rank that counts for commerce: 0 unless the member is currently a stage-2 Merchant
# (Contract Manager), clamped to the JP rank range so a tampered save cannot inflate it.
static func fair_quote_rank(member: Dictionary) -> int:
	if String(member.get("job_series", "")) != "merchant" or int(member.get("job_stage", 1)) < 2:
		return 0
	return clampi(skill_rank(member, FAIR_QUOTE_SKILL_ID), 0, SKILL_JP_BASE.size())


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
