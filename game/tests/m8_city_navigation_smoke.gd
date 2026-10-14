extends SceneTree

const Navigation := preload("res://scripts/city_navigation.gd")


class BoundaryOverlay extends Node2D:
	func _draw() -> void:
		for polygon in Navigation.OBSTACLES:
			draw_colored_polygon(polygon, Color(1.0, 0.25, 0.1, 0.25))
			var outline: PackedVector2Array = polygon.duplicate()
			outline.append(polygon[0])
			draw_polyline(outline, Color(1.0, 0.5, 0.2, 0.9), 1.0)


func _capture_evidence() -> void:
	var directory := OS.get_environment("WB_CITY_EVIDENCE_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless":
		return
	DirAccess.make_dir_recursive_absolute(directory)
	var captures: Array[String] = []
	var app: Node = root.get_node("AppState")
	for appearance in ["male", "female"]:
		app.begin_new_run()
		app.hero_appearance = appearance
		app.language = "zh" if appearance == "male" else "en"
		app.select_destination("scifi.city")
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await process_frame
		await process_frame
		current_scene.set_process(false)
		var actor: Sprite2D = current_scene.get("hero")
		actor.position = Vector2(263, 255) if appearance == "male" else Vector2(444, 280)
		actor.z_index = int(actor.position.y)
		var overlay := BoundaryOverlay.new()
		overlay.z_index = 400
		current_scene.add_child(overlay)
		for diagnostic in [false, true]:
			overlay.visible = diagnostic
			await RenderingServer.frame_post_draw
			var timestamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
			var variant: String = appearance + ("-boundaries" if diagnostic else "-paving")
			var filename := "rpg-2-star-ocean-the-second_scifi-city_navigation-capture_m8-%s_%s-%08x.png" % [variant, timestamp, randi()]
			if root.get_texture().get_image().save_png(directory.path_join(filename)) == OK:
				captures.append(filename)
	var manifest := {"purpose": "Engine viewport evidence for candidate navigation geometry; boundary overlays are diagnostics", "artAccepted": false, "humanPlaytest": false, "canvas": [640, 360], "captures": captures}
	var file := FileAccess.open(directory.path_join("navigation-check-manifest.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(manifest, "\t") + "\n")


func _initialize() -> void:
	call_deferred("_run")


func _check(ok: bool, message: String) -> bool:
	if not ok:
		push_error("CITY_NAVIGATION_FAILED: " + message)
		quit(1)
	return ok


func _run() -> void:
	# Flood the pavement using the same swept movement as the game. Every
	# interaction must have an approach from spawn, including return visits.
	var reached := {Vector2i(340, 252): true}
	var pending: Array[Vector2i] = [Vector2i(340, 252)]
	var cursor := 0
	while cursor < pending.size():
		var cell := pending[cursor]
		cursor += 1
		for offset in [Vector2i(4, 0), Vector2i(-4, 0), Vector2i(0, 4), Vector2i(0, -4)]:
			var next: Vector2i = cell + offset
			if reached.has(next) or not Navigation.walkable(Vector2(next)):
				continue
			if Navigation.slide_position(Vector2(cell), Vector2(next)).is_equal_approx(Vector2(next)):
				reached[next] = true
				pending.append(next)
	for target in [Vector2(285, 267), Vector2(378, 181), Vector2(120, 187), Vector2(282, 180), Vector2(558, 166), Vector2(470, 247)]:
		var reachable := false
		for cell in reached:
			if Vector2(cell).distance_to(target) <= 6.0:
				reachable = true
				break
		if not _check(reachable, "reachable hotspot " + str(target)):
			return
	if not _check(Navigation.walkable(Vector2(32, 210)), "west paving no longer blocked by broad rectangle"):
		return
	if not _check(not Navigation.walkable(Vector2(120, 240)), "garden is solid"):
		return
	if not _check(not Navigation.walkable(Vector2(240, 232)), "lamp base is solid"):
		return
	if not _check(not Navigation.walkable(Vector2(470, 288)), "planter is solid"):
		return
	var stopped := Navigation.slide_position(Vector2(270, 232), Vector2(220, 232))
	if not _check(stopped.x > 246.0, "long frame cannot cross lamp base"):
		return
	var sliding := Navigation.slide_position(Vector2(252, 220), Vector2(232, 244))
	if not _check(Navigation.walkable(sliding) and sliding != Vector2(252, 220), "diagonal contact slides along an edge"):
		return
	# Recovery must stay stable on repeated scene loads, including geometry edges.
	for x in range(-20, 661, 20):
		for y in range(120, 341, 10):
			var original := Vector2(x, y)
			var repaired := Navigation.safe_position(original)
			if not _check(Navigation.walkable(repaired), "safe recovery " + str(original)):
				return
			if not _check(Navigation.safe_position(repaired) == repaired, "stable repeated recovery"):
				return
			if Navigation.walkable(original) and not _check(original == repaired, "preserve valid position"):
				return
	await _capture_evidence()
	print("M8_CITY_NAVIGATION_OK: all hotspots connected, swept collision, edge sliding, save recovery")
	quit(0)
