extends SceneTree

# Standalone visual review only. Does not change the playable protagonist.
const HERO := preload("res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-male_high-fidelity-south-exploration_m8-concept_20261014-185706-6bbf80c1.png")
const CITY := preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png")


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var canvas := Control.new()
	canvas.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(canvas)
	var background := Sprite2D.new()
	background.texture = CITY
	background.position = Vector2.ZERO
	background.centered = false
	background.scale = Vector2(640.0 / CITY.get_width(), 360.0 / CITY.get_height())
	background.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	canvas.add_child(background)
	var hero := Sprite2D.new()
	hero.texture = HERO
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.centered = true
	hero.scale = Vector2(0.05, 0.05)
	hero.position = Vector2(320, 205)
	canvas.add_child(hero)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var frame := root.get_texture().get_image()
	if frame.get_size() != Vector2i(640, 360):
		push_error("HIGH_FIDELITY_SCALE_CHECK_FAILED: viewport is not 640x360")
		quit(1)
		return
	var output := OS.get_environment("WB_HIGH_FIDELITY_PREVIEW")
	if output.is_empty():
		push_error("HIGH_FIDELITY_SCALE_CHECK_FAILED: output path missing")
		quit(1)
		return
	if frame.save_png(output) != OK:
		push_error("HIGH_FIDELITY_SCALE_CHECK_FAILED: screenshot save failed")
		quit(1)
		return
	print("HIGH_FIDELITY_CITY_SCALE_OK size=640x360 figure~70px center=320,205 path=" + output)
	quit(0)
