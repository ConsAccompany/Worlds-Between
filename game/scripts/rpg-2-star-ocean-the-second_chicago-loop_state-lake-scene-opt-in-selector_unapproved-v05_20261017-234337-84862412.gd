extends "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"

# Chicago Loop runtime scene: opt-in selector for the State/Lake v05 material-depth pass (UNAPPROVED, art
# not accepted). NOT WIRED: in this pass the runtime Loop .tscn still names the v04 selector, because
# another session may be editing that shared file. The v05 Godot capture check proves this selector by
# handing the Loop scene path a test-only in-memory copy of the Loop scene whose root uses this script
# (exactly what a one-line `path=` change in the Loop .tscn would do), then flying in from the world map.
# Off by default: without a flag this script only inherits the unchanged v02 scene script, so the Loop
# plays exactly as v02. `-- --chicago-state-lake-v05` (or v05_override = 1 set before the scene loads)
# hands over to the v05 scene; every older opt-in keeps its own rules through the v04 selector:
# `--chicago-state-lake-v04`, then `--chicago-state-lake-v03r1`, then `--chicago-state-lake-v03`. The
# hand-over happens before any v02 code runs (no nodes, no playtest event, the pending resume is left for
# the candidate).

const V04Selector := preload("res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd")
const V05_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const V05_FLAG := "--chicago-state-lake-v05"

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
	if target == "":
		super()
		return
	set_process(false)
	set_process_unhandled_input(false)
	get_tree().change_scene_to_file.call_deferred(target)
