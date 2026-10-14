extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	change_scene_to_file("res://scenes/rpg-2-star-ocean-the-second_scifi-city_visual-preview_m8_20261013-231655-b47d801e.tscn")
	for frame in range(12):
		await process_frame
	var path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-city_in-engine-visual-sample_m8-v02_20261013-232003-7881fcaa.png"
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		quit(1)
		return
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	quit(0)
