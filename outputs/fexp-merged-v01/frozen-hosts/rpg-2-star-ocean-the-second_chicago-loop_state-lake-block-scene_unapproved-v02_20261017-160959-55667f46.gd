extends Node2D

# Chicago Loop: one walkable arrival block at State St and Lake St, under the 1895 Lake Street
# elevated (State/Lake station). Native 640x360 scene candidate v02 (UNAPPROVED, art not accepted):
# a quantized, repaired and layered underpainting of the nonruntime art-direction reference plus
# hand-placed pixel props, from
# tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v02_20261017-160959-55667f46.py,
# whose geometry must match the constants below. v01 (the district-placeholder script) is kept as
# the audit baseline. The intersection, the pedestrian Lake St plaza and the terrace are art-pilot
# choices, not canon. Walking here never advances the calendar. Travel time is charged only when the
# party leaves through the world map. The kiosk only shows a note: there is no survey, recruit, trace
# or battle, and the scene is never added to areas_visited, so the three-place demo goal is unchanged.

const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const SpriteSetPilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const MOVE_SPEED := 140.0
const GROUND := preload("res://assets/environments/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_ground-far_unapproved-v02_20261017-160959-55667f46.png")
# Drawn over the hero only while the hero's feet are north of (above) the pivot row.
const YSORT_LAYERS := [
	[preload("res://assets/environments/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_ysort-curb-lamp_unapproved-v02_20261017-160959-55667f46.png"), 180.5],
	[preload("res://assets/environments/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_ysort-kiosk-bench_unapproved-v02_20261017-160959-55667f46.png"), 195.5],
	[preload("res://assets/environments/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_ysort-l-columns_unapproved-v02_20261017-160959-55667f46.png"), 254.5],
	[preload("res://assets/environments/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_ysort-planters_unapproved-v02_20261017-160959-55667f46.png"), 256.5],
	[preload("res://assets/environments/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_ysort-forecourt_unapproved-v02_20261017-160959-55667f46.png"), 300.5],
	[preload("res://assets/environments/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_ysort-foreground-tree_unapproved-v02_20261017-160959-55667f46.png"), 330.5],
]
# Walkable ground: the pedestrian Lake St plaza under and south of the L, and the State St roadway
# and crosswalk, minus the bench and kiosk, the curb lamp, L column plinths and racks, planters, the
# raised terrace, the forecourt lamp, the cypress and fountain court, and the foreground tree.
const WALK := Rect2(8, 178, 624, 120)
const BLOCKS := [
	Rect2(392, 188, 26, 12), Rect2(419, 189, 26, 12),
	Rect2(79, 178, 14, 5),
	Rect2(143, 246, 38, 17), Rect2(460, 246, 38, 18),
	Rect2(180, 250, 15, 8), Rect2(453, 250, 8, 8),
	Rect2(120, 250, 23, 13), Rect2(497, 250, 22, 14),
	Rect2(518, 178, 122, 20),
	Rect2(520, 288, 26, 10),
	Rect2(574, 218, 66, 80),
	Rect2(86, 276, 44, 22),
]
const WALK_TOP := 178.0
const DECK_BOTTOM := 134.0
# Arrival on the Lake St plaza south of the L, looking north to the station.
const SPAWN := Vector2(320, 286)
const KIOSK := Vector2(432, 214)
const KIOSK_RADIUS := 26.0
# Real names stay in English on both language settings. The plaza lies east of State St (E Lake St).
const STREET_LABELS := [["E Lake St · 200 N", Vector2(268, 160)], ["N State St · 0 E/W", Vector2(6, 266)], ["State/Lake", Vector2(330, 119)]]
const KIOSK_TEXT := {
	"zh": "环线信息屏 · State St 与 Lake St 路口：头顶是 1895 年建成的湖街高架线（State/Lake 站）。State St 是门牌东西零线，Lake St 位于北 200 号。前往其他城市请回世界地图。",
	"en": "Loop info board · State St & Lake St: overhead runs the 1895 Lake Street elevated (State/Lake station). State St is the 0 E/W address line; Lake St is 200 N. For other cities, use the world map.",
}

var hero: Sprite2D
var facing := "south"
# Opt-in high-density sprite set driver (`--exploration-sprite-set-pilot`); null = legacy 32x48 textures.
var sprite_pilot
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


func _ready() -> void:
	AppState.record_playtest_event("location", "scifi.loop")
	var ground := Sprite2D.new()
	ground.texture = GROUND
	ground.centered = false
	ground.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(ground)
	var sorted := Node2D.new()
	sorted.y_sort_enabled = true
	add_child(sorted)
	for entry in YSORT_LAYERS:
		var layer := Sprite2D.new()
		layer.texture = entry[0]
		layer.centered = false
		layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		layer.position = Vector2(0, entry[1])
		layer.offset = Vector2(0, -float(entry[1]))
		sorted.add_child(layer)
	hero = Sprite2D.new()
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, facing)
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.offset = Vector2(0, -20)
	sprite_pilot = SpriteSetPilot.attach(hero, "protagonist-" + AppState.hero_appearance, facing)
	hero.position = SPAWN
	if AppState.resume_area_pending:
		hero.position = safe_position(AppState.resume_area_position)
		AppState.resume_area_pending = false
	sorted.add_child(hero)
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()


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


func _process(delta: float) -> void:
	if info_panel.visible and hero.position.distance_to(KIOSK) > KIOSK_RADIUS + 8.0:
		info_panel.visible = false
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if direction == Vector2.ZERO:
		_reset_walk_animation()
		return
	_set_facing(direction)
	var previous := hero.position
	hero.position = slide_position(hero.position, hero.position + direction * MOVE_SPEED * delta)
	if hero.position.distance_to(previous) > 0.05:
		_update_walk_animation(delta)
	else:
		_reset_walk_animation()


func _set_facing(direction: Vector2) -> void:
	var next := "east" if direction.x > 0.0 else "west"
	if absf(direction.y) >= absf(direction.x):
		next = "south" if direction.y > 0.0 else "north"
	if next == facing:
		return
	facing = next
	walk_time = 0.0
	walk_phase = 0
	if sprite_pilot != null:
		sprite_pilot.face(facing)
		return
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, facing)


func _update_walk_animation(delta: float) -> void:
	if sprite_pilot != null:
		sprite_pilot.walk()
		return
	walk_time += delta
	var next_phase := int(floor(walk_time / 0.12)) % 4 + 1
	if next_phase == walk_phase:
		return
	walk_phase = next_phase
	hero.texture = NativeMotion.texture_for("protagonist-" + AppState.hero_appearance, "walk", facing, walk_phase)


func _reset_walk_animation() -> void:
	if sprite_pilot != null:
		sprite_pilot.idle()
		return
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
	info_label.text = KIOSK_TEXT["en" if AppState.language == "en" else "zh"]
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
		elif hero.position.distance_to(KIOSK) <= KIOSK_RADIUS:
			info_panel.visible = true
	elif event.is_action_pressed("ui_cancel"):
		if info_panel.visible:
			info_panel.visible = false
		else:
			_return_to_map()
