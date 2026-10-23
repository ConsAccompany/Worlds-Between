extends SceneTree

# TEST-ONLY, external technical-QA support for review.content.audio. It does not judge audio and does not
# prove ordinary input gameplay. It instantiates the actual normal city scene, lets the scene's own music
# setup create/play its AudioStreamPlayer, then drives a fixed engine-frame schedule through the real
# GameSettings.set_master_volume path and the real GameAudioCues.play_cue path.
#
# Run windowed with Movie Maker (no --headless), e.g.:
#   <godot> --path <repo>/game --resolution 640x360 --fixed-fps 60 \
#     --write-movie <repo>/outputs/audio57/support/<name>.avi \
#     -s <repo>/tools/rpg-2-star-ocean-the-second_audio_real-mix-capture_test-only-v01_20261022-212657-710850bf.gd \
#     -- --out=<repo>/outputs/audio57/support/<report>.txt
#
# The AVI is the evidence carrier: Godot's movie writer records the postmix Master output. This harness
# rejects an AudioEffectCapture on Master rather than measuring a pre-gain tap. It records frame boundaries,
# stream paths/gains and cue dispatch; it makes no listening claim.
#
# Declared fixtures: AppState.begin_new_run(); AppState.select_destination("scifi.city"); the normal city
# scene resources; GameSettings.set_master_volume(..., false) (in memory only); and
# game_audio_cues.enabled_override = 1 (restored before exit). No game/defaults file is edited or saved.

const SOURCE_HEAD := "f1d2faca0a353cc2d916351eaac69ee8897850bc"
const HARNESS_FILE := "tools/rpg-2-star-ocean-the-second_audio_real-mix-capture_test-only-v01_20261022-212657-710850bf.gd"
const REPORT_REL := "outputs/audio57/support/rpg-2-star-ocean-the-second_audio_real-mix-capture_handoff-v01_20261022-212657-710850bf.txt"
const CITY_SCENE := "res://scenes/scifi_exploration_area.tscn"
const CUE_EVENTS := ["ui.confirm", "ui.cancel", "ui.notice", "attack", "dodge", "guard", "hit", "skill", "heal", "victory", "defeat"]
const A_FRAMES := 120
const B_FRAMES := 120
const C_FRAMES := 60
const CUE_GAP_FRAMES := 27
const SILENCE_FRAMES := 60
const MAX_TOTAL_FRAMES := 900
const LOAD_WAIT_FRAMES := 180
const EXPECTED_TOTAL_FRAMES := A_FRAMES + B_FRAMES + C_FRAMES + 11 * CUE_GAP_FRAMES + SILENCE_FRAMES

var _app: Node = null
var _host: Node = null
var _music: AudioStreamPlayer = null
var _prior_volume := 100
var _prior_cue_override := -1
var _report_path := ""
var _run_start_frame := 0
var _sched_start := 0
var _fatal := ""
var _info: Dictionary = {}
var _phases: Array[Dictionary] = []
var _cues: Array[Dictionary] = []
var _boundary_drift_max := 0


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	await process_frame
	_run_start_frame = Engine.get_process_frames()
	var opts := _parse_opts()
	_report_path = _resolve_report_path(String(opts["out"]))
	_info = {
		"tool": "rpg-2-star-ocean-the-second_audio_real-mix-capture_test-only-v01_20261022-212657-710850bf",
		"status": "FAIL",
		"source_head_declared": SOURCE_HEAD,
		"source_head_verified_by_harness": false,
		"scope": "technical QA support only; not artistic approval; no listening claim",
		"fixture": "AppState.begin_new_run + actual city scene + GameSettings.set_master_volume(...,false) + game_audio_cues.play_cue direct dispatch",
		"scene_path": CITY_SCENE,
		"scene_kind": "normal city exploration scene",
		"game_defaults_modified": false,
		"settings_written": false,
		"save_written": false,
		"audio_cues_enabled_override_fixture": 1,
		"music_selector_override_fixture": -1,
		"themed_music_pilot_arg": OS.get_cmdline_user_args().has("--themed-music-pilot"),
		"audio_cues_pilot_arg": OS.get_cmdline_user_args().has("--audio-cues-pilot"),
		"hash_normalization": "none (no source/asset bytes hashed by this harness)",
		"expected_cue_count": CUE_EVENTS.size(),
		"schedule_fixed_fps": 60,
		"schedule_a_music100_frames": A_FRAMES,
		"schedule_b_music50_restart0_frames": B_FRAMES,
		"schedule_c_master0_frames": C_FRAMES,
		"schedule_cue_gap_frames": CUE_GAP_FRAMES,
		"schedule_final_silence_frames": SILENCE_FRAMES,
		"schedule_expected_total_frames": EXPECTED_TOTAL_FRAMES,
		"schedule_expected_total_seconds": snappedf(float(EXPECTED_TOTAL_FRAMES) / 60.0, 0.001),
		"fatal": "",
	}
	_probe_io()
	var gate := _capture_gate(String(opts["scene"]))
	if gate != "":
		_abort(gate)
		return
	_app = root.get_node_or_null("AppState")
	if _app == null:
		_abort("AppState autoload missing")
		return
	if _app.settings == null or _app.audio_cues == null:
		_abort("AppState.settings or AppState.audio_cues missing")
		return
	_prior_volume = int(_app.settings.master_volume)
	_prior_cue_override = int(_app.audio_cues.enabled_override)
	_info["prior_master_volume"] = _prior_volume
	_info["prior_cue_override"] = _prior_cue_override
	_app.begin_new_run()
	_app.select_destination("scifi.city")
	_app.settings.set_master_volume(100, false)
	_app.audio_cues.enabled_override = 1
	_info["fixture_master_volume_set"] = 100
	_info["fixture_cue_override_set"] = 1
	var packed = load(CITY_SCENE)
	if packed == null or not (packed is PackedScene):
		_abort("failed to load actual city PackedScene: " + CITY_SCENE)
		return
	_host = packed.instantiate()
	if _host == null:
		_abort("failed to instantiate actual city scene")
		return
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.add_child(_host)
	current_scene = _host
	var music_result: AudioStreamPlayer = await _wait_for_music(_host)
	if music_result == null:
		_abort("actual city scene exposed no AudioStreamPlayer with a stream within %d frames" % LOAD_WAIT_FRAMES)
		return
	_music = music_result
	_info["music_player_count"] = _audio_player_count(_host)
	_info["music_stream"] = _stream_info(_music)
	_info["music_player_instance_id"] = str(_music.get_instance_id())
	_info["music_player_bus"] = _music.bus
	_info["music_player_gain_db"] = snappedf(_music.volume_db, 0.001)
	_info["music_player_stream_path"] = _stream_path(_music)
	_info["music_playing_at_schedule_start"] = _music.playing

	_music.stop()
	_music.play(0.0) # Match the phase of the later 50% replay.
	_sched_start = Engine.get_process_frames()
	_info["schedule_start_frame"] = _sched_start
	_record_phase("A_music100", 0, 100, _music)

	var ok: bool = await _wait_to(_sched_start + A_FRAMES)
	if not ok:
		_abort("watchdog hit before B boundary")
		return
	var restart_id := str(_music.get_instance_id())
	_music.stop()
	_music.play(0.0)
	_app.settings.set_master_volume(50, false)
	_info["restart_same_player_instance_id"] = restart_id
	_info["restart_same_player_after_instance_id"] = str(_music.get_instance_id())
	_info["restart_from_position_sec"] = snappedf(_music.get_playback_position(), 0.001)
	_record_phase("B_music50_restart0", A_FRAMES, 50, _music)

	ok = await _wait_to(_sched_start + A_FRAMES + B_FRAMES)
	if not ok:
		_abort("watchdog hit before C boundary")
		return
	_app.settings.set_master_volume(0, false)
	_record_phase("C_master0_music_playing", A_FRAMES + B_FRAMES, 0, _music)

	ok = await _wait_to(_sched_start + A_FRAMES + B_FRAMES + C_FRAMES)
	if not ok:
		_abort("watchdog hit before D boundary")
		return
	_app.settings.set_master_volume(100, false)
	_music.stop()
	_record_phase("D_master100_music_stopped_cues", A_FRAMES + B_FRAMES + C_FRAMES, 100, _music)
	_info["music_stopped_before_cues"] = not _music.playing

	var cue_base := _sched_start + A_FRAMES + B_FRAMES + C_FRAMES
	var planned_gaps: Array[int] = []
	var total_cue_frames := 0
	for event in CUE_EVENTS:
		var stream: AudioStreamWAV = _app.audio_cues._stream_for(String(event))
		var gap := maxi(CUE_GAP_FRAMES, ceili(stream.get_length() * 60.0) + 6)
		planned_gaps.append(gap)
		total_cue_frames += gap
	_info["schedule_expected_total_frames"] = A_FRAMES + B_FRAMES + C_FRAMES + total_cue_frames + SILENCE_FRAMES
	_info["schedule_expected_total_seconds"] = float(_info["schedule_expected_total_frames"]) / 60.0
	_info["cue_gap_rule"] = "max(27frames, actual stream duration rounded up to frames +6frames); isolated cues"
	var target_frame := cue_base
	for index in CUE_EVENTS.size():
		var event := String(CUE_EVENTS[index])
		var expected_offset := target_frame - _sched_start
		ok = await _wait_to(target_frame)
		if not ok:
			_abort("watchdog hit before cue %d (%s)" % [index, event])
			return
		var frame := Engine.get_process_frames()
		var accepted: bool = bool(_app.audio_cues.play_cue(event))
		var voice_info := _playing_voice(_app.audio_cues, event)
		var voice = voice_info["player"]
		var voice_index := int(voice_info["index"])
		var voice_playing := voice != null and bool(voice.playing)
		var voice_path := "" if voice == null else _stream_path(voice)
		var voice_gain := 0.0 if voice == null else snappedf(voice.volume_db, 0.001)
		var cue_source := String(_app.audio_cues.stream_sources.get(event, ""))
		var drift := absi((frame - _sched_start) - expected_offset)
		_boundary_drift_max = maxi(_boundary_drift_max, drift)
		_cues.append({
			"index": index,
			"event": event,
			"planned_gap_frames": planned_gaps[index],
			"stream_duration_seconds": voice.stream.get_length() if voice != null else 0.0,
			"frame": frame,
			"target_offset_frames": expected_offset,
			"actual_offset_frames": frame - _sched_start,
			"drift_frames": drift,
			"accepted": accepted,
			"accepted_count": int(_app.audio_cues.accepted_events.get(event, 0)),
			"voice_index": voice_index,
			"voice_playing": voice_playing,
			"voice_gain_db": voice_gain,
			"voice_stream_path": voice_path,
			"cue_stream_source": cue_source,
			"music_playing": _music.playing,
		})
		if not accepted or not voice_playing:
			_abort("cue %d (%s) was not accepted by an actually playing AudioStreamPlayer" % [index, event])
			return
		target_frame += planned_gaps[index]

	ok = await _wait_to(target_frame)
	if not ok:
		_abort("watchdog before final isolated silence")
		return
	_record_phase("E_final_isolated_silence", target_frame - _sched_start, 100, _music)
	var end_target := target_frame + SILENCE_FRAMES
	ok = await _wait_to(end_target)
	if not ok:
		_abort("watchdog hit before final silence boundary")
		return
	var final_frame := Engine.get_process_frames()
	_info["final_frame"] = final_frame
	_info["elapsed_frames"] = final_frame - _sched_start
	_info["elapsed_seconds"] = snappedf(float(final_frame - _sched_start) / 60.0, 0.001)
	_info["boundary_drift_max_frames"] = _boundary_drift_max
	_info["boundary_drift_ok"] = _boundary_drift_max <= 1
	_info["cue_events_accepted"] = _cues.size()
	_info["cue_voice_play_confirmed"] = _cues.filter(func(entry): return bool(entry["voice_playing"])).size()
	_info["master_volume_at_final"] = int(_app.settings.master_volume)
	_info["music_playing_at_final"] = _music.playing
	if _boundary_drift_max > 1:
		_abort("engine-frame boundary drift exceeded 1 frame: %d" % _boundary_drift_max)
		return
	_restore()
	_finish("READY")


func _probe_io() -> void:
	var movie := Engine.get_write_movie_path()
	var driver := AudioServer.get_driver_name()
	var bus := AudioServer.get_bus_index("Master")
	var effects: Array[String] = []
	var captures := 0
	if bus >= 0:
		for index in AudioServer.get_bus_effect_count(bus):
			var effect := AudioServer.get_bus_effect(bus, index)
			var class_name_value := "null" if effect == null else effect.get_class()
			effects.append(class_name_value)
			if effect is AudioEffectCapture:
				captures += 1
	_info["engine_version"] = String(Engine.get_version_info().get("string", ""))
	_info["display_driver"] = DisplayServer.get_name()
	_info["audio_driver"] = driver
	_info["offline_movie_mix_not_physical_audition"] = true
	_info["mix_rate"] = int(AudioServer.get_mix_rate())
	_info["master_bus_index"] = bus
	_info["master_bus_effects"] = effects
	_info["master_capture_effect_count"] = captures
	_info["movie_path"] = movie
	_info["movie_extension"] = movie.get_extension().to_lower()
	_info["movie_writer_active"] = movie != ""
	_info["capture_method"] = "Godot Movie Maker AVI postmix Master capture; no AudioEffectCapture tap"


func _capture_gate(scene: String) -> String:
	if scene != "city":
		return "unsupported --scene; this harness captures only the actual normal city scene"
	if DisplayServer.get_name() == "headless":
		return "headless display; windowed run is required so game_audio_cues calls AudioStreamPlayer.play()"
	var driver := String(_info.get("audio_driver", ""))
	# Movie Maker intentionally uses the offline Dummy mixer; its recorded PCM,
	# not a physical speaker or a playing flag, is the output under test.
	if driver == "":
		return "audio driver metadata missing"
	if String(_info.get("movie_path", "")) == "":
		return "Engine.get_write_movie_path() is empty; --write-movie AVI output is required"
	if String(_info.get("movie_extension", "")) != "avi":
		return "movie output is not .avi: " + String(_info.get("movie_path", ""))
	if int(_info.get("master_bus_index", -1)) < 0:
		return "Master audio bus missing"
	if int(_info.get("master_capture_effect_count", 0)) > 0:
		return "AudioEffectCapture present on Master; refusing a pre-gain capture instead of movie postmix"
	return ""


func _wait_for_music(host: Node) -> AudioStreamPlayer:
	var limit := mini(_run_start_frame + MAX_TOTAL_FRAMES, Engine.get_process_frames() + LOAD_WAIT_FRAMES)
	while Engine.get_process_frames() < limit:
		await process_frame
		var found := _find_music(host)
		if found != null:
			return found
	return null


func _find_music(host: Node) -> AudioStreamPlayer:
	var players := host.find_children("*", "AudioStreamPlayer", true, false)
	var best: AudioStreamPlayer = null
	for node in players:
		if node is AudioStreamPlayer and node.stream != null:
			var candidate: AudioStreamPlayer = node
			if candidate.playing:
				return candidate
			if best == null or candidate.stream.get_length() > best.stream.get_length():
				best = candidate
	return best


func _audio_player_count(host: Node) -> int:
	return host.find_children("*", "AudioStreamPlayer", true, false).size()


func _wait_to(target_frame: int) -> bool:
	while Engine.get_process_frames() < target_frame:
		if Engine.get_process_frames() - _run_start_frame > MAX_TOTAL_FRAMES:
			return false
		await process_frame
	return true


func _record_phase(label: String, expected_offset: int, requested_volume: int, music: AudioStreamPlayer) -> void:
	var frame := Engine.get_process_frames()
	var actual_offset := frame - _sched_start
	var drift := absi(actual_offset - expected_offset)
	_boundary_drift_max = maxi(_boundary_drift_max, drift)
	var bus := AudioServer.get_bus_index("Master")
	_phases.append({
		"phase": label,
		"frame": frame,
		"target_offset_frames": expected_offset,
		"actual_offset_frames": actual_offset,
		"drift_frames": drift,
		"requested_master_volume": requested_volume,
		"settings_master_volume": int(_app.settings.master_volume),
		"master_bus_mute": AudioServer.is_bus_mute(bus),
		"master_bus_db": snappedf(AudioServer.get_bus_volume_db(bus), 0.001),
		"music_playing": music.playing,
		"music_position_sec": snappedf(music.get_playback_position(), 0.001),
		"music_stream_path": _stream_path(music),
		"music_gain_db": snappedf(music.volume_db, 0.001),
	})


func _playing_voice(cues: Node, event: String) -> Dictionary:
	var index := -1
	var player: AudioStreamPlayer = null
	for candidate_index in cues.players.size():
		var candidate: AudioStreamPlayer = cues.players[candidate_index]
		if candidate != null and candidate.playing and candidate.stream == cues.streams.get(event):
			index = candidate_index
			player = candidate
			break
	return {"index": index, "player": player}


func _stream_path(player: AudioStreamPlayer) -> String:
	if player == null or player.stream == null:
		return ""
	if player.stream.resource_path != "":
		return player.stream.resource_path
	return "(in-memory AudioStreamWAV; no resource path)"


func _stream_info(player: AudioStreamPlayer) -> Dictionary:
	var result := {
		"class": "" if player.stream == null else player.stream.get_class(),
		"resource_path": _stream_path(player),
		"gain_db": snappedf(player.volume_db, 0.001),
		"bus": player.bus,
		"playing": player.playing,
		"position_sec": snappedf(player.get_playback_position(), 0.001),
	}
	if player.stream is AudioStreamWAV:
		var wav: AudioStreamWAV = player.stream
		result["mix_rate"] = wav.mix_rate
		result["stereo"] = wav.stereo
		result["loop_mode"] = int(wav.loop_mode)
		result["length_sec"] = snappedf(wav.get_length(), 0.001)
		result["data_bytes"] = wav.data.size()
	return result


func _restore() -> void:
	if _music != null and is_instance_valid(_music):
		_music.stop()
	if _app != null:
		if _app.settings != null:
			_app.settings.set_master_volume(_prior_volume, false)
		if _app.audio_cues != null:
			_app.audio_cues.enabled_override = _prior_cue_override
	if _host != null and is_instance_valid(_host):
		_host.queue_free()
	_info["restored_master_volume"] = _prior_volume
	_info["restored_cue_override"] = _prior_cue_override
	_info["music_stopped_at_exit"] = _music == null or not _music.playing


func _abort(reason: String) -> void:
	_fatal = reason
	_info["fatal"] = reason
	_restore()
	_finish("FAIL")


func _finish(status: String) -> void:
	_info["status"] = status
	_info["report_path"] = _report_path
	_info["final_marker"] = "AUDIO57_CAPTURE_READY" if status == "READY" else "AUDIO57_CAPTURE_FAIL"
	var lines := PackedStringArray()
	for key in _info:
		lines.append("%s=%s" % [String(key), _format_value(_info[key])])
	lines.append("phase_events:")
	for phase in _phases:
		lines.append("  " + _format_dictionary(phase))
	lines.append("cue_events:")
	for cue in _cues:
		lines.append("  " + _format_dictionary(cue))
	lines.append("limitations=Movie Maker AVI is the audio evidence; this harness records postmix capture metadata, frame boundaries, stream paths/gains and direct cue dispatch only. It does not listen to, inspect or judge the captured audio and does not establish ordinary-input gameplay, artistic approval or content acceptance.")
	lines.append(_info["final_marker"])
	var text := "\n".join(lines)
	DirAccess.make_dir_recursive_absolute(_report_path.get_base_dir())
	var file := FileAccess.open(_report_path, FileAccess.WRITE)
	if file == null:
		print("AUDIO57_REPORT_WRITE_FAIL path=%s" % _report_path)
		print(text)
		quit(1)
		return
	file.store_string(text)
	file.close()
	var structured := _info.duplicate(true)
	structured["phases"] = _phases
	structured["cues"] = _cues
	var json_file := FileAccess.open(_report_path.get_basename() + ".json", FileAccess.WRITE)
	if json_file == null:
		push_error("AUDIO57 structured report write failed")
		quit(1)
		return
	json_file.store_string(JSON.stringify(structured, "  ") + "\n")
	json_file.close()
	print(text)
	print("\nAUDIO57_REPORT=%s" % _report_path)
	quit(0 if status == "READY" else 1)


func _parse_opts() -> Dictionary:
	var result := {"out": "", "scene": "city"}
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--out="):
			result["out"] = argument.substr(6)
		elif argument.begins_with("--scene="):
			result["scene"] = argument.substr(8)
	return result


func _resolve_report_path(override: String) -> String:
	if override != "":
		if override.is_absolute_path():
			return override
		return ProjectSettings.globalize_path("res://").path_join(override).simplify_path()
	return ProjectSettings.globalize_path("res://").path_join("../" + REPORT_REL).simplify_path()


func _format_value(value: Variant) -> String:
	if typeof(value) == TYPE_ARRAY or typeof(value) == TYPE_DICTIONARY:
		return JSON.stringify(value)
	return str(value)


func _format_dictionary(value: Dictionary) -> String:
	var parts := PackedStringArray()
	for key in value:
		parts.append("%s=%s" % [String(key), _format_value(value[key])])
	return " ".join(parts)
