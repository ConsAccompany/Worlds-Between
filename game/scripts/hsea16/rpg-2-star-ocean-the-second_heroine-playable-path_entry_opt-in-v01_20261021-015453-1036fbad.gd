extends SceneTree

# Opt-in playable entry (motion/art UNAPPROVED):
#   godot --path game -s res://scripts/hsea16/<this>.gd -- --hsea16-language=en --hsea16-destination=scifi.outskirts
# Starts a fresh female run straight in the normal exploration scene with the heroine pilots on, prints
# HSEA16_PLAYABLE_READY once the Sea driver draws the hero, then leaves the game running for normal play.
# Any refusal prints HSEA16_PLAYABLE_REFUSED and quits with code 1; the legacy heroine is never shown instead.

const Config := preload("res://scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_config_opt-in-v01_20261021-015453-1036fbad.gd")
const LANGUAGE_ARG := "--hsea16-language="
const DESTINATION_ARG := "--hsea16-destination="
const READY_FRAME_LIMIT := 600


func _initialize() -> void:
	_run.call_deferred()


func _arg(prefix: String, fallback: String) -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(prefix):
			return argument.trim_prefix(prefix)
	return fallback


func _refuse(reason: String) -> void:
	print("HSEA16_PLAYABLE_REFUSED ", reason)
	quit(1)


func _run() -> void:
	var language := _arg(LANGUAGE_ARG, "en")
	var destination := _arg(DESTINATION_ARG, Config.DEFAULT_DESTINATION)
	var result: Dictionary = Config.configure(root.get_node_or_null("AppState"), language, destination)
	if not result["ok"]:
		_refuse(result["error"])
		return
	if change_scene_to_file(result["scene"]) != OK:
		_refuse("could not open " + result["scene"])
		return
	for _frame in READY_FRAME_LIMIT:
		await process_frame
		var scene := current_scene
		if scene != null and scene.scene_file_path == result["scene"] and scene.is_node_ready():
			if Config.driver_attached(scene):
				print("HSEA16_PLAYABLE_READY language=%s destination=%s" % [language, destination])
				return
			if scene is CanvasItem:
				scene.hide()
			_refuse("heroine driver did not attach; legacy heroine not shown")
			return
	_refuse("exploration scene not ready after %d frames" % READY_FRAME_LIMIT)
