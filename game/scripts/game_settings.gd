class_name GameSettings
extends Node

# Player preferences (language, master volume, movement key preset) and the F10 settings overlay.
# Stored only in their own config file, never in save data. With no file, nothing is applied: the
# bindings AppState installs, the Master bus gain and the language stay exactly as they are.
# AppState owns this node; it runs while the tree is paused so the overlay works over paused play.

signal settings_changed

const CONFIG_SECTION := "settings"
const CONFIG_VERSION := 1
const DEFAULT_VOLUME := 100
const PRESET_DEFAULT := "default"
const PRESET_ARROWS := "arrows"
const PRESETS := [PRESET_DEFAULT, PRESET_ARROWS]
const MOVEMENT_ACTIONS := ["move_left", "move_right", "move_up", "move_down"]
const ARROW_KEYS := [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN]
const OVERLAY_SCRIPT := preload("res://scripts/settings_overlay.gd")

# The AppState autoload (passed in rather than named, so scripts loaded before autoloads still compile).
var app: Node
var config_path := "user://settings.cfg"
var master_volume := DEFAULT_VOLUME
var movement_preset := PRESET_DEFAULT
# Why the last load fell back to defaults ("" when it did not): "missing", "corrupt" or "invalid".
var load_status := ""
var overlay: CanvasLayer = null
var _default_movement_events: Dictionary = {}
var _previous_paused := false
var _previous_focus: Control = null


func _init() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


# Call after the default controls are installed: those exact events are what "Default controls" restores.
func capture_default_controls() -> void:
	for action in MOVEMENT_ACTIONS:
		_default_movement_events[action] = InputMap.action_get_events(action)


func load_preferences() -> void:
	var config := ConfigFile.new()
	if not FileAccess.file_exists(config_path):
		load_status = "missing"
		return
	if config.load(config_path) != OK:
		load_status = "corrupt"
		return
	load_status = ""
	var language: Variant = config.get_value(CONFIG_SECTION, "language", "")
	if typeof(language) == TYPE_STRING and language in ["zh", "en"]:
		if app.language != language:
			app.toggle_language()
	elif config.has_section_key(CONFIG_SECTION, "language"):
		load_status = "invalid"
	var volume: Variant = config.get_value(CONFIG_SECTION, "master_volume", DEFAULT_VOLUME)
	if typeof(volume) in [TYPE_INT, TYPE_FLOAT]:
		set_master_volume(clampi(int(volume), 0, 100), false)
	else:
		load_status = "invalid"
	var preset: Variant = config.get_value(CONFIG_SECTION, "movement_preset", PRESET_DEFAULT)
	if typeof(preset) == TYPE_STRING and preset in PRESETS:
		set_movement_preset(preset, false)
	else:
		load_status = "invalid"


func save_preferences() -> bool:
	var config := ConfigFile.new()
	config.set_value(CONFIG_SECTION, "version", CONFIG_VERSION)
	config.set_value(CONFIG_SECTION, "language", app.language)
	config.set_value(CONFIG_SECTION, "master_volume", master_volume)
	config.set_value(CONFIG_SECTION, "movement_preset", movement_preset)
	return config.save(config_path) == OK


func set_language(language: String) -> void:
	if language in ["zh", "en"] and app.language != language:
		app.toggle_language()
		save_preferences()
		settings_changed.emit()


# 100 is the Master bus's own 0 dB; 0 mutes the bus instead of using an infinite attenuation.
func set_master_volume(volume: int, persist := true) -> void:
	master_volume = clampi(volume, 0, 100)
	var bus := AudioServer.get_bus_index("Master")
	AudioServer.set_bus_mute(bus, master_volume == 0)
	if master_volume > 0:
		AudioServer.set_bus_volume_db(bus, linear_to_db(master_volume / 100.0))
	if persist:
		save_preferences()
	settings_changed.emit()


# Only the four movement actions change. "arrows" keeps just the arrow-key events of the default set.
func set_movement_preset(preset: String, persist := true) -> void:
	if not preset in PRESETS or _default_movement_events.is_empty():
		return
	var changed := preset != movement_preset
	movement_preset = preset
	for action in MOVEMENT_ACTIONS:
		InputMap.action_erase_events(action)
		for event: InputEvent in _default_movement_events[action]:
			if preset == PRESET_DEFAULT or (event is InputEventKey and (event as InputEventKey).physical_keycode in ARROW_KEYS):
				InputMap.action_add_event(action, event)
	if persist:
		save_preferences()
	if changed:
		# Movement hints are chosen per preset by app.text_for; let every open screen relabel itself.
		app.language_changed.emit()
	settings_changed.emit()


func reset_defaults() -> void:
	set_movement_preset(PRESET_DEFAULT, false)
	set_master_volume(DEFAULT_VOLUME, false)
	save_preferences()


func is_open() -> bool:
	return overlay != null and overlay.visible


func open() -> void:
	if is_open():
		return
	_previous_paused = get_tree().paused
	_previous_focus = get_viewport().gui_get_focus_owner()
	if overlay == null:
		overlay = OVERLAY_SCRIPT.new()
		overlay.settings = self
		add_child(overlay)
	get_tree().paused = true
	overlay.show_overlay()


func close() -> void:
	if not is_open():
		return
	overlay.hide_overlay()
	get_tree().paused = _previous_paused
	if is_instance_valid(_previous_focus) and _previous_focus.is_inside_tree() and _previous_focus.is_visible_in_tree():
		_previous_focus.grab_focus()
	else:
		get_viewport().gui_release_focus()
	_previous_focus = null


func toggle() -> void:
	if is_open():
		close()
	else:
		open()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and (event.keycode == KEY_F10 or event.physical_keycode == KEY_F10):
		get_viewport().set_input_as_handled()
		toggle()
	elif is_open() and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		close()


# Anything the overlay's controls did not use stops here, so nothing reaches the game underneath.
func _unhandled_input(event: InputEvent) -> void:
	if is_open():
		get_viewport().set_input_as_handled()
