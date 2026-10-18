extends SceneTree

const Cues := preload("res://scripts/game_audio_cues.gd")
var checks := []
var app: Node
var cues: Node


func _initialize() -> void:
	call_deferred("_run")


func check(label: String, passed: bool) -> void:
	checks.append({"check": label, "passed": passed})
	print("AUDIO_CUE ", "PASS " if passed else "FAIL ", label)


func _run() -> void:
	app = root.get_node("AppState")
	cues = app.audio_cues
	cues.set_process(false)
	check("default disabled; no streams or players allocated", not cues.enabled() and not cues.play_cue("attack") and cues.players.is_empty() and cues.streams.is_empty())
	var before := JSON.stringify(app.make_snapshot("area", Vector2.ZERO, "audio-test"))
	cues.enabled_override = 1
	check("unknown cue rejected", not cues.play_cue("unknown"))
	seed(499)
	var expected_rng := randi()
	seed(499)
	check("first cue accepted", cues.play_cue("attack"))
	check("PCM generation does not consume global RNG", randi() == expected_rng)
	check("same-tick duplicate coalesced", not cues.play_cue("attack"))
	if DisplayServer.get_name() != "headless":
		check("windowed cue starts actual AudioStreamPlayer", cues.players.any(func(player): return player.playing))
	cues._process(0.05)
	check("cue can repeat after cooldown", cues.play_cue("attack"))
	for event in Cues.SPECS:
		cues._process(0.05)
		check("cue accepted: " + event, cues.play_cue(event))
		var stream: AudioStreamWAV = cues.streams[event]
		var peak := 0
		for index in stream.data.size() / 2:
			peak = maxi(peak, absi(stream.data.decode_s16(index * 2)))
		check("bounded click-free PCM: " + event, stream.mix_rate == 22050 and not stream.stereo and stream.data.decode_s16(0) == 0 and stream.data.decode_s16(stream.data.size() - 2) == 0 and peak > 100 and peak < 8000)
	check("four-voice pool and one cached stream per cue", cues.players.size() == 4 and cues.streams.size() == Cues.SPECS.size())
	var cached: AudioStreamWAV = cues.streams["attack"]
	cues._process(0.05)
	cues.play_cue("attack")
	check("repeated cue reuses cached stream", cues.streams["attack"] == cached)
	check("all voices route to Master volume", cues.players.all(func(player): return player.bus == "Master" and player.volume_db == -14.0))
	app.settings.set_master_volume(0, false)
	check("settings zero volume mutes cue bus", AudioServer.is_bus_mute(AudioServer.get_bus_index("Master")))
	app.settings.set_master_volume(50, false)
	check("settings restore affects cue bus", not AudioServer.is_bus_mute(0) and absf(AudioServer.get_bus_volume_db(0) - linear_to_db(0.5)) < 0.01)
	var button := Button.new()
	root.add_child(button)
	cues._process(0.05)
	var old_count := int(cues.accepted_events.get("ui.confirm", 0))
	button.pressed.emit()
	check("actual UI button pressed signal triggers cue", int(cues.accepted_events["ui.confirm"]) == old_count + 1)
	button.free()
	check("sound/UI event leaves game snapshot unchanged", JSON.stringify(app.make_snapshot("area", Vector2.ZERO, "audio-test")) == before)
	# Settings overlay pauses gameplay; its UI still emits on an ALWAYS service.
	paused = true
	cues._process(0.05)
	check("UI cue allowed while gameplay paused", cues.process_mode == Node.PROCESS_MODE_ALWAYS and cues.play_cue("ui.confirm"))
	paused = false
	if not OS.get_cmdline_user_args().has("--service-only"):
		await _battle_events()
	for player in cues.players:
		player.stop()
		player.stream = null
	# AudioServer retires playback references on its mixer thread. Allow a real
	# mixer interval before quitting this otherwise very short headless test.
	await create_timer(0.15).timeout
	var failed := checks.filter(func(row): return not row.passed).size()
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		var file := FileAccess.open(args[0], FileAccess.WRITE)
		file.store_string(JSON.stringify({"checks": checks, "passed": checks.size() - failed, "total": checks.size(), "audioArtApproved": false, "headlessPlaybackIsNotAudition": true}, "  "))
	print("AUDIO_CUE_RESULT ", checks.size() - failed, "/", checks.size())
	quit(1 if failed else 0)


func _battle_events() -> void:
	app.begin_new_run()
	app.begin_battle("patrol", Vector2(330, 215))
	var battle: Node = load("res://scenes/battle_arena.tscn").instantiate()
	root.add_child(battle)
	battle.set_process(false)
	battle.set_physics_process(false)
	await process_frame
	await process_frame
	var fighter: Dictionary = battle.fighters[0]
	fighter.x = battle.enemy_x - 30.0
	for event in ["attack", "dodge", "guard", "hit"]:
		cues._process(0.1)
		var old := int(cues.accepted_events.get(event, 0))
		fighter.attack_cooldown = 0.0
		fighter.dodge_cooldown = 0.0
		fighter.dodge_time = 0.0
		fighter.guard = event == "guard"
		app.member_state("hero")["energy"] = 60
		if event == "attack":
			battle._try_attack(0)
		elif event == "dodge":
			battle._try_dodge(0)
		else:
			battle.enemy_target_index = 0
			battle._apply_enemy_hit()
		check("normal battle event triggers with VFX off: " + event, int(cues.accepted_events.get(event, 0)) == old + 1)
	cues._process(0.1)
	fighter.dodge_cooldown = 0.0
	app.member_state("hero")["energy"] = 0
	var old_dodge := int(cues.accepted_events.get("dodge", 0))
	battle._try_dodge(0)
	check("rejected dodge emits no successful cue", int(cues.accepted_events.get("dodge", 0)) == old_dodge)
	cues._process(0.1)
	app.member_state("hero")["energy"] = 60
	fighter.skill_cooldown = 0.0
	var old_skill := int(cues.accepted_events.get("skill", 0))
	battle._use_skill(0)
	check("normal successful skill triggers cue", int(cues.accepted_events.get("skill", 0)) == old_skill + 1)
	cues._process(0.1)
	fighter.x = 10.0
	fighter.attack_cooldown = 0.0
	var old_attack := int(cues.accepted_events.get("attack", 0))
	battle._try_attack(0)
	check("out-of-range attack has no contact cue", int(cues.accepted_events.get("attack", 0)) == old_attack)
	# Heal is a presentation API only; the MVP has no healing combat mechanic.
	cues._process(0.1)
	var hp := int(app.member_state("hero")["hp"])
	check("heal presentation cue has no healing side effect", cues.play_cue("heal") and int(app.member_state("hero")["hp"]) == hp)
	cues._process(0.1)
	fighter.x = battle.enemy_x - 30.0
	fighter.attack_cooldown = 0.0
	battle.enemy_hp = 1
	var old_victory := int(cues.accepted_events.get("victory", 0))
	battle._try_attack(0)
	check("real lethal attack triggers victory cue", battle.battle_finished and int(cues.accepted_events.get("victory", 0)) == old_victory + 1)
	for child in battle.get_children():
		if child is AudioStreamPlayer:
			child.stop()
			child.stream = null
	battle.queue_free()
	await process_frame
	app.begin_new_run()
	app.begin_battle("patrol", Vector2(330, 215))
	var defeat_battle: Node = load("res://scenes/battle_arena.tscn").instantiate()
	root.add_child(defeat_battle)
	defeat_battle.set_process(false)
	await process_frame
	app.member_state("hero")["hp"] = 1
	defeat_battle.fighters[0]["x"] = defeat_battle.enemy_x - 30.0
	defeat_battle.enemy_target_index = 0
	var old_defeat := int(cues.accepted_events.get("defeat", 0))
	cues._process(0.1)
	defeat_battle._apply_enemy_hit()
	check("real party defeat triggers defeat cue", defeat_battle.battle_finished and int(cues.accepted_events.get("defeat", 0)) == old_defeat + 1)
	for child in defeat_battle.get_children():
		if child is AudioStreamPlayer:
			child.stop()
			child.stream = null
	defeat_battle.queue_free()
	await process_frame
