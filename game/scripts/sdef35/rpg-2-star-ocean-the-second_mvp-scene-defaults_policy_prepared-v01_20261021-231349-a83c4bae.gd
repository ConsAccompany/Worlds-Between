extends RefCounted

# MVP scene default policy. Chicago and Washington exterior/records common-style defaults are
# creator-authorized MVP use, including NYC STYLE46, with final art approval separate.
# Existing ledger tasks content.scene.{city,ruins,ruins-survey-inner,chicago-loop}.native-default.
# Each consumer asks
# this policy only after its own explicit override and CLI flags (and, for Washington and Chicago, after
# every older candidate flag), so it is a fallback, never a precedence change.
# Candidates (all UNAPPROVED art; switching a bit is a creator decision, not a test result):
#   CITY      NYC City Hall Park STYLE46 via v06 loader (city_hall_park_v06_scene.gd). Visible pixels include a
#             palette-reduced recomposition of an imported AI-generated reference plus native overlays;
#             not final native accepted art.
#   RUINS     Washington Capitol west v13 selector (scifi_exploration_area.tscn).
#   RECORDS   Washington common-style STYLE48 records chamber (survey_annex.gd, scifi.ruins room2 only).
#   CHICAGO   Chicago Loop State/Lake v05 selector (Loop .tscn).
# Adoption bits select the currently authorized common-style consumer. Historical prepared
# patches live under outputs/sdef35; rollback to the old default sets the corresponding bit false.
# preview_override is TEST/PREVIEW ONLY (never set by game code): key -> bool, consulted before the bits;
# clear_preview() restores the bits.

const CITY := "city"
const RUINS := "ruins"
const RECORDS := "ruins_survey_inner"
const CHICAGO := "chicago_loop"

const CITY_V06_DEFAULT := true
const RUINS_V13_DEFAULT := true
const RECORDS_ROOM2_DEFAULT := true
const CHICAGO_V05_DEFAULT := true

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
