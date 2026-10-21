extends SceneTree
# Setup fixture for profile isolation/rollback. Not normal-input gameplay or artistic acceptance.
const Config := preload("res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_config_opt-in-v01_20261021-170200-5e1c24a7.gd")
const Driver := preload("res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd")
var Arena: GDScript
var checks := 0
var failed := false

func _initialize() -> void:
	_run.call_deferred()

func ck(ok: bool, label: String) -> void:
	checks += 1
	failed = failed or not ok
	print("MALE_SCOPE ", "PASS " if ok else "FAIL ", label)

func _run() -> void:
	Arena = load("res://scripts/battle_arena.gd")
	var app: Node = root.get_node("AppState")
	ck(not Driver.DEFAULT_ADOPTED, "ordinary male adoption remains false")
	var cfg := Config.configure(app, "en", "scifi.outskirts")
	ck(cfg.get("ok", false), "complete male package validates")
	ck(Arena.combat_sprite_set_override == -1 and Arena.combat_sprite_set_index_override == "", "male config does not change generic combat choices")
	ck(Arena.male_playable_path_index_override == Config.COMBAT_INDEX_PATH, "male-specific combat profile selected")
	# Fixture: switch actor while the male profile remains active, as a later new run may do.
	app.hero_appearance = "female"
	ck(Arena.heroine_default_battle_applies(["hero"], "female"), "active male profile cannot suppress the authorized heroine default")
	ck(change_scene_to_file("res://scenes/battle_arena.tscn") == OK, "female arena enters with male profile still active")
	for i in 4:
		await process_frame
	var battle: Node = current_scene
	ck(battle.heroine_default_active and battle.fighters[0].has("contact_event_id"), "female default and contact logic still active")
	ck(battle.combat_sprite_sets != null and battle.combat_sprite_sets.sets[0]["key"] == "hero:female", "female receives the female combat set")
	Config.rollback()
	ck(Driver.male_enabled_override == -1 and Arena.male_playable_path_index_override == "", "rollback clears only the profile it installed")
	# Existing explicit settings must survive configure/rollback exactly, including nested configure calls.
	Driver.male_enabled_override = 0
	Driver.registry_path_override = "user://prior-registry.json"
	Driver.supplement_path_override = "user://prior-supplement.json"
	Arena.combat_sprite_set_override = 0
	Arena.combat_sprite_set_index_override = "user://prior-generic-combat.json"
	Arena.male_playable_path_index_override = "user://prior-male-combat.json"
	ck(Config.configure(app, "zh", "scifi.outskirts").get("ok", false), "configuration may temporarily replace an existing male profile")
	ck(Config.configure(app, "zh", "scifi.outskirts").get("ok", false), "reconfiguration is bounded and retains original rollback values")
	Config.rollback()
	ck(Driver.male_enabled_override == 0 and Driver.registry_path_override == "user://prior-registry.json" and Driver.supplement_path_override == "user://prior-supplement.json", "rollback restores all earlier exploration choices")
	ck(Arena.combat_sprite_set_override == 0 and Arena.combat_sprite_set_index_override == "user://prior-generic-combat.json" and Arena.male_playable_path_index_override == "user://prior-male-combat.json", "rollback preserves earlier generic and actor-specific battle choices")
	Config.rollback()
	ck(Driver.male_enabled_override == 0, "repeated rollback is harmless")
	if not failed:
		print("MALE_SCOPE_ALL_PASS checks=", checks)
	quit(1 if failed else 0)
