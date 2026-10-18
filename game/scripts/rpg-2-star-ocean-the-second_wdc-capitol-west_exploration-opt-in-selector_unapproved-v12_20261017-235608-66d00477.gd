extends "res://scripts/scifi_exploration_area.gd"

# Washington, D.C. ruins (scifi.ruins): opt-in selector for the Capitol west v12 viewport-integration
# candidate (UNAPPROVED, art not accepted). Off by default: without `-- --wdc-capitol-west-v12` (or
# v12_override = 1 set before the scene loads) every override below hands straight to the unchanged
# scifi_exploration_area.gd, so the city, outskirts and ruins play exactly as before.
# With the flag, only the ruins destination changes. The real HUD, input actions, markers, labels,
# dialogue, saves, survey annex hand-off and battle hand-off are the inherited ones. v12 swaps the m8 ruins
# plate for the layered v11 Capitol scene (base, four Y-sorted layers, foreground), moves the ruins anchors
# onto that art, walks on the v12 mask, and adds a vertical camera so the 62 px header and 42 px footer
# never cover the play area. It also shrinks the hint line if it would run under the Save button, and gives the
# records and patrol labels the dark outline the base already gives the other world labels.
# To remove the opt-in, point game/scenes/scifi_exploration_area.tscn back at
# res://scripts/scifi_exploration_area.gd.
# Package and checks: tools/rpg-2-star-ocean-the-second_wdc-capitol-west_viewport-integration_build-check_unapproved-v12_20261017-235608-66d00477.py

const V12_FLAG := "--wdc-capitol-west-v12"
const V12_DIR := "res://assets/environments/candidates/wdc-cw-v12_20261017-235608-66d00477/"
const V12_FILE := "rpg-2-star-ocean-the-second_wdc-capitol-west_%s_unapproved-v12_20261017-235608-66d00477.png"
const V12_BASE := "rt-base"
const V12_FG := "rt-fg"
const V12_WALK := "rt-walk"
# Y-sorted layers: [purpose, pivot row]. A layer covers an actor whose feet are north of its pivot.
const V12_YSORT := [["rt-ys-mast", 256], ["rt-ys-tripod", 276], ["rt-ys-beacon", 306], ["rt-ys-elm", 282]]
# Play area between the runtime header (rows 0..61) and footer (rows 318..359).
const V12_VIEW_TOP := 62
const V12_VIEW_BOTTOM := 317
# Runtime actors are 32x48 canvases drawn with offset (0, -20): rows y-44..y+3, columns x-16..x+15.
const V12_CANVAS_ABOVE := 44
const V12_CANVAS_BELOW := 3
const V12_SCROLL_MAX := 104
# Camera: scroll 0 (dome and statue in view) while the feet are at row 250 or above; south of that it scrolls
# twice as fast as the feet so the player sees ahead (up to 52 rows) instead of walking along the footer.
const V12_SCROLL_FROM := 250
const V12_SCROLL_RATE := 2
const V12_FG_Z := 2000
const V12_LABEL_Z := 4000
# Anchors on the v11 Capitol art (feet rows). Records = the Olmsted plaque on the left stair pier.
const V12_SPAWN := Vector2(372, 246)
const V12_SURVEY := Vector2(372, 192)
const V12_RECORDS := Vector2(302, 214)
const V12_NPC := Vector2(268, 243)
const V12_ASSIST := Vector2(548, 264)
const V12_TRACES := [Vector2(150, 232), Vector2(464, 240)]
const V12_ENEMY := Vector2(566, 320)
const V12_BYPASS := Rect2(606, 278, 18, 63)
const V12_BYPASS_MARKER := Vector2(614, 286)
const V12_HEADER_GAP := 8.0

static var v12_override := -1

var v12_active := false
var v12_walk: Image
var v12_textures := {}
var v12_camera: Camera2D
var v12_labels: Node2D
var v12_scroll := 0
var v12_hint_size := 11


static func v12_enabled() -> bool:
	if v12_override >= 0:
		return v12_override == 1
	return OS.get_cmdline_user_args().has(V12_FLAG)


func _ready() -> void:
	v12_active = v12_enabled() and AppState.current_destination_id == "scifi.ruins" and _v12_load()
	if not v12_active:
		super()
		return
	var resumed := AppState.returning_from_battle or AppState.resume_area_pending
	super()
	_v12_install(resumed)


func _process(delta: float) -> void:
	if not v12_active:
		super(delta)
		return
	if dialogue_open:
		_reset_walk_animation()
		return
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var was_in_bypass_zone := V12_BYPASS.has_point(hero.position)
	if direction != Vector2.ZERO:
		_set_city_facing(direction)
		var previous_position := hero.position
		hero.position = _v12_slide(previous_position, previous_position + direction * MOVE_SPEED * delta)
		if hero.position.distance_to(previous_position) > 0.05:
			_update_walk_animation(delta)
		else:
			_reset_walk_animation()
		if enemy_visible:
			if hero.position.distance_to(enemy_position) > 43.0:
				safe_position = hero.position
			if hero.position.distance_to(enemy_position) < 23.0:
				_v12_sync()
				_open_encounter()
				return
	else:
		_reset_walk_animation()
	if enemy_visible and not bypass_reached and direction != Vector2.ZERO and not was_in_bypass_zone and V12_BYPASS.has_point(hero.position):
		bypass_reached = true
		if not AppState.machine_observed:
			AppState.record_playtest_event("machine_bypass", destination_id)
		AppState.machine_observed = true
		feedback_key = "bypass_notice"
		_refresh_text()
	_v12_sync()


func _draw() -> void:
	if not v12_active:
		super()
		return
	# Same runtime markers and colours as the inherited ruins branch, at the v12 anchors.
	if enemy_visible:
		_draw_enemy()
		_draw_field_marker(V12_BYPASS_MARKER, Color("#8fd8cf"), "bypass")
	if not AppState.ji_records_checked:
		_draw_field_marker(V12_RECORDS, Color("#e5bb77"), "records")
	_draw_field_marker(V12_SURVEY, Color("#80d0c4" if AppState.survey_solved.has(destination_id) else "#d8be7f"), "survey")
	_draw_field_marker(V12_ASSIST, Color("#80d0c4" if AppState.field_insights.has(destination_id) else "#e3bf78"), "assist")
	for index in 2:
		var recorded: bool = AppState.field_traces.has("%s:%d" % [destination_id, index])
		_draw_field_marker(V12_TRACES[index], Color("#80d0c4" if recorded else "#f4ca81"), "trace")


func _refresh_text() -> void:
	super()
	if v12_active:
		_v12_fit_header()


func _unhandled_input(event: InputEvent) -> void:
	if not v12_active or not event.is_action_pressed("interact") or dialogue_open:
		super(event)
		return
	# Inherited ruins interaction order and radii, at the v12 anchors.
	if hero.position.distance_to(V12_SURVEY) < 43.0:
		AppState.current_annex_room = 1
		AppState.annex_surface_return_position = hero.position
		AppState.resume_area_position = hero.position
		AppState.resume_area_pending = true
		get_tree().change_scene_to_file("res://scenes/survey_annex.tscn")
	elif not AppState.ji_records_checked and hero.position.distance_to(V12_RECORDS) < 43.0:
		AppState.ji_records_checked = true
		AppState.record_playtest_event("ruin_record_checked", destination_id)
		cue_player.play()
		feedback_message = AppState.text_for("relic_done")
		_refresh_text()
		queue_redraw()
	elif not AppState.recruited_members.has(recruit_id) and hero.position.distance_to(npc_position) < 50.0:
		_open_dialogue()
	elif hero.position.distance_to(V12_ASSIST) < 40.0:
		_open_field_assist()
	else:
		for index in 2:
			if hero.position.distance_to(V12_TRACES[index]) < 34.0:
				_open_field_trace(index)
				return


func _v12_load() -> bool:
	v12_walk = _v12_image(V12_WALK)
	if v12_walk == null or v12_walk.get_size() != Vector2i(640, 360):
		push_warning("WDC Capitol west v12: walk mask missing; playing the default ruins scene")
		return false
	var purposes := [V12_BASE, V12_FG]
	for entry in V12_YSORT:
		purposes.append(entry[0])
	for purpose in purposes:
		var texture := _v12_texture(purpose)
		if texture == null:
			push_warning("WDC Capitol west v12: layer %s missing; playing the default ruins scene" % purpose)
			return false
		v12_textures[purpose] = texture
	return true


func _v12_path(purpose: String) -> String:
	return V12_DIR + V12_FILE % purpose


func _v12_image(purpose: String) -> Image:
	# Imported copies when the project has imported them; otherwise the PNG bytes themselves (no import step).
	var path := _v12_path(purpose)
	if FileAccess.file_exists(path + ".import"):
		var texture: Texture2D = load(path)
		return texture.get_image() if texture != null else null
	if not FileAccess.file_exists(path):
		return null
	return Image.load_from_file(ProjectSettings.globalize_path(path))


func _v12_texture(purpose: String) -> Texture2D:
	var path := _v12_path(purpose)
	if FileAccess.file_exists(path + ".import"):
		return load(path)
	var image := _v12_image(purpose)
	return ImageTexture.create_from_image(image) if image != null else null


func _v12_install(resumed: bool) -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	npc_position = V12_NPC
	enemy_position = V12_ENEMY
	if field_npc != null:
		field_npc.position = V12_NPC
	hero.position = _v12_safe(hero.position) if resumed else V12_SPAWN
	safe_position = hero.position
	_v12_add_layer(V12_BASE, -1)
	for entry in V12_YSORT:
		_v12_add_layer(entry[0], 2 * int(entry[1]))
	_v12_add_layer(V12_FG, V12_FG_Z)
	_v12_move_labels()
	v12_camera = Camera2D.new()
	v12_camera.name = "WdcV12Camera"
	v12_camera.anchor_mode = Camera2D.ANCHOR_MODE_FIXED_TOP_LEFT
	add_child(v12_camera)
	v12_camera.make_current()
	_v12_sync()
	queue_redraw()


func _v12_add_layer(purpose: String, depth: int) -> void:
	var sprite := Sprite2D.new()
	sprite.name = "WdcV12_" + purpose.replace("-", "_")
	sprite.texture = v12_textures[purpose]
	sprite.centered = false
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.z_index = depth
	add_child(sprite)


func _v12_move_labels() -> void:
	# World labels scroll with the camera; the HUD bars (CanvasLayer) stay fixed and draw over them.
	v12_labels = Node2D.new()
	v12_labels.name = "WdcV12Labels"
	v12_labels.z_index = V12_LABEL_Z
	add_child(v12_labels)
	var placed := [[npc_label, V12_NPC + Vector2(-38, -58)], [records_label, V12_RECORDS + Vector2(-25, -37)],
		[survey_label, V12_SURVEY + Vector2(-50, -42)], [assist_label, V12_ASSIST + Vector2(-46, -38)],
		[enemy_label, V12_ENEMY + Vector2(-39, -47)]]
	for index in 2:
		placed.append([trace_labels[index], V12_TRACES[index] + Vector2(-23, -34)])
	for entry in placed:
		var label: Label = entry[0]
		label.get_parent().remove_child(label)
		v12_labels.add_child(label)
		label.position = entry[1]
	# The base gives every world label but these two a dark outline; on the pale v11 lawn they need it too.
	for label in [records_label, enemy_label]:
		label.add_theme_color_override("font_outline_color", Color("#0d1723"))
		label.add_theme_constant_override("outline_size", 3)


func _v12_sync() -> void:
	var feet := int(round(hero.position.y))
	hero.z_index = 2 * feet + 1
	if field_npc != null:
		field_npc.z_index = 2 * int(round(field_npc.position.y)) + 1
	var lowest := feet + V12_CANVAS_BELOW - (V12_VIEW_BOTTOM - V12_VIEW_TOP)
	v12_scroll = clampi(maxi(V12_SCROLL_RATE * (feet - V12_SCROLL_FROM), lowest), 0, V12_SCROLL_MAX)
	if v12_camera != null:
		v12_camera.position = Vector2(0, v12_scroll - V12_VIEW_TOP)
		v12_camera.force_update_scroll()


func _v12_fit_header() -> void:
	# Candidate-only layout: keep the hint left of the Save button instead of running under it.
	var limit := save_button.position.x - V12_HEADER_GAP - hint_label.position.x
	var font := hint_label.get_theme_font("font")
	v12_hint_size = 11
	while v12_hint_size > 9 and font.get_string_size(hint_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, v12_hint_size).x > limit:
		v12_hint_size -= 1
	hint_label.add_theme_font_size_override("font_size", v12_hint_size)


func _v12_walkable(at: Vector2) -> bool:
	var x := int(round(at.x))
	var y := int(round(at.y))
	if x < 0 or y < 0 or x >= 640 or y >= 360:
		return false
	return v12_walk.get_pixel(x, y).a > 0.5


func _v12_safe(at: Vector2) -> Vector2:
	var start := Vector2(round(at.x), round(at.y))
	if _v12_walkable(start):
		return start
	# Nearest walkable foot position by expanding square rings; deterministic.
	for radius in range(1, 400):
		var best := Vector2.ZERO
		var best_distance := INF
		for dy in range(-radius, radius + 1):
			for dx in [-radius, radius]:
				var candidate := start + Vector2(dx, dy)
				if _v12_walkable(candidate) and candidate.distance_squared_to(start) < best_distance:
					best = candidate
					best_distance = candidate.distance_squared_to(start)
		for dx in range(-radius + 1, radius):
			for dy in [-radius, radius]:
				var candidate := start + Vector2(dx, dy)
				if _v12_walkable(candidate) and candidate.distance_squared_to(start) < best_distance:
					best = candidate
					best_distance = candidate.distance_squared_to(start)
		if best_distance < INF:
			return best
	return V12_SPAWN


func _v12_slide(from: Vector2, to: Vector2) -> Vector2:
	# Same swept stepping as city_navigation.gd, against the v12 mask.
	var position := from if _v12_walkable(from) else _v12_safe(from)
	var displacement := to - from
	var steps := maxi(1, ceili(displacement.length() / 2.0))
	var step := displacement / steps
	for index in steps:
		var candidate := position + step
		if _v12_walkable(candidate):
			position = candidate
		elif _v12_walkable(Vector2(candidate.x, position.y)):
			position.x = candidate.x
		elif _v12_walkable(Vector2(position.x, candidate.y)):
			position.y = candidate.y
	return position
