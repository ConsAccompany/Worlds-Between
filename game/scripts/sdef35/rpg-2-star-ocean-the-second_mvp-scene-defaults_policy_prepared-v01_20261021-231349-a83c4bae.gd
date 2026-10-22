extends RefCounted

# MVP scene default policy (PREPARED, NOT ADOPTED). Four default bits for the four unfinished
# ledger tasks content.scene.{city,ruins,ruins-survey-inner,chicago-loop}.native-default. All four are
# false: no creator default authorization exists, so the ordinary game is unchanged. Each consumer asks
# this policy only after its own explicit override and CLI flags (and, for Washington and Chicago, after
# every older candidate flag), so it is a fallback, never a precedence change.
# Candidates (all UNAPPROVED art; switching a bit is a creator decision, not a test result):
#   CITY      NYC City Hall Park v06 (city_hall_park_v06_scene.gd). Most visible pixels are a
#             palette-reduced recomposition of an imported AI-generated reference plus native overlays;
#             not final native accepted art.
#   RUINS     Washington Capitol west v13 selector (scifi_exploration_area.tscn).
#   RECORDS   Washington survey annex room 2 records chamber (survey_annex.gd, scifi.ruins room 2 only).
#   CHICAGO   Chicago Loop State/Lake v05 selector (Loop .tscn).
# Adoption = change exactly one `false` below to `true` (prepared one-line patches live under
# outputs/sdef35). Rollback = change it back; no other file needs to change.
# preview_override is TEST/PREVIEW ONLY (never set by game code): key -> bool, consulted before the bits;
# clear_preview() restores the bits.

const CITY := "city"
const RUINS := "ruins"
const RECORDS := "ruins_survey_inner"
const CHICAGO := "chicago_loop"

const CITY_V06_DEFAULT := false
const RUINS_V13_DEFAULT := false
const RECORDS_ROOM2_DEFAULT := false
const CHICAGO_V05_DEFAULT := false

static var preview_override := {}


static func default_on(key: String) -> bool:
	if preview_override.has(key):
		return bool(preview_override[key])
	match key:
		CITY:
			return CITY_V06_DEFAULT
		RUINS:
			return RUINS_V13_DEFAULT
		RECORDS:
			return RECORDS_ROOM2_DEFAULT
		CHICAGO:
			return CHICAGO_V05_DEFAULT
	push_error("mvp scene default policy: unknown key %s" % key)
	return false


static func clear_preview() -> void:
	preview_override.clear()
