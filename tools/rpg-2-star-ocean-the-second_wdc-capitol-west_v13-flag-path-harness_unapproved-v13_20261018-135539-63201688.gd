extends "res://../tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v13-texture-override-harness_test-only-unapproved-v13_20261018-100938-075675cf.gd"

# WDC Capitol west v13 (UNAPPROVED): the v13 harness's real-scene run (entry, real-input traversal, records
# prompt + real interact, occlusion, breach view, real walk into the sentry, real battle and return, zh and en)
# driven through the normal game flag path. Nothing is overridden in memory: the shared scene's own script (the
# v13 selector) loads whatever art its flag selects.
#   Godot --path game --resolution 640x360 -s <this file> -- <--wdc-capitol-west-v13 | --wdc-capitol-west-v12r2>
#         --wdc13-mode=v13flag|v12r2flag --wdc13-contract=<json> --wdc13-out=<dir> --wdc13-cap=<dir>
# Every shot also records the path the selector resolves for each layer and the hash of the walk mask in use.
# The flags-off pass-through additionally forces the v13 selector off.

const V13_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd"
const LAYERS := ["rt-base", "rt-fg", "rt-walk", "rt-ys-mast", "rt-ys-tripod", "rt-ys-beacon", "rt-ys-elm"]

var v13: GDScript


func _initialize() -> void:
	var contract_path := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--wdc13-mode="):
			mode = argument.trim_prefix("--wdc13-mode=")
		elif argument.begins_with("--wdc13-contract="):
			contract_path = argument.trim_prefix("--wdc13-contract=")
		elif argument.begins_with("--wdc13-out="):
			out_dir = argument.trim_prefix("--wdc13-out=")
		elif argument.begins_with("--wdc13-cap="):
			cap_dir = argument.trim_prefix("--wdc13-cap=")
	tag = "flag-v13" if mode == "v13flag" else "flag-v12r2"
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	if typeof(parsed) != TYPE_DICTIONARY or out_dir == "" or cap_dir == "" or not mode in ["v13flag", "v12r2flag"]:
		push_error("WDC v13 flag-path harness: missing arguments")
		quit(2)
		return
	contract = parsed
	report["mode"] = mode
	report["override"] = {"in_memory_override": false}
	call_deferred("_run")


func _passthrough() -> void:
	v13 = load(V13_SELECTOR)
	var probe: Node = load(SCENE).instantiate()
	report["scene_script"] = probe.get_script().resource_path
	probe.free()
	report["cmdline_flag_enables_v13"] = v13.v13_enabled()
	v13.v13_override = 0
	await super()
	v13.v13_override = -1


func _base_layer(scene) -> Dictionary:
	var result := super(scene)
	if not result["found"]:
		return result
	var paths := {}
	for purpose in LAYERS:
		paths[purpose] = scene._v12_path(purpose)
	result["layer_paths"] = paths
	result["walk_sha256"] = _sha(scene.v12_walk.get_data())
	result["v13_active"] = scene.get("v13_active")
	var fg: Sprite2D = scene.get_node_or_null("WdcV12_rt_fg")
	result["fg_image_sha256"] = _sha(fg.texture.get_image().get_data()) if fg != null else ""
	return result
