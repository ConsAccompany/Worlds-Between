extends SceneTree

# The field NPC must use the character's native art, remain recruitable, and
# disappear on recruitment and reload. This is a runtime check, not art approval.
const NativeIdle := preload("res://scripts/character_directional_idle.gd")


func _initialize() -> void:
	call_deferred("_run")


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, detail: String) -> bool:
	if condition:
		return true
	push_error("M8_FIELD_NPC_VISUAL_FAILED: " + detail)
	quit(1)
	return false


func _interact() -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	return event


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m8-field-npc-visual"
	var app: Node = root.get_node("AppState")
	for destination in ["scifi.outskirts", "scifi.ruins"]:
		app.begin_new_run()
		app.select_destination(destination)
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		var area: Node2D = current_scene
		area.set_process(false)
		var member: String = area.get("recruit_id")
		var npc: Sprite2D = area.get("field_npc")
		if not _check(npc != null and npc.visible, destination + " NPC exists before recruitment"):
			return
		if not _check(npc.texture == NativeIdle.texture_for(member, "south"), destination + " uses native character art"):
			return
		if not _check(npc.texture.get_size() == Vector2(32, 48) and npc.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, destination + " uses native dimensions/filter"):
			return
		if not _check(npc.position == area.get("npc_position") and npc.offset == Vector2(0, -20), destination + " NPC foot anchor"):
			return
		area.get("hero").position = area.get("npc_position")
		if destination == "scifi.ruins":
			app.ji_records_checked = true
		area._unhandled_input(_interact())
		if not _check(area.get("dialogue_open") and area.get("dialogue_mode") == "recruit", destination + " recruitment opens"):
			return
		area.get("invite_button").pressed.emit()
		if not _check(app.recruited_members.has(member) and not npc.visible and not area.get("npc_label").visible, destination + " recruitment hides art and label"):
			return
		var save_id: String = app.write_auto_save("area", area.get("hero").position, "manual_note")
		if not _check(app.load_save(save_id), destination + " save reloads"):
			return
		change_scene_to_file(app.loaded_scene_path())
		await _settle()
		area = current_scene
		if not _check(app.recruited_members.has(member) and not area.get("field_npc").visible and not area.get("npc_label").visible, destination + " recruitment persists after reload"):
			return
	print("M8_FIELD_NPC_VISUAL_OK")
	quit(0)
