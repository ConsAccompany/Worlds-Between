extends SceneTree

# Opt-in male playable entry (motion/art UNAPPROVED):
#   godot --path game -s res://scripts/mpath24/<this>.gd -- --mpath24-language=en --mpath24-destination=scifi.outskirts
# Starts a fresh male run in the normal exploration scene with the male exploration + combat sources, prints
# MPATH24_PLAYABLE_READY once the male driver draws the hero, then leaves the game running for normal play.
# Any refusal prints MPATH24_PLAYABLE_REFUSED and quits with code 1 before AppState changes (package refusals) or
# after rolling the overrides back (attach failures); the legacy male is never shown instead.

const Config := preload("res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_config_opt-in-v01_20261021-170200-5e1c24a7.gd")
const LANGUAGE_ARG := "--mpath24-language="
const DESTINATION_ARG := "--mpath24-destination="
const READY_FRAME_LIMIT := 600


func _initialize() -> void:
	_run.call_deferred()


func _arg(prefix: String, fallback: String) -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(prefix):
			return argument.trim_prefix(prefix)
	return fallback


func _refuse(reason: String) -> void:
	print("MPATH24_PLAYABLE_REFUSED ", reason)
	quit(1)


func _run() -> void:
	var language := _arg(LANGUAGE_ARG, "en")
	var destination := _arg(DESTINATION_ARG, Config.DEFAULT_DESTINATION)
	var result: Dictionary = Config.configure(root.get_node_or_null("AppState"), language, destination)
	if not result["ok"]:
		_refuse(result["error"])
		return
	if change_scene_to_file(result["scene"]) != OK:
		Config.rollback()
		_refuse("could not open " + result["scene"])
		return
	for _frame in READY_FRAME_LIMIT:
		await process_frame
		var scene := current_scene
		if scene != null and scene.scene_file_path == result["scene"] and scene.is_node_ready():
			if Config.driver_attached(scene):
				print("MPATH24_PLAYABLE_READY language=%s destination=%s" % [language, destination])
				return
			if scene is CanvasItem:
				scene.hide()
			Config.rollback()
			_refuse("male driver did not attach; legacy male not shown")
			return
	Config.rollback()
	_refuse("exploration scene not ready after %d frames" % READY_FRAME_LIMIT)
