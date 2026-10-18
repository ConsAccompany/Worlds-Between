extends SceneTree
# Source-only test injection. No scene/default changes, no character or animation approval.
const WEST := "res://../outputs/female-west-static-v01/rpg-2-star-ocean-the-second_protagonist-female_west-static_unapproved-v01_20261018-174421-618816ac.png"
const SOUTH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const SOUTH_SHA := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
var app: Node
var folder := ""
var stamp := ""
var checks := 0
var records := []
func _initialize() -> void:call_deferred("_run")
func _check(ok: bool, text: String) -> bool:
	if not ok:
		push_error("FEMALE_WEST FAIL " + text)
		quit(1)
		return false
	checks += 1
	print("PASS " + text)
	return true
func _bounds(image: Image) -> Rect2i:
	var low := Vector2i(image.get_size())
	var high := Vector2i(-1, -1)
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x, y).a8 == 255:
				low = Vector2i(mini(low.x, x), mini(low.y, y))
				high = Vector2i(maxi(high.x, x), maxi(high.y, y))
	return Rect2i(low, high - low + Vector2i.ONE)
func _difference(a: Image, b: Image) -> Rect2i:
	var low := Vector2i(a.get_size())
	var high := Vector2i(-1, -1)
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				low = Vector2i(mini(low.x, x), mini(low.y, y))
				high = Vector2i(maxi(high.x, x), maxi(high.y, y))
	return Rect2i(low, high - low + Vector2i.ONE)
func _grab() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	return image
func _run() -> void:
	app = root.get_node("AppState")
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-") + "-%08x" % (randi() & 0xffffffff)
	DirAccess.make_dir_recursive_absolute(folder)
	SaveStore.root_path = "user://test-saves/female-west-static"
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	if not _check(app.settings.load_status == "missing" and FileAccess.get_sha256(SOUTH) == SOUTH_SHA, "fresh isolated profile and unchanged approved v8 source"):
		return
	var source := Image.load_from_file(ProjectSettings.globalize_path(WEST))
	var approved := Image.load_from_file(ProjectSettings.globalize_path(SOUTH))
	if not _check(source != null and source.get_size() == Vector2i(80, 112) and _bounds(source) == Rect2i(24, 8, 35, 96), "west source80x112, distinct profile bounds35x96"):
		return
	for scene in ["city-bright", "annex-room2-dark"]:
		for language in ["zh", "en"]:
			app.begin_new_run()
			app.hero_appearance = "female"
			app.language = language
			app.select_destination("scifi.city")
			app.current_annex_room = 2
			var path := "res://scenes/scifi_exploration_area.tscn" if scene == "city-bright" else "res://scenes/survey_annex.tscn"
			var host: Node2D = load(path).instantiate()
			root.add_child(host)
			current_scene = host
			await process_frame
			await process_frame
			host.set_process(false)
			var hero: Sprite2D = host.hero
			var original := hero.texture.get_image()
			var old_bounds := _bounds(original)
			var floor_y: float = hero.position.y + hero.offset.y - original.get_height() * 0.5 + old_bounds.end.y
			hero.visible = false
			var sprite := Sprite2D.new()
			sprite.centered = false
			sprite.offset = Vector2(-40, -104)
			sprite.position = Vector2(hero.position.x, floor_y)
			sprite.scale = Vector2(0.5, 0.5)
			sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			sprite.z_index = int(floor_y)
			host.add_child(sprite)
			for variant in ["west640", "west1280", "approved-south-reference640"]:
				var window := Vector2i(1280, 720) if variant == "west1280" else Vector2i(640, 360)
				root.size = window
				sprite.visible = false
				var background := await _grab()
				var image := approved if variant == "approved-south-reference640" else source
				sprite.texture = ImageTexture.create_from_image(image)
				sprite.visible = true
				var capture := await _grab()
				var diff := _difference(background, capture)
				var exact := 0
				var opaque := 0
				if variant == "west1280":
					var bound := _bounds(source)
					for y in bound.size.y:
						for x in bound.size.x:
							var texel := source.get_pixel(bound.position.x + x, bound.position.y + y)
							if texel.a8 == 255:
								opaque += 1
								if capture.get_pixel(diff.position.x + x, diff.position.y + y) == texel:
									exact += 1
					if not _check(diff.size == Vector2i(35, 96) and exact == opaque and opaque == 2273, "%s/%s actual2x view shows all2273 source texels exactly" % [scene, language]):
						return
				else:
					if not _check(capture.get_size() == window and diff.size.y == 48 and diff.end.y == int(floor_y) and not hero.visible, "%s/%s/%s native48px body, sharedfloorpin, placeholderhidden" % [scene, language, variant]):
						return
				var filename := "rpg-2-star-ocean-the-second_protagonist-female_west-static-%s-%s-%s_test-only-v01_%s.png" % [scene, language, variant, stamp]
				var file := folder.path_join(filename)
				capture.save_png(file)
				records.append({"file": filename, "sha256": FileAccess.get_sha256(file), "scene": scene, "language": language, "variant": variant, "window": [window.x, window.y], "bodyHeight": diff.size.y, "exactTexels": exact, "opaqueTexels": opaque, "floorY": floor_y})
			host.queue_free()
			await process_frame
	var report := {"task": "content.char.protagonist-female.static-west", "checks": checks, "canvas": [640, 360], "sourceSha256": FileAccess.get_sha256(WEST), "approvedSouthSha256": SOUTH_SHA, "sourceOnlyTestInjection": true, "artApproved": false, "motionApproved": false, "captures": records}
	var file := FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_protagonist-female_west-static-capture-report_test-only-v01_%s.json" % stamp), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	print("FEMALE_WEST_CAPTURE PASS checks=%d captures=%d" % [checks, records.size()])
	quit(0)
