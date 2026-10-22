extends RefCounted

# NYC City Hall Park scene candidate v06 (UNAPPROVED; scene art not accepted).
# Opt-in only: launch with `-- --city-hall-park-v06`, or set enabled_override = 1
# before the city scene loads. Off by default, so the existing city plate and
# its tests stay unchanged; v05 (city_hall_park_scene.gd) stays as the audit baseline.
# Most visible pixels are a palette-reduced recomposition of an imported AI-generated
# nonruntime reference, plus native layers (walks, fixtures, collision, occluders).
# Scene data ships as a .tres resource so exported builds include it.

const RUN_DIR := "res://assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/"
const SCENE_RES := "rpg-2-star-ocean-the-second_nyc-city-hall-park_scene_unapproved-v06_20261017-165253-4519dffe.tres"
const SCENE_JSON := "rpg-2-star-ocean-the-second_nyc-city-hall-park_scene_unapproved-v06_20261017-165253-4519dffe.json"
const CLI_FLAG := "--city-hall-park-v06"
const SceneDefaults35 := preload("res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd")
const DEV_DIR_PREFIX := "--chp6-dir="
const SPAWN := Vector2(340, 253)
const SILHOUETTE_Z := 3000
const REVEAL_RATE := 6.0
const REVEAL_SHADER := """
shader_type canvas_item;
// Dithered reveal around the hero's body while she stands behind a crown (logical-pixel Bayer 4x4).
uniform vec2 hero_feet = vec2(-1000.0, -1000.0);
uniform float strength = 0.0;
uniform vec2 radius = vec2(15.0, 27.0);
uniform float lift = 22.0;
uniform float max_hole = 0.85;
varying vec2 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

void fragment() {
	vec4 color = texture(TEXTURE, UV);
	vec2 p = floor(world_pos);
	float d = length((p + 0.5 - (hero_feet - vec2(0.0, lift))) / radius);
	float t = strength * (1.0 - clamp((d - 0.75) / 0.25, 0.0, 1.0));
	const float BAYER[16] = float[16](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	int ix = int(mod(p.x, 4.0));
	int iy = int(mod(p.y, 4.0));
	if (BAYER[iy * 4 + ix] / 16.0 < t * max_hole) {
		color.a = 0.0;
	}
	COLOR = color;
}
"""

static var enabled_override := -1

var data: Dictionary = {}
var walk_mask: Image
var canopy_layers: Array[Dictionary] = []
var nodes: Array[Sprite2D] = []
var legacy: Array[Dictionary] = []
var source_dir := ""
var host_node: Node2D
var reveal_driver: Node


static func enabled() -> bool:
	if enabled_override >= 0:
		return enabled_override == 1
	if OS.get_cmdline_user_args().has(CLI_FLAG):
		return true
	# MVP default fallback (sdef35 policy; false until the creator authorizes it).
	return SceneDefaults35.default_on(SceneDefaults35.CITY)


static func dev_dir() -> String:
	# Test/preview only: load PNGs and scene JSON from an absolute directory without importing them.
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(DEV_DIR_PREFIX):
			return argument.trim_prefix(DEV_DIR_PREFIX)
	return ""


func load_scene() -> bool:
	source_dir = dev_dir()
	var json_text := ""
	if source_dir.is_empty():
		var resource: Resource = load(RUN_DIR + SCENE_RES)
		if resource != null and resource.has_meta("scene_json"):
			json_text = resource.get_meta("scene_json")
	else:
		json_text = FileAccess.get_file_as_string(source_dir.path_join(SCENE_JSON))
	var parsed = JSON.parse_string(json_text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("City Hall Park v06 scene data missing")
		return false
	data = parsed
	walk_mask = _image(data["walkmask"])
	if walk_mask == null or walk_mask.get_size() != Vector2i(640, 360):
		push_error("City Hall Park v06 walk mask missing")
		return false
	for entry in data.get("legacy_positions", []):
		var from: Array = entry["from"]
		var to: Array = entry["to"]
		legacy.append({"from": Vector2(from[0], from[1]), "to": Vector2(to[0], to[1])})
	return true


func _image(file_name: String) -> Image:
	if source_dir.is_empty():
		var texture: Texture2D = load(RUN_DIR + file_name)
		return texture.get_image() if texture != null else null
	return Image.load_from_file(source_dir.path_join(file_name))


func _texture(file_name: String) -> Texture2D:
	if source_dir.is_empty():
		return load(RUN_DIR + file_name)
	return ImageTexture.create_from_image(Image.load_from_file(source_dir.path_join(file_name)))


func build_nodes(host: Node2D) -> void:
	host_node = host
	_add_layer(host, data["base"], -100)
	var reveal: Dictionary = data.get("canopy_reveal", {})
	for entry in data["ysort"]:
		var sprite := _add_layer(host, entry["png"], int(entry["pivot"]))
		sprite.name = "CityHallParkV06_" + String(entry["name"]).replace("-", "_")
		if entry.get("canopy", false):
			var shader := Shader.new()
			shader.code = REVEAL_SHADER
			var material := ShaderMaterial.new()
			material.shader = shader
			if reveal.has("radius"):
				material.set_shader_parameter("radius", Vector2(reveal["radius"][0], reveal["radius"][1]))
				material.set_shader_parameter("lift", float(reveal["lift"]))
				material.set_shader_parameter("max_hole", float(reveal["max_hole"]))
			sprite.material = material
			canopy_layers.append({"pivot": int(entry["pivot"]), "image": _image(entry["png"]), "sprite": sprite,
				"material": material, "strength": 0.0})
	reveal_driver = RevealDriver.new()
	reveal_driver.name = "CityHallParkV06Reveal"
	reveal_driver.park = self
	host.add_child(reveal_driver)


func _add_layer(host: Node2D, file_name: String, depth: int) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = _texture(file_name)
	sprite.centered = false
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.z_index = depth
	host.add_child(sprite)
	nodes.append(sprite)
	return sprite


func walkable(at: Vector2) -> bool:
	var x := int(round(at.x))
	var y := int(round(at.y))
	if x < 0 or y < 0 or x >= 640 or y >= 360:
		return false
	return walk_mask.get_pixel(x, y).a > 0.5


func safe_position(at: Vector2) -> Vector2:
	# Declared legacy migration first (data-driven, logged, never silent): old city saves that still
	# hold the pre-navigation generic spawn land where the old plate always put them.
	for entry in legacy:
		if at == entry["from"] and walkable(entry["to"]):
			print("CityHallPark v06: legacy city position %s migrated to %s" % [at, entry["to"]])
			return entry["to"]
	var start := Vector2(round(at.x), round(at.y))
	if walkable(start):
		return start
	# Nearest walkable foot position by expanding square rings; deterministic.
	for radius in range(1, 400):
		var best := Vector2.ZERO
		var best_distance := INF
		for dy in range(-radius, radius + 1):
			for dx in [-radius, radius]:
				var candidate := start + Vector2(dx, dy)
				if walkable(candidate) and candidate.distance_squared_to(start) < best_distance:
					best = candidate
					best_distance = candidate.distance_squared_to(start)
		for dx in range(-radius + 1, radius):
			for dy in [-radius, radius]:
				var candidate := start + Vector2(dx, dy)
				if walkable(candidate) and candidate.distance_squared_to(start) < best_distance:
					best = candidate
					best_distance = candidate.distance_squared_to(start)
		if best_distance < INF:
			return best
	return SPAWN


func slide_position(from: Vector2, to: Vector2) -> Vector2:
	# Same swept stepping as city_navigation.gd, against the mask.
	var position := from if walkable(from) else safe_position(from)
	var displacement := to - from
	var steps := maxi(1, ceili(displacement.length() / 2.0))
	var step := displacement / steps
	for index in steps:
		var candidate := position + step
		if walkable(candidate):
			position = candidate
		elif walkable(Vector2(candidate.x, position.y)):
			position.x = candidate.x
		elif walkable(Vector2(position.x, candidate.y)):
			position.y = candidate.y
	return position


func layer_cover(layer: Dictionary, at: Vector2) -> float:
	# Share of the 48-px hero body (feet anchor `at`) covered by this crown when it is drawn in front.
	if int(at.y) >= int(layer["pivot"]):
		return 0.0
	var image: Image = layer["image"]
	var total := 0
	var covered := 0
	for y in range(int(at.y) - 44, int(at.y) + 3, 2):
		for x in range(int(at.x) - 7, int(at.x) + 8, 2):
			if x < 0 or y < 0 or x >= 640 or y >= 360:
				continue
			total += 1
			if image.get_pixel(x, y).a > 0.5:
				covered += 1
	return 0.0 if total == 0 else float(covered) / float(total)


func canopy_cover(at: Vector2) -> float:
	var best := 0.0
	for layer in canopy_layers:
		best = maxf(best, layer_cover(layer, at))
	return best


func hidden_by_canopy(_at: Vector2) -> bool:
	# v06 never hides the hero: crowns open a dithered reveal instead of the old silhouette cue.
	return false


func update_reveal(at: Vector2, delta: float) -> void:
	for layer in canopy_layers:
		var target := 1.0 if layer_cover(layer, at) > 0.04 else 0.0
		layer["strength"] = move_toward(float(layer["strength"]), target, delta * REVEAL_RATE)
		var material: ShaderMaterial = layer["material"]
		material.set_shader_parameter("hero_feet", at)
		material.set_shader_parameter("strength", layer["strength"])


func reveal_strength(index := 0) -> float:
	return float(canopy_layers[index]["strength"]) if index < canopy_layers.size() else 0.0


class RevealDriver extends Node:
	var park

	func _process(delta: float) -> void:
		var host: Node2D = park.host_node
		if host == null or not is_instance_valid(host):
			return
		var hero = host.get("hero")
		if hero is Sprite2D and is_instance_valid(hero):
			park.update_reveal((hero as Sprite2D).position, delta)
