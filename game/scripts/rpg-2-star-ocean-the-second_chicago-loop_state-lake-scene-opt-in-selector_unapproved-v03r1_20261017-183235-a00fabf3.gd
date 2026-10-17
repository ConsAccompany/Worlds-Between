extends "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"

# Chicago Loop runtime scene: opt-in selector for the State/Lake v03r1 correction (UNAPPROVED, art not
# accepted). Off by default: without a flag this script only inherits the unchanged v02 scene script,
# so the Loop plays exactly as v02. `-- --chicago-state-lake-v03r1` (or v03r1_override = 1 set before
# the scene loads) hands over to the v03r1 scene; `-- --chicago-state-lake-v03` (or the v03 selector's
# enabled_override) still hands over to the untouched v03 scene through the v03 selector's rule. The
# hand-over happens before any v02 code runs (no nodes, no playtest event, the pending resume is left
# for the candidate). To remove both opt-ins, point the Loop .tscn back at the v02 script; to keep
# only v03, point it at the v03 selector.

const V03Selector := preload("res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v03_20261017-174431-c223d3f7.gd")
const V03R1_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v03r1_20261017-183235-a00fabf3.tscn"
const V03R1_FLAG := "--chicago-state-lake-v03r1"

static var v03r1_override := -1


static func v03r1_enabled() -> bool:
	if v03r1_override >= 0:
		return v03r1_override == 1
	return OS.get_cmdline_user_args().has(V03R1_FLAG)


func _ready() -> void:
	var target := ""
	if v03r1_enabled():
		target = V03R1_SCENE
	elif V03Selector.v03_enabled():
		target = V03Selector.V03_SCENE
	if target == "":
		super()
		return
	set_process(false)
	set_process_unhandled_input(false)
	get_tree().change_scene_to_file.call_deferred(target)
