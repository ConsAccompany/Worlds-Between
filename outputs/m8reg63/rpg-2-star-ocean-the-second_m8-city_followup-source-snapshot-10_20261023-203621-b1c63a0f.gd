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
		"set_sha256": "6e3df976b3def0fdb56e1bd738dc13076e60108bf7b16b20a15824cd07dfd2da",
		"set_id": "hero-male-exploration-source-20261021-162551-6e3b1a7d",
		"idle_frames": 4,
	},
	"protagonist-female": {
		"driver": "res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd",
		"registry": "res://data/hsea-front17/rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set-registry_runtime-v01_20261020-222654-e8633039.json",
		"registry_sha256": "a0c6eeb745cc4116beb3ca402047c120cfd70922f0128f9b11c4cbee6b7805f6",
		"set_sha256": "3ccf615a536fef4938dafa869ea7f454860a3dca72fdb0c6c566e03f4fea3fa1",
		"set_id": "hero-female-exploration-source-20261020-222654-1478e147",
		"idle_frames": 1,
		# The hsea09 front17 profile's idle supplement (per-frame sha256 inside, checked below).
		"breathing": "res://data/hsea-idle21/rpg-2-star-ocean-the-second_heroine-sea_explore-breathing-idle-manifest_unapproved-idle21-v01_20261021-151339-cf9f5d3c.json",
		"breathing_sha256": "dc6f4496fe268fd07d1ba674c415f8063977263a29549e82a578d5901c657e96",
		"breathing_frames": 8,
	},
	"liang-xu": {
		"driver": "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_npc-driver_opt-in-v01_20261021-202247-ca439d91.gd",
		"registry": "res://data/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-sprite-set-registry_unapproved-lexplore28-v01_20261021-194350-4041cca1.json",
		"registry_sha256": "99d8fa23cc0ce28dd5dbc004f5f5044cc59a619d052dbe21cc7290c13ab2be91",
		"set_sha256": "138ae2f3660139d90a2e9d784315c9eac8ab1ca27c6d753ddf98d39ce40cd379",
		"set_id": "liang-xu-exploration-source-20261021-194350-3acdbd6e",
		"idle_frames": 4,
	},
}
# Contract values pinned here rather than read from the code under test.
const WALK_FRAMES := 12
const DENSITY := 2
const PIVOT := Vector2(40, 104)
const FRAME_SIZE := Vector2(80, 112)
const DISPLAY_SCALE := Vector2(0.5, 0.5)
const FLOOR_BELOW_NODE := 1.0
const BODY_LOGICAL := 48.0
const TICK := 1.0 / 60.0
var _expected_sets := {}


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


# Pinned source read by the test itself, before any production loader cache: raw registry sha256, the set manifest path
# derived from that registry and its raw sha256, the female breathing supplement and its per-frame sha256, then every
# frame loaded here and checked against the current contract (counts, 80x112, density 2, pivot, soles on/above the
# floor row). Byte pins are rechecked on every call; only the loaded result of already-pinned bytes is memoized.
func _expected(actor: String) -> Dictionary:
	var spec: Dictionary = ACTIVE[actor]
	if FileAccess.get_sha256(spec["registry"]) != spec["registry_sha256"]:
		return {"problem": "registry bytes are not pinned"}
	var registry = JSON.parse_string(FileAccess.get_file_as_string(spec["registry"]))
	var listed = registry["actors"].get(actor) if registry is Dictionary and registry.get("actors") is Dictionary else null
	if not listed is String or String(listed).is_empty():
		return {"problem": "pinned registry lists no set for " + actor}
	var set_path: String = listed if String(listed).contains("://") else String(spec["registry"]).get_base_dir().path_join(listed).simplify_path()
	if FileAccess.get_sha256(set_path) != spec["set_sha256"]:
		return {"problem": "set manifest bytes are not pinned: " + set_path.get_file()}
	if spec.has("breathing") and FileAccess.get_sha256(spec["breathing"]) != spec["breathing_sha256"]:
		return {"problem": "breathing manifest bytes are not pinned"}
	if _expected_sets.has(actor):
		return _expected_sets[actor]
	var data = JSON.parse_string(FileAccess.get_file_as_string(set_path))
	if not data is Dictionary or data.get("set_id") != spec["set_id"] or data.get("actor_id") != actor:
		return {"problem": "pinned set manifest is not " + String(spec["set_id"])}
	if int(data.get("density", 0)) != DENSITY or _pair(data.get("frame_size")) != FRAME_SIZE or _pair(data.get("pivot")) != PIVOT:
		return {"problem": "pinned set metadata is not density %d, %s, pivot %s" % [DENSITY, str(FRAME_SIZE), str(PIVOT)]}
	var result := {"problem": "", "clips": {"idle": {}, "walk": {}}, "breathing": {}}
	for action in ["idle", "walk"]:
		for facing in SpriteSetPilot.DIRECTIONS:
			var frames: Array = data["actions"][action][facing]
			var count: int = spec["idle_frames"] if action == "idle" else WALK_FRAMES
			if frames.size() != count:
				return {"problem": "%s %s has %d frames, not %d" % [action, facing, frames.size(), count]}
			var textures := []
			var problem := _load_frames(frames, set_path.get_base_dir(), action == "idle", textures)
			if problem != "":
				return {"problem": "%s %s %s" % [action, facing, problem]}
			result["clips"][action][facing] = textures
	if spec.has("breathing"):
		var supplement = JSON.parse_string(FileAccess.get_file_as_string(spec["breathing"]))
		if not supplement is Dictionary or supplement.get("source_set_sha256") != spec["set_sha256"]:
			return {"problem": "breathing supplement is not bound to the pinned set"}
		for facing in SpriteSetPilot.DIRECTIONS:
			var frames: Array = supplement["directions"][facing]["frames"]
			if frames.size() != spec["breathing_frames"]:
				return {"problem": "breathing %s has %d frames, not %d" % [facing, frames.size(), spec["breathing_frames"]]}
			var textures := []
			var problem := _load_frames(frames, String(spec["breathing"]).get_base_dir(), true, textures)
			if problem != "":
				return {"problem": "breathing %s %s" % [facing, problem]}
			result["breathing"][facing] = textures
	print("M8_ACTIVE_SET_VERIFIED: %s idle %d walk %d breathing %d per direction, all %s" % [actor, spec["idle_frames"], WALK_FRAMES, spec.get("breathing_frames", 0), str(FRAME_SIZE)])
	_expected_sets[actor] = result
	return result


func _pair(value) -> Vector2:
	return Vector2(value[0], value[1]) if value is Array and value.size() == 2 else Vector2(-1, -1)


# Loads manifest frames into `out`; a frame with a "sha256" field must match it byte for byte. "" means accepted.
func _load_frames(frames: Array, base_dir: String, idle: bool, out: Array) -> String:
	for index in frames.size():
		var entry = frames[index]
		if not entry is Dictionary or not entry.get("file") is String:
			return "frame %d has no file" % index
		var path: String = entry["file"] if String(entry["file"]).contains("://") else base_dir.path_join(entry["file"]).simplify_path()
		if entry.has("sha256") and FileAccess.get_sha256(path) != entry["sha256"]:
			return "frame %d bytes are not pinned" % index
		var texture := ResourceLoader.load(path, "Texture2D") as Texture2D
		if texture == null or texture.get_size() != FRAME_SIZE:
			return "frame %d is not a %s texture" % [index, str(FRAME_SIZE)]
		var used := texture.get_image().get_used_rect()
		if used.end.y > int(PIVOT.y) or (idle and used.end.y != int(PIVOT.y)):
			return "frame %d soles end on row %d (floor row %d)" % [index, used.end.y - 1, int(PIVOT.y)]
		out.append(texture)
	return ""


# Active source identity: the expected driver script on this sprite, the pinned bytes above, the pinned set id through
# the production loader, the driver's own idle/walk (and breathing) texture lists equal to the independently loaded
# ones, and the drawn texture belonging to the independent set. "" means accepted.
func _source_problem(sprite: Sprite2D, driver, actor: String) -> String:
	var spec: Dictionary = ACTIVE[actor]
	if driver == null or not is_instance_valid(driver) or driver.get_parent() != sprite:
		return "no driver attached to the sprite"
	if driver.get_script() == null or driver.get_script().resource_path != spec["driver"]:
		return "driver script is not " + String(spec["driver"]).get_file()
	var expected := _expected(actor)
	if expected["problem"] != "":
		return expected["problem"]
	var registry := SpriteSetPilot.load_registry(spec["registry"])
	var loaded := SpriteSetPilot.load_set(registry["actors"].get(actor, ""), actor) if registry["ok"] else {"ok": false}
	if not loaded["ok"] or loaded["set"]["set_id"] != spec["set_id"] or driver.sprite_set.get("set_id") != spec["set_id"]:
		return "set id is not " + String(spec["set_id"])
	for action in ["idle", "walk"]:
		for facing in SpriteSetPilot.DIRECTIONS:
			if driver.sprite_set["clips"][action][facing]["textures"] != expected["clips"][action][facing]:
				return "driver %s %s textures are not the pinned set's" % [action, facing]
			if loaded["set"]["clips"][action][facing]["textures"] != expected["clips"][action][facing]:
				return "loader %s %s textures are not the pinned set's" % [action, facing]
	var breathing = driver.get("breathing")
	var breathing_clips: Dictionary = breathing.clips if breathing != null else {}
	if breathing_clips.size() != expected["breathing"].size():
		return "driver breathing directions %d, pinned %d" % [breathing_clips.size(), expected["breathing"].size()]
	for facing in expected["breathing"]:
		if not breathing_clips.has(facing) or breathing_clips[facing]["textures"] != expected["breathing"][facing]:
			return "driver breathing %s textures are not the pinned supplement's" % facing
	for action in ["idle", "walk"]:
		for facing in SpriteSetPilot.DIRECTIONS:
			if _facing_textures(actor, action, facing).has(sprite.texture):
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
	var pivot := PIVOT
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


# Independently loaded frames for one facing; idle includes the pinned breathing supplement where the actor has one.
func _facing_textures(actor: String, action: String, facing: String) -> Array:
	var expected := _expected(actor)
	if expected["problem"] != "":
		return []
	var textures: Array = expected["clips"][action][facing].duplicate()
	if action == "idle" and expected["breathing"].has(facing):
		textures.append_array(expected["breathing"][facing])
	return textures


func _facing_problem(sprite: Sprite2D, driver, actor: String, action: String, facing: String) -> String:
	if String(driver.state()["facing"]) != facing:
		return "driver faces %s" % String(driver.state()["facing"])
	if not _facing_textures(actor, action, facing).has(sprite.texture):
		var state: Dictionary = driver.state()
		return "texture is not a %s %s frame (driver %s %s frame %d)" % [facing, action, state["action"], state["facing"], state["frame"]]
	return ""


# Mutate one property, require the same predicate used by the positive checks to reject it, then restore and re-accept.
func _negative(name: String, target: Object, property: String, wrong, predicate: Callable) -> bool:
	var saved = target.get(property)
	target.set(property, wrong)
	var reason: String = predicate.call()
	target.set(property, saved)
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
		if not _check(_geometry_problem(actor, true) == "" and _facing_problem(actor, pilot, actor_id, "idle", "south") == "", "hero entry geometry " + appearance + ": " + _geometry_problem(actor, true) + _facing_problem(actor, pilot, actor_id, "idle", "south")):
			return
		if not _check(LiangConfig.npc_attached(area) and _source_problem(npc, npc_driver, "liang-xu") == "", "active Liang source " + appearance + ": " + _source_problem(npc, npc_driver, "liang-xu")):
			return
		if not _check(_geometry_problem(npc, true) == "" and _facing_problem(npc, npc_driver, "liang-xu", "idle", "south") == "", "Liang geometry " + appearance + ": " + _geometry_problem(npc, true)):
			return
		# Negative controls through the same predicates: Liang's frame on the hero, a wrong-set driver.sprite_set that
		# keeps the expected set_id (shallow copy; Liang's own driver is untouched), legacy scale, legacy offset.
		var liang_idle: Texture2D = _expected("liang-xu")["clips"]["idle"]["south"][0]
		if not _negative("source", actor, "texture", liang_idle, _source_problem.bind(actor, pilot, actor_id)):
			return
		var same_id_wrong_set: Dictionary = npc_driver.sprite_set.duplicate()
		same_id_wrong_set["set_id"] = ACTIVE[actor_id]["set_id"]
		if not _negative("same_id_set", pilot, "sprite_set", same_id_wrong_set, _source_problem.bind(actor, pilot, actor_id)):
			return
		if pilot.get("breathing") != null:
			var foreign_breath: Dictionary = pilot.breathing.clips.duplicate(true)
			foreign_breath["south"]["textures"][1] = liang_idle
			if not _negative("breathing", pilot.breathing, "clips", foreign_breath, _source_problem.bind(actor, pilot, actor_id)):
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
			if not _check(actor.position != start and _facing_problem(actor, pilot, actor_id, "walk", facing) == "", "input starts walk " + appearance + " " + facing + ": " + _facing_problem(actor, pilot, actor_id, "walk", facing)):
				return
			# Short presses stay inside the open plaza (about 12 px south of spawn is a wall); every tick must move.
			for step in 3:
				var before := actor.position
				_tick(area)
				if not _check(actor.position.distance_to(before) > 0.05, "walk tick moves " + appearance + " " + facing):
					return
			if not _check(_facing_problem(actor, pilot, actor_id, "walk", facing) == "" and _geometry_problem(actor, false) == "", "walk continues " + appearance + " " + facing + ": " + _facing_problem(actor, pilot, actor_id, "walk", facing) + _geometry_problem(actor, false)):
				return
			if not _negative("direction", actor, "texture", _expected(actor_id)["clips"]["walk"][opposite[facing]][pilot.frame], _facing_problem.bind(actor, pilot, actor_id, "walk", facing)):
				return
			Input.action_release(actions[facing])
			for step in 30:
				_tick(area)
			if not _check(String(pilot.state()["action"]) == "idle" and _facing_problem(actor, pilot, actor_id, "idle", facing) == "", "release returns to idle " + appearance + " " + facing + ": " + _facing_problem(actor, pilot, actor_id, "idle", facing)):
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
