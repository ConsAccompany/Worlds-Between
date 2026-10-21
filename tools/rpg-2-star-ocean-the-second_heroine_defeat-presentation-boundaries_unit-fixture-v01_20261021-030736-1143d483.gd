extends SceneTree
# Synthetic unit fixture only: mutates in-memory copied actor/clock state, never game assets or an actual play run.
var failures := []
var checks := 0
func ck(value: bool, label: String) -> void:
	checks += 1
	if not value: failures.append(label);print("DEFEAT_UNIT_FAIL ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.hero_state["hp"] = 0
	var script = load("res://scripts/battle_arena.gd")
	script.heroine_sea_contact_override = 1
	var arena: Node = script.new()
	var fighters: Array[Dictionary] = [{"id":"hero"}]
	arena.fighters = fighters
	var player = load("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd").new()
	var keys: Array[String] = ["hero:female"]
	player.configure("res://data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json",keys)
	arena.combat_sprite_sets = player
	ck(player.has_set(0),"genuine heroine package loads")
	player.states[0]["action"] = "hit"
	ck(arena._authored_heroine_defeat_playing(),"finishing-damage handoff waits for defeat entry")
	player.states[0]["action"] = "defeat"
	var duration: float = player.sets[0]["actions"]["defeat"]["duration"]
	ck(absf(duration-0.3)<0.000000001,"duration comes from authored9/30s clip")
	for item in [[0.0,true],[0.1,true],[0.2,true],[duration-0.0000001,true],[duration,false],[duration+0.0000001,false]]:
		player.states[0]["clock"] = item[0]
		ck(arena._authored_heroine_defeat_playing() == item[1],"clock boundary "+str(item[0]))
	player.states[0]["clock"] = 0.0
	script.heroine_sea_contact_override = 0
	ck(not arena._authored_heroine_defeat_playing(),"explicit contact disable stays immediate")
	script.heroine_sea_contact_override = 1
	app.hero_appearance = "male"
	ck(not arena._authored_heroine_defeat_playing(),"male stays immediate")
	app.hero_appearance = "female"
	app.hero_state["hp"] = 100
	ck(not arena._authored_heroine_defeat_playing(),"alive heroine never delays results")
	app.hero_state["hp"] = 0
	player.sets[0]["set_id"] = "synthetic-other-set"
	ck(not arena._authored_heroine_defeat_playing(),"other loaded female fixture does not adopt heroine result timing")
	arena.combat_sprite_sets = null
	ck(not arena._authored_heroine_defeat_playing(),"missing set stays immediate")
	arena.free()
	script.heroine_sea_contact_override = -1
	print("DEFEAT_UNIT_", "PASS" if failures.is_empty() else "FAIL", " checks=",checks)
	quit(0 if failures.is_empty() else 1)
