extends Node2D

# Chicago Loop: a walkable technical placeholder (art not accepted). It is drawn from code, with
# no illustration. Street names, their order, the elevated loop's four streets (Lake, Wabash, Van Buren,
# Wells), the river to the north and west and the park and lake to the east follow real geography. Block
# sizes and spacing are schematic. Walking here never advances the calendar. Travel time is charged
# only when the party leaves through the world map. There is no survey, recruit, trace or battle, and
# the scene is never added to areas_visited, so the three-place demo goal is unchanged.

const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const MOVE_SPEED := 140.0
const STREET_HALF_WIDTH := 6.0
# West to east, then north to south. x / y in canvas pixels.
const NS_STREETS := [["Wells St", 80.0], ["LaSalle St", 160.0], ["Clark St", 240.0], ["Dearborn St", 320.0], ["State St", 400.0], ["Wabash Ave", 480.0], ["Michigan Ave", 560.0]]
const EW_STREETS := [["Lake St", 90.0], ["Randolph St", 120.0], ["Washington St", 150.0], ["Madison St", 180.0], ["Monroe St", 210.0], ["Adams St", 240.0], ["Jackson Blvd", 270.0], ["Van Buren St", 300.0]]
# Elevated tracks: Lake St (north), Wabash Ave (east), Van Buren St (south), Wells St (west).
const L_LOOP := Rect2(80, 90, 400, 210)
const STREET_SPAN := Rect2(80, 90, 480, 210)
# State and Madison is the origin of Chicago's street-address grid.
const SPAWN := Vector2(400, 180)
const COLOR_GROUND := Color("#1b2a33")
const COLOR_BLOCK := Color("#33464f")
const COLOR_BLOCK_EDGE := Color("#4d6670")
const COLOR_STREET := Color("#5b6b70")
const COLOR_RIVER := Color("#2e6f88")
const COLOR_LAKE := Color("#245c79")
const COLOR_PARK := Color("#3f6b47")
const COLOR_L := Color("#c9a45c")

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
var street_labels: Array[Label] = []


func _ready() -> void:
	AppState.record_playtest_event("location", "scifi.loop")
	hero = Sprite2D.new()
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, facing)
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.offset = Vector2(0, -20)
	hero.position = SPAWN
	if AppState.resume_area_pending:
		hero.position = safe_position(AppState.resume_area_position)
		AppState.resume_area_pending = false
	add_child(hero)
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()


# Walkable ground is the street network (the blocks between streets are solid).
static func walkable(at: Vector2) -> bool:
	if not STREET_SPAN.grow(STREET_HALF_WIDTH).has_point(at):
		return false
	for street in NS_STREETS:
		if absf(at.x - float(street[1])) <= STREET_HALF_WIDTH:
			return true
	for street in EW_STREETS:
		if absf(at.y - float(street[1])) <= STREET_HALF_WIDTH:
			return true
	return false


# Nearest street crossing, so a resumed save never starts inside a block.
static func safe_position(at: Vector2) -> Vector2:
	if walkable(at):
		return at
	var best := SPAWN
	for ns in NS_STREETS:
		for ew in EW_STREETS:
			var corner := Vector2(float(ns[1]), float(ew[1]))
			if corner.distance_to(at) < best.distance_to(at):
				best = corner
	return best


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


func _draw() -> void:
	draw_rect(Rect2(0, 0, 640, 360), COLOR_GROUND)
	# Chicago River: main stem north of the Loop, south branch to the west.
	draw_rect(Rect2(0, 64, 640, 12), COLOR_RIVER)
	draw_rect(Rect2(28, 64, 22, 254), COLOR_RIVER)
	# Grant Park and Lake Michigan to the east.
	draw_rect(Rect2(574, 76, 34, 242), COLOR_PARK)
	draw_rect(Rect2(608, 64, 32, 254), COLOR_LAKE)
	for i in NS_STREETS.size() - 1:
		for j in EW_STREETS.size() - 1:
			var x0: float = float(NS_STREETS[i][1]) + STREET_HALF_WIDTH
			var x1: float = float(NS_STREETS[i + 1][1]) - STREET_HALF_WIDTH
			var y0: float = float(EW_STREETS[j][1]) + STREET_HALF_WIDTH
			var y1: float = float(EW_STREETS[j + 1][1]) - STREET_HALF_WIDTH
			var block := Rect2(x0, y0, x1 - x0, y1 - y0)
			draw_rect(block, COLOR_BLOCK)
			draw_rect(block, COLOR_BLOCK_EDGE, false, 1.0)
	for street in NS_STREETS:
		draw_line(Vector2(street[1], STREET_SPAN.position.y - STREET_HALF_WIDTH), Vector2(street[1], STREET_SPAN.end.y + STREET_HALF_WIDTH), COLOR_STREET, STREET_HALF_WIDTH * 2.0)
	for street in EW_STREETS:
		draw_line(Vector2(STREET_SPAN.position.x - STREET_HALF_WIDTH, street[1]), Vector2(STREET_SPAN.end.x + STREET_HALF_WIDTH, street[1]), COLOR_STREET, STREET_HALF_WIDTH * 2.0)
	# Elevated loop drawn as a dashed track over its four streets.
	var corners := [L_LOOP.position, Vector2(L_LOOP.end.x, L_LOOP.position.y), L_LOOP.end, Vector2(L_LOOP.position.x, L_LOOP.end.y)]
	for i in 4:
		draw_dashed_line(corners[i], corners[(i + 1) % 4], COLOR_L, 3.0, 7.0)
	draw_circle(SPAWN, 4.0, Color("#e9d9a8"))


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
	# Street names are real and stay in English on both language settings.
	for street in NS_STREETS:
		var label := _label(self, Vector2(float(street[1]) - 20.0, 304.0), 8, Color("#d7e4e0"))
		label.text = String(street[0])
		street_labels.append(label)
	for street in EW_STREETS:
		var label := _label(self, Vector2(2.0, float(street[1]) - 7.0), 8, Color("#d7e4e0"))
		label.text = String(street[0]).trim_suffix(" St").trim_suffix(" Blvd")
		street_labels.append(label)


func _refresh_text() -> void:
	title_label.text = AppState.destination_name("scifi.loop")
	hint_label.text = AppState.text_for("area_loop_hint")
	badge_label.text = AppState.text_for("loop_placeholder_badge")
	note_label.text = AppState.text_for("loop_street_note")
	help_label.text = AppState.text_for("loop_walk_note") + " · " + AppState.text_for("area_help")
	back_button.text = AppState.text_for("area_back")
	save_button.text = AppState.text_for("save_open")
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
	if event.is_action_pressed("ui_cancel"):
		_return_to_map()
