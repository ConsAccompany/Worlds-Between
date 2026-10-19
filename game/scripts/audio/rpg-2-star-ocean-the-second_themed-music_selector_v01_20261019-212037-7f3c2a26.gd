class_name ThemedMusicSelector
extends RefCounted

## Read-only themed music selector for the Worlds Between pilot.
##
## This helper does not create players, autoloads, or settings. It returns a new
## AudioStreamWAV on success and null on every disabled, missing, or invalid
## condition. The caller keeps its existing ambience fallback on null.
##
## Public use:
##   var stream := ThemedMusicSelector.select("city")
##   var forced := ThemedMusicSelector.select("city", 1)

const PILOT_FLAG := "--themed-music-pilot"
const DEFAULT_ASSET_DIR := "res://assets/music/themed-v01"
const SCHEMA := "worlds-between.themed-music-package.v1"
const PACKAGE_ID := "rpg-2-star-ocean-the-second-themed-v01-20261019-212037-7f3c2a26"
const TASK := "content.audio.themed-music"
const MANIFEST_FILE := "rpg-2-star-ocean-the-second_themed-package_manifest_v01_20261019-212037-7f3c2a26.json"

const SAMPLE_RATE := 24000
const CHANNELS := 2
const BITS := 16
const BLOCK_ALIGN := 4
const BARS := 16
const BEATS_PER_BAR := 4
const TICKS_PER_QUARTER := 480
const LOOP_END_TICK := 30720
const MAX_MANIFEST_BYTES := 262144
const MAX_WAV_BYTES := 8000000
const MAX_WAV_FRAMES := 2000000

const CONTEXT_SUBJECTS := {
	"city": "city-dawn-inquiry",
	"field": "field-wayfarer-current",
	"ruins": "ruins-observatory-silence",
	"battle": "battle-controlled-pulse",
}

const KNOWN_SUBJECTS := {
	"city-dawn-inquiry": true,
	"field-wayfarer-current": true,
	"ruins-observatory-silence": true,
	"battle-controlled-pulse": true,
}

const SCORE_FILES := {
	"city": "rpg-2-star-ocean-the-second_city-dawn-inquiry_score_v01_20261019-212037-7f3c2a26.json",
	"field": "rpg-2-star-ocean-the-second_field-wayfarer-current_score_v01_20261019-212037-7f3c2a26.json",
	"ruins": "rpg-2-star-ocean-the-second_ruins-observatory-silence_score_v01_20261019-212037-7f3c2a26.json",
	"battle": "rpg-2-star-ocean-the-second_battle-controlled-pulse_score_v01_20261019-212037-7f3c2a26.json",
}

const MIDI_FILES := {
	"city": "rpg-2-star-ocean-the-second_city-dawn-inquiry_midi_v01_20261019-212037-7f3c2a26.mid",
	"field": "rpg-2-star-ocean-the-second_field-wayfarer-current_midi_v01_20261019-212037-7f3c2a26.mid",
	"ruins": "rpg-2-star-ocean-the-second_ruins-observatory-silence_midi_v01_20261019-212037-7f3c2a26.mid",
	"battle": "rpg-2-star-ocean-the-second_battle-controlled-pulse_midi_v01_20261019-212037-7f3c2a26.mid",
}

const WAV_FILES := {
	"city": "rpg-2-star-ocean-the-second_city-dawn-inquiry_audio_v01_20261019-212037-7f3c2a26.wav",
	"field": "rpg-2-star-ocean-the-second_field-wayfarer-current_audio_v01_20261019-212037-7f3c2a26.wav",
	"ruins": "rpg-2-star-ocean-the-second_ruins-observatory-silence_audio_v01_20261019-212037-7f3c2a26.wav",
	"battle": "rpg-2-star-ocean-the-second_battle-controlled-pulse_audio_v01_20261019-212037-7f3c2a26.wav",
}


static func select(context: String, enabled_override: int = -1, asset_dir: String = DEFAULT_ASSET_DIR) -> AudioStreamWAV:
	# Disabled paths return before any manifest, file, or directory access.
	if enabled_override == 0:
		return null
	var enabled := false
	if enabled_override == 1:
		enabled = true
	elif enabled_override == -1:
		enabled = _pilot_flag_present()
	else:
		return null
	if not enabled:
		return null
	if not CONTEXT_SUBJECTS.has(context):
		return null

	var subject := String(CONTEXT_SUBJECTS[context])
	var score_name := String(SCORE_FILES[context])
	var midi_name := String(MIDI_FILES[context])
	var wav_name := String(WAV_FILES[context])
	if not _safe_filename(score_name) or not _safe_filename(midi_name) or not _safe_filename(wav_name):
		return null

	var directory := _safe_asset_dir(asset_dir)
	if directory.is_empty():
		return null

	var root := _load_manifest(directory)
	if root.is_empty():
		return null
	var track := _find_track(root, subject)
	if track.is_empty():
		return null

	if _as_whole(track.get("bars"), BARS, BARS) != BARS:
		return null
	if _as_string(track.get("meter")) != "4/4":
		return null
	if _as_whole(track.get("ticks_per_quarter"), TICKS_PER_QUARTER, TICKS_PER_QUARTER) != TICKS_PER_QUARTER:
		return null
	var tempo := _as_finite(track.get("tempo_bpm"))
	if is_nan(tempo) or tempo < 20.0 or tempo > 400.0:
		return null

	var loop_value: Variant = track.get("loop")
	if typeof(loop_value) != TYPE_DICTIONARY:
		return null
	var loop: Dictionary = loop_value
	if _as_whole(loop.get("start_tick"), 0, 0) != 0:
		return null
	if _as_whole(loop.get("end_tick"), LOOP_END_TICK, LOOP_END_TICK) != LOOP_END_TICK:
		return null

	var files_value: Variant = track.get("files")
	if typeof(files_value) != TYPE_DICTIONARY:
		return null
	var files: Dictionary = files_value
	if not _has_expected_path(files.get("score"), score_name):
		return null
	if not _has_expected_path(files.get("midi"), midi_name):
		return null
	if not _has_expected_path(files.get("wav"), wav_name):
		return null

	var wav_ref_value: Variant = files.get("wav")
	if typeof(wav_ref_value) != TYPE_DICTIONARY:
		return null
	var wav_ref: Dictionary = wav_ref_value
	var declared_sha := _as_string(wav_ref.get("sha256")).to_lower()
	if not _is_sha256(declared_sha):
		return null
	var declared_bytes := _as_whole(wav_ref.get("bytes"), 44, MAX_WAV_BYTES)
	if declared_bytes < 44:
		return null

	var wav_bytes := _read_file_bounded(directory.path_join(wav_name), MAX_WAV_BYTES)
	if wav_bytes.is_empty() or wav_bytes.size() != declared_bytes:
		return null
	if _sha256_hex(wav_bytes) != declared_sha:
		return null

	var wav_info := _parse_pcm_container(wav_bytes)
	if wav_info.get("ok", false) != true:
		return null
	var frames: int = int(wav_info["frames"])
	var pcm: PackedByteArray = wav_info["pcm"]
	if frames <= 0 or frames > MAX_WAV_FRAMES or pcm.size() != frames * BLOCK_ALIGN:
		return null

	var wav_meta_value: Variant = track.get("wav")
	if typeof(wav_meta_value) != TYPE_DICTIONARY:
		return null
	var wav_meta: Dictionary = wav_meta_value
	if _as_whole(wav_meta.get("format"), 1, 1) != 1:
		return null
	if _as_whole(wav_meta.get("channels"), CHANNELS, CHANNELS) != CHANNELS:
		return null
	if _as_whole(wav_meta.get("sample_rate_hz"), SAMPLE_RATE, SAMPLE_RATE) != SAMPLE_RATE:
		return null
	if _as_whole(wav_meta.get("bit_depth"), BITS, BITS) != BITS:
		return null
	if _as_whole(wav_meta.get("frames"), 1, MAX_WAV_FRAMES) != frames:
		return null
	if _as_whole(wav_meta.get("data_bytes"), BLOCK_ALIGN, MAX_WAV_BYTES) != pcm.size():
		return null
	if _as_whole(loop.get("end_frame"), 1, MAX_WAV_FRAMES) != frames:
		return null

	var expected_frames := int(round(float(SAMPLE_RATE * BARS * BEATS_PER_BAR * 60) / tempo))
	if abs(frames - expected_frames) > 1:
		return null

	# Build a fresh stream from validated PCM. The source WAV is never loaded as
	# a shared resource and no existing stream is modified.
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = SAMPLE_RATE
	stream.stereo = true
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_begin = 0
	stream.loop_end = frames
	stream.data = pcm
	return stream


static func _pilot_flag_present() -> bool:
	if OS.get_cmdline_args().has(PILOT_FLAG):
		return true
	return OS.get_cmdline_user_args().has(PILOT_FLAG)


static func _safe_asset_dir(asset_dir: String) -> String:
	if asset_dir.is_empty() or asset_dir.contains("..") or asset_dir.contains("\\"):
		return ""
	var directory := asset_dir
	while directory.length() > 1 and directory.ends_with("/"):
		directory = directory.substr(0, directory.length() - 1)
	if directory.is_empty() or directory == "/":
		return ""
	return directory


static func _safe_filename(filename: String) -> bool:
	if filename.is_empty() or filename.contains("/") or filename.contains("\\") or filename.contains(".."):
		return false
	return filename.get_file() == filename


static func _load_manifest(directory: String) -> Dictionary:
	var bytes := _read_file_bounded(directory.path_join(MANIFEST_FILE), MAX_MANIFEST_BYTES)
	if bytes.is_empty():
		return {}
	var parser := JSON.new()
	if parser.parse(bytes.get_string_from_utf8()) != OK:
		return {}
	if typeof(parser.data) != TYPE_DICTIONARY:
		return {}
	return parser.data


static func _find_track(root: Dictionary, subject: String) -> Dictionary:
	if _as_string(root.get("schema")) != SCHEMA:
		return {}
	if _as_string(root.get("package_id")) != PACKAGE_ID:
		return {}
	if _as_string(root.get("task")) != TASK:
		return {}
	var tracks_value: Variant = root.get("tracks")
	if typeof(tracks_value) != TYPE_ARRAY:
		return {}
	var tracks: Array = tracks_value
	if tracks.size() != KNOWN_SUBJECTS.size():
		return {}
	var found := {}
	var seen := {}
	for entry in tracks:
		if typeof(entry) != TYPE_DICTIONARY:
			return {}
		var track: Dictionary = entry
		var track_subject := _as_string(track.get("subject"))
		if not KNOWN_SUBJECTS.has(track_subject) or seen.has(track_subject):
			return {}
		seen[track_subject] = true
		if track_subject == subject:
			found = track
	if found.is_empty():
		return {}
	return found


static func _has_expected_path(reference: Variant, expected: String) -> bool:
	if typeof(reference) != TYPE_DICTIONARY:
		return false
	var dictionary: Dictionary = reference
	if _as_string(dictionary.get("path")) != expected:
		return false
	return _safe_filename(expected)


static func _as_string(value: Variant) -> String:
	if typeof(value) != TYPE_STRING:
		return ""
	return String(value)


static func _as_finite(value: Variant) -> float:
	if typeof(value) != TYPE_INT and typeof(value) != TYPE_FLOAT:
		return NAN
	var number := float(value)
	if not is_finite(number):
		return NAN
	return number


static func _as_whole(value: Variant, minimum: int, maximum: int) -> int:
	var number := _as_finite(value)
	if is_nan(number) or number < float(minimum) or number > float(maximum):
		return minimum - 1
	if number != floor(number):
		return minimum - 1
	return int(number)


static func _is_sha256(value: String) -> bool:
	if value.length() != 64:
		return false
	for index in range(value.length()):
		if not "0123456789abcdef".contains(value.substr(index, 1)):
			return false
	return true


static func _sha256_hex(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if context.update(bytes) != OK:
		return ""
	return context.finish().hex_encode()


static func _read_file_bounded(path: String, maximum_bytes: int) -> PackedByteArray:
	if not FileAccess.file_exists(path):
		return PackedByteArray()
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return PackedByteArray()
	var length := file.get_length()
	if length <= 0 or length > maximum_bytes:
		file.close()
		return PackedByteArray()
	var bytes := file.get_buffer(length)
	file.close()
	if bytes.size() != length:
		return PackedByteArray()
	return bytes


static func _u16(bytes: PackedByteArray, offset: int) -> int:
	return int(bytes[offset]) | (int(bytes[offset + 1]) << 8)


static func _u32(bytes: PackedByteArray, offset: int) -> int:
	return int(bytes[offset]) | (int(bytes[offset + 1]) << 8) | (int(bytes[offset + 2]) << 16) | (int(bytes[offset + 3]) << 24)


static func _parse_pcm_container(bytes: PackedByteArray) -> Dictionary:
	var result := {
		"ok": false,
		"format": 0,
		"channels": 0,
		"sample_rate_hz": 0,
		"bit_depth": 0,
		"frames": 0,
		"pcm": PackedByteArray(),
	}
	if bytes.size() < 44:
		return result
	if _u32(bytes, 0) != 0x46464952 or _u32(bytes, 8) != 0x45564157:
		return result
	if _u32(bytes, 4) + 8 != bytes.size():
		return result

	var position := 12
	var have_fmt := false
	var have_data := false
	var data_offset := 0
	var data_size := 0
	var channels := 0
	var sample_rate := 0
	var bit_depth := 0
	while position < bytes.size():
		if position + 8 > bytes.size():
			return result
		var tag := _u32(bytes, position)
		var size := _u32(bytes, position + 4)
		var payload := position + 8
		if payload + size > bytes.size():
			return result
		if (size & 1) != 0:
			return result
		if tag == 0x20746D66:
			if have_fmt or have_data or size != 16:
				return result
			var audio_format := _u16(bytes, payload)
			channels = _u16(bytes, payload + 2)
			sample_rate = _u32(bytes, payload + 4)
			var byte_rate := _u32(bytes, payload + 8)
			var block_align := _u16(bytes, payload + 12)
			bit_depth = _u16(bytes, payload + 14)
			if audio_format != 1 or channels != CHANNELS or sample_rate != SAMPLE_RATE or bit_depth != BITS:
				return result
			if byte_rate != SAMPLE_RATE * BLOCK_ALIGN or block_align != BLOCK_ALIGN:
				return result
			have_fmt = true
		elif tag == 0x61746164:
			if not have_fmt or have_data:
				return result
			data_offset = payload
			data_size = size
			have_data = true
		else:
			return result
		position = payload + size

	if not have_fmt or not have_data:
		return result
	if position != bytes.size() or data_offset + data_size != bytes.size():
		return result
	if data_size <= 0 or data_size % BLOCK_ALIGN != 0:
		return result

	result["ok"] = true
	result["format"] = 1
	result["channels"] = channels
	result["sample_rate_hz"] = sample_rate
	result["bit_depth"] = bit_depth
	result["frames"] = int(data_size / float(BLOCK_ALIGN))
	result["pcm"] = bytes.slice(data_offset, data_offset + data_size)
	return result
