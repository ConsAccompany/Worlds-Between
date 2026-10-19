extends SceneTree

# Authored combat sounds v01 + interface v01: combined audio-cue contract on the actual battle arena.
# Run WINDOWED with an isolated APPDATA (a victory writes the auto save to user://):
#   Godot --path game --resolution 640x360 -s res://tests/<this>.gd -- <report.json> <combat-verify.json> <ui-verify.json>
# Supersedes the historical "prior combat cues keep generated 22.05 kHz PCM" assertion of the UI v01
# wiring checks: combat events now map to authored assets. Mixer recording proves non-silent output on
# the Master bus; it is not a listening audition.
const Cues := preload("res://scripts/game_audio_cues.gd")
const ARENA := "res://scenes/battle_arena.tscn"
const COMBAT := ["attack", "dodge", "guard", "hit", "skill", "heal", "victory", "defeat"]
const UI := ["ui.confirm", "ui.cancel", "ui.notice"]
const PNG := "res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-idle-right-phase-01_m8-prototype_20261014-144815-e729aa41.png"
const LOOP := "res://assets/audio/rpg-2-star-ocean-the-second_scifi-battle_ambient-loop_m7_20261013-211230-37fcaa02.wav"
var checks := []
var app: Node
var cues: Node
var expected_sha := {}
var record: AudioEffectRecord
var windows := {}


func _initialize() -> void:
	call_deferred("_run")


func check(label: String, passed: bool, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": passed, "detail": detail})
	print("COMBAT_SFX_CONTRACT ", "PASS " if passed else "FAIL ", label, "" if detail == null else " " + str(detail))


func count(event: String) -> int:
	return int(cues.accepted_events.get(event, 0))


func sha(data: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(data)
	return context.finish().hex_encode()


func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)


func recording_peak(seconds: float) -> int:
	record.set_recording_active(true)
	await create_timer(seconds, true).timeout
	record.set_recording_active(false)
	var data := record.get_recording()
	var peak := 0
	if data != null:
		for index in range(0, data.data.size() - 1, 2):
			peak = maxi(peak, absi(data.data.decode_s16(index)))
	return peak


func diff(a: Variant, b: Variant, path: String) -> Array:
	if JSON.stringify(a) == JSON.stringify(b):
		return []
	if a is Dictionary and b is Dictionary:
		var out := []
		for field in a.keys() + b.keys().filter(func(k): return not a.has(k)):
			out += diff(a.get(field), b.get(field), path + "/" + str(field))
		return out
	if a is Array and b is Array and a.size() == b.size():
		var out := []
		for index in a.size():
			out += diff(a[index], b[index], path + "/" + str(index))
		return out
	return [[path, a, b]]


# Bus peak meter (post-fader) maximum over a window, in dB.
func meter_peak_db(seconds: float) -> float:
	var best := -200.0
	var until := Time.get_ticks_msec() + int(seconds * 1000.0)
	while Time.get_ticks_msec() < until:
		await process_frame
		best = maxf(best, maxf(AudioServer.get_bus_peak_volume_left_db(0, 0), AudioServer.get_bus_peak_volume_right_db(0, 0)))
	return best


func open_arena() -> Node:
	app.begin_new_run()
	app.begin_battle("patrol", Vector2(330, 215))
	# The real arena scene becomes current with simulation frozen from before _ready, so the enemy and
	# visuals cannot advance by load-time frame deltas; the action script below drives combat exactly.
	var battle: Node = load(ARENA).instantiate()
	battle.process_mode = Node.PROCESS_MODE_DISABLED
	change_scene_to_node(battle)
	await process_frame
	await process_frame
	# The arena's looping ambience shares the Master bus; stop it in every run so recordings isolate cues.
	for child in battle.get_children():
		if child is AudioStreamPlayer:
			child.stop()
	return battle


func without_clock(snapshot: Dictionary) -> Dictionary:
	# Wall-clock fields advance with real frames on their own (the run's play clock and the
	# playtest log's atSeconds stamps); every other field must match exactly.
	snapshot.erase("playTimeSeconds")
	for row in snapshot.get("playtestEvents", []):
		if row is Dictionary:
			row.erase("atSeconds")
	return snapshot


func step(battle: Node, fighter: Dictionary, event: String) -> bool:
	var hero: Dictionary = app.member_state("hero")
	match event:
		"attack":
			fighter.attack_cooldown = 0.0
			return battle._try_attack()
		"dodge":
			hero["energy"] = 60
			fighter.dodge_cooldown = 0.0
			return battle._try_dodge()
		"guard", "hit":
			fighter.dodge_time = 0.0
			fighter.x = battle.enemy_x - 30.0
			fighter.guard = event == "guard"
			hero["energy"] = 60
			battle.enemy_target_index = 0
			battle._apply_enemy_hit()
			return true
		"skill":
			hero["energy"] = 60
			fighter.skill_cooldown = 0.0
			return battle._use_skill()
		"heal":
			# The return value reports the optional VFX layer only (false while VFX are off).
			battle.show_heal_vfx(0)
			return true
		"victory":
			fighter.attack_cooldown = 0.0
			fighter.x = battle.enemy_x - 30.0
			battle.enemy_hp = 1
			return battle._try_attack()
	return false


# One fixed action script through the arena's own combat methods. measure=true records each event's
# Master-bus window; the audio-off run uses the same script so resulting state can be compared.
func combat_script(measure: bool) -> Dictionary:
	seed(7919)
	var battle: Node = await open_arena()
	check("arena is the current scene (%s)" % ("on" if measure else "off"), battle != null and battle.scene_file_path == ARENA and battle.fighters.size() >= 1)
	var fighter: Dictionary = battle.fighters[0]
	fighter.x = battle.enemy_x - 30.0
	for event in ["attack", "dodge", "guard", "hit", "skill", "heal", "victory"]:
		cues._process(0.1)
		var before := count(event)
		var acted := step(battle, fighter, event)
		if measure:
			check("arena %s: action succeeded and dispatched exactly one cue" % event, acted and count(event) == before + 1, [acted, count(event) - before])
			check("arena %s: authored asset stream" % event, cues.stream_sources.get(event) == "asset" and cues.streams[event].resource_path == Cues.ASSETS[event])
			check("arena %s: a voice is playing that stream" % event, cues.players.any(func(player): return player.playing and player.stream == cues.streams[event]))
			windows[event] = await recording_peak(0.2)
		else:
			check("audio off, arena %s: action ran and no cue was accepted" % event, acted and count(event) == 0)
			await create_timer(0.2, true).timeout # same real-time pacing as the measured run
	check("victory finished the battle as a win (%s)" % ("on" if measure else "off"), battle.battle_finished and battle.battle_won)
	var snapshot := without_clock(app.make_snapshot("area", Vector2.ZERO, "combat-audio-test"))
	var state := JSON.stringify({"snapshot": snapshot, "enemyHp": battle.enemy_hp, "fighters": battle.fighters,
		"playerAttacks": battle.player_attack_count, "enemyAttacks": battle.enemy_attack_count,
		"feedback": battle.feedback_key, "rngNext": randi()})
	# Defeat path: a fresh arena, last party member at 1 HP takes the enemy hit.
	battle = await open_arena()
	cues._process(0.1)
	var before_defeat := count("defeat")
	for index in battle.fighters.size():
		app.member_state(String(battle.fighters[index]["id"]))["hp"] = 1
		battle.fighters[index]["x"] = battle.enemy_x - 30.0
	for index in battle.fighters.size():
		if not battle.battle_finished:
			battle.enemy_target_index = index
			battle._apply_enemy_hit()
	if measure:
		check("arena defeat: party loss dispatched exactly one cue", battle.battle_finished and not battle.battle_won and count("defeat") == before_defeat + 1)
		check("arena defeat: authored asset stream", cues.stream_sources.get("defeat") == "asset" and cues.streams["defeat"].resource_path == Cues.ASSETS["defeat"])
		check("arena defeat: a voice is playing that stream", cues.players.any(func(player): return player.playing and player.stream == cues.streams["defeat"]))
		windows["defeat"] = await recording_peak(0.2)
	else:
		check("audio off, arena defeat: party lost and no cue was accepted", battle.battle_finished and not battle.battle_won and count("defeat") == 0)
		await create_timer(0.2, true).timeout
	var defeat_snapshot := without_clock(app.make_snapshot("area", Vector2.ZERO, "combat-audio-test"))
	return {"state": state, "defeat": JSON.stringify({"snapshot": defeat_snapshot, "fighters": battle.fighters, "rngNext": randi()})}


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	for index in [1, 2]:
		var verify: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[index])) if args.size() > index else {}
		for event in verify.get("signal", {}):
			expected_sha[event] = String(verify["signal"][event].get("dataChunkSha256", ""))
	check("verify reports supply 8 combat + 3 UI data-chunk hashes", (COMBAT + UI).all(func(event): return String(expected_sha.get(event, "")).length() == 64))
	check("windowed run (real audio players, not headless dispatch)", DisplayServer.get_name() != "headless" and AudioServer.get_driver_name() != "Dummy", [DisplayServer.get_name(), AudioServer.get_driver_name()])
	var appdata := OS.get_environment("APPDATA").replace("\\", "/").to_lower()
	check("isolated user data dir under a temp APPDATA", appdata.contains("/temp/") and OS.get_user_data_dir().replace("\\", "/").to_lower().begins_with(appdata), OS.get_user_data_dir())
	app = root.get_node("AppState")
	cues = app.audio_cues
	await process_frame

	# Contract constants: flag, voices, gain and the full asset map.
	check("flag name unchanged and default OFF", Cues.FLAG == "--audio-cues-pilot" and not cues.enabled() and cues.enabled_override == -1)
	check("ASSETS maps exactly the 3 UI + 8 combat events, each with a generated fallback spec",
		Cues.ASSETS.size() == 11 and (COMBAT + UI).all(func(event): return Cues.ASSETS.has(event) and Cues.SPECS.has(event)) and Cues.SPECS.size() == 11)
	check("combat asset files exist as imported resources", COMBAT.all(func(event): return ResourceLoader.exists(Cues.ASSETS[event])))

	# Run 1, default OFF (no flag): the full arena script accepts no cue and allocates nothing.
	var off: Dictionary = await combat_script(false)
	check("default OFF: no players, streams or accepted events after the arena script", cues.players.is_empty() and cues.streams.is_empty() and cues.accepted_events.is_empty())

	# Run 2, cues ON with a Master-bus recorder.
	cues.enabled_override = 1
	record = AudioEffectRecord.new()
	AudioServer.add_bus_effect(0, record)
	var record_index := AudioServer.get_bus_effect_count(0) - 1
	await create_timer(0.3, true).timeout
	var baseline := await recording_peak(0.2)
	check("baseline Master window is silent with ambience stopped (peak < -60 dBFS)", baseline < 33, baseline)
	var on: Dictionary = await combat_script(true)
	for event in COMBAT:
		var peak := int(windows.get(event, 0))
		check("Master-bus window after arena %s is non-silent (peak > -50 dBFS)" % event, peak > 103, {"peakSample": peak, "peakDbfs": snappedf(linear_to_db(maxf(peak, 1) / 32768.0), 0.01)})
	check("audio ON/OFF arena runs end in identical game state and RNG position (win path)", on["state"] == off["state"], diff(JSON.parse_string(off["state"]), JSON.parse_string(on["state"]), ""))
	check("audio ON/OFF arena runs end in identical game state and RNG position (loss path)", on["defeat"] == off["defeat"], diff(JSON.parse_string(off["defeat"]), JSON.parse_string(on["defeat"]), ""))

	# Real input path: a J key press through the arena's own _process dispatches the attack cue.
	var battle: Node = await open_arena()
	battle.fighters[0]["x"] = battle.enemy_x - 30.0
	cues._process(0.1)
	var attacks := count("attack")
	var hits: int = battle.player_attack_count
	battle.process_mode = Node.PROCESS_MODE_INHERIT
	key(KEY_J, true)
	await process_frame
	await process_frame
	key(KEY_J, false)
	battle.process_mode = Node.PROCESS_MODE_DISABLED
	await process_frame
	check("real J key in the live arena dispatched the attack cue", battle.player_attack_count == hits + 1 and count("attack") == attacks + 1, [battle.player_attack_count - hits, count("attack") - attacks])
	# Rejected actions stay silent.
	cues._process(0.1)
	battle.fighters[0]["x"] = 10.0
	battle.fighters[0]["attack_cooldown"] = 0.0
	attacks = count("attack")
	battle._try_attack()
	check("out-of-range attack dispatches no cue", count("attack") == attacks)
	cues._process(0.1)
	app.member_state("hero")["energy"] = 0
	battle.fighters[0]["dodge_cooldown"] = 0.0
	var dodges := count("dodge")
	check("dodge rejected for energy dispatches no cue", not battle._try_dodge() and count("dodge") == dodges)
	var hp := int(app.member_state("hero")["hp"])
	cues._process(0.1)
	var heals := count("heal")
	battle.show_heal_vfx(0)
	check("heal cue dispatches with no healing side effect", count("heal") == heals + 1 and int(app.member_state("hero")["hp"]) == hp)

	# Exact delivered content: imported uncompressed PCM equals each authored WAV data chunk.
	for event in COMBAT + UI:
		cues._process(0.1)
		cues.play_cue(event)
		var stream: AudioStreamWAV = cues.streams[event]
		check("asset identity %s: 44.1 kHz mono 16-bit, no loop, <= 1 s, data sha256 = WAV data chunk" % event,
			cues.stream_sources[event] == "asset" and stream.mix_rate == 44100 and not stream.stereo and stream.format == AudioStreamWAV.FORMAT_16_BITS
			and stream.loop_mode == AudioStreamWAV.LOOP_DISABLED and stream.data.size() <= 88200 and sha(stream.data) == expected_sha[event], sha(stream.data))

	# Malformed names never dispatch.
	check("malformed/unknown event names rejected", ["", "ATTACK", "attack ", "unknown", "ui."].all(func(event): return not cues.play_cue(event)))

	# Master settings govern every cue voice; player gain unchanged.
	check("four voices route to Master at the existing -14 dB", cues.players.size() == Cues.VOICES and Cues.VOICES == 4 and cues.players.all(func(player): return player.bus == "Master" and player.volume_db == -14.0))
	app.settings.set_master_volume(0, false)
	check("settings volume 0 mutes the cue bus", AudioServer.is_bus_mute(AudioServer.get_bus_index("Master")))
	app.settings.set_master_volume(40, false)
	check("settings volume 40% applies to the cue bus", not AudioServer.is_bus_mute(0) and absf(AudioServer.get_bus_volume_db(0) - linear_to_db(0.4)) < 0.01, AudioServer.get_bus_volume_db(0))
	AudioServer.remove_bus_effect(0, record_index)
	# AudioEffectRecord taps the bus before its fader/mute, so level checks use the post-fader peak meter.
	# Transient cues read up to ~1 dB above their true peak depending on output-resampling phase (try5:
	# hit at 100% read -26.98 vs -28.01 dB in try3), so the level probe uses the low, transient-free defeat
	# cue and the median of five plays per level; the +-1 dB tolerance is unchanged.
	var levels := {}
	var readings := {}
	for volume in [100, 40, 0]:
		app.settings.set_master_volume(volume, false)
		var plays := []
		for repeat in 5:
			await meter_peak_db(0.3) # let the meter fall back
			cues._process(0.1)
			cues.play_cue("defeat")
			plays.append(snappedf(await meter_peak_db(0.4), 0.01))
		readings[volume] = plays.duplicate()
		plays.sort()
		levels[volume] = plays[2]
	check("post-fader meter: defeat at 40% is 40% of the 100% level (-7.96 dB +-1 dB, median of 5)", absf(levels[40] - levels[100] - linear_to_db(0.4)) <= 1.0, readings)
	check("post-fader meter: defeat while muted stays below -90 dB", levels[0] < -90.0 and levels[100] > -60.0, levels)
	app.settings.set_master_volume(100, false)

	# Coalescing boundary on a combat event, from an exact clock value.
	var base := float(int(cues._clock) + 100)
	check("boundary setup: exact float gaps of 40 ms (>= 0.04) and 39 ms (< 0.04) from the base clock",
		(base + 0.04) - base >= 0.04 and (base + 0.039) - base < 0.04, base)
	cues._clock = base
	var first: bool = cues.play_cue("guard")
	cues._clock = base + 0.039
	var at39: bool = cues.play_cue("guard")
	cues._clock = base + 0.04
	var at40ms: bool = cues.play_cue("guard")
	check("coalescing boundary: guard rejected at 39 ms, accepted at 40 ms", first and not at39 and at40ms, [first, at39, at40ms])

	# Four-voice bound: six distinct combat cues on one tick reuse the round-robin pool.
	cues._clock = base + 10.0
	var accepted := ["attack", "dodge", "guard", "hit", "skill", "heal"].filter(func(event): return cues.play_cue(event)).size()
	check("six same-tick distinct cues accepted on a bounded 4-voice pool", accepted == 6 and cues.players.size() == 4
		and cues.get_children().filter(func(child): return child is AudioStreamPlayer).size() == 4
		and cues.players.filter(func(player): return player.playing).size() <= 4, accepted)
	check("stream cache bounded by known cues", cues.streams.size() <= Cues.SPECS.size())

	# Missing, wrong-type, looped and out-of-contract assets fall back to the generated PCM.
	var probe: Node = Cues.new()
	probe.enabled_override = 1
	var broken := [PNG, LOOP, "res://assets/audio/missing-combat-attack.wav", ""]
	for index in COMBAT.size():
		probe.asset_paths[COMBAT[index]] = broken[index % broken.size()]
	root.add_child(probe)
	for event in COMBAT:
		probe._process(0.05)
		check("fallback %s (%s) plays generated 22.05 kHz PCM" % [event, String(probe.asset_paths[event]).get_file()],
			probe.play_cue(event) and probe.stream_sources[event] == "procedural" and probe.streams[event].mix_rate == 22050)
	var long := AudioStreamWAV.new()
	long.format = AudioStreamWAV.FORMAT_16_BITS
	long.mix_rate = 44100
	var long_pcm := PackedByteArray()
	long_pcm.resize(88202)
	long.data = long_pcm
	var stereo := AudioStreamWAV.new()
	stereo.format = AudioStreamWAV.FORMAT_16_BITS
	stereo.mix_rate = 44100
	stereo.stereo = true
	stereo.data = PackedByteArray([0, 0, 0, 0])
	var slow := AudioStreamWAV.new()
	slow.format = AudioStreamWAV.FORMAT_16_BITS
	slow.mix_rate = 22050
	slow.data = PackedByteArray([0, 0, 0, 0])
	check("usable_asset rejects > 1 s, stereo, 22.05 kHz, empty and null", not Cues.usable_asset(long) and not Cues.usable_asset(stereo)
		and not Cues.usable_asset(slow) and not Cues.usable_asset(AudioStreamWAV.new()) and not Cues.usable_asset(null))
	for player in probe.players:
		player.stop()
	probe.free()

	for player in cues.players:
		player.stop()
	change_scene_to_file("res://scenes/main_menu.tscn")
	await create_timer(0.2, true).timeout
	var failed := checks.filter(func(row): return not row.passed).size()
	if not args.is_empty():
		var file := FileAccess.open(args[0], FileAccess.WRITE)
		file.store_string(JSON.stringify({"checks": checks, "passed": checks.size() - failed, "total": checks.size(),
			"display": DisplayServer.get_name(), "audioDriver": AudioServer.get_driver_name(), "masterWindows": windows,
			"auditionedByListener": false, "audioArtApproved": false}, "  ") + "\n")
	print("COMBAT_SFX_CONTRACT_RESULT ", checks.size() - failed, "/", checks.size())
	if failed == 0:
		print("COMBAT_SFX_CONTRACT_OK")
	quit(1 if failed else 0)
