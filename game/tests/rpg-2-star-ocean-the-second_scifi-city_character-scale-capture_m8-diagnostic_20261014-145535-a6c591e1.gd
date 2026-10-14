extends SceneTree

# Disposable visual diagnostic. It never changes production scene or art files.
const OUTPUT_DIR := "res://../outputs"
const CAPTURE_STAMP := "20261014-145535"
const SOURCE := {
	"male": "res://assets/characters/rpg-2-star-ocean-the-second_protagonist-male_exploration-cutout_m8-sample_20261013-231655-70b1e89d.png",
	"female": "res://assets/characters/rpg-2-star-ocean-the-second_protagonist-female_exploration-cutout_m8-sample_20261013-233258-e2c0419a.png",
	"liang-xu": "res://assets/characters/rpg-2-star-ocean-the-second_liang-xu_exploration-cutout_m8-sample_20261013-231655-2f45a173.png",
}
# Approximate head/boot rows of the source-art *figure*, excluding soft vignette.
const SOURCE_FIGURE_ROWS := {
	"male": Vector2i(70, 1480),
	"female": Vector2i(90, 1470),
	"liang-xu": Vector2i(45, 1480),
}
const CAPTURE_IDS := {
	"male-native": "a6c59101",
	"female-native": "a6c59102",
	"liang-xu-native": "a6c59103",
	"male-source-60": "a6c59104",
	"male-source-72": "a6c59105",
	"male-source-80": "a6c59106",
	"female-source-60": "a6c59107",
	"female-source-72": "a6c59108",
	"female-source-80": "a6c59109",
	"liang-xu-source-60": "a6c5910a",
	"liang-xu-source-72": "a6c5910b",
	"liang-xu-source-80": "a6c5910c",
}

var captures: Array[Dictionary] = []


func _initialize() -> void:
	call_deferred("_run")


func _capture(character: String, variant: String, actor: Sprite2D) -> bool:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.get_size() != Vector2i(640, 360):
		push_error("Expected actual 640x360 viewport for " + character + " " + variant)
		return false
	var key := character + "-" + variant
	var filename := "rpg-2-star-ocean-the-second_scifi-city_character-scale-%s_m8-diagnostic_%s-%s.png" % [key, CAPTURE_STAMP, CAPTURE_IDS[key]]
	var path := ProjectSettings.globalize_path(OUTPUT_DIR).path_join(filename)
	if image.save_png(path) != OK:
		push_error("Could not save " + path)
		return false
	print("CAPTURED " + path)
	captures.append({
		"character": character,
		"variant": variant,
		"filename": filename,
		"viewport": [640, 360],
		"texture_size": [int(actor.texture.get_width()), int(actor.texture.get_height())],
		"scale": actor.scale.x,
		"filter": "nearest" if variant == "native" else "linear",
	})
	return true


func _run() -> void:
	var output_path := ProjectSettings.globalize_path(OUTPUT_DIR)
	DirAccess.make_dir_recursive_absolute(output_path)
	SaveStore.root_path = "user://test-saves/m8-character-scale"
	var app: Node = root.get_node("AppState")
	for character in ["male", "female", "liang-xu"]:
		app.begin_new_run()
		app.hero_appearance = "female" if character == "female" else "male"
		app.select_destination("scifi.city")
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await process_frame
		await process_frame
		var area: Node2D = current_scene
		area.set_process(false)
		var hero: Sprite2D = area.get("hero")
		var city_npc: Sprite2D = area.get("city_npc")
		var actor: Sprite2D = city_npc if character == "liang-xu" else hero
		hero.visible = character != "liang-xu"
		city_npc.visible = character == "liang-xu"
		area.get("npc_label").visible = false
		area.get("city_hero_silhouette").visible = false
		actor.position = Vector2(340, 253)
		actor.z_index = 253
		if not await _capture(character, "native", actor):
			quit(1)
			return
		var source: Texture2D = load(SOURCE[character])
		var rows: Vector2i = SOURCE_FIGURE_ROWS[character]
		var source_image := source.get_image()
		print("SOURCE_ALPHA ", character, " corners=", source_image.get_pixel(0, 0).a, ",", source_image.get_pixel(1023, 0).a, ",", source_image.get_pixel(0, 1535).a, ",", source_image.get_pixel(1023, 1535).a, " center=", source_image.get_pixel(512, 768).a)
		actor.texture = source
		actor.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		actor.offset = Vector2(0, source.get_height() * 0.5 - rows.y)
		for target_height in [60, 72, 80]:
			actor.scale = Vector2.ONE * (float(target_height) / float(rows.y - rows.x))
			if not await _capture(character, "source-" + str(target_height), actor):
				quit(1)
				return
	var filename := "rpg-2-star-ocean-the-second_scifi-city_character-scale-manifest_m8-diagnostic_%s-a6c591ed.json" % CAPTURE_STAMP
	var manifest_path := output_path.path_join(filename)
	var file := FileAccess.open(manifest_path, FileAccess.WRITE)
	if file == null:
		push_error("Could not save manifest")
		quit(1)
		return
	file.store_string(JSON.stringify({"status": "diagnostic only; not approved art", "captures": captures}, "\t"))
	file.close()
	print("MANIFEST " + manifest_path)
	quit(0)
