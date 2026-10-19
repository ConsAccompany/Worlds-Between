extends SceneTree

# Authored interface sounds v01: asset identity, real UI dispatch, fallback, routing and bounds.
# Root v02: explicitly inject viewport-local mouse coordinates at640/1280 backing; key dispatch unchanged.
# https://docs.godotengine.org/en/stable/classes/class_viewport.html#class-viewport-method-push-input
# Run WINDOWED at640x360 or1280x720 with an isolated APPDATA (the manual save and settings write user://):
#   Godot --path game --resolution 640x360 -s res://tests/<this>.gd -- <report.json> <wav-verify-report.json>
# Mixer recording proves non-silent output reached the Master bus; it is not a listening audition.
const Cues := preload("res://scripts/game_audio_cues.gd")
const UI_EVENTS := ["ui.confirm", "ui.cancel", "ui.notice"]
const PNG := "res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-idle-right-phase-01_m8-prototype_20261014-144815-e729aa41.png"
const LOOP := "res://assets/audio/rpg-2-star-ocean-the-second_scifi-battle_ambient-loop_m7_20261013-211230-37fcaa02.wav"
var checks := []
var app: Node
var cues: Node
var expected_sha := {}


func _initialize() -> void:
	call_deferred("_run")


func check(label: String, passed: bool, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": passed, "detail": detail})
	print("UI_SFX_WIRING ", "PASS " if passed else "FAIL ", label, "" if detail == null else " " + str(detail))


func count(event: String) -> int:
	return int(cues.accepted_events.get(event, 0))


func settle(seconds := 0.08) -> void:
	await create_timer(seconds, true).timeout


func click(control: Control) -> void:
	var at := control.get_global_rect().get_center()
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		event.position = at
		event.global_position = at
		control.get_viewport().push_input(event, true)
		await process_frame


func key(code: Key) -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = pressed
		Input.parse_input_event(event)
		await process_frame


func sha(data: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(data)
	return context.finish().hex_encode()


func playing_with(event: String) -> bool:
	return cues.players.any(func(player): return player.playing and player.stream == cues.streams.get(event))


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var verify: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[1])) if args.size() > 1 else {}
	for event in UI_EVENTS:
		expected_sha[event] = String(verify.get("signal", {}).get(event, {}).get("dataChunkSha256", ""))
	check("verify report supplies three data-chunk hashes", expected_sha.values().all(func(value): return value.length() == 64))
	check("windowed run (real audio players, not headless dispatch)", DisplayServer.get_name() != "headless" and AudioServer.get_driver_name() != "Dummy", [DisplayServer.get_name(), AudioServer.get_driver_name()])
	var appdata := OS.get_environment("APPDATA").replace("\\", "/").to_lower()
	check("isolated user data dir under a temp APPDATA", appdata.contains("/temp/") and OS.get_user_data_dir().replace("\\", "/").to_lower().begins_with(appdata), OS.get_user_data_dir())
	app = root.get_node("AppState")
	cues = app.audio_cues
	await process_frame

	# Default OFF: real button presses and every UI cue are rejected; nothing is allocated.
	check("flag name unchanged", Cues.FLAG == "--audio-cues-pilot")
	check("default disabled without the flag", not cues.enabled())
	await key(KEY_F10)
	check("F10 opens settings overlay", app.settings.is_open())
	await click(app.settings.overlay.reset_button)
	await key(KEY_ESCAPE)
	check("Esc closes settings overlay", not app.settings.is_open() and not paused)
	check("default OFF: real clicks/close accepted no cue, no players/streams", cues.accepted_events.is_empty() and cues.players.is_empty() and cues.streams.is_empty())
	check("default OFF: direct UI cues rejected", UI_EVENTS.all(func(event): return not cues.play_cue(event)))

	cues.enabled_override = 1
	var record := AudioEffectRecord.new()
	AudioServer.add_bus_effect(0, record)
	var record_index := AudioServer.get_bus_effect_count(0) - 1
	record.set_recording_active(true)

	# Settings overlay: a real button click plays the authored confirm cue.
	await settle()
	await key(KEY_F10)
	check("settings overlay pauses gameplay", app.settings.is_open() and paused)
	await settle()
	await click(app.settings.overlay.reset_button)
	check("real reset-button click accepted ui.confirm once", count("ui.confirm") == 1)
	check("ui.confirm uses authored asset", cues.stream_sources.get("ui.confirm") == "asset" and cues.streams["ui.confirm"].resource_path == Cues.ASSETS["ui.confirm"])
	check("ui.confirm voice actually playing", playing_with("ui.confirm"))
	# Esc (keycode + physical) closes the menu with the cancel cue.
	await settle()
	await key(KEY_ESCAPE)
	check("real Esc close accepted ui.cancel once", count("ui.cancel") == 1 and not app.settings.is_open() and not paused)
	check("ui.cancel uses authored asset", cues.stream_sources.get("ui.cancel") == "asset" and cues.streams["ui.cancel"].resource_path == Cues.ASSETS["ui.cancel"])
	check("ui.cancel voice actually playing", playing_with("ui.cancel"))
	# Close button: the specific cancel cue replaces the generic click of the same press.
	await settle()
	await key(KEY_F10)
	await settle()
	var confirms := count("ui.confirm")
	await click(app.settings.overlay.close_button)
	check("real Close-button click: one ui.cancel, generic confirm superseded", count("ui.cancel") == 2 and count("ui.confirm") == confirms and not app.settings.is_open())

	# Save screen: a successful manual save plays the neutral notice; Back plays cancel.
	await settle()
	app.begin_new_run()
	app.save_screen_mode = "save"
	app.save_return_scene = "res://scenes/main_menu.tscn"
	change_scene_to_file("res://scenes/save_screen.tscn")
	await process_frame
	await process_frame
	var screen: Node = current_scene
	check("save screen loaded", screen != null and screen.name == "SaveScreen")
	var snapshot_before := JSON.stringify(app.make_snapshot("map", Vector2.ZERO, "audio-test"))
	confirms = count("ui.confirm")
	await click(screen.manual_save_buttons[0])
	check("real Save click: save succeeded", screen.feedback_label.text != app.text_for("save_failed") and screen.feedback_label.text != "", screen.feedback_label.text)
	check("real Save click accepted ui.notice once; generic confirm superseded", count("ui.notice") == 1 and count("ui.confirm") == confirms)
	check("ui.notice uses authored asset", cues.stream_sources.get("ui.notice") == "asset" and cues.streams["ui.notice"].resource_path == Cues.ASSETS["ui.notice"])
	check("ui.notice voice actually playing", playing_with("ui.notice"))
	# Real frames pass during the click, and an active run's play clock advances on its own; only that field may differ.
	var before: Dictionary = JSON.parse_string(snapshot_before)
	var after: Dictionary = JSON.parse_string(JSON.stringify(app.make_snapshot("map", Vector2.ZERO, "audio-test")))
	var changed := before.keys().filter(func(field): return JSON.stringify(before[field]) != JSON.stringify(after.get(field)))
	check("save click leaves game snapshot unchanged apart from the running play clock", changed.all(func(field): return field == "playTimeSeconds"), changed)
	var same_frame := JSON.stringify(app.make_snapshot("map", Vector2.ZERO, "audio-test"))
	cues._process(0.05)
	for event in UI_EVENTS:
		cues.play_cue(event)
	check("same-frame UI cue playback leaves the full snapshot byte-identical", JSON.stringify(app.make_snapshot("map", Vector2.ZERO, "audio-test")) == same_frame)
	await settle(0.35)
	record.set_recording_active(false)
	var recording := record.get_recording()
	var peak := 0
	if recording != null:
		for index in range(0, recording.data.size() - 1, 2):
			peak = maxi(peak, absi(recording.data.decode_s16(index)))
	check("Master-bus recording of real UI dispatch is non-silent (peak > -50 dBFS)", peak > 103, {"peakSample": peak, "peakDbfs": snappedf(linear_to_db(maxf(peak, 1) / 32768.0), 0.01)})
	AudioServer.remove_bus_effect(0, record_index)
	await settle()
	var cancels := count("ui.cancel")
	await click(screen.back_button)
	await process_frame
	await process_frame
	check("real Back click accepted ui.cancel and returned", count("ui.cancel") == cancels + 1 and current_scene != null and current_scene.name == "MainMenu")

	# Exact delivered content: imported uncompressed PCM equals the authored WAV data chunk.
	for event in UI_EVENTS:
		var stream: AudioStreamWAV = cues.streams[event]
		check("asset identity %s: 44.1 kHz mono 16-bit, no loop, data sha256 = WAV data chunk" % event,
			stream.mix_rate == 44100 and not stream.stereo and stream.format == AudioStreamWAV.FORMAT_16_BITS
			and stream.loop_mode == AudioStreamWAV.LOOP_DISABLED and sha(stream.data) == expected_sha[event], sha(stream.data))

	# Master settings still govern every cue voice.
	check("all voices route to Master at the existing -14 dB", cues.players.all(func(player): return player.bus == "Master" and player.volume_db == -14.0))
	app.settings.set_master_volume(0, false)
	check("settings volume 0 mutes the cue bus", AudioServer.is_bus_mute(AudioServer.get_bus_index("Master")))
	app.settings.set_master_volume(40, false)
	check("settings volume 40 applies to the cue bus", not AudioServer.is_bus_mute(0) and absf(AudioServer.get_bus_volume_db(0) - linear_to_db(0.4)) < 0.01)
	app.settings.set_master_volume(100, false)

	# Coalescing and supersession at exact same-tick boundaries.
	await settle()
	check("same-tick duplicate notice coalesced", cues.play_cue("ui.notice") and not cues.play_cue("ui.notice"))
	await settle()
	check("confirm after a same-tick cancel is suppressed", cues.play_cue("ui.cancel") and not cues.play_cue("ui.confirm"))
	await settle()
	cues.play_cue("ui.confirm")
	var voice: AudioStreamPlayer = cues.players[cues._confirm_voice]
	check("notice after a same-tick confirm replaces that confirm voice", cues.play_cue("ui.notice") and voice.stream == cues.streams["ui.notice"])
	await settle()
	var boundary_start: bool = cues.play_cue("ui.notice")
	cues._process(0.039)
	var boundary_reject: bool = boundary_start and not cues.play_cue("ui.notice")
	cues._process(0.002)
	check("coalescing boundary: rejected at 39 ms, accepted at 41 ms", boundary_reject and cues.play_cue("ui.notice"))

	# Exact40ms boundary, isolated same-frame clock/last state; no threshold change.
	var saved_clock: float = cues._clock
	var saved_last: Dictionary = cues._last.duplicate(true)
	cues._clock = 0.0
	cues._last.clear()
	var exact_start: bool = cues.play_cue("ui.notice")
	cues._clock = 0.039
	var exact_before: bool = not cues.play_cue("ui.notice")
	cues._clock = 0.04
	check("exact40ms duplicate boundary accepts (39ms rejects)", exact_start and exact_before and cues.play_cue("ui.notice"))
	cues._clock = saved_clock
	cues._last = saved_last

	# Bounded voices and cache across many mixed UI/combat cues.
	var cached: AudioStreamWAV = cues.streams["ui.confirm"]
	for index in 24:
		cues._process(0.05)
		cues.play_cue(["ui.confirm", "ui.cancel", "ui.notice", "attack", "guard", "skill"][index % 6])
	check("four-voice pool reused", cues.players.size() == Cues.VOICES and cues.get_children().filter(func(child): return child is AudioStreamPlayer).size() == Cues.VOICES)
	check("stream cache bounded by known cues and reused", cues.streams.size() <= Cues.SPECS.size() and cues.streams["ui.confirm"] == cached)
	check("prior combat cues keep generated 22.05 kHz PCM", ["attack", "guard", "skill"].all(func(event): return cues.stream_sources.get(event) == "procedural" and cues.streams[event].mix_rate == 22050))

	# Missing, wrong-type and wrong-format assets fall back to generated PCM without errors.
	var probe: Node = Cues.new()
	probe.enabled_override = 1
	probe.asset_paths["ui.confirm"] = "res://assets/audio/missing-ui-confirm.wav"
	probe.asset_paths["ui.cancel"] = PNG
	probe.asset_paths["ui.notice"] = LOOP
	root.add_child(probe)
	for event in UI_EVENTS:
		probe._process(0.05)
		check("fallback %s (%s) plays generated PCM" % [event, probe.asset_paths[event].get_file()], probe.play_cue(event) and probe.stream_sources[event] == "procedural" and probe.streams[event].mix_rate == 22050)
	var eight := AudioStreamWAV.new()
	eight.format = AudioStreamWAV.FORMAT_8_BITS
	eight.mix_rate = 44100
	eight.data = PackedByteArray([0, 0, 0, 0])
	check("usable_asset rejects empty, 8-bit and null", not Cues.usable_asset(AudioStreamWAV.new()) and not Cues.usable_asset(eight) and not Cues.usable_asset(null))
	for player in probe.players:
		player.stop()
	probe.free()

	for player in cues.players:
		player.stop()
	await create_timer(0.15, true).timeout
	var failed := checks.filter(func(row): return not row.passed).size()
	if not args.is_empty():
		var file := FileAccess.open(args[0], FileAccess.WRITE)
		file.store_string(JSON.stringify({"checks": checks, "passed": checks.size() - failed, "total": checks.size(),
			"display": DisplayServer.get_name(), "audioDriver": AudioServer.get_driver_name(), "windowSize": [root.size.x,root.size.y], "mouseInputCoordinates": "explicit viewport-local via push_input(true); engine-injected, not physical desktop clicks",
			"auditionedByListener": false, "audioArtApproved": false}, "  ") + "\n")
	print("UI_SFX_WIRING_RESULT ", checks.size() - failed, "/", checks.size())
	if failed == 0:
		print("UI_SFX_WIRING_OK")
	quit(1 if failed else 0)
