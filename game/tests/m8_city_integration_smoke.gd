extends SceneTree

# Functional sample checks. Passing does not approve M8 art or human pacing.
var captures: Array[String] = []
const NativeIdle := preload("res://scripts/character_directional_idle.gd")


func _initialize() -> void:
	call_deferred("_run")


func _settle() -> void:
	await process_frame
	await process_frame


func _check(ok: bool, message: String) -> bool:
	if not ok:
		push_error("CITY_INTEGRATION_FAILED: " + message)
		quit(1)
	return ok


func _walk(area: Node2D, target: Vector2) -> bool:
	var actor: Sprite2D = area.get("hero")
	for step in 600:
		if actor.position.distance_to(target) < 2.5:
			return true
		var direction := actor.position.direction_to(target)
		Input.action_press("move_right", maxf(direction.x, 0.0))
		Input.action_press("move_left", maxf(-direction.x, 0.0))
		Input.action_press("move_down", maxf(direction.y, 0.0))
		Input.action_press("move_up", maxf(-direction.y, 0.0))
		area._process(1.0 / 60.0)
		for action in ["move_right", "move_left", "move_down", "move_up"]:
			Input.action_release(action)
	return false


func _capture(variant: String) -> void:
	var directory := OS.get_environment("WB_CITY_EVIDENCE_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless":
		return
	DirAccess.make_dir_recursive_absolute(directory)
	await RenderingServer.frame_post_draw
	var timestamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var filename := "rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-%s_%s-%08x.png" % [variant, timestamp, randi()]
	var path := directory.path_join(filename)
	if _check(root.get_texture().get_image().save_png(path) == OK, "save engine capture"):
		captures.append(filename)


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m8-city"
	var app: Node = root.get_node("AppState")
	for appearance in ["male", "female"]:
		app.begin_new_run()
		app.hero_appearance = appearance
		app.language = "zh" if appearance == "male" else "en"
		app.select_destination("scifi.city")
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		var area: Node2D = current_scene
		area.set_process(false)
		var actor: Sprite2D = area.get("hero")
		for sprite: Sprite2D in [actor, area.get("city_npc")]:
			var bounds := sprite.texture.get_image().get_used_rect()
			if not _check(sprite.texture.get_size() == Vector2(32, 48) and sprite.scale == Vector2.ONE and sprite.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "native pixel actor " + appearance):
				return
			if not _check(absf(sprite.offset.y + 44.0 - sprite.texture.get_height() * 0.5) < 0.01, "native foot anchoring " + appearance):
				return
			if not _check(bounds.size.y >= 38 and bounds.size.y <= 44, "native visible height " + appearance):
				return
		for facing in ["south", "west", "north", "east"]:
			var motion := Vector2.ZERO
			match facing:
				"west": motion = Vector2.LEFT
				"north": motion = Vector2.UP
				"east": motion = Vector2.RIGHT
				_: motion = Vector2.DOWN
			area._set_city_facing(motion)
			if not _check(actor.texture == NativeIdle.texture_for("protagonist-" + appearance, facing), "hero directional idle " + appearance + " " + facing):
				return
			await _capture(appearance + "-" + facing + "-entry")
		for target in [Vector2(285, 267), Vector2(378, 181), Vector2(120, 187), Vector2(282, 180), Vector2(558, 166), Vector2(470, 247)]:
			if not _check(_walk(area, target), "movement reaches city hotspot " + str(target)):
				return
		if not _check(_walk(area, Vector2(120, 187)), "return to west road"):
			return
		Input.action_press("move_down")
		for step in 60:
			area._process(1.0 / 60.0)
		Input.action_release("move_down")
		if not _check(actor.position.y < 204.0, "west plaza blocks movement"):
			return
		if not _check(_walk(area, Vector2(282, 180)), "walk to Liang Xu"):
			return
		var interact := InputEventAction.new()
		interact.action = "interact"
		interact.pressed = true
		area._unhandled_input(interact)
		if not _check(area.get("dialogue_open"), "walking reaches recruitment interaction"):
			return
		area.get("invite_button").pressed.emit()
		if not _check(app.recruited_members.has("liang-xu") and not area.get("city_npc").visible and not area.get("npc_label").visible, "recruit sprite and label hide together"):
			return
		area._close_dialogue()
		await _capture(appearance + "-recruited")
		var valid_position := Vector2(340, 253)
		var valid_save: String = app.write_auto_save("area", valid_position, "manual_note")
		if not _check(app.load_save(valid_save), "city save loads"):
			return
		change_scene_to_file(app.loaded_scene_path())
		await _settle()
		if not _check(current_scene.get("hero").position == valid_position, "valid save preserves exact position"):
			return
		var legacy_save: String = app.write_auto_save("area", Vector2(82, 260), "manual_note")
		if not _check(app.load_save(legacy_save), "legacy city save loads"):
			return
		change_scene_to_file(app.loaded_scene_path())
		await _settle()
		if not _check(current_scene.get("hero").position == Vector2(82, 203.5), "old city spawn recovers onto west road"):
			return
		current_scene.get("back_button").pressed.emit()
		await _settle()
		if not _check(current_scene.name == "ScifiWorldMap", "city returns to world map"):
			return
	var directory := OS.get_environment("WB_CITY_EVIDENCE_DIR")
	if not directory.is_empty() and not captures.is_empty():
		var manifest := {"purpose": "Automated functional and viewport evidence", "artAccepted": false, "humanPlaytest": false, "canvas": [640, 360], "captures": captures}
		var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
		var manifest_name := "rpg-2-star-ocean-the-second_scifi-city_native-idle-capture-manifest_m8-v01_%s-%08x.json" % [stamp, randi()]
		var file := FileAccess.open(directory.path_join(manifest_name), FileAccess.WRITE)
		file.store_string(JSON.stringify(manifest, "\t") + "\n")
	print("M8_CITY_INTEGRATION_OK")
	quit(0)
