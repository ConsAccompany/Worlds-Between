extends SceneTree
# TEST-ONLY zpath27 integration check (scripted; NOT the real-input playable flow, NOT a playtest or art approval).
# Covers: malformed language/appearance/package refusals with no state mutation; configure -> actual outskirts scene with
# the zpath27 driver on the real zhao-ling field NPC (position unchanged, hero untouched); call-driven (SCRIPTED) 4-dir
# walk/stop on that driver; a fixture-recruited battle (recruit_member called directly = SETUP FIXTURE) where only the
# Zhao slot uses the companion model and the hero keeps its existing model; rollback restores every knob exactly.
const CONFIG := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
var fails := 0
var passes := 0
var config
var area
var arena


func ck(ok: bool, label: String, detail: Variant = null) -> void:
	if ok:
		passes += 1
		print("ZPATH27_CHECK PASS ", label)
	else:
		fails += 1
		print("ZPATH27_CHECK FAIL ", label, " ", str(detail))


func knobs() -> Dictionary:
	return {"enabled": config.enabled_override, "presenter": area.field_npc_presenter_override,
		"member": arena.companion_combat_member_override, "index": arena.companion_combat_index_override,
		"arenaOverride": arena.combat_sprite_set_override, "arenaIndex": arena.combat_sprite_set_index_override,
		"male": arena.male_playable_path_index_override}


func app_snap(app: Node) -> Dictionary:
	return {"appearance": app.hero_appearance, "language": app.language, "party": app.active_party_ids.duplicate(),
		"recruited": app.recruited_members.duplicate(), "hp": int(app.hero_state["hp"])}


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	config = load(CONFIG)
	area = load("res://scripts/scifi_exploration_area.gd")
	arena = load("res://scripts/battle_arena.gd")
	var app: Node = root.get_node_or_null("AppState")
	var appearance := "male"
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--appearance="):
			appearance = argument.trim_prefix("--appearance=")
	ck(config.DEFAULT_ADOPTED == false and not config.enabled(), "ordinary Zhao default is off")
	var k0 := knobs()
	var a0 := app_snap(app)
	ck(not config.validate("fr", appearance)["ok"], "malformed language refused")
	ck(not config.configure(app, "", appearance)["ok"], "empty language refused by configure")
	ck(not config.configure(app, "en", "robot")["ok"], "malformed appearance refused by configure")
	config.combat_index_override = "res://data/zcombat26/missing.json"
	ck(not config.configure(app, "en", appearance)["ok"], "missing combat index refused")
	config.combat_index_override = ""
	config.supplement_path_override = "res://data/zexplore25/missing.json"
	ck(not config.configure(app, "en", appearance)["ok"], "missing stop supplement refused")
	config.supplement_path_override = ""
	ck(knobs() == k0 and app_snap(app) == a0, "refusals mutated no knob or AppState", [knobs(), app_snap(app)])
	for language in ["en", "zh"]:
		var r: Dictionary = config.configure(app, language, appearance)
		ck(r["ok"], "configure %s/%s" % [language, appearance], r)
		if not r["ok"]:
			break
		ck(app.language == language and app.hero_appearance == appearance and not app.recruited_members.has("zhao-ling"), "fresh run, no forced recruit " + language)
		change_scene_to_file(r["scene"])
		for _i in 10:
			await process_frame
		var scene := current_scene
		ck(scene != null and scene.scene_file_path == r["scene"] and scene.destination_id == "scifi.outskirts", "outskirts scene open " + language)
		ck(config.npc_attached(scene), "zpath27 driver attached to actual zhao-ling field NPC " + language)
		ck(scene.field_npc.position == Vector2(190, 150) and scene.npc_position == Vector2(190, 150), "NPC position unchanged " + language, scene.field_npc.position)
		ck(scene.sprite_pilot == null or scene.sprite_pilot.get_script().resource_path != config.DRIVER_PATH, "hero never uses the Zhao driver " + language)
		var d: Node = scene.field_npc_driver
		var idle0: Texture2D = d.sprite_set["clips"]["idle"]["south"]["textures"][0]
		ck(scene.field_npc.texture == idle0, "ordinary NPC shows south idle f00 statically " + language)
		# SCRIPTED: call-driven direction/walk/stop to prove the loaded banks; ordinary play never calls these.
		for direction in ["south", "west", "north", "east"]:
			d.face(direction)
			for _t in 9:
				d.advance(1.0 / 30.0)
				d.walk()
			var walk_state: Dictionary = d.state()
			d.idle()
			var stop_state: Dictionary = d.state()
			d.advance(0.121)
			d.idle()
			var settled: Dictionary = d.state()
			ck(walk_state["action"] == "walk" and stop_state["action"] == "stop" and settled["action"] == "idle" and settled["facing"] == direction,
				"SCRIPTED %s walk -> stop bridge -> idle " % direction, [walk_state, stop_state, settled])
		d.face("south")
		d.idle()
		ck(scene.field_npc.position == Vector2(190, 150), "scripted calls never move the NPC " + language)
		# SETUP FIXTURE: direct recruit to build a party for the battle-model check (the real-input recruit is not covered here).
		ck(app.recruit_member("zhao-ling"), "fixture recruit " + language)
		var battle: Node = load("res://scenes/battle_arena.tscn").instantiate()
		root.add_child(battle)
		await process_frame
		var slot: int = app.active_party_ids.find("zhao-ling")
		ck(battle.companion_sprite_sets != null and battle.companion_index == slot and battle.companion_sprite_sets.loaded_count() == 1, "only Zhao slot loads companion model " + language)
		var hero_slot: int = app.active_party_ids.find("hero")
		ck(battle.companion_sprite_sets != null and not battle.companion_sprite_sets.has_set(hero_slot), "companion model never holds the hero slot " + language)
		if battle.combat_sprite_sets != null:
			ck(not battle.combat_sprite_sets.has_set(slot) and battle.combat_sprite_sets.has_set(hero_slot), "hero model keeps hero slot only " + language)
		battle.queue_free()
		await process_frame
		# Refused Zhao set falls back for Zhao only; hero model untouched.
		var saved: String = arena.companion_combat_index_override
		arena.companion_combat_index_override = "res://data/zcombat26/missing.json"
		var b2: Node = load("res://scenes/battle_arena.tscn").instantiate()
		root.add_child(b2)
		await process_frame
		ck(b2.companion_sprite_sets == null, "refused Zhao set leaves Zhao legacy " + language)
		b2.queue_free()
		arena.companion_combat_index_override = saved
		# Explicit combat disable intent wins.
		arena.combat_sprite_set_override = 0
		var b3: Node = load("res://scenes/battle_arena.tscn").instantiate()
		root.add_child(b3)
		await process_frame
		ck(b3.companion_sprite_sets == null, "explicit combat_sprite_set_override=0 keeps companion off " + language)
		b3.queue_free()
		arena.combat_sprite_set_override = k0["arenaOverride"]
		await process_frame
		config.rollback()
		ck(knobs() == k0, "rollback restores every knob exactly " + language, [knobs(), k0])
	print("ZPATH27_CHECK_SUMMARY passes=%d fails=%d" % [passes, fails])
	if fails == 0:
		print("ZPATH27_CHECK_ALL_PASS appearance=" + appearance)
	quit(0 if fails == 0 else 1)
