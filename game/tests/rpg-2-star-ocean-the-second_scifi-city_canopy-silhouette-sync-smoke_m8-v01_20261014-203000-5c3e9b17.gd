extends SceneTree

# The canopy silhouette must mirror the hero's current walk/idle frame, anchor,
# and facing while the hero is under the city canopy (walking, idle, all four
# facings, and while dialogue is open), using nearest filtering.
# The 32x48 hero frames are functional placeholders; this is not art approval.
const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const CityNavigation := preload("res://scripts/city_navigation.gd")
const STEP := 0.05


func _initialize() -> void:
	call_deferred("_run")


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, detail: String) -> bool:
	if condition:
		return true
	push_error("M8_CANOPY_SILHOUETTE_SYNC_FAILED: " + detail)
	quit(1)
	return false


func _in_sync(area: Node2D, detail: String) -> bool:
	var hero: Sprite2D = area.get("hero")
	var silhouette: Sprite2D = area.get("city_hero_silhouette")
	if not _check(silhouette.visible, detail + ": silhouette visible under canopy"):
		return false
	if not _check(silhouette.texture == hero.texture, detail + ": texture tracks hero"):
		return false
	if not _check(silhouette.position == hero.position and silhouette.offset == hero.offset and silhouette.scale == hero.scale and silhouette.flip_h == hero.flip_h, detail + ": anchor/scale/facing track hero"):
		return false
	return _check(silhouette.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, detail + ": nearest filter")


# Finds a canopy point with walkable room for the east walk, four turns and the
# dialogue approach, so every check happens while the hero is hidden.
func _canopy_start(canopy: PackedVector2Array) -> Vector2:
	for y in range(200, 260, 2):
		for x in range(40, 216, 2):
			var at := Vector2(x, y)
			var clear := true
			for probe in [at, at + Vector2(56, 0), at + Vector2(56, -14), at + Vector2(14, -14), at + Vector2(14, 0)]:
				if not Geometry2D.is_point_in_polygon(probe, canopy) or not CityNavigation.walkable(probe):
					clear = false
			if clear:
				return at
	return Vector2.INF


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m8-canopy-silhouette-sync"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	var area: Node2D = current_scene
	area.set_process(false)
	var hero: Sprite2D = area.get("hero")
	var character := "protagonist-" + str(app.hero_appearance)
	var start := _canopy_start(area.get("city_canopy").polygon)
	if not _check(start != Vector2.INF, "walkable canopy route exists"):
		return
	if not _check(hero.texture.get_size() == Vector2(32, 48), "hero uses 32x48 placeholder frames"):
		return
	hero.position = start

	Input.action_press("move_right")
	var walk_frames := {}
	for frame in 6:
		area._process(STEP)
		if not _in_sync(area, "walking east frame %d" % frame):
			return
		var phase: int = area.get("walk_phase")
		if not _check(phase > 0 and hero.texture == NativeMotion.texture_for(character, "walk", "east", phase), "walking east uses walk frame"):
			return
		walk_frames[hero.texture] = true
	Input.action_release("move_right")
	if not _check(walk_frames.size() >= 2, "silhouette followed multiple walk phases"):
		return

	area._process(STEP)
	if not _check(area.get("walk_phase") == 0 and hero.texture == NativeIdle.texture_for(character, "east"), "release resets to east idle"):
		return
	if not _in_sync(area, "idle reset"):
		return

	# Every facing change swaps the hero frame; the silhouette must follow each one.
	for turn in [["move_up", "north"], ["move_left", "west"], ["move_down", "south"], ["move_right", "east"]]:
		Input.action_press(turn[0])
		area._process(STEP)
		Input.action_release(turn[0])
		if not _check(area.get("city_facing") == turn[1], "turn faces " + turn[1]):
			return
		if not _check(hero.texture == NativeMotion.texture_for(character, "walk", turn[1], area.get("walk_phase")) and area.get("walk_phase") > 0, "turn uses %s walk frame" % turn[1]):
			return
		if not _in_sync(area, "turn " + turn[1]):
			return

	# Dialogue opened mid-stride: _process resets the hero to idle and skips movement.
	# The silhouette must drop the stale walk frame on that same tick.
	Input.action_press("move_left")
	area._process(STEP)
	area._process(STEP)
	if not _check(area.get("walk_phase") > 0 and area.get("city_facing") == "west", "walking west before dialogue"):
		Input.action_release("move_left")
		return
	var before_dialogue := hero.position
	area._open_dialogue()
	for frame in 2:
		area._process(STEP)
		if not _check(area.get("dialogue_open") and hero.position == before_dialogue, "dialogue holds the hero in place"):
			Input.action_release("move_left")
			return
		if not _check(area.get("walk_phase") == 0 and hero.texture == NativeIdle.texture_for(character, "west"), "dialogue resets to west idle"):
			Input.action_release("move_left")
			return
		if not _in_sync(area, "dialogue frame %d" % frame):
			Input.action_release("move_left")
			return
	area._close_dialogue()
	area._process(STEP)
	Input.action_release("move_left")
	if not _check(area.get("walk_phase") > 0, "walk resumes after dialogue"):
		return
	if not _in_sync(area, "after dialogue"):
		return
	print("M8_CANOPY_SILHOUETTE_SYNC_OK")
	quit(0)
