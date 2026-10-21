extends Node2D

const CITY_BACKGROUND := preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png")
const OUTSKIRTS_BACKGROUND := preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts_environment-background_m8-candidate_20261014-142557-58f0c3a1.png")
const RUINS_BACKGROUND := preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-ruins_environment-background_m8-candidate_20261014-142522-e254c01a.png")
const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const SpriteSetPilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const BATTLE_SCENE := preload("res://scenes/battle_arena.tscn")
const ThemedMusic := preload("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd")
# Unapproved audio pilot: disabled by default; the existing player/settings/fallback stay in use.
static var themed_music_override := -1
static var themed_music_asset_dir := ThemedMusic.DEFAULT_ASSET_DIR
const CityNavigation := preload("res://scripts/city_navigation.gd")
const CityHallParkV06 := preload("res://scripts/city_hall_park_v06_scene.gd")
# Opt-in UNAPPROVED navigation UI skin pilot (presentation only): `-- --navigation-ui-skin-pilot`, or set
# navigation_ui_skin_override = 1 before the scene loads. Off by default; a refused package changes nothing.
const NavigationUiSkin := preload("res://scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd")
const NAVIGATION_UI_SKIN_FLAG := "--navigation-ui-skin-pilot"
const NAVIGATION_UI_SKIN_DIR := "res://assets/ui/battle-skin-v01"
static var navigation_ui_skin_override := -1
# Opt-in UNAPPROVED dialogue sideportrait from the fixed five-variant exact-crop
# kit. Trace/system/unknown speakers hide it; flag-off geometry is untouched.
const CharacterUiPortraits := preload("res://scripts/rpg-2-star-ocean-the-second_character-ui-portraits_helper_v01_20261019-233832-b7c4e912.gd")
static var character_ui_portraits_override := -1
var character_ui_portraits: Control = null
# Opt-in editable Yonkers environment; presentation only, no movement/interaction change.
const OUTSKIRTS_NATIVE_FLAG := "--yonkers-outskirts-native-v01"
const OUTSKIRTS_NATIVE_PATH := "res://assets/environments/outskirts-native-v01/rpg-2-star-ocean-the-second_yonkers-outskirts_merged-flat_native13-v01_20261020-200047-3e58269e.png"
const MOVE_SPEED := 140.0
const SPAWN := Vector2(82, 260)
const CITY_SPAWN := Vector2(340, 253)
const RECORDS_POSITION := Vector2(320, 250)
const RELAY_POSITION := Vector2(470, 128)
const REPORT_POSITION := Vector2(470, 247)
const SURVEY_ENTRANCES := {
	"scifi.city": Vector2(558, 166),
	"scifi.outskirts": Vector2(558, 277),
	"scifi.ruins": Vector2(548, 142),
}
const FIELD_ASSISTS := {
	"scifi.city": {"position": Vector2(120, 187), "member": "liang-xu"},
	"scifi.outskirts": {"position": Vector2(505, 258), "member": "zhao-ling"},
	"scifi.ruins": {"position": Vector2(505, 275), "member": "ji-cheng"},
}
const FIELD_TRACES := {
	"scifi.city": [Vector2(285, 267), Vector2(378, 181)],
	"scifi.outskirts": [Vector2(125, 240), Vector2(408, 95)],
	"scifi.ruins": [Vector2(115, 245), Vector2(470, 115)],
}
const AMBIENCE := {
	"scifi.city": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-city_ambient-loop_m7_20261013-211230-c8e1159a.wav",
	"scifi.outskirts": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-outskirts_ambient-loop_m7_20261013-211230-57ad4b20.wav",
	"scifi.ruins": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-ruins_ambient-loop_m7_20261013-211230-6be0d93f.wav",
}
const DISCOVERY_CUE := preload("res://assets/audio/rpg-2-star-ocean-the-second_discovery_interaction-cue_m7_20261013-211230-ad781e52.wav")
const AREA_CONFIG := {
	"scifi.city": {"npc": Vector2(282, 180), "recruit": "liang-xu", "enemy": Vector2(-100, -100), "color": Color("#365463")},
	"scifi.outskirts": {"npc": Vector2(190, 150), "recruit": "zhao-ling", "enemy": Vector2(355, 238), "color": Color("#546b57")},
	"scifi.ruins": {"npc": Vector2(200, 145), "recruit": "ji-cheng", "enemy": Vector2(420, 225), "color": Color("#70644f")},
}

var destination_id := ""
var outskirts_native_active := false
var outskirts_native_background: Texture2D
var hero: Sprite2D
var city_npc: Sprite2D
var field_npc: Sprite2D
var city_canopy: Polygon2D
var city_hero_silhouette: Sprite2D
var city_occlusion_indicator: Label
# Opt-in UNAPPROVED City Hall Park v06 layers (null = existing city plate).
var city_hall_park
var city_facing := "south"
# Opt-in high-density sprite set driver (`--exploration-sprite-set-pilot`); null = legacy 32x48 textures.
var sprite_pilot
var walk_time := 0.0
var walk_phase := 0
var npc_position := Vector2.ZERO
var recruit_id := ""
var enemy_position := Vector2(-100, -100)
var enemy_visible := false
var encounter_count := 0
var bypass_reached := false
var safe_position := SPAWN
var title_label: Label
var hint_label: Label
var help_label: Label
var feedback_label: Label
var enemy_label: Label
var back_button: Button
var save_button: Button
var npc_label: Label
var records_label: Label
var station_label: Label
var survey_label: Label
var assist_label: Label
var trace_labels: Array[Label] = []
var dialogue_overlay: ColorRect
var dialogue_panel: ColorRect
var dialogue_title: Label
var dialogue_text: Label
var invite_button: Button
var later_button: Button
var dialogue_open := false
var dialogue_mode := "recruit"
var trace_index := -1
var feedback_key := "npc_prompt"
var feedback_message := ""
var cue_player: AudioStreamPlayer
var navigation_ui_skin


static func navigation_ui_skin_enabled() -> bool:
	if navigation_ui_skin_override >= 0:
		return navigation_ui_skin_override == 1
	return OS.get_cmdline_user_args().has(NAVIGATION_UI_SKIN_FLAG)


static func character_ui_portraits_enabled() -> bool:
	if character_ui_portraits_override >= 0:
		return character_ui_portraits_override == 1
	return CharacterUiPortraits.pilot_requested(OS.get_cmdline_user_args())


func _ready() -> void:
	destination_id = AppState.current_destination_id
	if not AREA_CONFIG.has(destination_id):
		destination_id = "scifi.city"
	AppState.record_playtest_event("location", destination_id)
	var config: Dictionary = AREA_CONFIG[destination_id]
	npc_position = config["npc"]
	recruit_id = config["recruit"]
	enemy_position = config["enemy"]
	enemy_visible = destination_id != "scifi.city" and not AppState.enemy_cleared_for_return
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	if destination_id == "scifi.outskirts" and OS.get_cmdline_user_args().has(OUTSKIRTS_NATIVE_FLAG) and ResourceLoader.exists(OUTSKIRTS_NATIVE_PATH):
		var candidate := load(OUTSKIRTS_NATIVE_PATH) as Texture2D
		if candidate != null and candidate.get_size() == Vector2(640, 360):
			outskirts_native_background = candidate
			outskirts_native_active = true
	if destination_id == "scifi.city" and CityHallParkV06.enabled():
		city_hall_park = CityHallParkV06.new()
	if city_hall_park != null:
		if city_hall_park.load_scene():
			texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			city_hall_park.build_nodes(self)
		else:
			city_hall_park = null
	_build_actors()
	if destination_id == "scifi.city":
		_build_city_foreground()
	if AppState.returning_from_battle:
		hero.position = AppState.battle_return_position
		AppState.returning_from_battle = false
	elif AppState.resume_area_pending:
		hero.position = AppState.resume_area_position
		AppState.resume_area_pending = false
	if destination_id == "scifi.city":
		hero.position = _city_safe_position(hero.position)
		hero.z_index = int(hero.position.y)
	safe_position = hero.position
	if not AppState.areas_visited.has(destination_id):
		AppState.record_playtest_event("visit", destination_id)
	AppState.areas_visited[destination_id] = true
	_build_ui()
	if character_ui_portraits_enabled():
		character_ui_portraits = CharacterUiPortraits.new()
		if not character_ui_portraits.install_dialogue(self, dialogue_overlay, dialogue_panel, dialogue_title, dialogue_text, invite_button, later_button):
			character_ui_portraits = null
	_start_audio()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	_update_city_labels()
	if navigation_ui_skin_enabled():
		navigation_ui_skin = NavigationUiSkin.new(NAVIGATION_UI_SKIN_DIR)
		if not navigation_ui_skin.apply(self):
			navigation_ui_skin = null


func _exit_tree() -> void:
	if character_ui_portraits != null:
		character_ui_portraits.revert()
		character_ui_portraits = null
	if navigation_ui_skin != null:
		navigation_ui_skin.revert()
		navigation_ui_skin = null


func _process(delta: float) -> void:
	var pilot_from := hero.position
	if dialogue_open:
		_reset_walk_animation()
		_step_sprite_pilot(delta, pilot_from)
		_update_city_labels()
		return
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var was_in_bypass_zone := hero.position.x > 545.0 and hero.position.y < 205.0
	if direction != Vector2.ZERO:
		_set_city_facing(direction)
		var previous_position := hero.position
		var next_position := hero.position + direction * MOVE_SPEED * delta
		if destination_id == "scifi.city":
			next_position = _city_slide_position(next_position)
		else:
			next_position.x = clampf(next_position.x, 24.0, 616.0)
			next_position.y = clampf(next_position.y, 77.0, 306.0)
		hero.position = next_position
		if hero.position.distance_to(previous_position) > 0.05:
			_update_walk_animation(delta)
		else:
			_reset_walk_animation()
		if destination_id == "scifi.city":
			hero.z_index = int(hero.position.y)
		if enemy_visible:
			if hero.position.distance_to(enemy_position) > 43.0:
				safe_position = hero.position
			if hero.position.distance_to(enemy_position) < 23.0:
				_open_encounter()
	else:
		_reset_walk_animation()
	if enemy_visible and not bypass_reached and direction != Vector2.ZERO and not was_in_bypass_zone and hero.position.x > 545.0 and hero.position.y < 205.0:
		bypass_reached = true
		if not AppState.machine_observed:
			AppState.record_playtest_event("machine_bypass", destination_id)
		AppState.machine_observed = true
		feedback_key = "bypass_notice"
		_refresh_text()
	_step_sprite_pilot(delta, pilot_from)
	_update_city_labels()


# Presentation-only hook for the opt-in female complete-exploration pilot (after movement, before the silhouette copy).
func _step_sprite_pilot(delta: float, from: Vector2) -> void:
	if sprite_pilot != null and sprite_pilot.has_method("step"):
		sprite_pilot.step(delta, from, hero.position, city_facing)


func _draw() -> void:
	if not AREA_CONFIG.has(destination_id):
		return
	if destination_id == "scifi.city":
		if city_hall_park == null:
			draw_texture_rect(CITY_BACKGROUND, Rect2(0, 0, 640, 360), false)
		_draw_city_hotspots()
		return
	var background: Texture2D = OUTSKIRTS_BACKGROUND if destination_id == "scifi.outskirts" else RUINS_BACKGROUND
	if outskirts_native_active and destination_id == "scifi.outskirts":
		background = outskirts_native_background
	draw_texture_rect(background, Rect2(0, 0, 640, 360), false)
	if enemy_visible:
		_draw_enemy()
		_draw_field_marker(Vector2(575, 105), Color("#8fd8cf"), "bypass")
	if destination_id == "scifi.outskirts":
		_draw_field_marker(RELAY_POSITION, Color("#8fdecf" if AppState.relay_checked else "#e5bb77"), "relay")
	if destination_id == "scifi.ruins" and not AppState.ji_records_checked:
		_draw_field_marker(RECORDS_POSITION, Color("#e5bb77"), "records")
	var entrance: Vector2 = SURVEY_ENTRANCES[destination_id]
	_draw_field_marker(entrance, Color("#80d0c4" if AppState.survey_solved.has(destination_id) else "#d8be7f"), "survey")
	var assist_position: Vector2 = FIELD_ASSISTS[destination_id]["position"]
	_draw_field_marker(assist_position, Color("#80d0c4" if AppState.field_insights.has(destination_id) else "#e3bf78"), "assist")
	for index in 2:
		var trace_position: Vector2 = FIELD_TRACES[destination_id][index]
		var recorded: bool = AppState.field_traces.has("%s:%d" % [destination_id, index])
		_draw_field_marker(trace_position, Color("#80d0c4" if recorded else "#f4ca81"), "trace")


func _draw_field_marker(at: Vector2, color: Color, kind: String) -> void:
	# Native fixtures provide the physical affordance; retain a small progress indicator beside them.
	if outskirts_native_active and kind in ["relay", "survey", "assist", "trace"]:
		var corner := at + Vector2(15, -11)
		draw_circle(corner, 4.0, Color(0.04, 0.12, 0.16, 0.85))
		draw_rect(Rect2(corner - Vector2.ONE, Vector2(3, 3)), color)
		return
	draw_circle(at, 14.0, Color(0.04, 0.12, 0.16, 0.82))
	draw_arc(at, 12.0, 0.0, TAU, 26, color, 1.8)
	match kind:
		"trace":
			draw_circle(at, 3.0, color)
		"survey", "records":
			draw_rect(Rect2(at + Vector2(-5, -5), Vector2(10, 10)), color, false, 1.5)
			draw_line(at + Vector2(-2, -1), at + Vector2(2, -1), color, 1.4)
		"assist":
			draw_colored_polygon(PackedVector2Array([at + Vector2(0, -5), at + Vector2(5, 0), at + Vector2(0, 5), at + Vector2(-5, 0)]), color)
		"relay", "bypass":
			draw_arc(at, 5.0, PI * 0.15, PI * 1.85, 12, color, 1.5)
			draw_circle(at, 2.0, color)


func _draw_city_hotspots() -> void:
	_draw_city_marker(REPORT_POSITION, Color("#75d8ce"), "report")
	_draw_city_marker(SURVEY_ENTRANCES[destination_id], Color("#75d8ce" if AppState.survey_solved.has(destination_id) else "#f2cb81"), "survey")
	_draw_city_marker(FIELD_ASSISTS[destination_id]["position"], Color("#75d8ce" if AppState.field_insights.has(destination_id) else "#f2cb81"), "assist")
	for index in 2:
		var recorded: bool = AppState.field_traces.has("%s:%d" % [destination_id, index])
		_draw_city_marker(FIELD_TRACES[destination_id][index], Color("#75d8ce" if recorded else "#f2cb81"), "trace")


func _draw_city_marker(at: Vector2, color: Color, kind: String) -> void:
	draw_circle(at, 11.0, Color(0.03, 0.10, 0.14, 0.60))
	draw_arc(at, 9.0, 0.0, TAU, 24, color, 1.7)
	match kind:
		"report":
			for row in 3:
				draw_line(at + Vector2(-4, row * 3 - 3), at + Vector2(4, row * 3 - 3), color, 1.5)
		"survey":
			draw_rect(Rect2(at + Vector2(-4, -5), Vector2(8, 10)), color, false, 1.5)
			draw_circle(at + Vector2(2, 0), 1.0, color)
		"assist":
			draw_colored_polygon(PackedVector2Array([at + Vector2(0, -5), at + Vector2(5, 0), at + Vector2(0, 5), at + Vector2(-5, 0)]), color)
		"trace":
			draw_circle(at, 3.5, color)
			draw_circle(at, 1.25, Color("#16313a"))


func _build_city_foreground() -> void:
	if city_hall_park != null:
		_build_city_silhouette(CityHallParkV06.SILHOUETTE_Z)
		return
	# Reuse exact pixels from the city plate. These polygons draw in front of
	# actors whose feet are behind the garden canopy or street furniture.
	# They are scene geometry, not a second edited copy of the illustration.
	city_canopy = _add_city_foreground(PackedVector2Array([
		Vector2(31, 223), Vector2(46, 211), Vector2(63, 209), Vector2(70, 187),
		Vector2(85, 174), Vector2(95, 159), Vector2(112, 155), Vector2(126, 165),
		Vector2(144, 169), Vector2(158, 183), Vector2(174, 188), Vector2(185, 203),
		Vector2(203, 212), Vector2(216, 226), Vector2(217, 243), Vector2(199, 259),
		Vector2(178, 261), Vector2(157, 253), Vector2(132, 254), Vector2(111, 248),
		Vector2(87, 251), Vector2(65, 243), Vector2(46, 242)
	]), 305)
	_add_city_foreground(PackedVector2Array([
		Vector2(230, 192), Vector2(246, 192), Vector2(249, 205),
		Vector2(249, 275), Vector2(231, 275), Vector2(232, 207)
	]), 276)
	_add_city_foreground(PackedVector2Array([
		Vector2(497, 157), Vector2(509, 154), Vector2(519, 167),
		Vector2(524, 187), Vector2(518, 211), Vector2(504, 212), Vector2(498, 195)
	]), 213)
	_build_city_silhouette(306)


func _build_city_silhouette(depth: int) -> void:
	city_hero_silhouette = Sprite2D.new()
	city_hero_silhouette.texture = hero.texture
	city_hero_silhouette.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	city_hero_silhouette.offset = hero.offset
	city_hero_silhouette.scale = hero.scale
	city_hero_silhouette.modulate = Color(0.72, 0.93, 1.0, 0.55)
	city_hero_silhouette.z_index = depth
	city_hero_silhouette.visible = false
	add_child(city_hero_silhouette)


func _add_city_foreground(points: PackedVector2Array, depth: int) -> Polygon2D:
	var layer := Polygon2D.new()
	layer.polygon = points
	var uv := PackedVector2Array()
	var source_scale := CITY_BACKGROUND.get_size() / Vector2(640, 360)
	for point in points:
		uv.append(point * source_scale)
	layer.uv = uv
	layer.texture = CITY_BACKGROUND
	layer.z_index = depth
	add_child(layer)
	return layer


func _update_city_labels() -> void:
	if destination_id != "scifi.city" or hero == null or not is_instance_valid(hero) or assist_label == null:
		return
	var position := hero.position
	var hidden_by_canopy: bool = city_hall_park.hidden_by_canopy(position) if city_hall_park != null \
		else Geometry2D.is_point_in_polygon(position, city_canopy.polygon)
	# Mirror the hero's current walk/idle frame so the canopy outline never lags.
	city_hero_silhouette.texture = hero.texture
	city_hero_silhouette.offset = hero.offset
	city_hero_silhouette.scale = hero.scale
	city_hero_silhouette.flip_h = hero.flip_h
	city_hero_silhouette.position = position
	city_hero_silhouette.visible = hidden_by_canopy
	city_occlusion_indicator.visible = hidden_by_canopy
	city_occlusion_indicator.position = position + Vector2(-7, -58)
	assist_label.visible = position.distance_to(FIELD_ASSISTS[destination_id]["position"]) < 82.0
	for index in 2:
		trace_labels[index].visible = position.distance_to(FIELD_TRACES[destination_id][index]) < 72.0


func _city_safe_position(at: Vector2) -> Vector2:
	if city_hall_park != null:
		return city_hall_park.safe_position(at)
	return CityNavigation.safe_position(at)


func _city_slide_position(at: Vector2) -> Vector2:
	if city_hall_park != null:
		return city_hall_park.slide_position(hero.position, at)
	return CityNavigation.slide_position(hero.position, at)


func _city_walkable(at: Vector2) -> bool:
	if city_hall_park != null:
		return city_hall_park.walkable(at)
	return CityNavigation.walkable(at)


func _draw_enemy() -> void:
	draw_circle(enemy_position, 24.0, Color(0.62, 0.20, 0.22, 0.32))
	draw_rect(Rect2(enemy_position + Vector2(-13, -14), Vector2(26, 27)), Color("#8a3a42"))
	draw_rect(Rect2(enemy_position + Vector2(-8, -8), Vector2(16, 8)), Color("#eaa88b"))
	draw_rect(Rect2(enemy_position + Vector2(-17, 11), Vector2(8, 7)), Color("#463942"))
	draw_rect(Rect2(enemy_position + Vector2(9, 11), Vector2(8, 7)), Color("#463942"))


func _set_city_facing(direction: Vector2) -> void:
	var next_facing := "east" if direction.x > 0.0 else "west"
	if absf(direction.y) >= absf(direction.x):
		next_facing = "south" if direction.y > 0.0 else "north"
	if next_facing == city_facing:
		return
	city_facing = next_facing
	walk_time = 0.0
	walk_phase = 0
	if sprite_pilot != null:
		sprite_pilot.face(city_facing)
		return
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, city_facing)


func _update_walk_animation(delta: float) -> void:
	if sprite_pilot != null:
		sprite_pilot.walk()
		return
	walk_time += delta
	var next_phase := int(floor(walk_time / 0.12)) % 4 + 1
	if next_phase == walk_phase:
		return
	walk_phase = next_phase
	hero.texture = NativeMotion.texture_for("protagonist-" + AppState.hero_appearance, "walk", city_facing, walk_phase)


func _reset_walk_animation() -> void:
	if sprite_pilot != null:
		sprite_pilot.idle()
		return
	if walk_phase == 0:
		return
	walk_time = 0.0
	walk_phase = 0
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, city_facing)


func _build_actors() -> void:
	hero = Sprite2D.new()
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, "south")
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.offset = Vector2(0, -20)
	sprite_pilot = SpriteSetPilot.attach(hero, "protagonist-" + AppState.hero_appearance, "south")
	if destination_id == "scifi.city":
		hero.position = CITY_SPAWN
		hero.z_index = int(hero.position.y)
		city_npc = Sprite2D.new()
		city_npc.texture = NativeIdle.texture_for("liang-xu", "south")
		city_npc.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		city_npc.offset = Vector2(0, -20)
		city_npc.position = npc_position
		city_npc.z_index = int(npc_position.y)
		city_npc.visible = not AppState.recruited_members.has(recruit_id)
		add_child(city_npc)
	else:
		hero.position = SPAWN
		field_npc = Sprite2D.new()
		field_npc.texture = NativeIdle.texture_for(recruit_id, "south")
		field_npc.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		field_npc.offset = Vector2(0, -20)
		field_npc.position = npc_position
		field_npc.visible = not AppState.recruited_members.has(recruit_id)
		add_child(field_npc)
	add_child(hero)


func _start_audio() -> void:
	var ambient_player := AudioStreamPlayer.new()
	var music_context: String = {"scifi.city": "city", "scifi.outskirts": "field", "scifi.ruins": "ruins"}[destination_id]
	var ambient: AudioStreamWAV = ThemedMusic.select(music_context, themed_music_override, themed_music_asset_dir)
	if ambient == null:
		ambient = load(AMBIENCE[destination_id]).duplicate()
	ambient.loop_mode = AudioStreamWAV.LOOP_FORWARD
	if ambient.loop_end <= ambient.loop_begin:
		ambient.loop_begin = 0
		ambient.loop_end = int(round(ambient.get_length() * ambient.mix_rate))
	ambient_player.stream = ambient
	ambient_player.volume_db = -11.0
	add_child(ambient_player)
	ambient_player.play()
	cue_player = AudioStreamPlayer.new()
	cue_player.stream = DISCOVERY_CUE
	cue_player.volume_db = -7.0
	add_child(cue_player)


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 62)
	canvas.add_child(header)
	title_label = Label.new()
	title_label.position = Vector2(18, 5)
	title_label.add_theme_font_size_override("font_size", 18)
	title_label.add_theme_color_override("font_color", Color("#f0f8f4"))
	canvas.add_child(title_label)
	hint_label = Label.new()
	hint_label.position = Vector2(18, 33)
	hint_label.add_theme_font_size_override("font_size", 11)
	hint_label.add_theme_color_override("font_color", Color("#acc8c8"))
	canvas.add_child(hint_label)
	back_button = Button.new()
	back_button.position = Vector2(525, 12)
	back_button.size = Vector2(98, 38)
	back_button.pressed.connect(_return_to_map)
	canvas.add_child(back_button)
	save_button = Button.new()
	save_button.position = Vector2(418, 12)
	save_button.size = Vector2(98, 38)
	save_button.pressed.connect(_open_save)
	canvas.add_child(save_button)
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 318)
	footer.size = Vector2(640, 42)
	canvas.add_child(footer)
	feedback_label = Label.new()
	feedback_label.position = Vector2(18, 322)
	feedback_label.add_theme_font_size_override("font_size", 11)
	feedback_label.add_theme_color_override("font_color", Color("#e7cf9c"))
	canvas.add_child(feedback_label)
	help_label = Label.new()
	help_label.position = Vector2(18, 340)
	help_label.add_theme_font_size_override("font_size", 10)
	help_label.add_theme_color_override("font_color", Color("#9dbab9"))
	canvas.add_child(help_label)
	if destination_id == "scifi.city":
		city_occlusion_indicator = Label.new()
		city_occlusion_indicator.text = "▼"
		city_occlusion_indicator.add_theme_font_size_override("font_size", 14)
		city_occlusion_indicator.add_theme_color_override("font_color", Color("#aff1e6"))
		city_occlusion_indicator.add_theme_color_override("font_outline_color", Color("#0d1723"))
		city_occlusion_indicator.add_theme_constant_override("outline_size", 3)
		city_occlusion_indicator.visible = false
		canvas.add_child(city_occlusion_indicator)
	enemy_label = Label.new()
	enemy_label.position = enemy_position + Vector2(-39, -47)
	enemy_label.add_theme_font_size_override("font_size", 10)
	enemy_label.add_theme_color_override("font_color", Color("#ffe0cd"))
	enemy_label.visible = enemy_visible
	canvas.add_child(enemy_label)
	npc_label = Label.new()
	npc_label.position = npc_position + Vector2(-38, -58)
	npc_label.add_theme_font_size_override("font_size", 11)
	npc_label.add_theme_color_override("font_color", Color("#f4e6b9"))
	canvas.add_child(npc_label)
	records_label = Label.new()
	records_label.position = RECORDS_POSITION + Vector2(-25, -37)
	records_label.add_theme_font_size_override("font_size", 11)
	records_label.add_theme_color_override("font_color", Color("#e9dba8"))
	canvas.add_child(records_label)
	station_label = Label.new()
	station_label.position = (RELAY_POSITION if destination_id == "scifi.outskirts" else REPORT_POSITION) + Vector2(-40, -42)
	station_label.add_theme_font_size_override("font_size", 12 if destination_id == "scifi.city" else 11)
	station_label.add_theme_color_override("font_color", Color("#fff1c7" if destination_id == "scifi.city" else "#f0dda8"))
	canvas.add_child(station_label)
	survey_label = Label.new()
	survey_label.position = SURVEY_ENTRANCES[destination_id] + Vector2(-50, -42)
	survey_label.add_theme_font_size_override("font_size", 11)
	survey_label.add_theme_color_override("font_color", Color("#f0dda8"))
	canvas.add_child(survey_label)
	assist_label = Label.new()
	assist_label.position = FIELD_ASSISTS[destination_id]["position"] + Vector2(-46, -38)
	assist_label.add_theme_font_size_override("font_size", 10)
	assist_label.add_theme_color_override("font_color", Color("#f0dda8"))
	canvas.add_child(assist_label)
	for index in 2:
		var trace_label := Label.new()
		trace_label.position = FIELD_TRACES[destination_id][index] + Vector2(-23, -34)
		trace_label.add_theme_font_size_override("font_size", 10)
		trace_label.add_theme_color_override("font_color", Color("#f0dda8"))
		canvas.add_child(trace_label)
		trace_labels.append(trace_label)
	for marker_label in [npc_label, station_label, survey_label, assist_label] + trace_labels:
		marker_label.add_theme_color_override("font_outline_color", Color("#0d1723"))
		marker_label.add_theme_constant_override("outline_size", 3)
	_build_dialogue(canvas)


func _build_dialogue(canvas: CanvasLayer) -> void:
	dialogue_overlay = ColorRect.new()
	dialogue_overlay.color = Color(0.04, 0.08, 0.12, 0.82)
	dialogue_overlay.size = Vector2(640, 360)
	dialogue_overlay.visible = false
	canvas.add_child(dialogue_overlay)
	dialogue_panel = ColorRect.new()
	dialogue_panel.position = Vector2(87, 93)
	dialogue_panel.size = Vector2(466, 185)
	dialogue_panel.color = Color("#263e48")
	dialogue_overlay.add_child(dialogue_panel)
	dialogue_title = Label.new()
	dialogue_title.position = Vector2(110, 109)
	dialogue_title.add_theme_font_size_override("font_size", 19)
	dialogue_title.add_theme_color_override("font_color", Color("#f1e5c6"))
	dialogue_overlay.add_child(dialogue_title)
	dialogue_text = Label.new()
	dialogue_text.position = Vector2(110, 143)
	dialogue_text.size = Vector2(419, 74)
	dialogue_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_overlay.add_child(dialogue_text)
	invite_button = Button.new()
	invite_button.position = Vector2(110, 228)
	invite_button.size = Vector2(183, 35)
	invite_button.pressed.connect(_dialogue_primary)
	dialogue_overlay.add_child(invite_button)
	later_button = Button.new()
	later_button.position = Vector2(331, 228)
	later_button.size = Vector2(198, 35)
	later_button.pressed.connect(_close_dialogue)
	dialogue_overlay.add_child(later_button)


func _refresh_text() -> void:
	var key := destination_id.trim_prefix("scifi.")
	title_label.text = AppState.destination_name(destination_id)
	hint_label.text = AppState.text_for("area_" + key + "_hint")
	help_label.text = AppState.text_for("area_help")
	var feedback_text := AppState.text_for(feedback_key)
	if feedback_key == "field_assist_reward":
		feedback_text = feedback_text % AppState.member_name(FIELD_ASSISTS[destination_id]["member"])
	feedback_label.text = feedback_message if feedback_message != "" else feedback_text
	back_button.text = AppState.text_for("area_back")
	save_button.text = AppState.text_for("save_open")
	enemy_label.text = AppState.text_for("enemy_label")
	npc_label.text = AppState.member_name(recruit_id)
	npc_label.visible = not AppState.recruited_members.has(recruit_id)
	if city_npc != null:
		city_npc.visible = npc_label.visible
	if field_npc != null:
		field_npc.visible = npc_label.visible
	records_label.text = AppState.text_for("relic_marker")
	records_label.visible = destination_id == "scifi.ruins" and not AppState.ji_records_checked
	station_label.visible = destination_id != "scifi.ruins"
	station_label.text = AppState.text_for("relay_marker" if destination_id == "scifi.outskirts" else "report_marker")
	survey_label.text = AppState.text_for("survey_marker")
	assist_label.text = AppState.text_for("field_assist_marker_" + key)
	for index in 2:
		trace_labels[index].text = AppState.text_for("field_trace_marker") + " %d" % (index + 1)
	if dialogue_mode == "trace":
		dialogue_title.text = AppState.text_for("field_trace_marker") + " %d/2" % (trace_index + 1)
		dialogue_text.text = AppState.text_for("field_trace_" + key + "_%d" % trace_index)
		invite_button.visible = false
		later_button.text = AppState.text_for("field_assist_close")
	elif dialogue_mode == "assist":
		invite_button.visible = true
		var assistant_id: String = FIELD_ASSISTS[destination_id]["member"]
		dialogue_title.text = assist_label.text + " · " + AppState.member_name(assistant_id)
		if not AppState.recruited_members.has(assistant_id):
			dialogue_text.text = AppState.text_for("field_assist_need") % AppState.member_name(assistant_id)
		elif AppState.field_insights.has(destination_id):
			dialogue_text.text = AppState.text_for("field_assist_result_" + key)
		elif AppState.field_trace_count(destination_id) < 2:
			dialogue_text.text = AppState.text_for("field_trace_need") % AppState.member_name(assistant_id)
		else:
			dialogue_text.text = AppState.text_for("field_assist_ready_" + key)
		invite_button.text = AppState.text_for("field_assist_recorded" if AppState.field_insights.has(destination_id) else "field_assist_use")
		invite_button.disabled = not AppState.recruited_members.has(assistant_id) or AppState.field_insights.has(destination_id) or AppState.field_trace_count(destination_id) < 2
		later_button.text = AppState.text_for("field_assist_close")
	else:
		invite_button.visible = true
		dialogue_title.text = AppState.member_name(recruit_id)
		dialogue_text.text = AppState.text_for("recruit_ji_locked" if recruit_id == "ji-cheng" and not AppState.ji_records_checked else "recruit_" + recruit_id.split("-")[0])
		invite_button.text = AppState.text_for("recruit_invite")
		invite_button.disabled = recruit_id == "ji-cheng" and not AppState.ji_records_checked
		later_button.text = AppState.text_for("recruit_later")
	_refresh_character_ui_portrait()


func _refresh_character_ui_portrait() -> void:
	if character_ui_portraits == null:
		return
	var speaker := ""
	if dialogue_mode == "recruit":
		speaker = recruit_id
	elif dialogue_mode == "assist":
		speaker = String(FIELD_ASSISTS[destination_id]["member"])
	character_ui_portraits.apply_dialogue(dialogue_mode, speaker, true)


func _open_dialogue() -> void:
	dialogue_mode = "recruit"
	dialogue_open = true
	dialogue_overlay.visible = true
	_refresh_text()
	if invite_button.disabled:
		later_button.grab_focus()
	else:
		invite_button.grab_focus()


func _open_field_assist() -> void:
	dialogue_mode = "assist"
	dialogue_open = true
	dialogue_overlay.visible = true
	_refresh_text()
	if invite_button.disabled:
		later_button.grab_focus()
	else:
		invite_button.grab_focus()


func _open_field_trace(index: int) -> void:
	trace_index = index
	dialogue_mode = "trace"
	dialogue_open = true
	dialogue_overlay.visible = true
	if AppState.discover_field_trace(destination_id, index):
		cue_player.play()
		feedback_key = "field_trace_found"
		feedback_message = ""
		AppState.write_auto_save("area", hero.position, "field_assist")
		queue_redraw()
	_refresh_text()
	later_button.grab_focus()


func _dialogue_primary() -> void:
	if dialogue_mode == "assist":
		var assistant_id: String = FIELD_ASSISTS[destination_id]["member"]
		if AppState.complete_field_assist(destination_id, assistant_id):
			cue_player.play()
			feedback_key = "field_assist_reward"
			feedback_message = ""
			AppState.write_auto_save("area", hero.position, "field_assist")
			_refresh_text()
			queue_redraw()
			later_button.grab_focus()
	else:
		_invite_companion()


func _close_dialogue() -> void:
	dialogue_open = false
	dialogue_overlay.visible = false
	if character_ui_portraits != null:
		character_ui_portraits.hide_dialogue()
	back_button.grab_focus()


func _invite_companion() -> void:
	if AppState.recruit_member(recruit_id):
		feedback_message = AppState.text_for("recruit_joined") % AppState.member_name(recruit_id)
		_close_dialogue()
		_refresh_text()
		queue_redraw()
		AppState.write_auto_save("area", hero.position, "manual_note")
	else:
		feedback_message = AppState.text_for("recruit_full")
		_close_dialogue()
		_refresh_text()


func _open_encounter() -> void:
	encounter_count += 1
	var enemy_id := "patrol" if destination_id == "scifi.outskirts" else "sentry"
	AppState.write_auto_save("area", safe_position, "before_battle")
	if AppState.begin_battle(enemy_id, safe_position):
		get_tree().change_scene_to_packed(BATTLE_SCENE)


func _open_save() -> void:
	AppState.save_screen_mode = "save"
	AppState.save_return_scene = "res://scenes/scifi_exploration_area.tscn"
	AppState.save_return_position = hero.position
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")


func _return_to_map() -> void:
	get_tree().change_scene_to_file("res://scenes/scifi_world_map.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		if dialogue_open:
			_close_dialogue()
		else:
			_return_to_map()
	elif event.is_action_pressed("interact"):
		if dialogue_open:
			return
		if hero.position.distance_to(SURVEY_ENTRANCES[destination_id]) < 43.0:
			AppState.current_annex_room = 1
			AppState.annex_surface_return_position = hero.position
			AppState.resume_area_position = hero.position
			AppState.resume_area_pending = true
			get_tree().change_scene_to_file("res://scenes/survey_annex.tscn")
		elif destination_id == "scifi.city" and hero.position.distance_to(REPORT_POSITION) < 50.0:
			if AppState.can_submit_report():
				var first_report := not AppState.demo_completed
				AppState.demo_completed = true
				if first_report:
					AppState.record_playtest_event("report", destination_id)
				AppState.resume_area_position = hero.position
				AppState.resume_area_pending = true
				AppState.write_auto_save("area", hero.position, "manual_note")
				if first_report:
					AppState.write_playtest_receipt()
				get_tree().change_scene_to_file("res://scenes/demo_report.tscn")
			else:
				feedback_key = "report_locked"
				feedback_message = ""
				_refresh_text()
		elif destination_id == "scifi.outskirts" and hero.position.distance_to(RELAY_POSITION) < 46.0:
			if not AppState.relay_checked:
				AppState.record_playtest_event("relay_checked", destination_id)
			AppState.relay_checked = true
			cue_player.play()
			feedback_key = "relay_done"
			feedback_message = ""
			_refresh_text()
			queue_redraw()
		elif destination_id == "scifi.ruins" and not AppState.ji_records_checked and hero.position.distance_to(RECORDS_POSITION) < 43.0:
			AppState.ji_records_checked = true
			AppState.record_playtest_event("ruin_record_checked", destination_id)
			cue_player.play()
			feedback_message = AppState.text_for("relic_done")
			_refresh_text()
		elif not AppState.recruited_members.has(recruit_id) and hero.position.distance_to(npc_position) < 50.0:
			_open_dialogue()
		elif hero.position.distance_to(FIELD_ASSISTS[destination_id]["position"]) < 40.0:
			_open_field_assist()
		else:
			for index in 2:
				if hero.position.distance_to(FIELD_TRACES[destination_id][index]) < 34.0:
					_open_field_trace(index)
					return
