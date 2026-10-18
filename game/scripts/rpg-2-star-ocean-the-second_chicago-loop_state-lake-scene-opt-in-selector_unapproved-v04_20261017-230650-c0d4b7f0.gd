extends "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"

# Chicago Loop runtime scene: opt-in selector for the State/Lake v04 scene-art pass (UNAPPROVED, art not
# accepted). Off by default: without a flag this script only inherits the unchanged v02 scene script,
# so the Loop plays exactly as v02. `-- --chicago-state-lake-v04` (or v04_override = 1 set before the
# scene loads) hands over to the v04 scene; the earlier opt-ins keep their own rules through the v03r1
# selector: `-- --chicago-state-lake-v03r1` reaches the untouched v03r1 scene and `-- --chicago-state-lake-v03`
# the untouched v03 scene. The hand-over happens before any v02 code runs (no nodes, no playtest event,
# the pending resume is left for the candidate). To remove the v04 opt-in only, point the Loop .tscn back
# at the v03r1 selector; to remove every opt-in, point it at the v02 script.

const V03R1Selector := preload("res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v03r1_20261017-183235-a00fabf3.gd")
const V04_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v04_20261017-230650-c0d4b7f0.tscn"
const V04_FLAG := "--chicago-state-lake-v04"

static var v04_override := -1


static func v04_enabled() -> bool:
	if v04_override >= 0:
		return v04_override == 1
	return OS.get_cmdline_user_args().has(V04_FLAG)


func _ready() -> void:
	var target := ""
	if v04_enabled():
		target = V04_SCENE
	elif V03R1Selector.v03r1_enabled():
		target = V03R1Selector.V03R1_SCENE
	elif V03R1Selector.V03Selector.v03_enabled():
		target = V03R1Selector.V03Selector.V03_SCENE
	if target == "":
		super()
		return
	set_process(false)
	set_process_unhandled_input(false)
	get_tree().change_scene_to_file.call_deferred(target)
