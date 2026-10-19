extends SceneTree
var observations = []
func _initialize() -> void: call_deferred("run")
func sample(label: String, player: AudioStreamPlayer, started: int) -> void:
	var stream: AudioStreamWAV = player.stream
	observations.append({"label":label,"atMs":(Time.get_ticks_usec()-started)/1000.0,"playing":player.playing,"bus":player.bus,"position":player.get_playback_position(),"mixAgeMs":AudioServer.get_time_since_last_mix()*1000.0,"loopMode":stream.loop_mode,"loopBegin":stream.loop_begin,"loopEnd":stream.loop_end,"length":stream.get_length(),"format":stream.format,"rate":stream.mix_rate,"bytes":stream.data.size(),"hasPlayback":player.get_stream_playback()!=null if player.playing else false})
func run() -> void:
	var args = OS.get_cmdline_user_args()
	var app = root.get_node("AppState")
	app.set_process(false)
	SaveStore.root_path = "user://music-startup-diagnostic"
	for item in [{"kind":"area","path":args[0],"base":true},{"kind":"battle","path":args[1],"base":true},{"kind":"area","path":"res://scripts/scifi_exploration_area.gd","base":false},{"kind":"battle","path":"res://scripts/battle_arena.gd","base":false},{"kind":"area","path":"res://scripts/scifi_exploration_area.gd","base":false,"fixedBoundControl":true},{"kind":"battle","path":"res://scripts/battle_arena.gd","base":false,"fixedBoundControl":true}]:
		app.begin_new_run()
		app.select_destination("scifi.outskirts")
		if item.kind == "battle": app.begin_battle("patrol",Vector2(330,215))
		var script = load(item.path)
		if not item.base: script.themed_music_override = 0
		var scene = script.new()
		root.add_child(scene)
		scene.set_process(false)
		var player: AudioStreamPlayer
		for child in scene.get_children():
			if child is AudioStreamPlayer:
				player = child
				break
		var label = item.kind+"-"+("baseline" if item.base else "off")
		if item.get("fixedBoundControl",false):
			# Diagnostic-only control: same stream/PCM/player, full loop end before replay.
			# This does not edit the game source or silently repair a tested baseline.
			label += "-full-loop-bound-control"
			player.stop()
			player.stream.loop_end = int(round(player.stream.get_length()*player.stream.mix_rate))
			player.play()
		var started = Time.get_ticks_usec()
		sample(label+"-immediate",player,started)
		await process_frame
		sample(label+"-one-process-frame",player,started)
		for milliseconds in [10,20,70,200]:
			await create_timer(milliseconds/1000.0).timeout
			sample(label+"-after-extra-"+str(milliseconds)+"ms",player,started)
		scene.queue_free()
		await process_frame
	var file = FileAccess.open(args[2],FileAccess.WRITE)
	file.store_string(JSON.stringify({"observations":observations,"backend":AudioServer.get_driver_name()},"  "))
	file.close()
	for row in observations: print(JSON.stringify(row))
	print("MUSIC_STARTUP_DIAGNOSTIC_COMPLETE")
	quit()
