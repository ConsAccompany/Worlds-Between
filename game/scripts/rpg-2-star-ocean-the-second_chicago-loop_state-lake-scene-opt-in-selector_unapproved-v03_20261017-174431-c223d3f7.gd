extends "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"

# Chicago Loop runtime scene: opt-in selector for the State/Lake v03 candidate (UNAPPROVED, art not
# accepted). Off by default: without the flag this script only inherits the unchanged v02 scene
# script, so the Loop plays exactly as v02. With `-- --chicago-state-lake-v03` on the command line, or
# enabled_override = 1 set before the scene loads, the Loop hands over to the v03 candidate scene
# before any v02 code runs (no nodes, no playtest event, the pending resume is left for v03).
# To remove the opt-in, point the Loop .tscn back at the v02 script.

const V03_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v03_20261017-174431-c223d3f7.tscn"
const CLI_FLAG := "--chicago-state-lake-v03"

static var enabled_override := -1


static func v03_enabled() -> bool:
	if enabled_override >= 0:
		return enabled_override == 1
	return OS.get_cmdline_user_args().has(CLI_FLAG)


func _ready() -> void:
	if not v03_enabled():
		super()
		return
	set_process(false)
	set_process_unhandled_input(false)
	get_tree().change_scene_to_file.call_deferred(V03_SCENE)
