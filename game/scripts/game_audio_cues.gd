extends Node

# Presentation capability, not final SFX art. Generated, cached PCM avoids external
# files and global RNG changes. Default OFF until sound content is accepted.
const FLAG := "--audio-cues-pilot"
const RATE := 22050
const VOICES := 4
const SPECS := {
	"ui.confirm": [880.0, 0.055, 0.0],
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
var _last: Dictionary = {}
var _clock := 0.0
var _voice := 0


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
	if players.is_empty():
		for index in VOICES:
			var player := AudioStreamPlayer.new()
			player.bus = "Master"
			player.volume_db = -14.0
			add_child(player)
			players.append(player)
	if not streams.has(event):
		streams[event] = _make_stream(SPECS[event])
	var voice := players[_voice]
	_voice = (_voice + 1) % VOICES
	voice.stop()
	voice.stream = streams[event]
	# Headless runs prove dispatch/PCM/routing only; their dummy audio backend
	# cannot establish audible playback. Windowed checks exercise real players.
	if DisplayServer.get_name() != "headless":
		voice.play()
	_last[event] = _clock
	accepted_events[event] = int(accepted_events.get(event, 0)) + 1
	return true


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
