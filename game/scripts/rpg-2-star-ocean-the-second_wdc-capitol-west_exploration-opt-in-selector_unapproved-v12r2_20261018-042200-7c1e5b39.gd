extends "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r1_20261018-034933-23596520.gd"

# Washington, D.C. ruins (scifi.ruins): opt-in v12r2 amendment of the v12r1 candidate (UNAPPROVED, art not
# accepted). Off by default: without `-- --wdc-capitol-west-v12r2` (or r2_override = 1) every override hands
# straight to the v12r1 selector, which itself is inert without its own flag.
# v12r2 changes one thing: the camera curve's ease is shorter and its rate 1.7 instead of 1.5, so walking
# south into the sentry (the north approach) brings its feet blocks above the footer before the encounter
# triggers. Everything else (art, walk mask, anchors, radii, encounter, glyph pinning, label layout, annex
# and battle hand-offs, spawn) is v12r1's.
# To remove the opt-in, point game/scenes/scifi_exploration_area.tscn back at the v12r1 selector.
# Checks: tools/rpg-2-star-ocean-the-second_wdc-capitol-west_sentry-viewport-check_unapproved-v12r2_20261018-042200-7c1e5b39.py

const R2_FLAG := "--wdc-capitol-west-v12r2"
const R2_CAM_EASE := 12.0
const R2_CAM_RATE := 1.7

static var r2_override := -1

var r2_active := false


static func r2_enabled() -> bool:
	if r2_override >= 0:
		return r2_override == 1
	return OS.get_cmdline_user_args().has(R2_FLAG)


static func r2_scroll_for(feet: float) -> int:
	# Same eased shape as r1_scroll_for (start row R1_CAM_START), shorter ease and higher hold rate.
	var d := feet - float(R1_CAM_START)
	var rise := 0.5 * R2_CAM_RATE * R2_CAM_EASE
	var hold := (float(V12_SCROLL_MAX) - 2.0 * rise) / R2_CAM_RATE
	var scroll := 0.0
	if d <= 0.0:
		scroll = 0.0
	elif d < R2_CAM_EASE:
		scroll = 0.5 * R2_CAM_RATE * d * d / R2_CAM_EASE
	elif d < R2_CAM_EASE + hold:
		scroll = rise + R2_CAM_RATE * (d - R2_CAM_EASE)
	elif d < 2.0 * R2_CAM_EASE + hold:
		var rest := 2.0 * R2_CAM_EASE + hold - d
		scroll = float(V12_SCROLL_MAX) - 0.5 * R2_CAM_RATE * rest * rest / R2_CAM_EASE
	else:
		scroll = float(V12_SCROLL_MAX)
	var lowest := roundi(feet) + V12_CANVAS_BELOW - (V12_VIEW_BOTTOM - V12_VIEW_TOP)
	return clampi(maxi(roundi(scroll), lowest), 0, V12_SCROLL_MAX)


func _ready() -> void:
	if not r2_enabled():
		super()
		return
	var saved := r1_override
	r1_override = 1
	r2_active = true
	super()
	r1_override = saved
	r2_active = r1_active


func _v12_sync() -> void:
	super()
	if not r2_active:
		return
	var scroll := r2_scroll_for(hero.position.y)
	if scroll == v12_scroll:
		return
	v12_scroll = scroll
	if v12_camera != null:
		v12_camera.position = Vector2(0, v12_scroll - V12_VIEW_TOP)
		v12_camera.force_update_scroll()
	if v12_labels != null:
		_r1_layout()
