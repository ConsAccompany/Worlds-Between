extends SceneTree
const Music = preload("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd")
var checks: Array = []
func ck(key: String,value: bool) -> void: checks.append({"key":key,"pass":value})
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var out = OS.get_cmdline_user_args()[0]
	var app = root.get_node("AppState")
	app.set_process(false)
	SaveStore.root_path = "user://music-cli-check"
	ck("actual-cli-flag-present",OS.get_cmdline_user_args().has("--themed-music-pilot"))
	for context in ["city","field","ruins","battle"]:
		ck(context+"-automatic-enabled-by-cli",Music.select(context,-1) != null)
		ck(context+"-explicit-off-overrides-cli",Music.select(context,0) == null)
	for kind in ["area","annex","battle"]:
		app.begin_new_run()
		app.select_destination("scifi.city")
		if kind == "battle": app.begin_battle("patrol",Vector2(330,215))
		var script = load({"area":"res://scripts/scifi_exploration_area.gd","annex":"res://scripts/survey_annex.gd","battle":"res://scripts/battle_arena.gd"}[kind])
		script.themed_music_override = -1
		script.themed_music_asset_dir = Music.DEFAULT_ASSET_DIR
		var scene = script.new()
		root.add_child(scene)
		scene.set_process(false)
		await process_frame
		var players = []
		for child in scene.get_children():
			if child is AudioStreamPlayer: players.append(child)
		ck(kind+"-one-existing-ambient-player",players.size() == (1 if kind == "battle" else 2))
		ck(kind+"-automatic-normal-scene-path",players[0].stream.data == Music.select("battle" if kind == "battle" else "city",1).data)
		ck(kind+"-actual-player-started",players[0].playing)
		for sound in players:
			sound.stop()
			sound.stream = null
		scene.queue_free()
		await process_frame
	var failed = checks.filter(func(row):return not row["pass"])
	var hashes = {}
	for path in ["res://scripts/battle_arena.gd","res://scripts/scifi_exploration_area.gd","res://scripts/survey_annex.gd","res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd"]: hashes[path] = FileAccess.get_sha256(path)
	var report = {"count":checks.size(),"checks":checks,"failed":failed,"sourceRawSha256":hashes,"listened":false,"backend":AudioServer.get_driver_name()}
	var file = FileAccess.open(out,FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	print("THEMED_MUSIC_CLI ",checks.size()-failed.size(),"/",checks.size()," PASS" if failed.is_empty() else " FAIL")
	call_deferred("finish",failed.is_empty())
func finish(passed: bool) -> void:
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
