extends SceneTree


const CITY := "res://assets/environments/rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png"
const SPRITE_PREFIX := "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-"
const SPRITE_SUFFIX := "_m8-v03_20261014-175132-"
const CAPTURE_PREFIX := "res://../outputs/rpg-2-star-ocean-the-second_liang-xu_native-game-preview-"
const ART_IDS := {"south": "e17b4c09", "west": "b52910e1", "north": "c742d602", "east": "d853a711"}
const CAPTURE_IDS := {"south": "f3128e01", "west": "f3128e02", "north": "f3128e03", "east": "f3128e04"}


func _initialize() -> void:
	call_deferred("_capture_all")


func _capture_all() -> void:
	var stage := Node2D.new()
	root.add_child(stage)
	var city := Sprite2D.new()
	city.texture = load(CITY)
	city.position = Vector2(320, 180)
	city.scale = Vector2(640.0 / 1672.0, 360.0 / 941.0)
	stage.add_child(city)
	var sprite := Sprite2D.new()
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	# Center of 32x48 art is 20 pixels above its (16,44) foot anchor.
	sprite.position = Vector2(320, 226 - 20)
	stage.add_child(sprite)
	for direction in ["south", "west", "north", "east"]:
		var name: String = str(direction)
		sprite.texture = load(SPRITE_PREFIX + name + SPRITE_SUFFIX + str(ART_IDS[name]) + ".png")
		await process_frame
		await process_frame
		var path: String = CAPTURE_PREFIX + name + "_m8-v03_20261014-180100-" + str(CAPTURE_IDS[name]) + ".png"
		var image := root.get_viewport().get_texture().get_image()
		if image == null or image.save_png(path) != OK:
			push_error("Capture failed: " + path)
			quit(1)
			return
		print("CAPTURED " + ProjectSettings.globalize_path(path))
	quit(0)
