extends SceneTree

# Functional sample checks. Passing does not approve M8 art or human pacing.
# Ordinary defaults (creator default use authorized 2026-10-21; art/motion UNAPPROVED): the male hero uses the mpath24
# mexplore23 driver, the female hero the hsea18 front17 Sea distance driver and Liang Xu the lpath30 lexplore28 driver.
# All three draw 80x112 density-2 frames at scale 0.5 (48 logical px body) with the floor line 1 logical px below the
# node. The legacy 32x48 banks remain only as the whole-package refusal fallback. No opt-in override is set here.
var captures: Array[String] = []
var capture_size := Vector2i.ZERO
const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const SpriteSetPilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const LiangConfig := preload("res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd")
const ACTIVE := {
	"protagonist-male": {
		"driver": "res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd",
		"registry": "res://data/mexplore23/rpg-2-star-ocean-the-second_protagonist-male_explore-sprite-set-registry_unapproved-mexplore23-v01_20261021-162551-15fcefc2.json",
		"registry_sha256": "e156bbc344795b7c21300dabcc9f060bd58a8bd856aec0cf3f937f170fb3290c",
		"set_id": "hero-male-exploration-source-20261021-162551-6e3b1a7d",
	},
	"protagonist-female": {
		"driver": "res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd",
		"registry": "res://data/hsea-front17/rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set-registry_runtime-v01_20261020-222654-e8633039.json",
		"registry_sha256": "a0c6eeb745cc4116beb3ca402047c120cfd70922f0128f9b11c4cbee6b7805f6",
		"set_id": "hero-female-exploration-source-20261020-222654-1478e147",
	},
	"liang-xu": {
		"driver": "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_npc-driver_opt-in-v01_20261021-202247-ca439d91.gd",
		"registry": "res://data/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-sprite-set-registry_unapproved-lexplore28-v01_20261021-194350-4041cca1.json",
		"registry_sha256": "99d8fa23cc0ce28dd5dbc004f5f5044cc59a619d052dbe21cc7290c13ab2be91",
		"set_id": "liang-xu-exploration-source-20261021-194350-3acdbd6e",
	},
}
# Contract values pinned here rather than read from the code under test.
const FRAME_SIZE := Vector2(80, 112)
const DISPLAY_SCALE := Vector2(0.5, 0.5)
const FLOOR_BELOW_NODE := 1.0
const BODY_LOGICAL := 48.0
const TICK := 1.0 / 60.0


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


# One host frame in real order: the driver clock (process_priority -1) advances before the host moves.
func _tick(area: Node2D) -> void:
	var pilot = area.get("sprite_pilot")
	if pilot != null and pilot.has_method("advance"):
		pilot.advance(TICK)
	area._process(TICK)


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
		_tick(area)
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
	var image := root.get_texture().get_image()
	if _check(image.save_png(path) == OK, "save engine capture"):
		captures.append(filename)
		capture_size = image.get_size()


# Active source identity: pinned registry bytes, the expected driver script on this sprite, the pinned set id loaded
# through the production loader, and the drawn texture belonging to that set. "" means accepted.
func _source_problem(sprite: Sprite2D, driver, actor: String) -> String:
	var spec: Dictionary = ACTIVE[actor]
	if driver == null or not is_instance_valid(driver) or driver.get_parent() != sprite:
		return "no driver attached to the sprite"
	if driver.get_script() == null or driver.get_script().resource_path != spec["driver"]:
		return "driver script is not " + String(spec["driver"]).get_file()
	if FileAccess.get_sha256(spec["registry"]) != spec["registry_sha256"]:
		return "registry bytes are not pinned"
	var registry := SpriteSetPilot.load_registry(spec["registry"])
	var loaded := SpriteSetPilot.load_set(registry["actors"].get(actor, ""), actor) if registry["ok"] else {"ok": false}
	if not loaded["ok"] or loaded["set"]["set_id"] != spec["set_id"] or driver.sprite_set["set_id"] != spec["set_id"]:
		return "set id is not " + String(spec["set_id"])
	for action in ["idle", "walk"]:
		for facing in SpriteSetPilot.DIRECTIONS:
			if _facing_textures(driver, action, facing).has(sprite.texture):
				return ""
	return "drawn texture is not from the active set"


# Scale, pivot/floor placement and filtering of the drawn frame; `idle` adds the standing body and sole checks.
func _geometry_problem(sprite: Sprite2D, idle: bool) -> String:
	if sprite.texture == null or sprite.texture.get_size() != FRAME_SIZE:
		return "native frame is not %s" % str(FRAME_SIZE)
	if sprite.scale != DISPLAY_SCALE:
		return "scale %s is not %s" % [str(sprite.scale), str(DISPLAY_SCALE)]
	if sprite.texture_filter != CanvasItem.TEXTURE_FILTER_NEAREST:
		return "filter is not nearest"
	var pivot := Vector2(40, 104)
	var floor_y := (pivot.y - FRAME_SIZE.y * 0.5 + sprite.offset.y) * sprite.scale.y
	if absf(floor_y - FLOOR_BELOW_NODE) > 0.01 or absf(pivot.x - FRAME_SIZE.x * 0.5 + sprite.offset.x) > 0.01:
		return "floor line is %.2f logical px below the node (offset %s)" % [floor_y, str(sprite.offset)]
	if idle:
		var used := sprite.texture.get_image().get_used_rect()
		if used.end.y != int(pivot.y):
			return "soles end on texel row %d, not above the floor row %d" % [used.end.y - 1, int(pivot.y)]
		if absf(used.size.y * sprite.scale.y - BODY_LOGICAL) > 0.5:
			return "displayed body is %.1f logical px" % (used.size.y * sprite.scale.y)
	return ""


func _facing_textures(driver, action: String, facing: String) -> Array:
	var textures: Array = driver.sprite_set["clips"][action][facing]["textures"].duplicate()
	var breathing = driver.get("breathing")
	if action == "idle" and breathing != null and breathing.clips.has(facing):
		textures.append_array(breathing.clips[facing]["textures"])
	return textures


func _facing_problem(sprite: Sprite2D, driver, action: String, facing: String) -> String:
	if String(driver.state()["facing"]) != facing:
		return "driver faces %s" % String(driver.state()["facing"])
	if not _facing_textures(driver, action, facing).has(sprite.texture):
		return "texture is not a %s %s frame (state %s)" % [facing, action, str(driver.state())]
	return ""


# Mutate one property, require the same predicate used by the positive checks to reject it, then restore and re-accept.
func _negative(name: String, sprite: Sprite2D, property: String, wrong, predicate: Callable) -> bool:
	var saved = sprite.get(property)
	sprite.set(property, wrong)
	var reason: String = predicate.call()
	sprite.set(property, saved)
	if not _check(reason != "", "negative control accepted wrong " + name):
		return false
	print("M8_NEGATIVE_%s_REJECTED: %s" % [name.to_upper(), reason])
	return _check(predicate.call() == "", "negative control did not restore " + name)


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m8-city"
	var app: Node = root.get_node("AppState")
	for appearance in ["male", "female"]:
		var actor_id: String = "protagonist-" + appearance
		app.begin_new_run()
		app.hero_appearance = appearance
		app.language = "zh" if appearance == "male" else "en"
		app.select_destination("scifi.city")
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		var area: Node2D = current_scene
		area.set_process(false)
		var actor: Sprite2D = area.get("hero")
		var pilot = area.get("sprite_pilot")
		var npc: Sprite2D = area.get("city_npc")
		var npc_driver = area.get("field_npc_driver")
		if not _check(_source_problem(actor, pilot, actor_id) == "", "active hero source " + appearance + ": " + _source_problem(actor, pilot, actor_id)):
			return
		if not _check(_geometry_problem(actor, true) == "" and _facing_problem(actor, pilot, "idle", "south") == "", "hero entry geometry " + appearance + ": " + _geometry_problem(actor, true) + _facing_problem(actor, pilot, "idle", "south")):
			return
		if not _check(LiangConfig.npc_attached(area) and _source_problem(npc, npc_driver, "liang-xu") == "", "active Liang source " + appearance + ": " + _source_problem(npc, npc_driver, "liang-xu")):
			return
		if not _check(_geometry_problem(npc, true) == "" and _facing_problem(npc, npc_driver, "idle", "south") == "", "Liang geometry " + appearance + ": " + _geometry_problem(npc, true)):
			return
		# Negative controls through the same predicates: Liang's frame on the hero, legacy scale, legacy offset.
		if not _negative("source", actor, "texture", npc_driver.sprite_set["clips"]["idle"]["south"]["textures"][0], _source_problem.bind(actor, pilot, actor_id)):
			return
		if not _negative("scale", actor, "scale", Vector2.ONE, _geometry_problem.bind(actor, true)):
			return
		if not _negative("pivot", actor, "offset", Vector2(0, -20), _geometry_problem.bind(actor, true)):
			return
		# Legacy 32x48 banks stay intact as the refusal fallback.
		for facing in SpriteSetPilot.DIRECTIONS:
			if not _check(NativeIdle.texture_for(actor_id, facing).get_size() == Vector2(32, 48), "fallback idle frame " + appearance + " " + facing):
				return
			for phase in range(1, 5):
				var walk_frame: Texture2D = NativeMotion.texture_for(actor_id, "walk", facing, phase)
				if not _check(walk_frame != null and walk_frame.get_size() == Vector2(32, 48), "fallback walk frame " + appearance + " " + facing + " " + str(phase)):
					return
		# Real input in each direction: walk starts on the first moving frame, release settles back to that facing's idle.
		var opposite := {"south": "north", "north": "south", "west": "east", "east": "west"}
		var actions := {"south": "move_down", "north": "move_up", "west": "move_left", "east": "move_right"}
		for facing in ["south", "north", "west", "east"]:
			var start := actor.position
			Input.action_press(actions[facing])
			_tick(area)
			if not _check(actor.position != start and _facing_problem(actor, pilot, "walk", facing) == "", "input starts walk " + appearance + " " + facing + ": " + _facing_problem(actor, pilot, "walk", facing)):
				return
			for step in 5:
				_tick(area)
			if not _check(_facing_problem(actor, pilot, "walk", facing) == "" and _geometry_problem(actor, false) == "", "walk continues " + appearance + " " + facing + ": " + _facing_problem(actor, pilot, "walk", facing) + _geometry_problem(actor, false)):
				return
			if not _negative("direction", actor, "texture", pilot.sprite_set["clips"]["walk"][opposite[facing]]["textures"][pilot.frame], _facing_problem.bind(actor, pilot, "walk", facing)):
				return
			Input.action_release(actions[facing])
			for step in 30:
				_tick(area)
			if not _check(String(pilot.state()["action"]) == "idle" and _facing_problem(actor, pilot, "idle", facing) == "", "release returns to idle " + appearance + " " + facing + ": " + _facing_problem(actor, pilot, "idle", facing)):
				return
			if not _check(_geometry_problem(actor, true) == "", "idle geometry " + appearance + " " + facing + ": " + _geometry_problem(actor, true)):
				return
			await _capture(appearance + "-" + facing + "-entry")
		for target in [Vector2(285, 267), Vector2(378, 181), Vector2(120, 187), Vector2(282, 180), Vector2(558, 166), Vector2(470, 247)]:
			if not _check(_walk(area, target), "movement reaches city hotspot " + str(target)):
				return
		if not _check(_walk(area, Vector2(120, 187)), "return to west road"):
			return
		Input.action_press("move_down")
		for step in 60:
			_tick(area)
		Input.action_release("move_down")
		if not _check(actor.position.y < 204.0, "west plaza blocks movement"):
			return
		if not _check(_walk(area, Vector2(282, 180)), "walk to Liang Xu"):
			return
		var interact := InputEventAction.new()
		interact.action = "interact"
		interact.pressed = true
		area._unhandled_input(interact)
		var invite: Button = area.get("invite_button")
		if not _check(area.get("dialogue_open") and area.get("dialogue_panel").is_visible_in_tree() and invite.is_visible_in_tree() and not invite.disabled, "walking reaches recruitment interaction"):
			return
		if not _check(npc.visible and area.get("npc_label").visible, "Liang and label visible before invite"):
			return
		invite.pressed.emit()
		if not _check(app.recruited_members.has("liang-xu") and not npc.visible and not area.get("npc_label").visible, "recruit sprite and label hide together"):
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
		var reloaded: Sprite2D = current_scene.get("hero")
		if not _check(_source_problem(reloaded, current_scene.get("sprite_pilot"), actor_id) == "" and _geometry_problem(reloaded, true) == "", "reloaded hero keeps active source " + appearance):
			return
		var legacy_save: String = app.write_auto_save("area", Vector2(82, 260), "manual_note")
		if not _check(app.load_save(legacy_save), "legacy city save loads"):
			return
		change_scene_to_file(app.loaded_scene_path())
		await _settle()
		if not _check(current_scene.get("hero").position == Vector2(82, 203.5), "old city spawn recovers onto west road"):
			return
		if not _check(current_scene._city_walkable(current_scene.get("hero").position), "recovered legacy position is standable in the active city layout"):
			return
		current_scene.get("back_button").pressed.emit()
		await _settle()
		if not _check(current_scene.name == "ScifiWorldMap", "city returns to world map"):
			return
	var directory := OS.get_environment("WB_CITY_EVIDENCE_DIR")
	if not directory.is_empty() and not captures.is_empty():
		var manifest := {"purpose": "Automated functional and viewport evidence", "artAccepted": false, "humanPlaytest": false, "canvas": [capture_size.x, capture_size.y], "captures": captures}
		var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
		var manifest_name := "rpg-2-star-ocean-the-second_scifi-city_native-idle-capture-manifest_m8-v01_%s-%08x.json" % [stamp, randi()]
		var file := FileAccess.open(directory.path_join(manifest_name), FileAccess.WRITE)
		file.store_string(JSON.stringify(manifest, "\t") + "\n")
	print("M8_CITY_INTEGRATION_OK")
	quit(0)
