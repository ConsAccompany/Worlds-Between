extends SceneTree

# MVP settings: dumps every InputMap action's events and the Master bus state right after AppState starts,
# so a tree without the settings code (origin/main) and the candidate can be compared with no prefs file.
# Run with an isolated APPDATA: Godot --headless --path game -s <absolute path to this file> -- <output json>


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	await process_frame
	var out_path: String = OS.get_cmdline_user_args()[0]
	var actions := {}
	for action in InputMap.get_actions():
		var events := []
		for event in InputMap.action_get_events(action):
			events.append(_describe(event))
		actions[String(action)] = events
	var file := FileAccess.open(out_path, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"language": root.get_node("AppState").language,
		"masterBusIndex": AudioServer.get_bus_index("Master"),
		"masterVolumeDb": AudioServer.get_bus_volume_db(0),
		"masterMuted": AudioServer.is_bus_mute(0),
		"busCount": AudioServer.bus_count,
		"actions": actions,
	}, "  ", true) + "\n")
	file.close()
	print("SETTINGS_BASELINE_DUMP_OK actions=%d" % actions.size())
	quit(0)


func _describe(event: InputEvent) -> Dictionary:
	if event is InputEventKey:
		return {"type": "key", "keycode": event.keycode, "physical": event.physical_keycode, "unicode": event.unicode, "mods": event.get_modifiers_mask()}
	if event is InputEventJoypadButton:
		return {"type": "joy_button", "button": event.button_index, "device": event.device}
	if event is InputEventJoypadMotion:
		return {"type": "joy_motion", "axis": event.axis, "value": event.axis_value, "device": event.device}
	if event is InputEventMouseButton:
		return {"type": "mouse", "button": event.button_index}
	return {"type": event.get_class()}
