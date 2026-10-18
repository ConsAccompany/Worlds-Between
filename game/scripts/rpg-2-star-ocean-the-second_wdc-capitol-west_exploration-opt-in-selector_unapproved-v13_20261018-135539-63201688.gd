extends "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r2_20261018-042200-7c1e5b39.gd"

# Washington, D.C. ruins (scifi.ruins): opt-in v13 ruin/material candidate (UNAPPROVED, art not accepted).
# Off by default: without `-- --wdc-capitol-west-v13` (or v13_override = 1) every override hands straight to
# the v12r2 selector, which itself is inert without its own flag, so the default game is unchanged.
# v13 changes one thing: the base layer (rt-base) is the v13 localized-collapse art of run
# wdc-cw-v13_20261018-100938-075675cf. The foreground, the four Y-sorted layers, the walk mask, anchors,
# radii, encounter, camera, labels and every hand-off are v12r2's (and v12's files), unchanged.
# Precedence: v13 builds on v12r2, so `--wdc-capitol-west-v13` turns v12r2 (and through it v12r1 and v12) on
# and wins over any of their flags given with it. The Washington records chamber (survey annex room 2,
# `--wdc-records-chamber-v01`) is a separate scene and flag; neither affects the other.
# To remove the opt-in, point game/scenes/scifi_exploration_area.tscn back at the v12r2 selector.
# Checks: tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v13-flag-integration-check_unapproved-v13_20261018-135539-63201688.py

const V13_FLAG := "--wdc-capitol-west-v13"
const V13_BASE_PATH := "res://assets/environments/candidates/wdc-cw-v13_20261018-100938-075675cf/rpg-2-star-ocean-the-second_wdc-capitol-west_rt-base_unapproved-v13_20261018-100938-075675cf.png"

static var v13_override := -1

var v13_active := false


static func v13_enabled() -> bool:
	if v13_override >= 0:
		return v13_override == 1
	return OS.get_cmdline_user_args().has(V13_FLAG)


func _ready() -> void:
	if not v13_enabled():
		super()
		return
	var saved := r2_override
	r2_override = 1
	v13_active = true
	super()
	r2_override = saved
	v13_active = r2_active


func _v12_path(purpose: String) -> String:
	if v13_active and purpose == V12_BASE:
		return V13_BASE_PATH
	return super(purpose)
