extends Node2D

const CONTENT := preload("res://scripts/survey_content.gd")
const ThemedMusic := preload("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd")
# Unapproved audio pilot: disabled by default; the existing player/settings/fallback stay in use.
static var themed_music_override := -1
static var themed_music_asset_dir := ThemedMusic.DEFAULT_ASSET_DIR
const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const SpriteSetPilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const ROOM_ONE_BACKGROUND := {
	"scifi.city": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-survey-annex-room-01_environment-background_m8-concept_20261014-142350-f2ab83d1.png"),
	# UNAPPROVED v03 antenna-corridor candidate (native pixel plate from a layered Pixelorama source; v03 art pass over v02); this room only.
	"scifi.outskirts": preload("res://assets/environments/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-plate_unapproved-v03_20261017-224447-15709be4.png"),
	# UNAPPROVED v02 Capitol-annex candidate (palette-reduced underpainting + hand layers); replaces the rejected m8-concept plate for this room only.
	"scifi.ruins": preload("res://assets/environments/wdc-survey-room1/rpg-2-star-ocean-the-second_wdc-annex-room1_capitol-interior-scene_unapproved-v02_20261017-160235-71300729.png"),
}
const CITY_ROOM_ONE_FIXTURES := [
	preload("res://assets/props/nyc-public-facilities-room1/rpg-2-star-ocean-the-second_nyc-public-facilities-room1_usage-console-pixel-fixture_unapproved-v01_20261017-011700-b45e18a9.png"),
	preload("res://assets/props/nyc-public-facilities-room1/rpg-2-star-ocean-the-second_nyc-public-facilities-room1_old-conduit-pixel-fixture_unapproved-v01_20261017-011700-b45e18a9.png"),
	preload("res://assets/props/nyc-public-facilities-room1/rpg-2-star-ocean-the-second_nyc-public-facilities-room1_resident-notes-board-pixel-fixture_unapproved-v01_20261017-011700-b45e18a9.png"),
]
const ROOM_TWO_BACKGROUND := {
	"scifi.city": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-survey-annex-room-02_environment-background_m8-concept_20261014-142926-e2e661fc.png"),
	"scifi.outskirts": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-survey-annex-room-02_environment-background_m8-concept_20261014-143030-3784c1e2.png"),
	"scifi.ruins": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-ruins-survey-annex-room-02_environment-background_m8-concept_20261014-143300-042ae336.png"),
}
const CITY_ROOM_TWO_FIXTURES := [
	preload("res://assets/props/nyc-public-facilities-room2/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_repair-manual-bench-pixel-fixture_unapproved-v01_20261017-010000-7d3c8a91.png"),
	preload("res://assets/props/nyc-public-facilities-room2/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_duty-log-lectern-pixel-fixture_unapproved-v01_20261017-010000-7d3c8a91.png"),
	preload("res://assets/props/nyc-public-facilities-room2/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_analog-load-meter-pixel-fixture_unapproved-v01_20261017-010000-7d3c8a91.png"),
]
const YONKERS_ROOM_TWO_FIXTURES := [
	preload("res://assets/props/yonkers-maintenance-room2/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_line-checker-pixel-fixture_unapproved-v01_20261017-012500-a73e60b4.png"),
	preload("res://assets/props/yonkers-maintenance-room2/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_patrol-log-terminal-pixel-fixture_unapproved-v01_20261017-012500-a73e60b4.png"),
	preload("res://assets/props/yonkers-maintenance-room2/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_battery-log-rack-pixel-fixture_unapproved-v01_20261017-012500-a73e60b4.png"),
]
# Yonkers room 1: three tall antennas y-sorted with the heroine (anchor = plinth front at y 210), feet
# blockers, floor clue markers in front of each plinth and a foreground shrub layer.
const YONKERS_ROOM_ONE_ANTENNAS := [
	preload("res://assets/props/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_antenna-a-lattice-yagi_unapproved-v03_20261017-224447-15709be4.png"),
	preload("res://assets/props/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_antenna-b-dish_unapproved-v03_20261017-224447-15709be4.png"),
	preload("res://assets/props/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_antenna-c-guyed-whip_unapproved-v03_20261017-224447-15709be4.png"),
]
const YONKERS_ROOM_ONE_FOREGROUND := preload("res://assets/environments/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_foreground-occluder_unapproved-v03_20261017-224447-15709be4.png")
const YONKERS_ANTENNA_BASE_Y := 210.0
const YONKERS_ROOM_ONE_MARKERS := [Vector2(163, 228), Vector2(320, 228), Vector2(477, 228)]
const YONKERS_ROOM_ONE_BLOCKERS := [
	Rect2(0, 0, 640, 166), Rect2(0, 166, 38, 70), Rect2(602, 166, 38, 70), Rect2(0, 281, 640, 79),
	Rect2(42, 160, 58, 26), Rect2(124, 186, 68, 26), Rect2(290, 166, 72, 46), Rect2(443, 186, 80, 26),
	Rect2(428, 199, 14, 12), Rect2(524, 199, 14, 12), Rect2(494, 166, 14, 8), Rect2(224, 166, 34, 20), Rect2(380, 166, 34, 16),
]
const WDC_ROOM_ONE_FIXTURES := [
	preload("res://assets/props/wdc-annex-room1/rpg-2-star-ocean-the-second_wdc-annex-room1_layered-wall-pixel-fixture_unapproved-v02_20261017-160235-71300729.png"),
	preload("res://assets/props/wdc-annex-room1/rpg-2-star-ocean-the-second_wdc-annex-room1_broken-index-pixel-fixture_unapproved-v02_20261017-160235-71300729.png"),
	preload("res://assets/props/wdc-annex-room1/rpg-2-star-ocean-the-second_wdc-annex-room1_code-47-pixel-fixture_unapproved-v02_20261017-160235-71300729.png"),
]
# Corner stubs drawn above the heroine; feet blockers for the bench, rubble, stairwell, stubs and fixtures.
const WDC_ROOM_ONE_FOREGROUND := preload("res://assets/environments/wdc-survey-room1/rpg-2-star-ocean-the-second_wdc-annex-room1_foreground-occluder_unapproved-v02_20261017-160235-71300729.png")
const WDC_ROOM_ONE_BLOCKERS := [
	Rect2(0, 0, 640, 156), Rect2(0, 0, 84, 178), Rect2(0, 178, 64, 24), Rect2(552, 0, 88, 182), Rect2(570, 182, 70, 26),
	Rect2(584, 214, 56, 48), Rect2(0, 262, 62, 60), Rect2(578, 262, 62, 60), Rect2(550, 280, 30, 40),
	Rect2(129, 212, 70, 16), Rect2(288, 213, 69, 15), Rect2(443, 210, 70, 18),
]
const WDC_FIXTURE_BASE_Y := 228.0
# Washington room 2: UNAPPROVED v01 records-chamber fixtures, test-only opt-in `-- --wdc-records-chamber-v01`.
# Only the fixtures, their markers/labels, the fixture and table blockers and the lifted clue discs are opt-in.
# The default build intentionally differs from before in Washington rooms only: room 2's wall blockers always
# apply, and the English header fits (14 px title in both rooms, Back label font-fit); zh frames are unchanged.
# Clue fixtures are y-sorted with the heroine and carry their clue marker; the terminal table sorts first and its
# blocker keeps her clear of it.
const WDC_ROOM_TWO_FLAG := "--wdc-records-chamber-v01"
# Washington room 2 STYLE48 common-style background (UNAPPROVED, opt-in `-- --wdc-records-style48`): new background
# texture only; the v01 fixtures, anchors and blockers are unchanged and also enabled by this flag.
const WDC_RECORDS_STYLE48_FLAG := "--wdc-records-style48"
const WDC_RECORDS_STYLE48_BACKGROUND := preload("res://assets/environments/style48/rpg-2-star-ocean-the-second_wdc-records-room2_style48-rt-background_unapproved-v01_20261022-185913-713cdcb1.png")
const SceneDefaults35 := preload("res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd")
# Opt-in UNAPPROVED navigation UI skin pilot (presentation only): `-- --navigation-ui-skin-pilot`, or set
# navigation_ui_skin_override = 1 before the scene loads. Off by default; a refused package changes nothing.
const NavigationUiSkin := preload("res://scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd")
const NAVIGATION_UI_SKIN_FLAG := "--navigation-ui-skin-pilot"
const NAVIGATION_UI_SKIN_DIR := "res://assets/ui/battle-skin-v01"
static var navigation_ui_skin_override := -1
const WDC_ROOM_TWO_FIXTURES := [
	preload("res://assets/props/wdc-annex-room2/rpg-2-star-ocean-the-second_wdc-annex-room2_machine-translation-pixel-fixture_unapproved-v01_20261018-001157-151fb8d0.png"),
	preload("res://assets/props/wdc-annex-room2/rpg-2-star-ocean-the-second_wdc-annex-room2_parallel-inscription-pixel-fixture_unapproved-v01_20261018-001157-151fb8d0.png"),
	preload("res://assets/props/wdc-annex-room2/rpg-2-star-ocean-the-second_wdc-annex-room2_erased-heading-pixel-fixture_unapproved-v01_20261018-001157-151fb8d0.png"),
]
const WDC_ROOM_TWO_TERMINAL := preload("res://assets/props/wdc-annex-room2/rpg-2-star-ocean-the-second_wdc-annex-room2_analysis-light-table-pixel-fixture_unapproved-v01_20261018-001157-151fb8d0.png")
const WDC_ROOM_TWO_FIXTURE_TOP := 164.0
const WDC_ROOM_TWO_SORT_Y := 218.0
const WDC_ROOM_TWO_TERMINAL_ORIGIN := Vector2(272, 278)
# Feet blockers: back wall, the three fixture bases and the terminal table (from the author manifest), then the
# plate's stepped back corners, side walls and near-corner rubble (exit and lane stay clear). The plate is the same
# with or without the flag, so its walls (every entry outside WDC_ROOM_TWO_FIXTURE_BLOCKERS) always block in room 2.
const WDC_ROOM_TWO_FIXTURE_BLOCKERS := [1, 2, 3, 4]
const WDC_ROOM_TWO_BLOCKERS := [
	Rect2(0, 0, 640, 114), Rect2(116, 212, 99, 14), Rect2(279, 212, 83, 14), Rect2(440, 212, 88, 14), Rect2(258, 272, 113, 34),
	Rect2(0, 114, 96, 14), Rect2(0, 128, 74, 16), Rect2(0, 144, 56, 18), Rect2(0, 162, 40, 20), Rect2(0, 182, 32, 80), Rect2(0, 266, 48, 54),
	Rect2(528, 114, 112, 14), Rect2(548, 128, 92, 16), Rect2(568, 144, 72, 18), Rect2(588, 162, 52, 20), Rect2(600, 182, 40, 70), Rect2(604, 252, 36, 70),
]
# Clue discs are drawn this far above the logical clue site so they float over the fixture tops instead of covering
# the inscriptions; inspection still uses CLUE_POSITIONS and the inspect rects.
const WDC_ROOM_TWO_MARKER_LIFT := Vector2(0, -19)
const YONKERS_ANALYSIS_CONSOLE := preload("res://assets/props/yonkers-maintenance-room2/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_analysis-console-pixel-fixture_unapproved-v01_20261017-012500-a73e60b4.png")
const DISCOVERY_CUE := preload("res://assets/audio/rpg-2-star-ocean-the-second_discovery_interaction-cue_m7_20261013-211230-ad781e52.wav")
const CLUE_POSITIONS := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]
const EXIT_POSITION := Vector2(57, 257)
const NEXT_POSITION := Vector2(580, 257)
const TERMINAL_POSITION := Vector2(320, 263)
const MOVE_SPEED := 140.0
const PALETTES := {
	"scifi.city": [Color("#284652"), Color("#94bbb1")],
	"scifi.outskirts": [Color("#455d56"), Color("#a7c5a3")],
	"scifi.ruins": [Color("#5d574a"), Color("#d0b98a")],
}
const AMBIENCE := {
	"scifi.city": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-city_ambient-loop_m7_20261013-211230-c8e1159a.wav",
	"scifi.outskirts": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-outskirts_ambient-loop_m7_20261013-211230-57ad4b20.wav",
	"scifi.ruins": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-ruins_ambient-loop_m7_20261013-211230-6be0d93f.wav",
}

var destination_id := "scifi.city"
var room := 1
var hero: Sprite2D
var hero_facing := "south"
# Opt-in high-density sprite set driver (`--exploration-sprite-set-pilot`); null = legacy 32x48 textures.
var sprite_pilot
var walk_time := 0.0
var walk_phase := 0
var title_label: Label
var progress_label: Label
var help_label: Label
var back_button: Button
var save_button: Button
var clue_labels: Array[Label] = []
var exit_label: Label
var next_label: Label
var terminal_label: Label
var overlay: ColorRect
var overlay_title: Label
var overlay_body: RichTextLabel
var option_buttons: Array[Button] = []
var link_buttons: Array[Button] = []
var notes_button: Button
var previous_note_button: Button
var next_note_button: Button
var close_button: Button
var overlay_mode := ""
var notes_return_mode := ""
var notes_index := 0
var overlay_clue_index := -1
var link_selected_index := -1
var overlay_message := ""
var cue_player: AudioStreamPlayer
var wdc_front: Node2D
var wdc_front_mask := 0
var yonkers_room_one := false
var wdc_room_two := false
var wdc_room_two_walls := false
var wdc_room_two_markers: Array[Node2D] = []
var navigation_ui_skin


static func navigation_ui_skin_enabled() -> bool:
	if navigation_ui_skin_override >= 0:
		return navigation_ui_skin_override == 1
	return OS.get_cmdline_user_args().has(NAVIGATION_UI_SKIN_FLAG)


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	destination_id = AppState.current_destination_id
	if not CONTENT.DATA.has(destination_id):
		destination_id = "scifi.city"
	room = clampi(AppState.current_annex_room, 1, 2)
	_build_hero()
	if AppState.resume_annex_pending:
		hero.position = AppState.resume_annex_position
		AppState.resume_annex_pending = false
	if room == 1 and destination_id == "scifi.ruins":
		wdc_front = Node2D.new()
		wdc_front.draw.connect(_draw_wdc_front)
		add_child(wdc_front)
		_wdc_update_front()
	if room == 1 and destination_id == "scifi.outskirts":
		_build_yonkers_room_one()
	wdc_room_two_walls = room == 2 and destination_id == "scifi.ruins"
	# Flag first, then the MVP default fallback (sdef35 policy; false until the creator authorizes it).
	if wdc_room_two_walls and (OS.get_cmdline_user_args().has(WDC_ROOM_TWO_FLAG) or OS.get_cmdline_user_args().has(WDC_RECORDS_STYLE48_FLAG) or SceneDefaults35.default_on(SceneDefaults35.RECORDS)):
		_build_wdc_room_two()
	_build_ui()
	_start_audio()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	if navigation_ui_skin_enabled():
		navigation_ui_skin = NavigationUiSkin.new(NAVIGATION_UI_SKIN_DIR)
		if not navigation_ui_skin.apply(self):
			navigation_ui_skin = null


func _exit_tree() -> void:
	if navigation_ui_skin != null:
		navigation_ui_skin.revert()
		navigation_ui_skin = null


func _data() -> Dictionary:
	return CONTENT.DATA[destination_id][AppState.language]


func _clue_key(index: int) -> String:
	return "%s:%d" % [destination_id, index]


func _clue_count() -> int:
	var count := 0
	for index in 6:
		if AppState.survey_clues.has(_clue_key(index)):
			count += 1
	return count


func _link_key(index: int) -> String:
	return "%s:%d" % [destination_id, index]


func _link_count() -> int:
	var count := 0
	for index in 3:
		if AppState.survey_links.has(_link_key(index)):
			count += 1
	return count


func _linked_clue(index: int) -> bool:
	var links: Array = _data()["links"]
	for link_index in 3:
		if AppState.survey_links.has(_link_key(link_index)) and links[link_index]["pair"].has(index):
			return true
	return false


func _process(delta: float) -> void:
	if wdc_front != null:
		_wdc_update_front()
	var pilot_from := hero.position
	if overlay.visible:
		_reset_walk_animation()
		_step_sprite_pilot(delta, pilot_from)
		return
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if direction != Vector2.ZERO:
		_set_hero_facing(direction)
		var previous_position := hero.position
		hero.position += direction * MOVE_SPEED * delta
		hero.position.x = clampf(hero.position.x, 25.0, 615.0)
		hero.position.y = clampf(hero.position.y, 78.0, 305.0)
		if wdc_front != null:
			hero.position = _slide(previous_position, hero.position, _wdc_blocked)
			_wdc_update_front()
		elif yonkers_room_one:
			hero.position = _slide(previous_position, hero.position, _yonkers_blocked)
		elif wdc_room_two_walls:
			hero.position = _slide(previous_position, hero.position, _wdc_room_two_blocked)
		if hero.position.distance_to(previous_position) > 0.05:
			_update_walk_animation(delta)
		else:
			_reset_walk_animation()
	else:
		_reset_walk_animation()
	_step_sprite_pilot(delta, pilot_from)


# Presentation-only hook for the opt-in female complete-exploration pilot (after movement and collision).
func _step_sprite_pilot(delta: float, from: Vector2) -> void:
	if sprite_pilot != null and sprite_pilot.has_method("step"):
		sprite_pilot.step(delta, from, hero.position, hero_facing)


func _set_hero_facing(direction: Vector2) -> void:
	var facing := "east" if direction.x > 0.0 else "west"
	if absf(direction.y) >= absf(direction.x):
		facing = "south" if direction.y > 0.0 else "north"
	if facing == hero_facing:
		return
	hero_facing = facing
	walk_time = 0.0
	walk_phase = 0
	if sprite_pilot != null:
		sprite_pilot.face(hero_facing)
		return
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, hero_facing)


func _update_walk_animation(delta: float) -> void:
	if sprite_pilot != null:
		sprite_pilot.walk()
		return
	walk_time += delta
	var phase := int(floor(walk_time / 0.12)) % 4 + 1
	if phase == walk_phase:
		return
	walk_phase = phase
	hero.texture = NativeMotion.texture_for("protagonist-" + AppState.hero_appearance, "walk", hero_facing, walk_phase)


func _reset_walk_animation() -> void:
	if sprite_pilot != null:
		sprite_pilot.idle()
		return
	if walk_phase == 0:
		return
	walk_time = 0.0
	walk_phase = 0
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, hero_facing)


func _draw() -> void:
	var palette: Array = PALETTES[destination_id]
	var floor_color: Color = palette[0].darkened(0.10) if room == 2 else palette[0]
	draw_rect(Rect2(0, 0, 640, 360), Color("#11232c"))
	draw_rect(Rect2(16, 67, 608, 250), floor_color)
	for x in range(25, 625, 38):
		draw_line(Vector2(x, 68), Vector2(x, 317), floor_color.lightened(0.07), 1.0)
	for y in range(75, 317, 38):
		draw_line(Vector2(16, y), Vector2(624, y), floor_color.lightened(0.07), 1.0)
	match destination_id:
		"scifi.city":
			for x in [90, 235, 405, 548]:
				draw_rect(Rect2(x, 91, 43, 50), Color("#1b3541"))
				draw_rect(Rect2(x + 7, 98, 29, 9), Color("#749c9f"))
			if room == 2:
				draw_line(Vector2(42, 293), Vector2(590, 293), Color("#91aaa1"), 5.0)
				for x in [120, 270, 430, 550]:
					draw_circle(Vector2(x, 293), 7.0, Color("#c4a67a"))
		"scifi.outskirts":
			for x in [90, 235, 405, 548]:
				draw_rect(Rect2(x, 86, 7, 51), Color("#263f42"))
				draw_line(Vector2(x + 3, 91), Vector2(x + 30, 82), Color("#b0c7af"), 2.0)
			if room == 2:
				for x in [110, 260, 420, 555]:
					draw_rect(Rect2(x, 285, 37, 18), Color("#273f43"))
					draw_rect(Rect2(x + 5, 290, 27, 5), Color("#92b5a8"))
		"scifi.ruins":
			for x in [78, 233, 398, 553]:
				draw_rect(Rect2(x, 83, 30, 58), Color("#aa9670"))
				draw_rect(Rect2(x - 7, 78, 44, 8), Color("#d3b985"))
			if room == 2:
				draw_circle(Vector2(320, 266), 59.0, Color("#87775a"))
				draw_circle(Vector2(320, 266), 46.0, floor_color)
	if room == 1 and ROOM_ONE_BACKGROUND.has(destination_id):
		draw_texture_rect(ROOM_ONE_BACKGROUND[destination_id], Rect2(0, 0, 640, 360), false)
	elif room == 2 and ROOM_TWO_BACKGROUND.has(destination_id):
		draw_texture_rect(_room_two_background(), Rect2(0, 0, 640, 360), false)
	if room == 1 and destination_id == "scifi.city":
		for index in CITY_ROOM_ONE_FIXTURES.size():
			var fixture_position: Vector2 = CLUE_POSITIONS[index] + Vector2(-32, 2)
			draw_texture_rect(CITY_ROOM_ONE_FIXTURES[index], Rect2(fixture_position, Vector2(64, 64)), false)
	if room == 2 and destination_id == "scifi.city":
		for index in CITY_ROOM_TWO_FIXTURES.size():
			var fixture_position: Vector2 = CLUE_POSITIONS[index] + Vector2(-32, 2)
			draw_texture_rect(CITY_ROOM_TWO_FIXTURES[index], Rect2(fixture_position, Vector2(64, 64)), false)
	if room == 2 and destination_id == "scifi.outskirts":
		for index in YONKERS_ROOM_TWO_FIXTURES.size():
			var fixture_position: Vector2 = CLUE_POSITIONS[index] + Vector2(-32, 2)
			draw_texture_rect(YONKERS_ROOM_TWO_FIXTURES[index], Rect2(fixture_position, Vector2(64, 64)), false)
		draw_texture_rect(YONKERS_ANALYSIS_CONSOLE, Rect2(TERMINAL_POSITION + Vector2(-32, -34), Vector2(64, 64)), false)
	if room == 1 and destination_id == "scifi.ruins":
		for index in WDC_ROOM_ONE_FIXTURES.size():
			if wdc_front_mask & (1 << index):
				continue
			var fixture_position: Vector2 = CLUE_POSITIONS[index] + Vector2(-32, 2)
			draw_texture_rect(WDC_ROOM_ONE_FIXTURES[index], Rect2(fixture_position, Vector2(64, 64)), false)
	if not wdc_room_two:
		for index in CLUE_POSITIONS.size():
			_draw_clue_marker(self, index)
	_draw_annex_marker(EXIT_POSITION, Color("#8bcfca"), false)
	if room == 1:
		_draw_annex_marker(NEXT_POSITION, Color("#e4c377"), false)
	elif not wdc_room_two:
		_draw_annex_marker(TERMINAL_POSITION, palette[1] if AppState.survey_solved.has(destination_id) else Color("#e4c377"), true)


func _draw_clue_marker(target: CanvasItem, index: int, strokes_only := false) -> void:
	var palette: Array = PALETTES[destination_id]
	var position: Vector2 = YONKERS_ROOM_ONE_MARKERS[index] if yonkers_room_one else CLUE_POSITIONS[index]
	var already := AppState.survey_clues.has(_clue_key((room - 1) * 3 + index))
	var clue_color: Color = palette[1] if already else Color("#e2bb77")
	if not strokes_only:
		target.draw_circle(position, 16.0, Color(0.04, 0.12, 0.16, 0.82))
	target.draw_arc(position, 14.0, 0.0, TAU, 28, clue_color, 2.0)
	target.draw_rect(Rect2(position + Vector2(-6, -6), Vector2(12, 12)), clue_color, false, 1.7)
	target.draw_line(position + Vector2(-3, -2), position + Vector2(3, -2), clue_color, 1.5)
	target.draw_line(position + Vector2(-3, 2), position + Vector2(2, 2), clue_color, 1.5)


# Washington room 1 only: fixtures the heroine stands behind move to this front node (the marker
# disc stays under her, its ring is redrawn on top), which also draws the corner-stub foreground.
func _draw_wdc_front() -> void:
	for index in WDC_ROOM_ONE_FIXTURES.size():
		if wdc_front_mask & (1 << index):
			wdc_front.draw_texture_rect(WDC_ROOM_ONE_FIXTURES[index], Rect2(CLUE_POSITIONS[index] + Vector2(-32, 2), Vector2(64, 64)), false)
			_draw_clue_marker(wdc_front, index, true)
	wdc_front.draw_texture_rect(WDC_ROOM_ONE_FOREGROUND, Rect2(0, 0, 640, 360), false)


func _wdc_update_front() -> void:
	var mask := 0
	for index in WDC_ROOM_ONE_FIXTURES.size():
		if hero.position.y < WDC_FIXTURE_BASE_Y and absf(hero.position.x - CLUE_POSITIONS[index].x) < 48.0:
			mask |= 1 << index
	if mask != wdc_front_mask:
		wdc_front_mask = mask
		queue_redraw()
		wdc_front.queue_redraw()


func _wdc_blocked(at: Vector2) -> bool:
	for rect in WDC_ROOM_ONE_BLOCKERS:
		if rect.has_point(at):
			return true
	return false


func _slide(from: Vector2, to: Vector2, blocked: Callable) -> Vector2:
	# A start inside a blocker (e.g. an older save) may walk out freely.
	if not blocked.call(to) or blocked.call(from):
		return to
	if not blocked.call(Vector2(to.x, from.y)):
		return Vector2(to.x, from.y)
	if not blocked.call(Vector2(from.x, to.y)):
		return Vector2(from.x, to.y)
	return from


func _wdc_inspect_rect(index: int) -> Rect2:
	return Rect2(CLUE_POSITIONS[index].x - 40.0, 150.0, 80.0, 100.0)


func _build_yonkers_room_one() -> void:
	yonkers_room_one = true
	# Native pixel plate and sprites: keep texels crisp at the 2x integer window scale.
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	y_sort_enabled = true
	for index in YONKERS_ROOM_ONE_ANTENNAS.size():
		var antenna := Sprite2D.new()
		antenna.name = "YonkersAntenna%d" % index
		antenna.texture = YONKERS_ROOM_ONE_ANTENNAS[index]
		antenna.centered = false
		antenna.position = Vector2(CLUE_POSITIONS[index].x, YONKERS_ANTENNA_BASE_Y)
		antenna.offset = Vector2(-64, -YONKERS_ANTENNA_BASE_Y + 58)
		add_child(antenna)
	var foreground := Sprite2D.new()
	foreground.name = "YonkersForeground"
	foreground.texture = YONKERS_ROOM_ONE_FOREGROUND
	foreground.centered = false
	foreground.z_index = 1
	add_child(foreground)


func _yonkers_blocked(at: Vector2) -> bool:
	for rect in YONKERS_ROOM_ONE_BLOCKERS:
		if rect.has_point(at):
			return true
	return false


# STYLE48: the new background only in Washington room 2 with its flag (or the sdef35 RECORDS default once the
# creator authorizes it); --wdc-records-chamber-v01 alone and every other destination/room keep the original plate.
func _room_two_background() -> Texture2D:
	if destination_id == "scifi.ruins" and room == 2 and (OS.get_cmdline_user_args().has(WDC_RECORDS_STYLE48_FLAG) or SceneDefaults35.default_on(SceneDefaults35.RECORDS)):
		return WDC_RECORDS_STYLE48_BACKGROUND
	return ROOM_TWO_BACKGROUND[destination_id]


func _build_wdc_room_two() -> void:
	wdc_room_two = true
	y_sort_enabled = true
	var terminal := Sprite2D.new()
	terminal.name = "WdcRecordsTerminal"
	terminal.texture = WDC_ROOM_TWO_TERMINAL
	terminal.centered = false
	terminal.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	terminal.position = Vector2(WDC_ROOM_TWO_TERMINAL_ORIGIN.x, 0)
	terminal.offset = Vector2(0, WDC_ROOM_TWO_TERMINAL_ORIGIN.y)
	terminal.add_child(_wdc_room_two_marker(-1, terminal.position))
	add_child(terminal)
	for index in WDC_ROOM_TWO_FIXTURES.size():
		var fixture := Sprite2D.new()
		fixture.name = "WdcRecordsFixture%d" % index
		fixture.texture = WDC_ROOM_TWO_FIXTURES[index]
		fixture.centered = false
		fixture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		fixture.position = Vector2(CLUE_POSITIONS[index].x - 48.0, WDC_ROOM_TWO_SORT_Y)
		fixture.offset = Vector2(0, WDC_ROOM_TWO_FIXTURE_TOP - WDC_ROOM_TWO_SORT_Y)
		fixture.add_child(_wdc_room_two_marker(index, fixture.position))
		add_child(fixture)


# A marker drawn in room coordinates as a child of its fixture, so it stays above that fixture.
func _wdc_room_two_marker(index: int, parent_position: Vector2) -> Node2D:
	var marker := Node2D.new()
	marker.position = -parent_position + (WDC_ROOM_TWO_MARKER_LIFT if index >= 0 else Vector2.ZERO)
	marker.draw.connect(_draw_wdc_room_two_marker.bind(marker, index))
	wdc_room_two_markers.append(marker)
	return marker


func _draw_wdc_room_two_marker(marker: Node2D, index: int) -> void:
	if index >= 0:
		_draw_clue_marker(marker, index)
	else:
		var palette: Array = PALETTES[destination_id]
		_draw_annex_marker(TERMINAL_POSITION, palette[1] if AppState.survey_solved.has(destination_id) else Color("#e4c377"), true, marker)


func _wdc_room_two_blocked(at: Vector2) -> bool:
	for index in WDC_ROOM_TWO_BLOCKERS.size():
		if not wdc_room_two and WDC_ROOM_TWO_FIXTURE_BLOCKERS.has(index):
			continue
		if WDC_ROOM_TWO_BLOCKERS[index].has_point(at):
			return true
	return false


func _wdc_room_two_inspect_rect(index: int) -> Rect2:
	return Rect2(CLUE_POSITIONS[index].x - 54.0, 150.0, 108.0, 87.0)


func _draw_annex_marker(at: Vector2, color: Color, terminal: bool, target: CanvasItem = null) -> void:
	var canvas: CanvasItem = self if target == null else target
	canvas.draw_circle(at, 16.0, Color(0.04, 0.12, 0.16, 0.82))
	canvas.draw_arc(at, 14.0, 0.0, TAU, 28, color, 2.0)
	if terminal:
		canvas.draw_rect(Rect2(at + Vector2(-6, -5), Vector2(12, 9)), color, false, 1.5)
		canvas.draw_line(at + Vector2(-3, 7), at + Vector2(3, 7), color, 1.5)
	else:
		canvas.draw_line(at + Vector2(-4, -5), at + Vector2(3, 0), color, 2.0)
		canvas.draw_line(at + Vector2(3, 0), at + Vector2(-4, 5), color, 2.0)


func _build_hero() -> void:
	hero = Sprite2D.new()
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, "south")
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.offset = Vector2(0, -20)
	sprite_pilot = SpriteSetPilot.attach(hero, "protagonist-" + AppState.hero_appearance, "south")
	hero.position = Vector2(87, 261)
	add_child(hero)


func _start_audio() -> void:
	var ambience := AudioStreamPlayer.new()
	var music_context: String = {"scifi.city": "city", "scifi.outskirts": "field", "scifi.ruins": "ruins"}[destination_id]
	var stream: AudioStreamWAV = ThemedMusic.select(music_context, themed_music_override, themed_music_asset_dir)
	if stream == null:
		stream = load(AMBIENCE[destination_id]).duplicate()
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	if stream.loop_end <= stream.loop_begin:
		stream.loop_begin = 0
		stream.loop_end = int(round(stream.get_length() * stream.mix_rate))
	ambience.stream = stream
	ambience.volume_db = -12.0
	add_child(ambience)
	ambience.play()
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
	title_label = _label(canvas, Vector2(18, 6), 18, Color("#edf7f3"))
	progress_label = _label(canvas, Vector2(18, 34), 11, Color("#acc9c5"))
	save_button = _button(canvas, Vector2(418, 12), Vector2(98, 38), _open_save)
	back_button = _button(canvas, Vector2(525, 12), Vector2(98, 38), _back_room)
	for index in CLUE_POSITIONS.size():
		var label := _label(canvas, CLUE_POSITIONS[index] + Vector2(-48, -45), 11, Color("#f4e4b7"))
		label.size = Vector2(96, 36)
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.add_theme_color_override("font_outline_color", Color("#0d1920"))
		label.add_theme_constant_override("outline_size", 2)
		if yonkers_room_one:
			# Caption beside the floor marker so it never covers an antenna.
			label.position = YONKERS_ROOM_ONE_MARKERS[index] + Vector2(18, -9)
			label.size = Vector2(80, 18)
			label.autowrap_mode = TextServer.AUTOWRAP_OFF
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		elif wdc_room_two:
			# One line above the lifted disc, so a wrapped English name never covers the marker.
			label.position = CLUE_POSITIONS[index] + WDC_ROOM_TWO_MARKER_LIFT + Vector2(-70, -42)
			label.size = Vector2(140, 18)
			label.autowrap_mode = TextServer.AUTOWRAP_OFF
		clue_labels.append(label)
	exit_label = _label(canvas, EXIT_POSITION + Vector2(-38, -52), 10, Color("#e0e5cf"))
	next_label = _label(canvas, NEXT_POSITION + Vector2(-33, -52), 10, Color("#e0e5cf"))
	# Room 2 records chamber: beside the terminal disc instead of on the parallel-inscription plinth.
	terminal_label = _label(canvas, TERMINAL_POSITION + (Vector2(20, -8) if wdc_room_two else Vector2(-46, -48)), 11, Color("#f1e0ac"))
	for label in [exit_label, next_label, terminal_label]:
		label.add_theme_color_override("font_outline_color", Color("#0d1920"))
		label.add_theme_constant_override("outline_size", 2)
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 318)
	footer.size = Vector2(640, 42)
	canvas.add_child(footer)
	help_label = _label(canvas, Vector2(18, 327), 11, Color("#c0d5d1"))
	_build_overlay(canvas)


func _build_overlay(canvas: CanvasLayer) -> void:
	overlay = ColorRect.new()
	overlay.color = Color(0.04, 0.08, 0.12, 0.93)
	overlay.size = Vector2(640, 360)
	overlay.visible = false
	canvas.add_child(overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(53, 41)
	panel.size = Vector2(534, 278)
	panel.color = Color("#29434d")
	overlay.add_child(panel)
	overlay_title = _label(overlay, Vector2(75, 58), 19, Color("#f0e2bd"))
	overlay_body = RichTextLabel.new()
	overlay_body.position = Vector2(75, 95)
	overlay_body.size = Vector2(488, 92)
	overlay_body.scroll_active = true
	overlay_body.add_theme_font_size_override("normal_font_size", 13)
	overlay.add_child(overlay_body)
	for index in 3:
		var button := _button(overlay, Vector2(75, 190 + index * 34), Vector2(488, 30), _choose_answer.bind(index))
		button.add_theme_font_size_override("font_size", 11)
		option_buttons.append(button)
	for index in 6:
		var button := _button(overlay, Vector2(75 + (index % 2) * 249, 155 + (index / 2) * 37), Vector2(239, 32), _select_link_clue.bind(index))
		button.add_theme_font_size_override("font_size", 11)
		link_buttons.append(button)
	notes_button = _button(overlay, Vector2(409, 56), Vector2(154, 29), _open_notes)
	previous_note_button = _button(overlay, Vector2(75, 275), Vector2(145, 32), _shift_note.bind(-1))
	next_note_button = _button(overlay, Vector2(232, 275), Vector2(145, 32), _shift_note.bind(1))
	close_button = _button(overlay, Vector2(409, 275), Vector2(154, 32), _on_close_button)


func _label(parent: Node, position: Vector2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = position
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)
	return label


func _button(parent: Node, position: Vector2, size: Vector2, callback: Callable) -> Button:
	var button := Button.new()
	button.position = position
	button.size = size
	button.pressed.connect(callback)
	parent.add_child(button)
	return button


func _refresh_text() -> void:
	var data := _data()
	title_label.text = AppState.destination_name(destination_id) + " · " + String(data["rooms"][room - 1])
	title_label.add_theme_font_size_override("font_size", 14 if AppState.language == "en" and (destination_id in ["scifi.city", "scifi.ruins"]) else 18)
	progress_label.text = AppState.text_for("survey_progress") % [_clue_count(), AppState.text_for("field_yes" if AppState.survey_solved.has(destination_id) else "field_no")]
	help_label.text = AppState.text_for("survey_help")
	back_button.text = AppState.text_for("survey_leave" if room == 1 else "survey_previous")
	save_button.text = AppState.text_for("save_open")
	if yonkers_room_one:
		# "Return outside" overflows a 98 px button in English: widen it and shift Save left (this room only).
		var wide := AppState.language == "en"
		save_button.position.x = 398.0 if wide else 418.0
		back_button.position.x = 503.0 if wide else 525.0
		back_button.size.x = 125.0 if wide else 98.0
	elif destination_id in ["scifi.ruins", "scifi.city"]:
		# Washington and NYC rooms: a label too long for the 98 px button ("Return outside", "Outer room") steps its
		# font down until it fits; labels that already fit keep the default size.
		back_button.remove_theme_font_size_override("font_size")
		var font_size := back_button.get_theme_font_size("font_size")
		while font_size > 11 and back_button.get_minimum_size().x > 98.0:
			font_size -= 1
			back_button.add_theme_font_size_override("font_size", font_size)
		back_button.size = Vector2(98, 38)
	for index in CLUE_POSITIONS.size():
		clue_labels[index].text = String(data["clues"][(room - 1) * 3 + index]["name"])
	exit_label.text = AppState.text_for("survey_leave" if room == 1 else "survey_previous")
	next_label.text = AppState.text_for("survey_next")
	next_label.visible = room == 1
	terminal_label.text = AppState.text_for("survey_terminal")
	terminal_label.visible = room == 2
	if overlay.visible:
		_refresh_overlay()
	queue_redraw()
	for marker in wdc_room_two_markers:
		marker.queue_redraw()


func _refresh_overlay() -> void:
	var data := _data()
	for button in option_buttons:
		button.visible = overlay_mode == "question"
	for button in link_buttons:
		button.visible = overlay_mode == "link"
	notes_button.visible = overlay_mode in ["link", "question", "message"] and _clue_count() > 0
	notes_button.text = AppState.text_for("survey_notes")
	previous_note_button.visible = overlay_mode == "notes"
	next_note_button.visible = overlay_mode == "notes"
	previous_note_button.text = AppState.text_for("survey_notes_previous")
	next_note_button.text = AppState.text_for("survey_notes_next")
	close_button.visible = overlay_mode != "question"
	close_button.text = AppState.text_for("survey_notes_back" if overlay_mode == "notes" else ("survey_link_continue" if overlay_mode == "link" and _link_count() == 3 else "survey_close"))
	overlay_body.size.y = 151 if overlay_mode == "notes" else (50 if overlay_mode == "link" else 92)
	match overlay_mode:
		"clue":
			var clue: Dictionary = data["clues"][overlay_clue_index]
			overlay_title.text = String(clue["name"])
			overlay_body.text = String(clue["text"])
		"question":
			overlay_title.text = AppState.text_for("survey_terminal")
			overlay_body.text = String(data["question"]) + ("\n" + overlay_message if overlay_message != "" else "")
			for index in 3:
				option_buttons[index].text = String(data["options"][index])
		"link":
			overlay_title.text = AppState.text_for("survey_link_title")
			overlay_body.text = overlay_message if overlay_message != "" else AppState.text_for("survey_link_instruction") % _link_count()
			for index in 6:
				var prefix := "▶ " if link_selected_index == index else ("✓ " if _linked_clue(index) else "")
				link_buttons[index].text = prefix + String(data["clues"][index]["name"])
		"message":
			overlay_title.text = AppState.text_for("survey_terminal")
			overlay_body.text = overlay_message
		"notes":
			var clue: Dictionary = data["clues"][notes_index]
			overlay_title.text = AppState.text_for("survey_notes") + " %d/6" % (notes_index + 1)
			overlay_body.text = String(clue["name"]) + "\n\n" + String(clue["text"])
			previous_note_button.disabled = _clue_count() < 2
			next_note_button.disabled = _clue_count() < 2


func _inspect_clue(index: int) -> void:
	if index < 0 or index >= 6:
		return
	if not AppState.survey_clues.has(_clue_key(index)):
		AppState.survey_clues[_clue_key(index)] = true
		AppState.write_auto_save("annex", hero.position, "survey_note")
		cue_player.play()
	overlay_clue_index = index
	overlay_mode = "clue"
	overlay.visible = true
	_refresh_text()
	close_button.grab_focus()


func _open_question() -> void:
	overlay.visible = true
	if AppState.survey_solved.has(destination_id):
		overlay_mode = "message"
		overlay_message = AppState.text_for("survey_completed")
	elif _clue_count() < 6:
		overlay_mode = "message"
		overlay_message = AppState.text_for("survey_locked")
	elif _link_count() < 3:
		overlay_mode = "link"
		overlay_message = ""
		link_selected_index = -1
	else:
		overlay_mode = "question"
		overlay_message = ""
	_refresh_text()
	(option_buttons[0] if overlay_mode == "question" else (link_buttons[0] if overlay_mode == "link" else close_button)).grab_focus()


func _select_link_clue(index: int) -> void:
	if overlay_mode != "link" or index < 0 or index >= 6:
		return
	if link_selected_index < 0:
		link_selected_index = index
		overlay_message = AppState.text_for("survey_link_instruction") % _link_count()
		_refresh_overlay()
		return
	if link_selected_index == index:
		link_selected_index = -1
		overlay_message = ""
		_refresh_overlay()
		return
	var first := link_selected_index
	link_selected_index = -1
	var data := _data()
	for link_index in 3:
		var link: Dictionary = data["links"][link_index]
		var pair: Array = link["pair"]
		if pair.has(first) and pair.has(index):
			if AppState.survey_links.has(_link_key(link_index)):
				overlay_message = AppState.text_for("survey_link_found")
			else:
				AppState.survey_links[_link_key(link_index)] = true
				AppState.write_auto_save("annex", hero.position, "survey_note")
				cue_player.play()
				overlay_message = String(link["insight"]) + "\n" + AppState.text_for("survey_link_instruction") % _link_count()
			_refresh_overlay()
			return
	overlay_message = AppState.text_for("survey_link_wrong")
	AppState.record_playtest_mistake("pair", destination_id)
	_refresh_overlay()


func _on_close_button() -> void:
	if overlay_mode == "notes":
		overlay_mode = notes_return_mode
		_refresh_overlay()
		(notes_button if notes_button.visible else close_button).grab_focus()
	elif overlay_mode == "link" and _link_count() == 3:
		_open_question()
	else:
		_close_overlay()


func _open_notes() -> void:
	if not overlay.visible or overlay_mode == "notes" or _clue_count() == 0:
		return
	AppState.record_playtest_event("notes_open", destination_id)
	notes_return_mode = overlay_mode
	for index in 6:
		if AppState.survey_clues.has(_clue_key(index)):
			notes_index = index
			break
	overlay_mode = "notes"
	_refresh_overlay()
	next_note_button.grab_focus()


func _shift_note(direction: int) -> void:
	if overlay_mode != "notes":
		return
	var available: Array[int] = []
	for index in 6:
		if AppState.survey_clues.has(_clue_key(index)):
			available.append(index)
	if available.size() < 2:
		return
	var current := available.find(notes_index)
	notes_index = available[posmod(current + direction, available.size())]
	_refresh_overlay()


func _choose_answer(index: int) -> void:
	if overlay_mode != "question":
		return
	var data := _data()
	if index != int(data["answer"]):
		overlay_message = AppState.text_for("survey_retry")
		AppState.record_playtest_mistake("judgment", destination_id)
		_refresh_overlay()
		return
	if not AppState.survey_solved.has(destination_id):
		AppState.survey_solved[destination_id] = true
		AppState.record_playtest_event("survey_complete", destination_id)
		AppState.award_survey_jp()
		AppState.write_auto_save("annex", hero.position, "survey_note")
		cue_player.play()
	overlay_mode = "message"
	overlay_message = String(data["success"]) + "\n" + AppState.text_for("survey_reward")
	_refresh_text()
	close_button.grab_focus()


func _close_overlay() -> void:
	overlay.visible = false
	overlay_mode = ""
	back_button.grab_focus()


func _go_next_room() -> void:
	if room != 1:
		return
	AppState.current_annex_room = 2
	AppState.resume_annex_pending = false
	get_tree().change_scene_to_file("res://scenes/survey_annex.tscn")


func _back_room() -> void:
	if overlay.visible:
		if overlay_mode == "notes":
			_on_close_button()
		else:
			_close_overlay()
		return
	if room == 2:
		AppState.current_annex_room = 1
		AppState.resume_annex_position = Vector2(555, 257)
		AppState.resume_annex_pending = true
		get_tree().change_scene_to_file("res://scenes/survey_annex.tscn")
	else:
		AppState.resume_area_position = AppState.annex_surface_return_position
		AppState.resume_area_pending = true
		get_tree().change_scene_to_file("res://scenes/scifi_exploration_area.tscn")


func _open_save() -> void:
	AppState.save_screen_mode = "save"
	AppState.save_return_scene = "res://scenes/survey_annex.tscn"
	AppState.save_return_position = hero.position
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_back_room()
	elif event.is_action_pressed("interact"):
		if overlay.visible:
			return
		for index in CLUE_POSITIONS.size():
			if hero.position.distance_to(CLUE_POSITIONS[index]) < 45.0 or (wdc_front != null and _wdc_inspect_rect(index).has_point(hero.position)) \
					or (yonkers_room_one and hero.position.distance_to(YONKERS_ROOM_ONE_MARKERS[index]) < 42.0) \
					or (wdc_room_two and _wdc_room_two_inspect_rect(index).has_point(hero.position)):
				_inspect_clue((room - 1) * 3 + index)
				return
		if room == 2 and hero.position.distance_to(TERMINAL_POSITION) < 46.0:
			_open_question()
		elif hero.position.distance_to(EXIT_POSITION) < 46.0:
			_back_room()
		elif room == 1 and hero.position.distance_to(NEXT_POSITION) < 46.0:
			_go_next_room()
