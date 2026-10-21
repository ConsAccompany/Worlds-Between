extends Node2D

# Result-only drawing surface for the opt-in encounter pilot. It lives on its own
# high canvas layer so finished-battle effects stay above the result overlay.
class EncounterResultSurface extends Node2D:
	var module: RefCounted = null

	func _draw() -> void:
		if module != null:
			module.draw(self)

const ENEMIES := {
	"patrol": {"name": "enemy_patrol", "max_hp": 64, "damage": 12, "speed": 55.0, "windup": 0.65, "cooldown": 1.35, "color": Color("#ab5b52")},
	"sentry": {"name": "enemy_sentry", "max_hp": 96, "damage": 18, "speed": 68.0, "windup": 0.48, "cooldown": 1.10, "color": Color("#96516f")},
}
const MOVE_SPEED := 168.0
const DODGE_COST := 12
const GUARD_HIT_COST := 6
const BATTLE_AMBIENCE := preload("res://assets/audio/rpg-2-star-ocean-the-second_scifi-battle_ambient-loop_m7_20261013-211230-37fcaa02.wav")
const ThemedMusic := preload("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd")
# Unapproved audio pilot: disabled by default; the existing player/settings/fallback stay in use.
static var themed_music_override := -1
static var themed_music_asset_dir := ThemedMusic.DEFAULT_ASSET_DIR
const MaleCombatFrames := preload("res://scripts/rpg-2-star-ocean-the-second_protagonist-male_sideview-combat-frames_m8-prototype_20261014-142500-75b6d7ec.gd")
const FemaleCombatFrames := preload("res://scripts/rpg-2-star-ocean-the-second_protagonist-female_sideview-combat-frames_m8-prototype_20261014-143330-d94057ea.gd")
const LiangCombatFrames := preload("res://scripts/rpg-2-star-ocean-the-second_liang-xu_sideview-combat-frames_m8-prototype_20261014-144100-a41f6b9c.gd")
const ZhaoCombatFrames := preload("res://scripts/rpg-2-star-ocean-the-second_zhao-ling_sideview-combat-frames_m8-prototype_20261014-144510-9d264ec4.gd")
const JiCombatFrames := preload("res://scripts/rpg-2-star-ocean-the-second_ji-cheng_sideview-combat-frames_m8-prototype_20261014-144950-51da030d.gd")
const HERO_COMBAT_ANCHOR := Vector2(30, 73)
const HERO_COMBAT_ACTION_DURATION := {"attack": 0.39, "hit": 0.24, "skill": 0.45, "down": 0.30}
const ARENA_FLOOR_Y := 272.0
# M8 sentry automaton sprite + animation v2 pilot (UNAPPROVED; art acceptance 0). The creator approved v2 as the action
# direction baseline only, not the sprite or its art. Opt-in only: launch with `-- --sentry-v2-pilot`, or set
# sentry_v2_override = 1 before the battle scene loads. Off by default, so the sentry keeps the placeholder block.
# Visual only: stats, reach, AI, timers and positions are the same with the pilot on or off.
const SENTRY_V2_CLI_FLAG := "--sentry-v2-pilot"
const SENTRY_V2_ART_APPROVED := false
const SENTRY_V2_SPRITE_ACCEPTED := false
const ENEMY_SPRITE_PILOTS := {
	# It is low and 96 px wide, so its wind-up ring is a wider ellipse that clears the silhouette.
	"sentry": {"path": "res://assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png", "anchor": Vector2(48, 60), "telegraph_center_y": 241.0, "telegraph_scale": Vector2(2.0, 1.2)},
}
# One strip of equal cells. Without "cell" / "anchor" the cells match the static pilot and share its anchor. Strike and hit play once; defeat holds its last frame.
# v2 (visual only): 112 px cells anchored at static x 30, so the sprite sits 18 px further from the party and the heroes no longer cover its eye and claw.
# The ring follows "body_center_x". "gait_step_px" picks gait frames by distance and moves the drawn sprite in those steps, so planted feet stay put.
# "front_states" draw over the fighters (its own strike).
const ENEMY_SPRITE_ANIMATIONS := {
	"sentry": {
		"path": "res://assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v02_20261014-230329-ffefdc6f.png",
		"cell": Vector2(112, 62),
		"anchor": Vector2(46, 60),
		"body_center_x": 64.0,
		"states": {"idle": [0, 1, 2, 3], "move": [4, 5, 6, 7, 8, 9, 10, 11], "windup": [12, 13], "strike": [14, 15], "hit": [16, 17], "defeat": [18, 19, 20]},
		"frame_time": {"idle": 0.22, "strike": 0.15, "hit": 0.12, "defeat": 0.16},
		"gait_step_px": 4.0,
		"move_grace": 0.08,
		"front_states": ["strike"],
	},
}
# Patrol machine battle animation pilot v01 (UNAPPROVED; art acceptance 0). Opt-in only: launch with
# `-- --patrol-battle-animation-pilot`, or set patrol_animation_override = 1 before the battle scene loads. Off by default,
# so the patrol keeps the placeholder block and the loader script is never loaded. It is independent of the sentry flag.
# Any package, file or type defect keeps the placeholder. Visual only: stats, reach, AI, timers and positions are unchanged.
const PATROL_ANIMATION_CLI_FLAG := "--patrol-battle-animation-pilot"
const PATROL_ANIMATION_ART_APPROVED := false
const PATROL_ANIMATION_LOADER := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-loader_v01_20261019-194007-a4b10a85.gd"
const PATROL_ANIMATION_PACKAGE := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-runtime-package_v01_20261019-194007-a4b10a85.json"
const ENEMY_WINDUP_MODULATE := Color(1.0, 0.70, 0.66)
const ENEMY_TELEGRAPH_CENTER_Y := 240.0
const ENEMY_TELEGRAPH_RADIUS := 30.0
const ENEMY_TELEGRAPH_COLOR := Color(1.0, 0.23, 0.20, 0.28)
# Battle backdrop loader pilot: a TECHNICAL capability. Every band below is UNAPPROVED candidate art (acceptance 0), and none is
# the default. Opt-in only: launch with `-- --battle-backdrop-pilot`, or set battle_backdrop_override = 1 before the battle scene
# loads. Off by default, so every battle keeps the geometric backdrop. The arena comes from the battle's destination;
# `-- --battle-backdrop-arena=<id>` or battle_backdrop_arena_override picks one directly (no battle starts in the archive yet).
# An arena without a band, a missing file or a band that is not an integer multiple of the play band falls back to the geometric
# backdrop. Visual only: stats, AI, input, timers and positions are the same with the pilot on or off.
const BATTLE_BACKDROP_CLI_FLAG := "--battle-backdrop-pilot"
# Editable environment candidate; explicit opt-in, no combat or default change.
const BATTLE_NATIVE_ENVIRONMENT_FLAG := "--battle-native-environment-v01"
const BATTLE_NATIVE_ENVIRONMENT_PATH := "res://assets/environments/battle-native-v01/rpg-2-star-ocean-the-second_outskirts-arena_merged-flat_env12-v01_20261020-230516-b1e5838c.png"
const BATTLE_BACKDROP_ARENA_ARG := "--battle-backdrop-arena="
const BATTLE_BACKDROP_ART_APPROVED := false
# The logical play band between the opaque header (0-90) and footer (302-360).
const BATTLE_BACKDROP_RECT := Rect2i(0, 90, 640, 212)
const BATTLE_ARENA_BY_DESTINATION := {"scifi.city": "city-terrace", "scifi.outskirts": "outskirts", "scifi.ruins": "ruins"}
# Tracked 1280x424 bands only (2x the play band). city-terrace and ruins have no tracked band, so they keep the geometric backdrop.
const BATTLE_BACKDROP_BANDS := {
	"archive": "res://assets/environments/rpg-2-star-ocean-the-second_scifi-archive-battle-arena_runtime-band_m8-candidate_20261014-213622-14315e18.png",
	"outskirts": "res://assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-battle-arena_runtime-band_m8-candidate_20261014-213622-14315e18.png",
}
# Combat sprite set pilot: a TECHNICAL capability that loads data-driven high-density side-view action sets for the party
# (contract in the helper below). No set is approved art (acceptance 0) and none is the default. Opt-in only: launch with
# `-- --combat-sprite-set-pilot`, or set combat_sprite_set_override = 1 before the battle scene loads. Off by default, so every
# fighter keeps its existing frames and the helper is never created. The index defaults to the SYNTHETIC DIAGNOSTIC test
# fixtures (not art); `-- --combat-sprite-set-index=<res path>` or combat_sprite_set_index_override picks another index.
# A fighter without a valid set (missing, invalid, unknown or partial) keeps its existing frames. Visual only: stats, reach,
# AI, input, hit timing, positions, party order and saves are the same with the pilot on or off.
# Exception (prepared, creator adoption pending, art UNAPPROVED): see heroine_default_battle_applies() for the female hero.
const HeroineDefault := preload("res://scripts/hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd")
const CombatSpriteSets := preload("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd")
const BattleVfx := preload("res://scripts/rpg-2-star-ocean-the-second_common-vfx_native-layer_root-v02_20261019-164412-1f3bff80.gd")
const COMMON_VFX_ASSET_DIR := "res://assets/vfx/common-v01"
const BattleUiSkin := preload("res://scripts/rpg-2-star-ocean-the-second_battle-ui_skin-helper_root-v02_20261019-172332-dc55a291.gd")
const BATTLE_UI_SKIN_CLI_FLAG := "--battle-ui-skin-pilot"
static var battle_ui_skin_override := -1
const SkillVfx := preload("res://scripts/rpg-2-star-ocean-the-second_mvp-skill-vfx_native-layer_v01_20261019-170721-90a8737c.gd")
const SKILL_VFX_ASSET_DIR := "res://assets/vfx/skills-v01"
const SKILL_VFX_CLI_FLAG := "--mvp-skill-vfx-pilot"
static var skill_vfx_override := -1
const BATTLE_VFX_CLI_FLAG := "--battle-vfx-pilot"
static var battle_vfx_override := -1
# Optional four-effect encounter pilot (presentation only, UNAPPROVED). Opt-in only: launch with
# `-- --encounter-feedback-pilot`, or set encounter_feedback_override = 1 before the battle scene loads. Off by
# default, so the module and its assets are never created. Missing or invalid assets draw nothing.
const EncounterFeedback := preload("res://scripts/rpg-2-star-ocean-the-second_encounter_feedback-layer_timing-v03_20261019-003109-1e5c2cef.gd")
const ENCOUNTER_FEEDBACK_CLI_FLAG := "--encounter-feedback-pilot"
const ENCOUNTER_FEEDBACK_ASSET_DIR := "res://assets/vfx/encounter-v02"
static var encounter_feedback_override := -1

const COMBAT_SPRITE_SET_CLI_FLAG := "--combat-sprite-set-pilot"
const COMBAT_SPRITE_SET_INDEX_ARG := "--combat-sprite-set-index="
const COMBAT_SPRITE_SET_ART_APPROVED := false
const COMBAT_SPRITE_SET_INDEX := "res://tests/fixtures/csp-fixture-v01_03f4172a/rpg-2-star-ocean-the-second_combat-set_fixture-index_not-art-v01_20261018-153656-03f4172a.json"
# Heroine contact timing pilot (UNAPPROVED, TECHNICAL). Opt-in only: launch with `-- --heroine-sea-contact-pilot`, or set
# heroine_sea_contact_override = 1 before the battle scene loads. Off by default, so every fighter keeps the immediate attack.
# Scoped to the female protagonist only ("hero" with appearance female); every other fighter and the enemy are unchanged.
# Her attack request starts a per-fighter event (monotonic id, elapsed 0, latched facing); damage, VFX and the shared bonus
# resolve exactly once at contact (5/30 s, range rechecked then); recovery ends at 12/30 s. Cooldown (0.43 s) and the attack
# count are spent at the request. A dodge, skill, job skill, hit or down before contact cancels it with no damage and no
# refund; a result, pause or scene exit never resolves it. Draw with --combat-sprite-set-pilot to share the event clock.
const HEROINE_CONTACT_CLI_FLAG := "--heroine-sea-contact-pilot"
const HEROINE_CONTACT_ART_APPROVED := false
const HEROINE_CONTACT_TICK_RATE := 30
const HEROINE_CONTACT_TICKS := 5
const HEROINE_RECOVERY_END_TICKS := 12
const HEROINE_CONTACT_LOG_LIMIT := 64

static var sentry_v2_override := -1
static var patrol_animation_override := -1
static var patrol_animation_package_override := ""
static var battle_backdrop_override := -1
static var battle_backdrop_arena_override := ""
static var combat_sprite_set_override := -1
static var combat_sprite_set_index_override := ""
# Actor-scoped male demonstration profile; it cannot suppress the authorized heroine default.
static var male_playable_path_index_override := ""
static var heroine_sea_contact_override := -1
# Opt-in member-scoped companion combat set (zpath27); "" = off. Separate from combat_sprite_sets so hero sets stay exact.
static var companion_combat_member_override := ""
static var companion_combat_index_override := ""

var enemy_id := "patrol"
var enemy: Dictionary
var enemy_x := 493.0
var enemy_hp := 0
var enemy_cooldown := 0.6
var enemy_windup := 0.0
var enemy_target_index := 0
var enemy_attack_count := 0
var player_attack_count := 0
var fighters: Array[Dictionary] = []
var controlled_index := 0
var auto_mode := false
var paused := false
var queued_skill := false
var queued_job_skill := false
var queued_job_skill_id := ""
var selected_order_id := ""
var next_attack_bonus := 0
# Heroine contact pilot: monotonic event ids across the battle, and a bounded resolution log for checks.
var contact_event_serial := 0
var contact_event_log: Array[Dictionary] = []
var battle_finished := false
# Presentation-only hold: a valid Patrol pilot defeat is visible before the victory panel.
var patrol_result_pending := false
var heroine_result_pending := false
# Authored defeat is visible before results; existing two-second return timer is preserved.
var heroine_defeat_result_pending := false
var patrol_result_elapsed := 0.0
var battle_won := false
var feedback_key := "battle_ready"
var feedback_message := ""
var result_reward_text := ""
var result_reward_xp := 0
var result_reward_jp := 0
# Per-instance switches only narrow the opt-in pilot (static only, or none); they never enable it without the flag.
var enemy_sprite_pilot_enabled := true
var enemy_sprite_override := ""
var enemy_texture: Texture2D
var enemy_anchor := Vector2.ZERO
var enemy_telegraph_center_y := ENEMY_TELEGRAPH_CENTER_Y
var enemy_telegraph_scale := Vector2.ONE
var enemy_sprite_animation_enabled := true
var enemy_animation_override := ""
var enemy_animation_texture: Texture2D
var enemy_animation: Dictionary = {}
var enemy_animation_cell := Vector2.ZERO
var enemy_animation_anchor := Vector2.ZERO
var enemy_visual_state := "idle"
var enemy_visual_clock := 0.0
var enemy_visual_last_hp := 0
var enemy_visual_last_attack_count := 0
var enemy_visual_still_time := 0.0
var enemy_visual_gait_origin_x := 0.0
# Like the sentry switches, the path override only swaps the band file of the opt-in pilot; it never enables the pilot.
var battle_backdrop_path_override := ""
var battle_backdrop_arena_id := ""
var battle_backdrop_status := "off"
var battle_backdrop_texture: Texture2D
# Null unless the combat sprite set pilot is on.
var combat_sprite_sets: RefCounted = null
# Null unless the companion override loads exactly its own member slot.
var companion_sprite_sets: RefCounted = null
var companion_index := -1
# True only while the prepared heroine default (not an explicit flag/override) drives the hero set and contact.
var heroine_default_active := false
# Opt-in provisional presentation only; disabled renderer and simulation stay unchanged.
var battle_ui_skin: RefCounted = null
var battle_ui_skin_status := "off"
var battle_vfx: RefCounted = null
var skill_vfx: RefCounted = null
# Null unless the encounter feedback pilot is on; its module and assets load only in that case.
var encounter_feedback: RefCounted = null
# Foreground result surface, created with the module and hidden until a finished battle has effects.
var encounter_result_layer: CanvasLayer = null
var encounter_result_surface: EncounterResultSurface = null

var title_label: Label
var help_label: Label
var feedback_label: Label
var hp_label: Label
var energy_label: Label
var enemy_hp_label: Label
var hp_bar: ProgressBar
var energy_bar: ProgressBar
var enemy_bar: ProgressBar
var telegraph_label: Label
var party_buttons: Array[Button] = []
var auto_button: Button
var quick_skill_button: Button
var pause_overlay: ColorRect
var pause_title: Label
var pause_skill_button: Button
var pause_job_skill_buttons: Array[Button] = []
var pause_target_label: Label
var pause_order_feedback: Label
var pause_policy_button: Button
var pause_target_buttons: Array[Button] = []
var pause_order_buttons: Dictionary = {}
var pause_resume_button: Button
var result_overlay: ColorRect
var result_title: Label
var result_note: Label
var result_button: Button


static func patrol_animation_enabled() -> bool:
	if patrol_animation_override >= 0:
		return patrol_animation_override == 1
	return OS.get_cmdline_user_args().has(PATROL_ANIMATION_CLI_FLAG)


static func sentry_v2_enabled() -> bool:
	if sentry_v2_override >= 0:
		return sentry_v2_override == 1
	return OS.get_cmdline_user_args().has(SENTRY_V2_CLI_FLAG)


static func battle_backdrop_enabled() -> bool:
	if battle_backdrop_override >= 0:
		return battle_backdrop_override == 1
	return OS.get_cmdline_user_args().has(BATTLE_BACKDROP_CLI_FLAG)


static func battle_backdrop_arena(destination_id: String) -> String:
	var arena_id := battle_backdrop_arena_override
	if arena_id == "":
		for argument in OS.get_cmdline_user_args():
			if argument.begins_with(BATTLE_BACKDROP_ARENA_ARG):
				arena_id = argument.trim_prefix(BATTLE_BACKDROP_ARENA_ARG)
	return arena_id if arena_id != "" else BATTLE_ARENA_BY_DESTINATION.get(destination_id, "")


static func combat_sprite_set_enabled() -> bool:
	if combat_sprite_set_override >= 0:
		return combat_sprite_set_override == 1
	return OS.get_cmdline_user_args().has(COMBAT_SPRITE_SET_CLI_FLAG)


static func heroine_sea_contact_enabled() -> bool:
	if heroine_sea_contact_override >= 0:
		return heroine_sea_contact_override == 1
	return OS.get_cmdline_user_args().has(HEROINE_CONTACT_CLI_FLAG)


# Prepared heroine default (creator adoption pending, art UNAPPROVED): the female hero gets the heroine combat set and
# contact timing exactly as the opt-in path does, but only when no combat set flag/override/index and no explicit contact
# enable is given (contact override 0 still keeps the immediate attack) and the whole pinned heroine package passes.
static func heroine_default_battle_applies(party_ids: Array, appearance: String) -> bool:
	if appearance != "female" or not party_ids.has("hero"):
		return false
	var args := OS.get_cmdline_user_args()
	if combat_sprite_set_override >= 0 or args.has(COMBAT_SPRITE_SET_CLI_FLAG) or combat_sprite_set_index_override != "":
		return false
	for argument in args:
		if argument.begins_with(COMBAT_SPRITE_SET_INDEX_ARG):
			return false
	if heroine_sea_contact_override == 1 or (heroine_sea_contact_override < 0 and args.has(HEROINE_CONTACT_CLI_FLAG)):
		return false
	return HeroineDefault.package_ok()


static func combat_sprite_set_index() -> String:
	if combat_sprite_set_index_override != "":
		return combat_sprite_set_index_override
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(COMBAT_SPRITE_SET_INDEX_ARG):
			return argument.trim_prefix(COMBAT_SPRITE_SET_INDEX_ARG)
	return COMBAT_SPRITE_SET_INDEX


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	enemy_id = AppState.battle_enemy_id if ENEMIES.has(AppState.battle_enemy_id) else "patrol"
	enemy = ENEMIES[enemy_id]
	enemy_hp = int(enemy["max_hp"])
	heroine_default_active = heroine_default_battle_applies(AppState.active_party_ids, AppState.hero_appearance)
	var heroine_contact := heroine_sea_contact_enabled() or (heroine_default_active and heroine_sea_contact_override < 0)
	for index in AppState.active_party_ids.size():
		fighters.append({"id": AppState.active_party_ids[index], "x": 135.0 + index * 36.0, "attack_cooldown": 0.0, "dodge_cooldown": 0.0, "dodge_time": 0.0, "dodge_direction": -1.0, "skill_cooldown": 0.0, "command": "default", "guard": false, "boost": 0, "visual_action": "", "visual_elapsed": 0.0, "visual_loop_kind": "idle", "visual_loop_clock": 0.0, "visual_moving": false})
		# Only the pilot fighter carries event keys; their presence selects the contact path and the loader's explicit clock.
		if heroine_contact and AppState.active_party_ids[index] == "hero" and AppState.hero_appearance == "female":
			fighters[index].merge({"contact_event_id": 0, "contact_event_clock": 0.0, "contact_event_facing": 0, "contact_event_active": false, "contact_event_state": "none"})
	_load_enemy_sprite_pilot()
	_load_battle_backdrop()
	_load_combat_sprite_sets()
	_load_companion_sprite_sets()
	if battle_vfx_override == 1 or (battle_vfx_override < 0 and OS.get_cmdline_user_args().has(BATTLE_VFX_CLI_FLAG)):
		battle_vfx = BattleVfx.new(COMMON_VFX_ASSET_DIR)
	if skill_vfx_override == 1 or (skill_vfx_override < 0 and OS.get_cmdline_user_args().has(SKILL_VFX_CLI_FLAG)):
		skill_vfx = SkillVfx.new(SKILL_VFX_ASSET_DIR)
	if encounter_feedback_override == 1 or (encounter_feedback_override < 0 and OS.get_cmdline_user_args().has(ENCOUNTER_FEEDBACK_CLI_FLAG)):
		encounter_feedback = EncounterFeedback.new(ENCOUNTER_FEEDBACK_ASSET_DIR)
		_build_encounter_result_surface()
		_emit_encounter_feedback("encounter", _encounter_party_origin())
	_build_ui()
	var audio_player := AudioStreamPlayer.new()
	var ambient: AudioStreamWAV = ThemedMusic.select("battle", themed_music_override, themed_music_asset_dir)
	if ambient == null:
		ambient = BATTLE_AMBIENCE.duplicate()
	ambient.loop_mode = AudioStreamWAV.LOOP_FORWARD
	if ambient.loop_end <= ambient.loop_begin:
		ambient.loop_begin = 0
		ambient.loop_end = int(round(ambient.get_length() * ambient.mix_rate))
	audio_player.stream = ambient
	audio_player.volume_db = -13.0
	add_child(audio_player)
	audio_player.play()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	if battle_ui_skin_override == 1 or (battle_ui_skin_override < 0 and OS.get_cmdline_user_args().has(BATTLE_UI_SKIN_CLI_FLAG)):
		battle_ui_skin = BattleUiSkin.new("res://assets/ui/battle-skin-v01")
		battle_ui_skin_status = "applied" if battle_ui_skin.apply(self) else "fallback"
	AppState.last_battle_transition_ms = float(Time.get_ticks_usec() - AppState.battle_transition_started_usec) / 1000.0
	print("BATTLE_TRANSITION_MS %.2f" % AppState.last_battle_transition_ms)


func _process(delta: float) -> void:
	if paused:
		return
	if battle_vfx != null:
		battle_vfx.advance(delta)
	if skill_vfx != null:
		skill_vfx.advance(delta)
	if encounter_feedback != null:
		encounter_feedback.advance(delta)
	if battle_finished:
		_advance_finished_contact_recovery(delta)
		_advance_fighter_visuals(delta, [])
		_advance_combat_sprite_sets(delta)
		_advance_enemy_visual(delta, false)
		_advance_patrol_result_presentation(delta)
		_refresh_encounter_result_surface()
		queue_redraw()
		return
	var initial_positions: Array[float] = []
	for fighter in fighters:
		initial_positions.append(float(fighter["x"]))
	# Pilot events requested in earlier frames advance first; requests made later in this frame start at elapsed 0.
	_advance_contact_events(delta)
	if battle_finished:
		_advance_fighter_visuals(delta, [])
		_advance_combat_sprite_sets(delta)
		_advance_enemy_visual(delta, false)
		_update_hud()
		queue_redraw()
		return
	for fighter in fighters:
		fighter["attack_cooldown"] = maxf(0.0, float(fighter["attack_cooldown"]) - delta)
		fighter["dodge_cooldown"] = maxf(0.0, float(fighter["dodge_cooldown"]) - delta)
		fighter["dodge_time"] = maxf(0.0, float(fighter["dodge_time"]) - delta)
		fighter["skill_cooldown"] = maxf(0.0, float(fighter["skill_cooldown"]) - delta)
		if float(fighter["dodge_time"]) > 0.0:
			fighter["x"] = clampf(float(fighter["x"]) + float(fighter["dodge_direction"]) * 420.0 * delta, 28.0, 612.0)
	if not auto_mode and _is_alive(controlled_index):
		var current: Dictionary = fighters[controlled_index]
		current["guard"] = Input.is_action_pressed("battle_guard")
		if Input.is_action_just_pressed("battle_attack"):
			_try_attack()
		if Input.is_action_just_pressed("battle_dodge"):
			_try_dodge()
		if Input.is_action_just_pressed("battle_skill"):
			_use_skill()
		if Input.is_action_just_pressed("battle_job_skill"):
			_use_job_skill()
		if float(current["dodge_time"]) == 0.0:
			current["x"] = clampf(float(current["x"]) + Input.get_axis("move_left", "move_right") * MOVE_SPEED * delta, 28.0, 612.0)
	for index in fighters.size():
		if battle_finished:
			break
		if auto_mode or index != controlled_index:
			_update_ai(index, delta)
	var enemy_start_x := enemy_x
	if not battle_finished:
		_update_enemy(delta)
	_advance_fighter_visuals(delta, initial_positions)
	_advance_combat_sprite_sets(delta)
	_advance_enemy_visual(delta, absf(enemy_x - enemy_start_x) > 0.01)
	_update_hud()
	queue_redraw()


func _set_fighter_visual_action(fighter: Dictionary, action: String) -> void:
	# Any other action (dodge, skill, job skill, hit, down) interrupts the pilot fighter's attack event.
	if action != "attack" and fighter.has("contact_event_id"):
		_interrupt_contact_event(fighter, action)
	fighter["visual_action"] = action
	fighter["visual_elapsed"] = 0.0
	if action == "skill":
		_emit_battle_cue("skill")


func _advance_fighter_visuals(delta: float, initial_positions: Array[float]) -> void:
	for index in fighters.size():
		var fighter: Dictionary = fighters[index]
		var action: String = fighter["visual_action"]
		if action != "":
			var elapsed: float = float(fighter["visual_elapsed"]) + delta
			var duration: float = float(HERO_COMBAT_ACTION_DURATION.get(action, 0.0))
			if action == "down":
				fighter["visual_elapsed"] = minf(elapsed, duration)
			elif duration == 0.0 or elapsed >= duration:
				fighter["visual_action"] = ""
				fighter["visual_elapsed"] = 0.0
			else:
				fighter["visual_elapsed"] = elapsed
		if initial_positions.size() == fighters.size():
			fighter["visual_moving"] = absf(float(fighter["x"]) - initial_positions[index]) > 0.01
		var loop_kind := "guard" if bool(fighter["guard"]) else ("move" if bool(fighter["visual_moving"]) else "idle")
		if String(fighter["visual_loop_kind"]) != loop_kind:
			fighter["visual_loop_kind"] = loop_kind
			fighter["visual_loop_clock"] = 0.0
		else:
			fighter["visual_loop_clock"] = float(fighter["visual_loop_clock"]) + delta


func _advance_combat_sprite_sets(delta: float) -> void:
	# Reads combat state only; it never changes stats, timers or positions.
	if companion_sprite_sets != null:
		companion_sprite_sets.advance(companion_index, fighters[companion_index], _is_alive(companion_index), enemy_x, delta)
	if combat_sprite_sets == null:
		return
	for index in fighters.size():
		combat_sprite_sets.advance(index, fighters[index], _is_alive(index), enemy_x, delta)


func _advance_enemy_visual(delta: float, moved: bool) -> void:
	# Reads combat state only; it never changes stats, timers or positions.
	if enemy_animation_texture == null:
		return
	var restart := false
	enemy_visual_still_time = 0.0 if moved else enemy_visual_still_time + delta
	# A brief grace keeps the gait through a one-frame stop, so it does not flicker to idle; the distance gait holds its pose meanwhile.
	var walking := moved or (enemy_visual_state == "move" and enemy_visual_still_time < float(enemy_animation.get("move_grace", 0.0)))
	var next := "move" if walking else "idle"
	if (enemy_visual_state == "strike" or enemy_visual_state == "hit") and enemy_visual_clock + delta < _enemy_visual_duration(enemy_visual_state):
		next = enemy_visual_state
	# A hit restarts the flinch only once the previous one has played out, so a party combo does not pin it on one frame.
	if enemy_hp < enemy_visual_last_hp and next != "strike" and next != "hit":
		next = "hit"
		restart = true
	if enemy_attack_count != enemy_visual_last_attack_count:
		next = "strike"
		restart = true
	# The wind-up pose is the telegraph, so it wins over a hit reaction.
	if enemy_windup > 0.0:
		next = "windup"
	if enemy_hp <= 0:
		next = "defeat"
	enemy_visual_last_hp = enemy_hp
	enemy_visual_last_attack_count = enemy_attack_count
	if restart or next != enemy_visual_state:
		if next == "move":
			enemy_visual_gait_origin_x = roundf(enemy_x)
		enemy_visual_state = next
		enemy_visual_clock = 0.0
	else:
		enemy_visual_clock += delta


func _enemy_visual_duration(state: String) -> float:
	return float(enemy_animation["frame_time"].get(state, 0.0)) * Array(enemy_animation["states"][state]).size()


func _enemy_gait_step() -> int:
	# Whole gait steps travelled toward the party since the gait began (negative when backing away, which plays the gait in reverse).
	return roundi((enemy_visual_gait_origin_x - enemy_x) / float(enemy_animation["gait_step_px"]))


func _enemy_distance_gait() -> bool:
	return enemy_visual_state == "move" and float(enemy_animation.get("gait_step_px", 0.0)) > 0.0


func _enemy_draw_x() -> float:
	# The distance gait draws the sprite in whole steps (at most half a step from enemy_x), so each stance foot stays on one floor pixel.
	if enemy_animation_texture != null and _enemy_distance_gait():
		return enemy_visual_gait_origin_x - _enemy_gait_step() * float(enemy_animation["gait_step_px"])
	return roundf(enemy_x)


func _enemy_body_offset_x() -> float:
	# Where the drawn body centre sits relative to enemy_x, for the wind-up ring (0 for the static pilot and block).
	if enemy_animation_texture == null:
		return 0.0
	return float(enemy_animation.get("body_center_x", enemy_animation_anchor.x)) - enemy_animation_anchor.x


func _enemy_visual_in_front() -> bool:
	return enemy_animation_texture != null and Array(enemy_animation.get("front_states", [])).has(enemy_visual_state)


func _enemy_visual_frame() -> int:
	var frames: Array = enemy_animation["states"][enemy_visual_state]
	var frame_time: float = enemy_animation["frame_time"].get(enemy_visual_state, 0.0)
	var index := 0
	if enemy_visual_state == "windup" and enemy_animation.get("windup_phases", false):
		# Evenly spaced phases across the real wind-up time (the patrol pilot); the sentry keeps its two halves.
		index = clampi(int((1.0 - enemy_windup / float(enemy["windup"])) * frames.size()), 0, frames.size() - 1)
	elif enemy_visual_state == "windup":
		index = 0 if enemy_windup > float(enemy["windup"]) * 0.5 else 1
	elif _enemy_distance_gait():
		index = posmod(_enemy_gait_step(), frames.size())
	elif enemy_visual_state == "idle" or enemy_visual_state == "move":
		index = int(enemy_visual_clock / frame_time) % frames.size()
	else:
		index = mini(int(enemy_visual_clock / frame_time), frames.size() - 1)
	return int(frames[index])


func _male_combat_texture(fighter: Dictionary, index: int) -> Texture2D:
	return _hero_combat_texture(fighter, index, false)


func _female_combat_texture(fighter: Dictionary, index: int) -> Texture2D:
	return _hero_combat_texture(fighter, index, true)


func _liang_combat_texture(fighter: Dictionary, index: int) -> Texture2D:
	return _hero_combat_texture(fighter, index, false, true)


func _zhao_combat_texture(fighter: Dictionary, index: int) -> Texture2D:
	return _hero_combat_texture(fighter, index, false, false, true)


func _ji_combat_texture(fighter: Dictionary, index: int) -> Texture2D:
	return _hero_combat_texture(fighter, index, false, false, false, true)


func _hero_combat_texture(fighter: Dictionary, index: int, female: bool, liang: bool = false, zhao: bool = false, ji: bool = false) -> Texture2D:
	var action := "idle"
	var phase := 1
	if not _is_alive(index):
		action = "down"
		phase = 1 if float(fighter["visual_elapsed"]) < 0.15 else 2
	elif float(fighter["dodge_time"]) > 0.0:
		action = "dodge"
		phase = 1 if float(fighter["dodge_time"]) > 0.135 else 2
	elif ["attack", "hit", "skill"].has(String(fighter["visual_action"])):
		action = String(fighter["visual_action"])
		var duration: float = float(HERO_COMBAT_ACTION_DURATION[action])
		phase = mini(MaleCombatFrames.count(action), 1 + int(floor(float(fighter["visual_elapsed"]) * MaleCombatFrames.count(action) / duration)))
	elif bool(fighter["guard"]):
		action = "guard"
		phase = 1 + int(floor(float(fighter["visual_loop_clock"]) / 0.18)) % MaleCombatFrames.count(action)
	elif bool(fighter["visual_moving"]):
		action = "move"
		phase = 1 + int(floor(float(fighter["visual_loop_clock"]) / 0.11)) % MaleCombatFrames.count(action)
	else:
		phase = 1 + int(floor(float(fighter["visual_loop_clock"]) / 0.36)) % MaleCombatFrames.count(action)
	if liang:
		return LiangCombatFrames.frame(action, phase)
	if zhao:
		return ZhaoCombatFrames.frame(action, phase)
	if ji:
		return JiCombatFrames.frame(action, phase)
	return FemaleCombatFrames.frame(action, phase) if female else MaleCombatFrames.frame(action, phase)


func _is_alive(index: int) -> bool:
	return index >= 0 and index < fighters.size() and int(AppState.member_state(String(fighters[index]["id"]))["hp"]) > 0


func _nearest_living() -> int:
	var best := -1
	var distance := INF
	for index in fighters.size():
		if not _is_alive(index):
			continue
		var current := absf(enemy_x - float(fighters[index]["x"]))
		if current < distance:
			best = index
			distance = current
	return best


func _update_ai(index: int, delta: float) -> void:
	if not _is_alive(index) or battle_finished:
		return
	var fighter: Dictionary = fighters[index]
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	var definition: Dictionary = AppState.MEMBER_DEFS[String(fighter["id"])]
	var separation := absf(enemy_x - float(fighter["x"]))
	var command: String = fighter["command"]
	var policy: String = member.get("ai_policy", "balanced")
	fighter["guard"] = (command == "defend" or (command == "default" and policy == "cautious")) and enemy_windup > 0.0 and separation < 85.0
	if enemy_windup > 0.0 and separation < 85.0 and command != "focus" and command != "defend" and policy != "aggressive" and policy != "cautious":
		if int(member["energy"]) >= DODGE_COST and float(fighter["dodge_cooldown"]) == 0.0:
			_try_dodge(index)
			return
	if float(fighter["dodge_time"]) > 0.0:
		return
	if (command == "skill" or (command == "default" and policy == "aggressive")) and float(fighter["skill_cooldown"]) == 0.0 and int(member["energy"]) >= 14:
		if int(member.get("level", 1)) >= 10 and _use_job_skill(index):
			return
		if _use_skill(index):
			return
	if separation > float(definition["attack_range"]) - 8.0:
		fighter["x"] = clampf(float(fighter["x"]) + signf(enemy_x - float(fighter["x"])) * MOVE_SPEED * 0.72 * delta, 28.0, 612.0)
	elif float(fighter["attack_cooldown"]) == 0.0:
		_try_attack(index)


func _update_enemy(delta: float) -> void:
	if enemy_windup > 0.0:
		enemy_windup = maxf(0.0, enemy_windup - delta)
		if enemy_windup == 0.0:
			_apply_enemy_hit()
			enemy_cooldown = float(enemy["cooldown"])
		return
	if enemy_cooldown > 0.0:
		enemy_cooldown = maxf(0.0, enemy_cooldown - delta)
	var target := _nearest_living()
	if target < 0:
		_finish_battle(false)
		return
	var separation := absf(enemy_x - float(fighters[target]["x"]))
	if separation > 53.0:
		enemy_x = clampf(enemy_x + signf(float(fighters[target]["x"]) - enemy_x) * float(enemy["speed"]) * delta, 28.0, 612.0)
	elif enemy_cooldown == 0.0:
		enemy_target_index = target
		enemy_windup = float(enemy["windup"])


func _try_attack(index: int = -1) -> bool:
	if index < 0:
		index = controlled_index
	if battle_finished or not _is_alive(index):
		return false
	var fighter: Dictionary = fighters[index]
	if float(fighter["attack_cooldown"]) > 0.0:
		return false
	if fighter.has("contact_event_id"):
		return _request_contact_attack(index)
	fighter["attack_cooldown"] = 0.43
	_set_fighter_visual_action(fighter, "attack")
	player_attack_count += 1
	var definition: Dictionary = AppState.MEMBER_DEFS[String(fighter["id"])]
	if absf(enemy_x - float(fighter["x"])) > float(definition["attack_range"]):
		if index == controlled_index:
			feedback_message = ""
			feedback_key = "battle_far"
		return false
	var damage := int(definition["attack_damage"]) + int(fighter["boost"]) + next_attack_bonus
	fighter["boost"] = 0
	next_attack_bonus = 0
	enemy_hp = maxi(0, enemy_hp - damage)
	_emit_battle_vfx("attack", Vector2(enemy_x, ARENA_FLOOR_Y - 28.0), signf(enemy_x - float(fighter["x"])))
	feedback_message = ""
	feedback_key = "battle_hit"
	if enemy_hp == 0:
		_finish_battle(true)
	return true


# Pilot request: spends cooldown and the attack count now; damage waits for contact. Returns true when the request starts.
func _request_contact_attack(index: int) -> bool:
	var fighter: Dictionary = fighters[index]
	# Cooldown (0.43 s) outlasts recovery (0.40 s), so an older event is never pending here; cancel defensively if it were.
	if String(fighter["contact_event_state"]) == "pending":
		_resolve_contact_log(fighter, "cancelled_repress", 0)
	fighter["attack_cooldown"] = 0.43
	_set_fighter_visual_action(fighter, "attack")
	player_attack_count += 1
	contact_event_serial += 1
	var dx := enemy_x - float(fighter["x"])
	fighter["contact_event_id"] = contact_event_serial
	fighter["contact_event_clock"] = 0.0
	fighter["contact_event_facing"] = -1 if dx < 0.0 else 1
	fighter["contact_event_active"] = true
	fighter["contact_event_state"] = "pending"
	return true


func _advance_contact_events(delta: float) -> void:
	for index in fighters.size():
		var fighter: Dictionary = fighters[index]
		if not fighter.has("contact_event_id") or not bool(fighter["contact_event_active"]):
			continue
		var elapsed := float(fighter["contact_event_clock"]) + delta
		fighter["contact_event_clock"] = elapsed
		# Same boundary predicate as the sprite loader's frame_at, so the contact pose and the hit share one instant.
		var tolerance: float = CombatSpriteSets.CLOCK_EPSILON
		if String(fighter["contact_event_state"]) == "pending" and elapsed + tolerance >= float(HEROINE_CONTACT_TICKS) / HEROINE_CONTACT_TICK_RATE:
			_commit_contact(index)
		if battle_finished:
			return
		if String(fighter["contact_event_state"]) == "recovery" and elapsed + tolerance >= float(HEROINE_RECOVERY_END_TICKS) / HEROINE_CONTACT_TICK_RATE:
			fighter["contact_event_state"] = "ended"
			fighter["contact_event_active"] = false


func _commit_contact(index: int) -> void:
	var fighter: Dictionary = fighters[index]
	fighter["contact_event_state"] = "recovery"
	if not _is_alive(index):
		_resolve_contact_log(fighter, "cancelled_down", 0)
		fighter["contact_event_state"] = "cancelled"
		fighter["contact_event_active"] = false
		return
	var definition: Dictionary = AppState.MEMBER_DEFS[String(fighter["id"])]
	if absf(enemy_x - float(fighter["x"])) > float(definition["attack_range"]):
		# A miss keeps the fighter boost and the shared bonus for the next successful contact.
		if index == controlled_index:
			feedback_message = ""
			feedback_key = "battle_far"
		_resolve_contact_log(fighter, "missed", 0)
		return
	var damage := int(definition["attack_damage"]) + int(fighter["boost"]) + next_attack_bonus
	fighter["boost"] = 0
	next_attack_bonus = 0
	enemy_hp = maxi(0, enemy_hp - damage)
	_emit_battle_vfx("attack", Vector2(enemy_x, ARENA_FLOOR_Y - 28.0), float(fighter["contact_event_facing"]))
	feedback_message = ""
	feedback_key = "battle_hit"
	_resolve_contact_log(fighter, "hit", damage)
	if enemy_hp == 0:
		_finish_battle(true)


# Results cancel unresolved damage, but a hit already committed must still show its
# contact/recovery poses. This path advances presentation only and can never hit again.
func _advance_finished_contact_recovery(delta: float) -> void:
	for fighter in fighters:
		if not fighter.has("contact_event_id") or not bool(fighter["contact_event_active"]):
			continue
		if String(fighter["contact_event_state"]) != "recovery":
			continue
		var elapsed := float(fighter["contact_event_clock"]) + delta
		fighter["contact_event_clock"] = elapsed
		if elapsed + CombatSpriteSets.CLOCK_EPSILON >= float(HEROINE_RECOVERY_END_TICKS) / HEROINE_CONTACT_TICK_RATE:
			fighter["contact_event_state"] = "ended"
			fighter["contact_event_active"] = false


func _has_contact_recovery() -> bool:
	for fighter in fighters:
		if fighter.has("contact_event_id") and bool(fighter["contact_event_active"]) and String(fighter["contact_event_state"]) == "recovery":
			return true
	return false


func _interrupt_contact_event(fighter: Dictionary, reason: String) -> void:
	if not bool(fighter["contact_event_active"]):
		return
	if String(fighter["contact_event_state"]) == "pending":
		_resolve_contact_log(fighter, "cancelled_" + reason, 0)
		fighter["contact_event_state"] = "cancelled"
	else:
		fighter["contact_event_state"] = "interrupted"
	fighter["contact_event_active"] = false


func _resolve_contact_log(fighter: Dictionary, outcome: String, damage: int) -> void:
	contact_event_log.append({"id": int(fighter["contact_event_id"]), "outcome": outcome, "damage": damage, "clock": float(fighter["contact_event_clock"]), "facing": int(fighter["contact_event_facing"]), "enemy_hp": enemy_hp})
	if contact_event_log.size() > HEROINE_CONTACT_LOG_LIMIT:
		contact_event_log.pop_front()


func _try_dodge(index: int = -1) -> bool:
	if index < 0:
		index = controlled_index
	if battle_finished or not _is_alive(index):
		return false
	var fighter: Dictionary = fighters[index]
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	if float(fighter["dodge_cooldown"]) > 0.0:
		return false
	if int(member["energy"]) < DODGE_COST:
		feedback_message = ""
		feedback_key = "battle_no_energy"
		return false
	member["energy"] = int(member["energy"]) - DODGE_COST
	fighter["dodge_cooldown"] = 0.75
	fighter["dodge_time"] = 0.27
	_set_fighter_visual_action(fighter, "dodge")
	var axis := Input.get_axis("move_left", "move_right") if index == controlled_index and not auto_mode else 0.0
	fighter["dodge_direction"] = axis if axis != 0.0 else signf(float(fighter["x"]) - enemy_x)
	_emit_battle_vfx("dodge", Vector2(float(fighter["x"]), ARENA_FLOOR_Y - 3.0), fighter["dodge_direction"])
	return true


func _use_skill(index: int = -1) -> bool:
	if index < 0:
		index = controlled_index
	if battle_finished or not _is_alive(index):
		return false
	var fighter: Dictionary = fighters[index]
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	var member_id: String = fighter["id"]
	var cost := 16 if member_id == "liang-xu" else 14
	if member_id == "hero":
		cost = 12
	if int(member["energy"]) < cost:
		feedback_message = ""
		feedback_key = "battle_no_energy"
		return false
	if float(fighter["skill_cooldown"]) > 0.0:
		return false
	member["energy"] = int(member["energy"]) - cost
	fighter["skill_cooldown"] = 2.2
	_set_fighter_visual_action(fighter, "skill")
	var rank := int(member.get("personal_skill_rank", 1))
	match member_id:
		"hero":
			next_attack_bonus += 5 * rank
		"liang-xu":
			for ally in fighters:
				if ally != fighter and int(AppState.member_state(String(ally["id"]))["hp"]) > 0:
					ally["command"] = "focus"
					ally["boost"] = int(ally["boost"]) + 4 * rank
		"zhao-ling":
			next_attack_bonus += 8 * rank
		"ji-cheng":
			enemy_windup += 0.65 * rank if enemy_windup > 0.0 else 0.0
			enemy_cooldown += 0.65 * rank
	_emit_skill_vfx("personal-" + member_id, Vector2(float(fighter["x"]), ARENA_FLOOR_Y - 34.0), signf(enemy_x - float(fighter["x"])))
	feedback_message = AppState.text_for("battle_skill_used") % [AppState.member_name(member_id), AppState.text_for(String(AppState.MEMBER_DEFS[member_id]["skill_key"]))]
	return true


func _use_job_skill(index: int = -1, requested_skill_id: String = "") -> bool:
	if index < 0:
		index = controlled_index
	if battle_finished or not _is_alive(index):
		return false
	var fighter: Dictionary = fighters[index]
	var member_id: String = fighter["id"]
	var member: Dictionary = AppState.member_state(member_id)
	# Merchant guard: its job skills are placeholders with no battle effect, so they never run or spend energy.
	if not GrowthRules.job_skills_have_effect(String(member["job_series"])):
		return false
	var skill_id := requested_skill_id if requested_skill_id != "" else GrowthRules.current_skill_id(member)
	var available: Array = GrowthRules.SERIES[String(member["job_series"])]["skills"]
	if not available.has(skill_id) or available.find(skill_id) >= int(member["job_stage"]):
		return false
	var rank := GrowthRules.skill_rank(member, skill_id)
	var skill_stage: int = available.find(skill_id) + 1
	var cost := 10 + 3 * skill_stage
	if rank < 1 or float(fighter["skill_cooldown"]) > 0.0:
		return false
	if int(member["energy"]) < cost:
		feedback_message = ""
		feedback_key = "battle_no_energy"
		return false
	var series_id: String = member["job_series"]
	var range_needed := 175.0 if series_id == "firearms" else 105.0
	if ["sword", "firearms"].has(series_id) and absf(enemy_x - float(fighter["x"])) > range_needed:
		feedback_message = ""
		feedback_key = "battle_far"
		return false
	member["energy"] = int(member["energy"]) - cost
	fighter["skill_cooldown"] = 2.2
	_set_fighter_visual_action(fighter, "skill")
	match series_id:
		"sword", "firearms":
			enemy_hp = maxi(0, enemy_hp - (8 + rank * 4 + skill_stage * 3))
		"tactics":
			for ally in fighters:
				if int(AppState.member_state(String(ally["id"]))["hp"]) > 0:
					ally["boost"] = int(ally["boost"]) + 2 + rank * 2 + (skill_stage - 1) * 2
		"relics":
			enemy_cooldown += 0.25 + 0.2 * rank + 0.2 * (skill_stage - 1)
			if enemy_windup > 0.0:
				enemy_windup += 0.25 + 0.2 * rank + 0.2 * (skill_stage - 1)
	var skill_origin_x := enemy_x if ["sword", "firearms"].has(series_id) else float(fighter["x"])
	_emit_skill_vfx("job-" + series_id, Vector2(skill_origin_x, ARENA_FLOOR_Y - 28.0), signf(enemy_x - float(fighter["x"])))
	feedback_message = AppState.text_for("battle_skill_used") % [AppState.member_name(member_id), AppState.text_for("job_skill_" + skill_id)]
	if enemy_hp == 0:
		_finish_battle(true)
	return true


func _apply_enemy_hit() -> void:
	enemy_attack_count += 1
	var index := enemy_target_index if _is_alive(enemy_target_index) else _nearest_living()
	if index < 0:
		_finish_battle(false)
		return
	var fighter: Dictionary = fighters[index]
	if absf(enemy_x - float(fighter["x"])) > 69.0:
		return
	if float(fighter["dodge_time"]) > 0.0:
		feedback_message = ""
		feedback_key = "battle_dodge_feedback"
		return
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	var damage: int = int(enemy["damage"])
	var guarded := false
	feedback_message = ""
	if bool(fighter["guard"]) or (index == controlled_index and not auto_mode and Input.is_action_pressed("battle_guard")):
		if int(member["energy"]) >= GUARD_HIT_COST:
			member["energy"] = int(member["energy"]) - GUARD_HIT_COST
			damage = maxi(1, ceili(float(damage) * 0.30))
			guarded = true
			feedback_key = "battle_guard_feedback"
		else:
			feedback_key = "battle_hurt"
	else:
		feedback_key = "battle_hurt"
	member["hp"] = maxi(0, int(member["hp"]) - damage)
	_emit_battle_vfx("guard" if guarded else "hit", Vector2(float(fighter["x"]), ARENA_FLOOR_Y - 26.0), signf(enemy_x - float(fighter["x"])))
	if int(member["hp"]) == 0:
		_set_fighter_visual_action(fighter, "down")
		feedback_message = AppState.text_for("battle_member_down") % AppState.member_name(String(fighter["id"]))
		if index == controlled_index:
			_select_next_living()
		if _nearest_living() < 0:
			_finish_battle(false)
	else:
		_set_fighter_visual_action(fighter, "hit")


func _select_next_living() -> void:
	for offset in range(1, fighters.size() + 1):
		var next := (controlled_index + offset) % fighters.size()
		if _is_alive(next):
			controlled_index = next
			return


func _switch_control() -> void:
	if paused or battle_finished:
		return
	_select_next_living()
	auto_mode = false
	feedback_message = ""
	_refresh_text()


func _toggle_auto() -> void:
	if paused or battle_finished:
		return
	auto_mode = not auto_mode
	_refresh_text()


func _toggle_pause() -> void:
	if battle_finished:
		return
	paused = not paused
	pause_overlay.visible = paused
	if paused:
		selected_order_id = ""
		for fighter in fighters:
			if String(fighter["id"]) != String(fighters[controlled_index]["id"]) and int(AppState.member_state(String(fighter["id"]))["hp"]) > 0:
				selected_order_id = fighter["id"]
				break
		_refresh_text()
		pause_resume_button.grab_focus()
	else:
		if queued_skill:
			queued_skill = false
			_use_skill(controlled_index)
		if queued_job_skill:
			queued_job_skill = false
			_use_job_skill(controlled_index, queued_job_skill_id)
			queued_job_skill_id = ""
		_refresh_text()


func _queue_skill() -> void:
	queued_skill = true
	_refresh_text()


func _queue_job_skill(skill_id: String) -> void:
	queued_job_skill = true
	queued_job_skill_id = skill_id
	_refresh_text()


func _select_order_target(member_id: String) -> void:
	selected_order_id = member_id
	_refresh_text()


func _issue_order(command: String) -> void:
	for fighter in fighters:
		if String(fighter["id"]) == selected_order_id:
			fighter["command"] = command
			feedback_key = "battle_" + ("skill_order" if command == "skill" else command)
			break
	_refresh_text()


func _cycle_ai_policy() -> void:
	if selected_order_id == "":
		return
	var member: Dictionary = AppState.member_state(selected_order_id)
	var policies := ["balanced", "aggressive", "cautious"]
	var current: String = member.get("ai_policy", "balanced")
	member["ai_policy"] = policies[(policies.find(current) + 1) % policies.size()]
	_refresh_text()


func _finish_battle(won: bool) -> void:
	if battle_finished:
		return
	battle_finished = true
	# A pending contact never resolves behind results. A committed hit retains only
	# presentation recovery, so the finishing contact frame is not replaced by idle.
	for fighter in fighters:
		if fighter.has("contact_event_id") and String(fighter["contact_event_state"]) == "pending":
			_interrupt_contact_event(fighter, "result")
	paused = false
	pause_overlay.visible = false
	battle_won = won
	_emit_battle_cue("victory" if won else "defeat")
	_emit_encounter_feedback("victory" if won else "defeat", _encounter_result_origin())
	AppState.record_playtest_event("battle_win" if won else "battle_loss", AppState.current_destination_id)
	if won:
		AppState.machine_observed = true
		for fighter in fighters:
			var member_id: String = fighter["id"]
			var recovered := BattleRules.recover_after_battle(AppState.member_state(member_id))
			if member_id == "hero":
				AppState.hero_state = recovered
			else:
				AppState.member_states[member_id] = recovered
		var recovery_slot := 0
		for index in fighters.size():
			if _is_alive(index):
				_emit_encounter_feedback("recovery", _encounter_result_origin(recovery_slot))
				recovery_slot += 1
		AppState.enemy_cleared_for_return = true
		AppState.returning_from_battle = true
		var rewards := AppState.award_battle_rewards(enemy_id)
		result_reward_xp = int(rewards["xp"])
		result_reward_jp = int(rewards["jp"])
		AppState.write_auto_save("area", AppState.battle_return_position, "after_battle")
	else:
		AppState.enemy_cleared_for_return = false
		AppState.returning_from_battle = false
		get_tree().create_timer(2.0).timeout.connect(_return_to_menu)
	patrol_result_pending = won and enemy_hp <= 0 and enemy_id == "patrol" and patrol_animation_enabled() and enemy_animation_texture != null
	heroine_result_pending = won and _has_contact_recovery()
	heroine_defeat_result_pending = not won and _authored_heroine_defeat_playing()
	patrol_result_elapsed = 0.0
	result_overlay.visible = not (patrol_result_pending or heroine_result_pending or heroine_defeat_result_pending)
	if patrol_result_pending:
		_advance_enemy_visual(0.0, false)
	if patrol_result_pending or heroine_result_pending or heroine_defeat_result_pending:
		result_button.disabled = true
		result_button.focus_mode = Control.FOCUS_NONE
		result_button.release_focus()
	_refresh_encounter_result_surface()
	_refresh_text()
	if not patrol_result_pending and not heroine_result_pending and not heroine_defeat_result_pending:
		result_button.grab_focus()
	queue_redraw()


func _advance_patrol_result_presentation(delta: float) -> void:
	if not patrol_result_pending and not heroine_result_pending and not heroine_defeat_result_pending:
		return
	if patrol_result_pending:
		patrol_result_elapsed += delta
		# Epsilon compensates binary floating-point summation only (one nanosecond, never a frame).
		if patrol_result_elapsed + 0.000000001 >= _enemy_visual_duration("defeat"):
			patrol_result_pending = false
	if heroine_result_pending and not _has_contact_recovery():
		heroine_result_pending = false
	if heroine_defeat_result_pending and not _authored_heroine_defeat_playing():
		heroine_defeat_result_pending = false
	if patrol_result_pending or heroine_result_pending or heroine_defeat_result_pending:
		return
	result_overlay.visible = true
	result_button.disabled = false
	result_button.focus_mode = Control.FOCUS_ALL
	result_button.grab_focus()


func _authored_heroine_defeat_playing() -> bool:
	# Current source-bound protagonist packages show defeat before results. Legacy/other fighters remain unchanged.
	var female_source := AppState.hero_appearance == "female" and (heroine_sea_contact_enabled() or (heroine_default_active and heroine_sea_contact_override < 0))
	var male_source := AppState.hero_appearance == "male" and _male_playable_path_index() != ""
	if combat_sprite_sets == null or not (female_source or male_source):
		return false
	for index in fighters.size():
		if String(fighters[index]["id"]) != "hero" or _is_alive(index) or not combat_sprite_sets.has_set(index):
			continue
		var sprite_set: Dictionary = combat_sprite_sets.sets[index]
		var expected_key := "hero:male" if male_source else "hero:female"
		var expected_set := "protagonist-male-combat-mcombat22-v01" if male_source else "heroine-sea-combat-v01"
		if sprite_set.get("key") != expected_key or sprite_set.get("set_id") != expected_set:
			continue
		var clip: Dictionary = sprite_set["actions"]["defeat"]
		var state: Dictionary = combat_sprite_sets.states[index]
		# At the finishing damage frame the playback can still be in hit; wait for the real defeat clock.
		return String(state["action"]) != "defeat" or float(state["clock"]) + 0.000000001 < float(clip["duration"])
	return false


func _return_after_result() -> void:
	if patrol_result_pending or heroine_result_pending or heroine_defeat_result_pending:
		return
	if battle_won:
		AppState.battle_enemy_id = ""
		if AppState.has_pending_job_choice():
			AppState.growth_return_scene = "res://scenes/scifi_exploration_area.tscn"
			get_tree().change_scene_to_file("res://scenes/growth_screen.tscn")
		else:
			get_tree().change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	else:
		_return_to_menu()


func _return_to_menu() -> void:
	if not is_inside_tree():
		return
	AppState.battle_enemy_id = ""
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("battle_pause") or (paused and event.is_action_pressed("ui_cancel")):
		_toggle_pause()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("battle_switch"):
		_switch_control()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("battle_auto"):
		_toggle_auto()
		get_viewport().set_input_as_handled()


func _load_enemy_sprite_pilot() -> void:
	enemy_texture = null
	enemy_telegraph_center_y = ENEMY_TELEGRAPH_CENTER_Y
	enemy_telegraph_scale = Vector2.ONE
	if enemy_id == "patrol" and enemy_sprite_pilot_enabled and patrol_animation_enabled():
		_load_patrol_animation_pilot()
		return
	if not sentry_v2_enabled() or not enemy_sprite_pilot_enabled or not ENEMY_SPRITE_PILOTS.has(enemy_id):
		return
	var pilot: Dictionary = ENEMY_SPRITE_PILOTS[enemy_id]
	var path: String = enemy_sprite_override if enemy_sprite_override != "" else pilot["path"]
	if not ResourceLoader.exists(path):
		return
	enemy_texture = load(path)
	if enemy_texture == null:
		return
	enemy_anchor = pilot["anchor"]
	enemy_telegraph_center_y = pilot.get("telegraph_center_y", ENEMY_TELEGRAPH_CENTER_Y)
	enemy_telegraph_scale = pilot.get("telegraph_scale", Vector2.ONE)
	_load_enemy_animation()


func _load_enemy_animation() -> void:
	enemy_animation_texture = null
	enemy_animation = {}
	enemy_visual_state = "idle"
	enemy_visual_clock = 0.0
	enemy_visual_last_hp = enemy_hp
	enemy_visual_last_attack_count = enemy_attack_count
	enemy_visual_still_time = 0.0
	enemy_visual_gait_origin_x = roundf(enemy_x)
	if not sentry_v2_enabled() or enemy_texture == null or not enemy_sprite_animation_enabled or not ENEMY_SPRITE_ANIMATIONS.has(enemy_id):
		return
	var animation: Dictionary = ENEMY_SPRITE_ANIMATIONS[enemy_id]
	var path: String = enemy_animation_override if enemy_animation_override != "" else animation["path"]
	if not ResourceLoader.exists(path):
		return
	var strip: Texture2D = load(path)
	var frame_count := 0
	for frames in animation["states"].values():
		for frame in frames:
			frame_count = maxi(frame_count, int(frame) + 1)
	var cell: Vector2 = animation.get("cell", enemy_texture.get_size())
	# The strip must hold every frame in cells of the declared size (the static pilot's by default), or the static pilot stays.
	if strip == null or strip.get_height() != int(cell.y) or strip.get_width() != int(cell.x) * frame_count:
		return
	enemy_animation_texture = strip
	enemy_animation = animation
	enemy_animation_cell = cell
	enemy_animation_anchor = animation.get("anchor", enemy_anchor)


func _load_patrol_animation_pilot() -> void:
	# Resets the visual state like the sentry path; the loader validates everything and returns {} on any defect.
	_load_enemy_animation()
	var loader: Script = load(PATROL_ANIMATION_LOADER)
	if loader == null:
		return
	var path := patrol_animation_package_override if patrol_animation_package_override != "" else PATROL_ANIMATION_PACKAGE
	var package: Dictionary = loader.load_package(path)
	if package.is_empty():
		return
	enemy_texture = package["texture"]
	enemy_animation_texture = package["texture"]
	enemy_animation = package["animation"]
	enemy_animation_cell = enemy_animation["cell"]
	enemy_anchor = enemy_animation["anchor"]
	enemy_animation_anchor = enemy_anchor
	enemy_telegraph_center_y = package["telegraph_center_y"]
	enemy_telegraph_scale = package["telegraph_scale"]


func _load_battle_backdrop() -> void:
	battle_backdrop_texture = null
	battle_backdrop_arena_id = ""
	battle_backdrop_status = "off"
	var selected_arena := battle_backdrop_arena(AppState.current_destination_id)
	var native_selected := selected_arena == "outskirts" and (OS.get_cmdline_user_args().has(BATTLE_NATIVE_ENVIRONMENT_FLAG) or battle_backdrop_override == -1)
	if not battle_backdrop_enabled() and not native_selected:
		return
	battle_backdrop_arena_id = selected_arena
	if not BATTLE_BACKDROP_BANDS.has(battle_backdrop_arena_id):
		battle_backdrop_status = "no_band"
		return
	var path: String = battle_backdrop_path_override if battle_backdrop_path_override != "" else BATTLE_BACKDROP_BANDS[battle_backdrop_arena_id]
	if native_selected:
		path = BATTLE_NATIVE_ENVIRONMENT_PATH
	if not ResourceLoader.exists(path):
		battle_backdrop_status = "missing"
		return
	var band := load(path) as Texture2D
	var image: Image = null
	if band != null:
		var factor := roundi(band.get_size().x / BATTLE_BACKDROP_RECT.size.x)
		if factor >= 1 and Vector2i(band.get_size()) == BATTLE_BACKDROP_RECT.size * factor:
			image = band.get_image()
	if image == null:
		battle_backdrop_status = "unsupported"
		return
	# Nearest-neighbour down to the 640x212 logical band, so the band shares the sprites' pixel grid at every window size.
	image.resize(BATTLE_BACKDROP_RECT.size.x, BATTLE_BACKDROP_RECT.size.y, Image.INTERPOLATE_NEAREST)
	battle_backdrop_texture = ImageTexture.create_from_image(image)
	battle_backdrop_status = "loaded"


func _male_playable_path_index() -> String:
	if AppState.hero_appearance != "male" or not AppState.active_party_ids.has("hero"):
		return ""
	if male_playable_path_index_override != "":
		return male_playable_path_index_override
	# Ordinary male use stays false until creator authorization. Explicit combat choices retain their semantics.
	var male_driver = load("res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd")
	if not male_driver.DEFAULT_ADOPTED or combat_sprite_set_override >= 0 or combat_sprite_set_index_override != "":
		return ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with(COMBAT_SPRITE_SET_INDEX_ARG):
			return ""
	var package: Dictionary = male_driver.prepare_package(male_driver.REGISTRY_PATH, male_driver.SUPPLEMENT_PATH)
	return male_driver.COMBAT_INDEX_PATH if package.get("ok", false) else ""


func _load_combat_sprite_sets() -> void:
	combat_sprite_sets = null
	var explicit := combat_sprite_set_enabled()
	var male_index := "" if explicit else _male_playable_path_index()
	if not explicit and not heroine_default_active and male_index == "":
		return
	var keys: Array[String] = []
	for fighter in fighters:
		keys.append(CombatSpriteSets.set_key(String(fighter["id"]), AppState.hero_appearance))
	combat_sprite_sets = CombatSpriteSets.new()
	combat_sprite_sets.configure(combat_sprite_set_index() if explicit else (male_index if male_index != "" else HeroineDefault.COMBAT_INDEX_PATH), keys)
	if not explicit and male_index != "":
		if not combat_sprite_sets.has_set(AppState.active_party_ids.find("hero")):
			combat_sprite_sets = null
			return
	if not explicit and male_index == "":
		var hero_index := AppState.active_party_ids.find("hero")
		if not combat_sprite_sets.has_set(hero_index) or combat_sprite_sets.loaded_count() != 1:
			# Fail closed as one unit: legacy frames and the legacy immediate attack, never retimed placeholder art.
			push_warning("Heroine normal default combat set refused at load; legacy hero kept")
			combat_sprite_sets = null
			heroine_default_active = false
			for fighter in fighters:
				for key in ["contact_event_id", "contact_event_clock", "contact_event_facing", "contact_event_active", "contact_event_state"]:
					fighter.erase(key)
			return
	# The first frame shows each fighter's current state even before a combat step runs.
	_advance_combat_sprite_sets(0.0)


# Companion set: only the configured member slot loads; any explicit combat set choice (flag or override, including 0) or a
# hero-model set already drawing that slot keeps its existing behaviour. A refused set leaves only that member legacy.
func _load_companion_sprite_sets() -> void:
	companion_sprite_sets = null
	companion_index = -1
	# Existing explicit generic choices win, including an index given without the pilot flag.
	if combat_sprite_set_override >= 0 or combat_sprite_set_index_override != "" or OS.get_cmdline_user_args().has(COMBAT_SPRITE_SET_CLI_FLAG):
		return
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(COMBAT_SPRITE_SET_INDEX_ARG):
			return
	var zhao = load("res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd")
	if not zhao.enabled():
		return
	var member: String = companion_combat_member_override
	var source_index: String = companion_combat_index_override
	if member == "" and source_index == "":
		member = zhao.MEMBER_ID
		source_index = zhao.combat_index_path()
	if member != zhao.MEMBER_ID or source_index == "" or not zhao.validate(AppState.language, AppState.hero_appearance).get("ok", false):
		return
	var slot := AppState.active_party_ids.find(member)
	if slot < 0 or (combat_sprite_sets != null and combat_sprite_sets.has_set(slot)):
		return
	var keys: Array[String] = []
	for fighter in fighters:
		keys.append(member if String(fighter["id"]) == member else "")
	var model = CombatSpriteSets.new()
	model.configure(source_index, keys)
	if not model.has_set(slot) or model.loaded_count() != 1:
		push_warning("Companion combat set refused for %s; legacy frames kept for that member only" % member)
		return
	companion_sprite_sets = model
	companion_index = slot
	companion_sprite_sets.advance(slot, fighters[slot], _is_alive(slot), enemy_x, 0.0)

func _draw() -> void:
	draw_rect(Rect2(0, 0, 640, 360), Color("#101a27"))
	if battle_backdrop_texture != null:
		draw_texture(battle_backdrop_texture, Vector2(BATTLE_BACKDROP_RECT.position))
	else:
		var backdrop := Color("#2b4050") if enemy_id == "patrol" else Color("#463b4a")
		draw_rect(Rect2(0, 89, 640, 213), backdrop)
		for x in range(0, 640, 40):
			draw_rect(Rect2(x, 248, 22, 3), Color("#8ca5a4"))
		draw_rect(Rect2(0, 268, 640, 34), Color("#718883"))
		draw_rect(Rect2(0, 296, 640, 6), Color("#394f55"))
		for x in range(35, 640, 120 if enemy_id == "patrol" else 150):
			draw_rect(Rect2(x, 101, 12 if enemy_id == "patrol" else 25, 145), Color("#334f5d") if enemy_id == "patrol" else Color("#766b63"))
	# The sprite pilot is wider than the block, so it draws behind fighters to keep their attack frames on top, except in its own front states (strike).
	var enemy_behind := enemy_texture != null and not _enemy_visual_in_front()
	# An animated pilot stays on the field in its defeat pose; the static pilot and block vanish as before.
	var enemy_shown := enemy_hp > 0 or enemy_animation_texture != null
	if enemy_shown and enemy_behind:
		_draw_enemy()
	for index in fighters.size():
		_draw_fighter(fighters[index], index)
	if enemy_shown and not enemy_behind:
		_draw_enemy()

	if battle_vfx != null:
		battle_vfx.draw(self)
	if skill_vfx != null:
		skill_vfx.draw(self)
	if encounter_feedback != null and not _encounter_result_surface_draws():
		encounter_feedback.draw(self)


func _emit_battle_cue(event: String) -> void:
	# Service is optional until the disjoint audio workstream is integrated; no dependency on its source here.
	var service: Variant = AppState.get("audio_cues")
	if service is Object and service.has_method("play_cue"):
		service.call("play_cue", event)


func _emit_skill_vfx(kind: String, origin: Vector2, facing: float = 1.0) -> bool:
	return skill_vfx.emit(kind, origin, facing) if skill_vfx != null else false


func _emit_battle_vfx(kind: String, origin: Vector2, facing: float = 1.0) -> bool:
	_emit_battle_cue(kind)
	return battle_vfx.emit(kind, origin, facing) if battle_vfx != null else false


# Presentation API for a future successful healing action; current combat has no healing mechanic.
# Calling this never restores HP, spends energy or changes combat state.
func show_heal_vfx(index: int) -> bool:
	if not _is_alive(index):
		return false
	return _emit_battle_vfx("heal", Vector2(float(fighters[index]["x"]), ARENA_FLOOR_Y - 26.0))


func _emit_encounter_feedback(kind: String, origin: Vector2) -> bool:
	return encounter_feedback.emit(kind, origin) if encounter_feedback != null else false


func _build_encounter_result_surface() -> void:
	if encounter_feedback == null or is_instance_valid(encounter_result_surface):
		return
	encounter_result_layer = CanvasLayer.new()
	encounter_result_layer.layer = 100
	add_child(encounter_result_layer)
	encounter_result_surface = EncounterResultSurface.new()
	encounter_result_surface.module = encounter_feedback
	encounter_result_surface.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	encounter_result_surface.z_index = 100
	encounter_result_surface.visible = false
	encounter_result_layer.add_child(encounter_result_surface)


func _refresh_encounter_result_surface() -> void:
	if not is_instance_valid(encounter_result_surface) or encounter_feedback == null:
		return
	var active: bool = battle_finished and not encounter_feedback.events.is_empty()
	encounter_result_surface.visible = active
	if active:
		encounter_result_surface.queue_redraw()


func _encounter_result_surface_draws() -> bool:
	return battle_finished and is_instance_valid(encounter_result_surface) and encounter_result_surface.visible


func _encounter_result_origin(recovery_slot: int = -1) -> Vector2:
	# Victory/defeat sit in the left margin; recoveries stack compact slots there.
	if recovery_slot < 0:
		return Vector2(64.0, 176.0)
	var slot := clampi(recovery_slot, 0, AppState.PARTY_CAPACITY - 1)
	return Vector2(64.0, 134.0 + slot * 30.0)


func _encounter_party_origin() -> Vector2:
	var index := controlled_index if _is_alive(controlled_index) else _nearest_living()
	if index < 0 and not fighters.is_empty():
		index = clampi(controlled_index, 0, fighters.size() - 1)
	if index < 0:
		return Vector2(160.0, ARENA_FLOOR_Y - 26.0)
	return _encounter_fighter_origin(index)


func _encounter_fighter_origin(index: int) -> Vector2:
	return Vector2(float(fighters[index]["x"]), ARENA_FLOOR_Y - 26.0)


func _draw_fighter(fighter: Dictionary, index: int) -> void:
	var x: float = fighter["x"]
	var member_id: String = fighter["id"]
	if combat_sprite_sets != null and combat_sprite_sets.has_set(index):
		if _is_alive(index) and index == controlled_index and not auto_mode:
			draw_circle(Vector2(x, 272), 13.0, Color("#f5e1a6"))
		combat_sprite_sets.draw_fighter(self, index, x, ARENA_FLOOR_Y)
		return
	if companion_sprite_sets != null and index == companion_index:
		if _is_alive(index) and index == controlled_index and not auto_mode:
			draw_circle(Vector2(x, 272), 13.0, Color("#f5e1a6"))
		companion_sprite_sets.draw_fighter(self, index, x, ARENA_FLOOR_Y)
		return
	if (member_id == "hero" and ["male", "female"].has(AppState.hero_appearance)) or ["liang-xu", "zhao-ling", "ji-cheng"].has(member_id):
		if _is_alive(index) and index == controlled_index and not auto_mode:
			draw_circle(Vector2(x, 272), 13.0, Color("#f5e1a6"))
		var native_frame: Texture2D
		if member_id == "liang-xu":
			native_frame = _liang_combat_texture(fighter, index)
		elif member_id == "zhao-ling":
			native_frame = _zhao_combat_texture(fighter, index)
		elif member_id == "ji-cheng":
			native_frame = _ji_combat_texture(fighter, index)
		else:
			native_frame = _female_combat_texture(fighter, index) if AppState.hero_appearance == "female" else _male_combat_texture(fighter, index)
		if native_frame != null:
			draw_texture(native_frame, Vector2(roundf(x) - HERO_COMBAT_ANCHOR.x, 272.0 - HERO_COMBAT_ANCHOR.y))
			return
	var color: Color = AppState.MEMBER_DEFS[member_id]["color"]
	if not _is_alive(index):
		draw_rect(Rect2(x - 12, 263, 24, 5), Color("#56636d"))
		return
	if index == controlled_index and not auto_mode:
		draw_circle(Vector2(x, 272), 13.0, Color("#f5e1a6"))
	if float(fighter["dodge_time"]) > 0.0:
		color = color.lightened(0.25)
	draw_circle(Vector2(x, 239), 15.0, Color(0.09, 0.18, 0.21, 0.50))
	draw_rect(Rect2(x - 9, 223, 18, 39), color)
	draw_circle(Vector2(x, 215), 10.0, Color("#e5c594"))
	match member_id:
		"hero":
			if AppState.hero_appearance == "female":
				draw_rect(Rect2(x - 10, 201, 21, 7), Color("#453948"))
				draw_rect(Rect2(x + 9, 205, 5, 32), Color("#453948"))
			else:
				draw_rect(Rect2(x - 10, 202, 18, 5), Color("#273f47"))
		"liang-xu":
			draw_rect(Rect2(x - 10, 202, 19, 5), Color("#c3c4c2"))
			draw_circle(Vector2(x + 11, 207), 5.0, Color("#b3b9ba"))
			draw_rect(Rect2(x + 6, 233, 8, 14), Color("#9b8162"))
		"zhao-ling":
			draw_rect(Rect2(x - 10, 202, 19, 5), Color("#293743"))
			draw_circle(Vector2(x - 10, 215), 4.0, Color("#65c5dc"))
			draw_circle(Vector2(x + 10, 215), 4.0, Color("#65c5dc"))
		"ji-cheng":
			draw_rect(Rect2(x - 10, 202, 14, 6), Color("#abb7b7"))
			draw_rect(Rect2(x + 5, 207, 5, 14), Color("#303a42"))
	draw_rect(Rect2(x - 9, 262, 7, 9), Color("#263e4a"))
	draw_rect(Rect2(x + 2, 262, 7, 9), Color("#263e4a"))
	if bool(fighter["guard"]):
		draw_rect(Rect2(x + (13 if enemy_x > x else -20), 217, 6, 35), Color("#a7d7ee"))
	if float(fighter["attack_cooldown"]) > 0.30:
		draw_rect(Rect2(x + (19 if enemy_x > x else -42), 225, 23, 5), Color("#e3ecde"))


func _draw_enemy() -> void:
	var color: Color = enemy["color"]
	var winding_up := enemy_windup > 0.0 and enemy_hp > 0
	if winding_up:
		var ring_x := enemy_x + _enemy_body_offset_x()
		if enemy_telegraph_scale == Vector2.ONE:
			draw_circle(Vector2(ring_x, enemy_telegraph_center_y), ENEMY_TELEGRAPH_RADIUS, ENEMY_TELEGRAPH_COLOR)
		else:
			draw_set_transform(Vector2(ring_x, enemy_telegraph_center_y), 0.0, enemy_telegraph_scale)
			draw_circle(Vector2.ZERO, ENEMY_TELEGRAPH_RADIUS, ENEMY_TELEGRAPH_COLOR)
			draw_set_transform(Vector2.ZERO)
	if enemy_texture != null:
		var tint := ENEMY_WINDUP_MODULATE if winding_up else Color.WHITE
		if enemy_animation_texture != null:
			var cell := enemy_animation_cell
			var cell_origin := Vector2(_enemy_draw_x() - enemy_animation_anchor.x, ARENA_FLOOR_Y - enemy_animation_anchor.y)
			draw_texture_rect_region(enemy_animation_texture, Rect2(cell_origin, cell), Rect2(Vector2(_enemy_visual_frame() * cell.x, 0.0), cell), tint)
		else:
			draw_texture(enemy_texture, Vector2(roundf(enemy_x) - enemy_anchor.x, ARENA_FLOOR_Y - enemy_anchor.y), tint)
		return
	draw_circle(Vector2(enemy_x, 241), 20.0, Color(0.14, 0.14, 0.21, 0.55))
	draw_rect(Rect2(enemy_x - 17, 217, 34, 41), color)
	draw_rect(Rect2(enemy_x - 11, 227, 22, 9), Color("#f4b293"))
	draw_rect(Rect2(enemy_x - 17, 257, 10, 12), Color("#343a43"))
	draw_rect(Rect2(enemy_x + 7, 257, 10, 12), Color("#343a43"))


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 90)
	canvas.add_child(header)
	title_label = _label(canvas, Vector2(16, 4), 18, Color("#eef7ef"))
	quick_skill_button = Button.new()
	quick_skill_button.position = Vector2(430, 6)
	quick_skill_button.size = Vector2(194, 27)
	quick_skill_button.add_theme_font_size_override("font_size", 11)
	quick_skill_button.pressed.connect(func(): _use_skill())
	canvas.add_child(quick_skill_button)
	hp_label = _label(canvas, Vector2(16, 38), 11, Color("#f2c8ad"))
	energy_label = _label(canvas, Vector2(228, 38), 11, Color("#9edbd9"))
	enemy_hp_label = _label(canvas, Vector2(438, 38), 11, Color("#e4adad"))
	hp_bar = _bar(canvas, Vector2(62, 39), Vector2(146, 11), Color("#d6736d"))
	energy_bar = _bar(canvas, Vector2(282, 39), Vector2(141, 11), Color("#62c9ce"))
	enemy_bar = _bar(canvas, Vector2(505, 39), Vector2(119, 11), Color("#bb6174"))
	for slot in AppState.PARTY_CAPACITY:
		var button := Button.new()
		button.position = Vector2(15 + slot * 103, 65)
		button.size = Vector2(98, 20)
		button.add_theme_font_size_override("font_size", 10)
		button.pressed.connect(_choose_control.bind(slot))
		canvas.add_child(button)
		party_buttons.append(button)
	auto_button = Button.new()
	auto_button.position = Vector2(535, 65)
	auto_button.size = Vector2(91, 20)
	auto_button.add_theme_font_size_override("font_size", 10)
	auto_button.pressed.connect(_toggle_auto)
	canvas.add_child(auto_button)
	telegraph_label = _label(canvas, Vector2(350, 186), 13, Color("#ffe0bf"))
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 302)
	footer.size = Vector2(640, 58)
	canvas.add_child(footer)
	feedback_label = _label(canvas, Vector2(16, 309), 12, Color("#f5d5a7"))
	help_label = _label(canvas, Vector2(16, 332), 11, Color("#aac6c6"))
	_build_pause_overlay(canvas)
	_build_result_overlay(canvas)


func _label(parent: Node, position: Vector2, font_size: int, font_color: Color) -> Label:
	var label := Label.new()
	label.position = position
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", font_color)
	parent.add_child(label)
	return label


func _bar(parent: Node, position: Vector2, size: Vector2, fill: Color) -> ProgressBar:
	var bar := ProgressBar.new()
	bar.position = position
	bar.size = size
	bar.show_percentage = false
	bar.add_theme_stylebox_override("background", _style(Color("#273744")))
	bar.add_theme_stylebox_override("fill", _style(fill))
	parent.add_child(bar)
	return bar


func _style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	return style


func _build_pause_overlay(canvas: CanvasLayer) -> void:
	pause_overlay = ColorRect.new()
	pause_overlay.color = Color(0.04, 0.07, 0.12, 0.89)
	pause_overlay.size = Vector2(640, 360)
	pause_overlay.visible = false
	canvas.add_child(pause_overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(55, 43)
	panel.size = Vector2(530, 286)
	panel.color = Color("#263945")
	pause_overlay.add_child(panel)
	pause_title = _label(pause_overlay, Vector2(78, 57), 19, Color("#f2e7c8"))
	pause_skill_button = Button.new()
	pause_skill_button.position = Vector2(78, 99)
	pause_skill_button.size = Vector2(288, 36)
	pause_skill_button.pressed.connect(_queue_skill)
	pause_overlay.add_child(pause_skill_button)
	for stage in 2:
		var button := Button.new()
		button.position = Vector2(78 + stage * 246, 142)
		button.size = Vector2(230, 32)
		button.add_theme_font_size_override("font_size", 10)
		button.pressed.connect(_queue_job_skill.bind(""))
		pause_overlay.add_child(button)
		pause_job_skill_buttons.append(button)
	pause_resume_button = Button.new()
	pause_resume_button.position = Vector2(430, 99)
	pause_resume_button.size = Vector2(124, 36)
	pause_resume_button.pressed.connect(_toggle_pause)
	pause_overlay.add_child(pause_resume_button)
	pause_target_label = _label(pause_overlay, Vector2(78, 185), 12, Color("#bfd7d3"))
	pause_order_feedback = _label(pause_overlay, Vector2(78, 292), 11, Color("#d8c99f"))
	pause_policy_button = Button.new()
	pause_policy_button.position = Vector2(365, 179)
	pause_policy_button.size = Vector2(189, 27)
	pause_policy_button.add_theme_font_size_override("font_size", 11)
	pause_policy_button.pressed.connect(_cycle_ai_policy)
	pause_overlay.add_child(pause_policy_button)
	for slot in 4:
		var button := Button.new()
		button.position = Vector2(78 + slot * 119, 211)
		button.size = Vector2(111, 28)
		button.add_theme_font_size_override("font_size", 10)
		pause_overlay.add_child(button)
		pause_target_buttons.append(button)
	for command in ["focus", "defend", "skill"]:
		var button := Button.new()
		button.position = Vector2(78 + pause_order_buttons.size() * 160, 249)
		button.size = Vector2(148, 37)
		button.pressed.connect(_issue_order.bind(command))
		pause_overlay.add_child(button)
		pause_order_buttons[command] = button


func _build_result_overlay(canvas: CanvasLayer) -> void:
	result_overlay = ColorRect.new()
	result_overlay.color = Color(0.04, 0.07, 0.12, 0.88)
	result_overlay.size = Vector2(640, 360)
	result_overlay.visible = false
	canvas.add_child(result_overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(112, 99)
	panel.size = Vector2(416, 171)
	panel.color = Color("#263945")
	result_overlay.add_child(panel)
	result_title = _label(result_overlay, Vector2(139, 117), 22, Color("#f2e7c8"))
	result_note = _label(result_overlay, Vector2(139, 158), 12, Color("#c6dcda"))
	result_note.size = Vector2(355, 50)
	result_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	result_button = Button.new()
	result_button.position = Vector2(333, 219)
	result_button.size = Vector2(168, 33)
	result_button.pressed.connect(_return_after_result)
	result_overlay.add_child(result_button)


func _choose_control(index: int) -> void:
	if paused or battle_finished or not _is_alive(index):
		return
	controlled_index = index
	auto_mode = false
	_refresh_text()


func _refresh_text() -> void:
	title_label.text = AppState.text_for("battle_title") % AppState.text_for(String(enemy["name"]))
	hp_label.text = AppState.text_for("battle_hp")
	energy_label.text = AppState.text_for("battle_energy")
	enemy_hp_label.text = AppState.text_for("battle_enemy_hp")
	help_label.text = AppState.text_for("battle_help")
	telegraph_label.text = AppState.text_for("battle_telegraph")
	auto_button.text = AppState.text_for("battle_auto_on" if auto_mode else "battle_auto_off")
	pause_title.text = AppState.text_for("battle_pause_title") % AppState.member_name(String(fighters[controlled_index]["id"]))
	var skill_key: String = AppState.MEMBER_DEFS[String(fighters[controlled_index]["id"])]["skill_key"]
	quick_skill_button.text = "Q · " + AppState.text_for(skill_key)
	pause_skill_button.text = AppState.text_for("battle_skill_use") + " · " + AppState.text_for(skill_key) + (" ✓" if queued_skill else "")
	var job_skill_id := GrowthRules.current_skill_id(AppState.member_state(String(fighters[controlled_index]["id"])))
	var controlled_member: Dictionary = AppState.member_state(String(fighters[controlled_index]["id"]))
	var skills: Array = GrowthRules.SERIES[String(controlled_member["job_series"])]["skills"]
	for stage in pause_job_skill_buttons.size():
		var button: Button = pause_job_skill_buttons[stage]
		var id: String = skills[stage]
		button.visible = stage < int(controlled_member["job_stage"]) and GrowthRules.job_skills_have_effect(String(controlled_member["job_series"]))
		button.text = AppState.text_for("job_skill_" + id) + (" ✓" if queued_job_skill_id == id else "")
		for connection in button.pressed.get_connections():
			button.pressed.disconnect(connection["callable"])
		button.pressed.connect(_queue_job_skill.bind(id))
	pause_resume_button.text = AppState.text_for("battle_resume")
	pause_target_label.text = AppState.text_for("battle_target") % (AppState.member_name(selected_order_id) if selected_order_id != "" else "—")
	pause_policy_button.disabled = selected_order_id == ""
	pause_policy_button.text = AppState.text_for("ai_policy_" + String(AppState.member_state(selected_order_id).get("ai_policy", "balanced"))) if selected_order_id != "" else "AI —"
	pause_order_feedback.text = ""
	for fighter in fighters:
		if String(fighter["id"]) == selected_order_id:
			var order: String = fighter["command"]
			pause_order_feedback.text = AppState.member_name(selected_order_id) + " · " + AppState.text_for("battle_" + ("skill_order" if order == "skill" else order))
			break
	for command in pause_order_buttons:
		pause_order_buttons[command].text = AppState.text_for("battle_" + ("skill_order" if command == "skill" else command))
		pause_order_buttons[command].disabled = selected_order_id == ""
	var targets: Array[String] = []
	for fighter in fighters:
		if String(fighter["id"]) != String(fighters[controlled_index]["id"]) and int(AppState.member_state(String(fighter["id"]))["hp"]) > 0:
			targets.append(String(fighter["id"]))
	for slot in pause_target_buttons.size():
		var button: Button = pause_target_buttons[slot]
		button.visible = slot < targets.size()
		if slot < targets.size():
			button.text = AppState.member_name(targets[slot])
			if not button.pressed.is_connected(_select_order_target.bind(targets[slot])):
				for connection in button.pressed.get_connections():
					button.pressed.disconnect(connection["callable"])
				button.pressed.connect(_select_order_target.bind(targets[slot]))
	result_reward_text = AppState.text_for("growth_rewards") % [result_reward_xp, result_reward_jp] if battle_won else ""
	result_title.text = AppState.text_for("battle_win" if battle_won else "battle_loss")
	result_note.text = AppState.text_for("battle_win_note" if battle_won else "battle_loss_note") + ("\n" + result_reward_text if battle_won else "")
	result_button.text = AppState.text_for("battle_continue" if battle_won else "battle_menu")
	_update_hud()


func _update_hud() -> void:
	var member_id: String = fighters[controlled_index]["id"]
	var member: Dictionary = AppState.member_state(member_id)
	hp_bar.max_value = int(member["max_hp"])
	hp_bar.value = int(member["hp"])
	energy_bar.max_value = int(member["max_energy"])
	energy_bar.value = int(member["energy"])
	enemy_bar.max_value = int(enemy["max_hp"])
	enemy_bar.value = enemy_hp
	feedback_label.text = "%s  %d/%d · %d/%d · %s" % [AppState.member_name(member_id), int(member["hp"]), int(member["max_hp"]), int(member["energy"]), int(member["max_energy"]), feedback_message if feedback_message != "" else AppState.text_for(feedback_key)]
	quick_skill_button.disabled = battle_finished or paused or auto_mode or not _is_alive(controlled_index)
	telegraph_label.visible = enemy_windup > 0.0 and not battle_finished
	for slot in AppState.PARTY_CAPACITY:
		var button: Button = party_buttons[slot]
		button.disabled = slot >= fighters.size() or (slot < fighters.size() and not _is_alive(slot))
		button.text = "%d %s" % [slot + 1, AppState.member_name(String(fighters[slot]["id"]))] if slot < fighters.size() else "%d —" % [slot + 1]


func _exit_tree() -> void:
	if battle_ui_skin != null:
		battle_ui_skin.revert()
