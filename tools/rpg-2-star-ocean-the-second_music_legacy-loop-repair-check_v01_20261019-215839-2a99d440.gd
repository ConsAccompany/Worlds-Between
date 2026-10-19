extends SceneTree
const TAG = "20261019-215839-2a99d440"
var checks: Array = []
var observations: Array = []
var app: Node
func ck(key: String,value: bool) -> void: checks.append({"key":key,"pass":value})
func _initialize() -> void: call_deferred("run")
func wait_ms(ms: int) -> float:
	var start = Time.get_ticks_usec()
	var deadline = start + ms*1000
	while Time.get_ticks_usec() < deadline: await process_frame
	return (Time.get_ticks_usec()-start)/1000.0
func snapshot(player: AudioStreamPlayer) -> Dictionary:
	return {"playing":player.playing,"bus":player.bus,"position":player.get_playback_position(),"loopBegin":player.stream.loop_begin,"loopEnd":player.stream.loop_end,"mode":player.stream.loop_mode,"length":player.stream.get_length(),"rate":player.stream.mix_rate,"format":player.stream.format,"bytes":player.stream.data.size()}
func setup(script: Script,item: Dictionary) -> Node2D:
	app.begin_new_run()
	app.language = "en"
	app.select_destination(item.destination)
	app.current_annex_room = item.room
	if item.kind == "battle": app.begin_battle("patrol",Vector2(330,215))
	var scene = script.new()
	root.add_child(scene)
	scene.set_process(false)
	return scene
func run() -> void:
	var args = OS.get_cmdline_user_args()
	var original = {"area":load(args[0]),"annex":load(args[1]),"battle":load(args[2])}
	var repaired = {"area":load(args[3]),"annex":load(args[4]),"battle":load(args[5])}
	app = root.get_node("AppState")
	app.set_process(false)
	SaveStore.root_path = "user://legacy-loop-proof"
	var cases = []
	for destination in ["scifi.city","scifi.outskirts","scifi.ruins"]:
		cases.append({"kind":"area","destination":destination,"room":1})
		for room in [1,2]: cases.append({"kind":"annex","destination":destination,"room":room})
	cases.append({"kind":"battle","destination":"scifi.city","room":1})
	var master = AudioServer.get_bus_index("Master")
	for item in cases:
		var label: String = item.kind+"-"+item.destination+"-r"+str(item.room)
		var streams = []
		for mode in ["original","repaired"]:
			var scene = setup(original[item.kind] if mode == "original" else repaired[item.kind],item)
			var ps = []
			for child in scene.get_children():
				if child is AudioStreamPlayer: ps.append(child)
			var player: AudioStreamPlayer = ps[0]
			var stream: AudioStreamWAV = player.stream
			var initial = snapshot(player)
			streams.append(stream)
			ck(label+"-"+mode+"-Master",player.bus == "Master" and not AudioServer.is_bus_mute(master))
			ck(label+"-"+mode+"-one-existing-player",ps.size() == (1 if item.kind == "battle" else 2))
			var waited = await wait_ms(300)
			var after_mix = snapshot(player)
			if mode == "original":
				ck(label+"-original-zero-loop-end-reproduced",stream.loop_end == 0 and stream.loop_begin == 0 and stream.loop_mode == AudioStreamWAV.LOOP_FORWARD)
				ck(label+"-original-stopped-after-real-mix",not player.playing)
			else:
				ck(label+"-repaired-full-bound",stream.loop_begin == 0 and stream.loop_end == int(round(stream.get_length()*stream.mix_rate)))
				ck(label+"-repaired-sustained-after-real-mix",player.playing and player.get_playback_position() > .1)
				ck(label+"-same-imported-pcm-format-rate",stream.data == streams[0].data and stream.format == streams[0].format and stream.mix_rate == streams[0].mix_rate and stream.stereo == streams[0].stereo)
				app.settings.set_master_volume(25,false)
				ck(label+"-Master-volume-retained",absf(AudioServer.get_bus_volume_db(master)-linear_to_db(.25)) < .0001)
				app.settings.set_master_volume(0,false)
				ck(label+"-Master-mute-retained",AudioServer.is_bus_mute(master))
				app.settings.set_master_volume(100,false)
				ck(label+"-Master-unmute-retained",not AudioServer.is_bus_mute(master) and absf(AudioServer.get_bus_volume_db(master)) < .0001)
				player.seek(stream.get_length()-.1)
				var before_wrap = snapshot(player)
				var seek_waited = await wait_ms(350)
				var after_wrap = snapshot(player)
				ck(label+"-real-duration-boundary-wrap",player.playing and player.get_playback_position() > 0 and player.get_playback_position() < 1)
				observations.append({"label":label+"-wrap","requestedSeekSeconds":stream.get_length()-.1,"waitedMs":seek_waited,"before":before_wrap,"after":after_wrap})
			observations.append({"label":label+"-"+mode,"waitedMs":waited,"initial":initial,"afterMix":after_mix})
			for sound in ps:
				sound.stop()
				sound.stream = null
			scene.queue_free()
			await process_frame
	var failed = checks.filter(func(row):return not row["pass"])
	var hashes = {}
	for path in args.slice(0,6): hashes[path] = FileAccess.get_sha256(path)
	var file = FileAccess.open(args[6],FileAccess.WRITE)
	file.store_string(JSON.stringify({"tag":TAG,"checks":checks,"count":checks.size(),"failed":failed,"observations":observations,"sourceRawSha256":hashes,"backend":AudioServer.get_driver_name(),"listened":false,"scope":"Only legacy loop bounds repaired; original broken baselines intentionally retained and failures explicitly reproduced."},"  "))
	file.close()
	print("LEGACY_LOOP_REPAIR ",checks.size()-failed.size(),"/",checks.size()," PASS" if failed.is_empty() else " FAIL")
	# Let run()'s two retained AudioStreamWAVs and six Script refs leave scope
	# before the engine performs its final ObjectDB cleanup.
	call_deferred("finish",failed.is_empty())
func finish(passed: bool) -> void:
	# Dummy backend mixes asynchronously. Drain at most two real mix boundaries,
	# bounded to 300 ms, after detaching the last players' streams.
	var previous_age = AudioServer.get_time_since_last_mix()
	var mixes = 0
	var deadline = Time.get_ticks_usec()+300000
	while mixes < 2 and Time.get_ticks_usec() < deadline:
		await process_frame
		var age = AudioServer.get_time_since_last_mix()
		if age < previous_age: mixes += 1
		previous_age = age
	print("AUDIO_CLEANUP_MIX_BOUNDARIES ",mixes)
	quit(0 if passed else 1)
