extends "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"

# Chicago Loop runtime scene: opt-in selector for the State/Lake v05 material-depth pass (UNAPPROVED, art
# not accepted). WIRED (sdef35, 2026-10-21): the runtime Loop .tscn names this selector. It was previously
# proven through a test-only in-memory copy of the Loop scene (v05 Godot capture check); that check's
# 'still names v04' source pin is now historical.
# Off by default: without a flag this script only inherits the unchanged v02 scene script, so the Loop
# plays exactly as v02. `-- --chicago-state-lake-v05` (or v05_override = 1 set before the scene loads)
# hands over to the v05 scene; every older opt-in keeps its own rules through the v04 selector:
# `--chicago-state-lake-v04`, then `--chicago-state-lake-v03r1`, then `--chicago-state-lake-v03`. The
# hand-over happens before any v02 code runs (no nodes, no playtest event, the pending resume is left for
# the candidate).

const V04Selector := preload("res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd")
const V05_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const V05_FLAG := "--chicago-state-lake-v05"
const SceneDefaults35 := preload("res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd")

static var v05_override := -1


static func v05_enabled() -> bool:
	if v05_override >= 0:
		return v05_override == 1
	return OS.get_cmdline_user_args().has(V05_FLAG)


func _ready() -> void:
	var target := ""
	if v05_enabled():
		target = V05_SCENE
	elif V04Selector.v04_enabled():
		target = V04Selector.V04_SCENE
	elif V04Selector.V03R1Selector.v03r1_enabled():
		target = V04Selector.V03R1Selector.V03R1_SCENE
	elif V04Selector.V03R1Selector.V03Selector.v03_enabled():
		target = V04Selector.V03R1Selector.V03Selector.V03_SCENE
	elif v05_override != 0 and SceneDefaults35.default_on(SceneDefaults35.CHICAGO):
		# MVP default fallback after every explicit flag (sdef35 policy; false until the creator authorizes it).
		target = "res://scenes/style42/rpg-2-star-ocean-the-second_chicago-loop-style42_state-lake-scene_unapproved-v01_20261022-161615-69eb4eee.tscn"
	if target == "":
		super()
		return
	set_process(false)
	set_process_unhandled_input(false)
	get_tree().change_scene_to_file.call_deferred(target)
