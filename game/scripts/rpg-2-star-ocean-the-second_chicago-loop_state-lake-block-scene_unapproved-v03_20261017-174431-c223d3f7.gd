extends Node2D

# Chicago Loop: one walkable arrival block at State St and Lake St, under the 1895 Lake Street
# elevated (State/Lake station). Native 640x360 scene candidate v03 (UNAPPROVED, art not accepted),
# opt-in only: the runtime Loop scene keeps v02 unless launched with `-- --chicago-state-lake-v03`
# (see the opt-in selector script). Art from
# tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v03_20261017-174431-c223d3f7.py,
# whose geometry must match the constants below: an underpainted facade and storefront backdrop
# plus an authored deck girder, ground, L columns, stair and props. The intersection, the pedestrian
# Lake St plaza, the medallion, the stair and the terrace are art-pilot choices, not canon. Walking
# here never advances the calendar. Travel time is charged only when the party leaves through the
# world map. The three sites only show notes: there is no survey, recruit, trace or battle, and the
# scene is never added to areas_visited, so the three-place demo goal is unchanged.

const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const MOVE_SPEED := 140.0
const ART := "res://assets/environments/chicago-loop-state-lake-v03/rpg-2-star-ocean-the-second_chicago-loop_state-lake_%s_unapproved-v03_20261017-174431-c223d3f7.png"
const GROUND := "ground-far"
const YSORT_LAYERS := ["ysort-underdeck-props", "ysort-l-columns", "ysort-station-stair-east", "ysort-plaza-props", "ysort-foreground"]
# Each y-sort prop is a region of its layer, drawn over the hero only while her feet are north of
# (above) the pivot row: [layer, Rect2 region, pivot row].
const YSORT_PROPS := [
	["ysort-underdeck-props", Rect2(80, 128, 19, 55), 182.5],
	["ysort-underdeck-props", Rect2(214, 153, 40, 33), 185.5],
	["ysort-underdeck-props", Rect2(258, 172, 43, 16), 186.5],
	["ysort-underdeck-props", Rect2(304, 158, 14, 26), 184.5],
	["ysort-underdeck-props", Rect2(364, 156, 22, 29), 184.5],
	["ysort-underdeck-props", Rect2(397, 171, 16, 21), 190.5],
	["ysort-underdeck-props", Rect2(419, 147, 26, 54), 200.5],
	["ysort-underdeck-props", Rect2(498, 140, 26, 48), 187.5],
	["ysort-l-columns", Rect2(102, 135, 77, 129), 263.5],
	["ysort-l-columns", Rect2(436, 135, 77, 129), 263.5],
	["ysort-station-stair-east", Rect2(540, 130, 68, 77), 206.5],
	["ysort-station-stair-east", Rect2(608, 128, 32, 136), 263.5],
	["ysort-plaza-props", Rect2(566, 256, 74, 42), 297.5],
	["ysort-plaza-props", Rect2(100, 235, 22, 26), 261.5],
	["ysort-plaza-props", Rect2(488, 236, 22, 25), 261.5],
	["ysort-plaza-props", Rect2(89, 206, 3, 8), 213.5],
	["ysort-plaza-props", Rect2(89, 218, 3, 8), 225.5],
	["ysort-plaza-props", Rect2(89, 246, 3, 8), 253.5],
	["ysort-plaza-props", Rect2(89, 258, 3, 8), 265.5],
	["ysort-plaza-props", Rect2(235, 194, 10, 39), 232.5],
	["ysort-plaza-props", Rect2(232, 252, 30, 15), 265.5],
	["ysort-plaza-props", Rect2(372, 252, 30, 15), 265.5],
	["ysort-plaza-props", Rect2(171, 220, 54, 72), 293.5],
	["ysort-plaza-props", Rect2(406, 220, 53, 72), 293.5],
	["ysort-plaza-props", Rect2(324, 272, 80, 25), 297.5],
	["ysort-foreground", Rect2(96, 252, 464, 70), 340.5],
]
# Hero feet positions where y-sort props would hide more than half of her: the props drawn over her
# there open a dithered window around her body (same technique as the NYC v06 candidate).
const REVEAL_MASK := "occlusion-reveal-mask"
const REVEAL_RATE := 6.0
const REVEAL_SHADER := """
shader_type canvas_item;
// Dithered reveal around the hero's body while she stands behind a tall prop (logical-pixel Bayer 4x4).
uniform vec2 hero_feet = vec2(-1000.0, -1000.0);
uniform float strength = 0.0;
uniform vec2 radius = vec2(15.0, 26.0);
uniform float lift = 21.0;
uniform float max_hole = 0.8;
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
# Walkable ground: the pedestrian Lake St plaza under and south of the L, and the State St roadway
# and crosswalk, minus every prop footprint, the stair and newel posts, the east terrace and fountain.
const WALK := Rect2(8, 178, 624, 120)
const BLOCKS := [
	Rect2(258, 181, 42, 6), Rect2(419, 189, 26, 12), Rect2(397, 182, 14, 9),
	Rect2(83, 178, 11, 5), Rect2(214, 178, 40, 8), Rect2(304, 178, 14, 7), Rect2(364, 178, 22, 7), Rect2(498, 180, 26, 8),
	Rect2(126, 250, 28, 14), Rect2(460, 250, 28, 14), Rect2(100, 251, 22, 11), Rect2(488, 251, 22, 11),
	Rect2(236, 228, 8, 5), Rect2(232, 258, 28, 8), Rect2(372, 258, 28, 8),
	Rect2(191, 285, 15, 9), Rect2(425, 285, 15, 9), Rect2(324, 288, 80, 10),
	Rect2(89, 212, 3, 2), Rect2(89, 224, 3, 2), Rect2(89, 252, 3, 2), Rect2(89, 264, 3, 2),
	Rect2(540, 178, 68, 29), Rect2(608, 178, 32, 86), Rect2(566, 264, 74, 34),
]
const WALK_TOP := 178.0
const DECK_BOTTOM := 134.0
# Arrival on the Lake St plaza south of the L, looking north to the station.
const SPAWN := Vector2(320, 286)
const KIOSK := Vector2(432, 214)
const KIOSK_RADIUS := 26.0
# Three read-only sites: the v02 info kiosk, the station stair and the wayfinding pylon.
const SITES := [["kiosk", Vector2(432, 214)], ["stair", Vector2(574, 214)], ["pylon", Vector2(240, 240)]]
# Real names stay in English on both language settings. The plaza lies east of State St (E Lake St).
const STREET_LABELS := [["E Lake St · 200 N", Vector2(150, 187)], ["N State St · 0 E/W", Vector2(4, 283)], ["State/Lake", Vector2(309, 110)]]
const SITE_TEXT := {
	"kiosk": {
		"zh": "环线信息屏 · State St 与 Lake St 路口：头顶是 1895 年建成的湖街高架线（State/Lake 站）。State St 是门牌东西零线，Lake St 位于北 200 号。前往其他城市请回世界地图。",
		"en": "Loop info board · State St & Lake St: overhead runs the 1895 Lake Street elevated (State/Lake station). State St is the 0 E/W address line; Lake St is 200 N. For other cities, use the world map.",
	},
	"stair": {
		"zh": "站台楼梯 · 通往 State/Lake 站的高架站台。本演示不能乘坐高架列车；前往其他城市请使用世界地图。",
		"en": "Station stair · up to the State/Lake elevated platform. Riding the L is not part of this demo; to travel to other cities, use the world map.",
	},
	"pylon": {
		"zh": "环线导视柱 · 环线高架由棕、绿、橙、粉、紫五条线共用。你在 State St 与 Lake St 路口，环线北侧。",
		"en": "Loop wayfinding pylon · the elevated Loop is shared by the Brown, Green, Orange, Pink and Purple lines. You are at State St & Lake St, on the north side of the Loop.",
	},
}

var hero: Sprite2D
var facing := "south"
var walk_time := 0.0
var walk_phase := 0
var title_label: Label
var hint_label: Label
var badge_label: Label
var note_label: Label
var help_label: Label
var back_button: Button
var save_button: Button
var info_panel: ColorRect
var info_label: Label
var street_labels: Array[Label] = []
var active_site := ""
var prop_sprites: Array[Sprite2D] = []
var reveal_mask: Image
var reveal_strength := 0.0


func _ready() -> void:
	AppState.record_playtest_event("location", "scifi.loop")
	var ground := Sprite2D.new()
	ground.texture = load(ART % GROUND)
	ground.centered = false
	ground.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(ground)
	var sorted := Node2D.new()
	sorted.y_sort_enabled = true
	add_child(sorted)
	var shader := Shader.new()
	shader.code = REVEAL_SHADER
	var textures := {}
	for layer in YSORT_LAYERS:
		textures[layer] = load(ART % layer)
	for entry in YSORT_PROPS:
		var region: Rect2 = entry[1]
		var sprite := Sprite2D.new()
		sprite.texture = textures[entry[0]]
		sprite.region_enabled = true
		sprite.region_rect = region
		sprite.centered = false
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		sprite.position = Vector2(region.position.x, entry[2])
		sprite.offset = Vector2(0, region.position.y - float(entry[2]))
		var material := ShaderMaterial.new()
		material.shader = shader
		sprite.material = material
		sorted.add_child(sprite)
		prop_sprites.append(sprite)
	reveal_mask = (load(ART % REVEAL_MASK) as Texture2D).get_image()
	hero = Sprite2D.new()
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, facing)
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.offset = Vector2(0, -20)
	hero.position = SPAWN
	if AppState.resume_area_pending:
		hero.position = safe_position(AppState.resume_area_position)
		AppState.resume_area_pending = false
	sorted.add_child(hero)
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	_update_reveal(1.0)


static func walkable(at: Vector2) -> bool:
	if not WALK.has_point(at):
		return false
	for block in BLOCKS:
		if block.has_point(at):
			return false
	return true


# Nearest walkable spot, so a resumed save (including old street-grid saves) never starts in scenery.
static func safe_position(at: Vector2) -> Vector2:
	if walkable(at):
		return at
	for radius in range(2, 400, 2):
		for step in 32:
			var angle := TAU * float(step) / 32.0
			var candidate := (at + Vector2(cos(angle), sin(angle)) * float(radius)).round()
			if walkable(candidate):
				return candidate
	return SPAWN


# Full move, else slide along one axis.
static func slide_position(from: Vector2, to: Vector2) -> Vector2:
	if walkable(to):
		return to
	if walkable(Vector2(to.x, from.y)):
		return Vector2(to.x, from.y)
	if walkable(Vector2(from.x, to.y)):
		return Vector2(from.x, to.y)
	return from


static func site_at(at: Vector2) -> String:
	var best := ""
	var best_distance := KIOSK_RADIUS
	for site in SITES:
		var distance: float = at.distance_to(site[1])
		if distance <= best_distance:
			best = site[0]
			best_distance = distance
	return best


func needs_reveal(at: Vector2) -> bool:
	var p := Vector2i(at.round())
	if p.x < 0 or p.y < 0 or p.x >= reveal_mask.get_width() or p.y >= reveal_mask.get_height():
		return false
	return reveal_mask.get_pixelv(p).r > 0.5


func _update_reveal(delta: float) -> void:
	var target := 1.0 if needs_reveal(hero.position) else 0.0
	reveal_strength = move_toward(reveal_strength, target, REVEAL_RATE * delta)
	for sprite in prop_sprites:
		# Only props drawn over the hero open the window; props behind her never get holes.
		var over := sprite.position.y > hero.position.y
		var material := sprite.material as ShaderMaterial
		material.set_shader_parameter("hero_feet", hero.position)
		material.set_shader_parameter("strength", reveal_strength if over else 0.0)


func _process(delta: float) -> void:
	if info_panel.visible and site_at(hero.position) != active_site and hero.position.distance_to(_site_point(active_site)) > KIOSK_RADIUS + 8.0:
		info_panel.visible = false
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if direction == Vector2.ZERO:
		_reset_walk_animation()
		_update_reveal(delta)
		return
	_set_facing(direction)
	var previous := hero.position
	hero.position = slide_position(hero.position, hero.position + direction * MOVE_SPEED * delta)
	if hero.position.distance_to(previous) > 0.05:
		_update_walk_animation(delta)
	else:
		_reset_walk_animation()
	_update_reveal(delta)


func _site_point(id: String) -> Vector2:
	for site in SITES:
		if site[0] == id:
			return site[1]
	return KIOSK


func _set_facing(direction: Vector2) -> void:
	var next := "east" if direction.x > 0.0 else "west"
	if absf(direction.y) >= absf(direction.x):
		next = "south" if direction.y > 0.0 else "north"
	if next == facing:
		return
	facing = next
	walk_time = 0.0
	walk_phase = 0
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, facing)


func _update_walk_animation(delta: float) -> void:
	walk_time += delta
	var next_phase := int(floor(walk_time / 0.12)) % 4 + 1
	if next_phase == walk_phase:
		return
	walk_phase = next_phase
	hero.texture = NativeMotion.texture_for("protagonist-" + AppState.hero_appearance, "walk", facing, walk_phase)


func _reset_walk_animation() -> void:
	if walk_phase == 0:
		return
	walk_time = 0.0
	walk_phase = 0
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, facing)


func _build_ui() -> void:
	for street in STREET_LABELS:
		var label := _label(self, street[1], 8, Color("#d7e4e0"))
		label.text = String(street[0])
		# Painted on the ground: drawn before the y-sort node, so the hero and props pass over it.
		move_child(label, 1)
		street_labels.append(label)
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 62)
	canvas.add_child(header)
	title_label = _label(canvas, Vector2(18, 5), 18, Color("#f0f8f4"))
	hint_label = _label(canvas, Vector2(18, 33), 11, Color("#acc8c8"))
	badge_label = _label(canvas, Vector2(250, 9), 10, Color("#ffd28a"))
	back_button = Button.new()
	back_button.name = "BackButton"
	back_button.position = Vector2(525, 12)
	back_button.size = Vector2(98, 38)
	back_button.pressed.connect(_return_to_map)
	canvas.add_child(back_button)
	save_button = Button.new()
	save_button.name = "SaveButton"
	save_button.position = Vector2(418, 12)
	save_button.size = Vector2(98, 38)
	save_button.pressed.connect(_open_save)
	canvas.add_child(save_button)
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 318)
	footer.size = Vector2(640, 42)
	canvas.add_child(footer)
	note_label = _label(canvas, Vector2(18, 321), 10, Color("#e7cf9c"))
	help_label = _label(canvas, Vector2(18, 340), 10, Color("#9dbab9"))
	info_panel = ColorRect.new()
	info_panel.color = Color(0.051, 0.09, 0.137, 0.94)
	info_panel.position = Vector2(96, 68)
	info_panel.size = Vector2(448, 60)
	info_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	info_panel.visible = false
	canvas.add_child(info_panel)
	info_label = _label(info_panel, Vector2(10, 6), 10, Color("#c8f0e6"))
	info_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	info_label.size = Vector2(428, 48)


func _refresh_text() -> void:
	title_label.text = AppState.destination_name("scifi.loop")
	hint_label.text = AppState.text_for("area_loop_hint")
	badge_label.text = AppState.text_for("loop_placeholder_badge")
	note_label.text = AppState.text_for("loop_street_note")
	help_label.text = AppState.text_for("loop_walk_note") + " · " + AppState.text_for("area_help")
	back_button.text = AppState.text_for("area_back")
	save_button.text = AppState.text_for("save_open")
	info_label.text = SITE_TEXT[active_site if active_site != "" else "kiosk"]["en" if AppState.language == "en" else "zh"]
	_place_badge()


# The badge sits right after the title so it never runs under the Save button; when the title is too
# long it moves to the hint row, after the hint.
func _place_badge() -> void:
	var limit := save_button.position.x - 8.0
	var badge_width := badge_label.get_minimum_size().x
	var after_title := title_label.position.x + title_label.get_minimum_size().x + 14.0
	if after_title + badge_width <= limit:
		badge_label.position = Vector2(after_title, 9.0)
	else:
		badge_label.position = Vector2(hint_label.position.x + hint_label.get_minimum_size().x + 14.0, hint_label.position.y)


func _label(parent: Node, at: Vector2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = at
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color("#0d1723"))
	label.add_theme_constant_override("outline_size", 3)
	parent.add_child(label)
	return label


func _open_save() -> void:
	AppState.save_screen_mode = "save"
	AppState.save_return_scene = AppState.area_scene_path("scifi.loop")
	AppState.save_return_position = hero.position
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")


func _return_to_map() -> void:
	get_tree().change_scene_to_file(MAP_SCENE)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact"):
		if info_panel.visible:
			info_panel.visible = false
		else:
			var site := site_at(hero.position)
			if site != "":
				active_site = site
				_refresh_text()
				info_panel.visible = true
	elif event.is_action_pressed("ui_cancel"):
		if info_panel.visible:
			info_panel.visible = false
		else:
			_return_to_map()
