extends Node

# Presentation capability. Interface and combat cues play authored WAVs and fall back to
# generated, cached PCM (no global RNG changes) when an asset is missing or unusable.
# Default OFF until sound content is accepted.
const FLAG := "--audio-cues-pilot"
const RATE := 22050
const VOICES := 4
# Authored interface set v01 (44.1 kHz mono 16-bit PCM, imported uncompressed). Source:
# tools/rpg-2-star-ocean-the-second_ui-sfx_wav-source-builder_v01_20261018-215528-960dcf71.py
const ASSETS := {
	"ui.confirm": "res://assets/audio/rpg-2-star-ocean-the-second_ui-confirm_interface-sfx_v01_20261018-215528-fd2f02df.wav",
	"ui.cancel": "res://assets/audio/rpg-2-star-ocean-the-second_ui-cancel_interface-sfx_v01_20261018-215528-b6b84df7.wav",
	"ui.notice": "res://assets/audio/rpg-2-star-ocean-the-second_ui-notice_interface-sfx_v01_20261018-215528-09a0a294.wav",
	# Authored combat set v01, same format. Source:
	# tools/rpg-2-star-ocean-the-second_combat-sfx_wav-source-builder_v01_20261018-222500-47342433.py
	"attack": "res://assets/audio/rpg-2-star-ocean-the-second_combat-attack_battle-sfx_v01_20261018-222500-44fc6fe0.wav",
	"dodge": "res://assets/audio/rpg-2-star-ocean-the-second_combat-dodge_battle-sfx_v01_20261018-222500-de3cac5f.wav",
	"guard": "res://assets/audio/rpg-2-star-ocean-the-second_combat-guard_battle-sfx_v01_20261018-222500-f17092a4.wav",
	"hit": "res://assets/audio/rpg-2-star-ocean-the-second_combat-hit_battle-sfx_v01_20261018-222500-58dc96e7.wav",
	"skill": "res://assets/audio/rpg-2-star-ocean-the-second_combat-skill_battle-sfx_v01_20261018-222500-7576322a.wav",
	"heal": "res://assets/audio/rpg-2-star-ocean-the-second_combat-heal_battle-sfx_v01_20261018-222500-868719df.wav",
	"victory": "res://assets/audio/rpg-2-star-ocean-the-second_combat-victory_battle-sfx_v01_20261018-222500-3e851f4e.wav",
	"defeat": "res://assets/audio/rpg-2-star-ocean-the-second_combat-defeat_battle-sfx_v01_20261018-222500-5b91e159.wav",
}
# A specific interface cue replaces the generic button click of the same press.
const SUPERSEDE_CONFIRM := ["ui.cancel", "ui.notice"]
const SPECS := {
	"ui.confirm": [880.0, 0.055, 0.0],
	"ui.cancel": [520.0, 0.07, 0.0],
	"ui.notice": [660.0, 0.12, 0.0],
	"attack": [210.0, 0.09, 0.4],
	"dodge": [520.0, 0.10, 0.22],
	"guard": [360.0, 0.11, 0.12],
	"hit": [145.0, 0.12, 0.35],
	"skill": [660.0, 0.16, 0.0],
	"heal": [740.0, 0.20, 0.0],
	"victory": [990.0, 0.25, 0.0],
	"defeat": [110.0, 0.24, 0.0],
}
var enabled_override := -1
var players: Array[AudioStreamPlayer] = []
var streams: Dictionary = {}
var accepted_events: Dictionary = {}
# Tests may point an entry at a missing or unusable resource to exercise the fallback.
var asset_paths: Dictionary = ASSETS.duplicate()
var stream_sources: Dictionary = {}
var _last: Dictionary = {}
var _clock := 0.0
var _voice := 0
var _confirm_voice := -1


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS # UI remains usable in the settings overlay.
	get_tree().node_added.connect(_watch_button)
	for button in get_tree().get_nodes_in_group("audio_cue_buttons"):
		_watch_button(button)


func enabled() -> bool:
	return enabled_override == 1 if enabled_override >= 0 else OS.get_cmdline_user_args().has(FLAG)


func _exit_tree() -> void:
	for player in players:
		player.stop()
		player.stream = null
	streams.clear()


func _watch_button(node: Node) -> void:
	if node is BaseButton and not node.pressed.is_connected(_button_pressed):
		node.pressed.connect(_button_pressed)


func _button_pressed() -> void:
	play_cue("ui.confirm")


func _process(delta: float) -> void:
	_clock += maxf(0.0, delta)


func play_cue(event: String) -> bool:
	if not enabled() or not SPECS.has(event):
		return false
	# Coalesce repeated AI/UI events; four voices bound overlapping playback.
	if _clock - float(_last.get(event, -1.0)) < 0.04:
		return false
	if event == "ui.confirm" and SUPERSEDE_CONFIRM.any(func(other): return _clock - float(_last.get(other, -1.0)) < 0.04):
		return false
	if players.is_empty():
		for index in VOICES:
			var player := AudioStreamPlayer.new()
			player.bus = "Master"
			player.volume_db = -14.0
			add_child(player)
			players.append(player)
	if not streams.has(event):
		streams[event] = _stream_for(event)
	var index := _voice
	if SUPERSEDE_CONFIRM.has(event) and _confirm_voice >= 0 and _clock - float(_last.get("ui.confirm", -1.0)) < 0.04:
		index = _confirm_voice
	else:
		_voice = (_voice + 1) % VOICES
	if event == "ui.confirm":
		_confirm_voice = index
	var voice := players[index]
	voice.stop()
	voice.stream = streams[event]
	# Headless runs prove dispatch/PCM/routing only; their dummy audio backend
	# cannot establish audible playback. Windowed checks exercise real players.
	if DisplayServer.get_name() != "headless":
		voice.play()
	_last[event] = _clock
	accepted_events[event] = int(accepted_events.get(event, 0)) + 1
	return true


func _stream_for(event: String) -> AudioStreamWAV:
	var path := String(asset_paths.get(event, ""))
	# exists() is silent for missing paths; only usable authored PCM replaces the generated cue.
	if path != "" and ResourceLoader.exists(path):
		var asset := ResourceLoader.load(path)
		if usable_asset(asset):
			stream_sources[event] = "asset"
			return asset
	stream_sources[event] = "procedural"
	return _make_stream(SPECS[event])


static func usable_asset(asset: Resource) -> bool:
	if not asset is AudioStreamWAV:
		return false
	var wav: AudioStreamWAV = asset
	return wav.format == AudioStreamWAV.FORMAT_16_BITS and not wav.stereo and wav.mix_rate == 44100 \
		and wav.loop_mode == AudioStreamWAV.LOOP_DISABLED and wav.data.size() >= 2 and wav.data.size() <= 44100 * 2


static func _make_stream(spec: Array) -> AudioStreamWAV:
	var count := int(round(float(spec[1]) * RATE))
	var pcm := PackedByteArray()
	pcm.resize(count * 2)
	var seed_value := 173
	for index in count:
		var phase := index / float(count - 1)
		# Raised-sine envelope starts and ends at zero, avoiding abrupt PCM clicks.
		var envelope := pow(sin(PI * phase), 2.0)
		seed_value = (seed_value * 1103515245 + 12345) & 0x7fffffff
		var noise := seed_value / 1073741824.0 - 1.0
		var tone := sin(TAU * float(spec[0]) * index / RATE)
		var value := 0.22 * envelope * lerpf(tone, noise, float(spec[2]))
		pcm.encode_s16(index * 2, int(round(value * 32767.0)))
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = RATE
	stream.stereo = false
	stream.data = pcm
	return stream
