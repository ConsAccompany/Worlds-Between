extends SceneTree
const Music = preload("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd")
const TAG = "20261019-215013-95dc2f6a"
const ASSETS = "res://assets/music/themed-v01"
var checks: Array = []
var out: String
var fixtures: String
var app: Node
var baseline: Dictionary = {}
var candidate: Dictionary = {}
var originals: Dictionary
func ck(key: String, value: bool) -> void: checks.append({"key":key,"pass":value})
func _initialize() -> void: call_deferred("run")
func digest(bytes: PackedByteArray) -> String:
	var hash = HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	return hash.finish().hex_encode()
func put(path: String, bytes: PackedByteArray) -> void:
	var file = FileAccess.open(path, FileAccess.WRITE)
	file.store_buffer(bytes)
	file.close()
func put_manifest(value: Variant) -> void: put(fixtures.path_join(Music.MANIFEST_FILE), JSON.stringify(value).to_utf8_buffer())
func negative(label: String, value: Variant) -> void:
	put_manifest(value)
	ck("metadata-reject-" + label, Music.select("city",1,fixtures) == null)
func stream_description(stream: AudioStreamWAV) -> Array:
	return [digest(stream.data),stream.format,stream.mix_rate,stream.stereo,stream.loop_mode,stream.loop_begin,stream.loop_end]
func players(scene: Node) -> Array:
	var found = []
	for child in scene.get_children():
		if child is AudioStreamPlayer: found.append(child)
	return found
func dispose(scene: Node) -> void:
	scene.queue_free()
	await process_frame
func scene_state(scene: Node2D,kind: String) -> Dictionary:
	var position: Vector2 = scene.hero.position if kind != "battle" else Vector2.ZERO
	var result = app.make_snapshot(kind,position,"music-parity")
	if kind == "battle":
		result["battle"] = [scene.fighters.duplicate(true),scene.enemy_hp,scene.enemy_x,scene.enemy_cooldown,scene.enemy_windup,scene.battle_finished,scene.battle_won]
	return result
func setup(script: Script,kind: String,destination: String,room: int,enabled: int,asset_dir: String = ASSETS) -> Node2D:
	seed(15429)
	app.begin_new_run()
	app.language = "en"
	app.hero_appearance = "female"
	app.select_destination(destination)
	app.current_annex_room = room
	if kind == "battle":
		app.recruit_member("liang-xu")
		app.recruit_member("zhao-ling")
		app.ji_records_checked = true
		app.recruit_member("ji-cheng")
		app.begin_battle("patrol",Vector2(330,215))
		script.battle_vfx_override = 0
		script.skill_vfx_override = 0
		script.sentry_v2_override = 0
		script.encounter_feedback_override = 0
		script.combat_sprite_set_override = 0
		script.battle_ui_skin_override = 0
	if script == candidate[kind]:
		script.themed_music_override = enabled
		script.themed_music_asset_dir = asset_dir
	var scene = script.new()
	root.add_child(scene)
	current_scene = scene
	scene.set_process(false)
	return scene
func picture(scene: Node2D,label: String) -> Image:
	scene.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	var image = root.get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	ck("saved-"+label,image.save_png(out.path_join("rpg-2-star-ocean-the-second_music_"+label+"_actual-640_v01_"+TAG+".png")) == OK)
	return image
func run() -> void:
	var args = OS.get_cmdline_user_args()
	baseline = {"area":load(args[0]),"annex":load(args[1]),"battle":load(args[2])}
	candidate = {"area":load("res://scripts/scifi_exploration_area.gd"),"annex":load("res://scripts/survey_annex.gd"),"battle":load("res://scripts/battle_arena.gd")}
	out = args[3]
	fixtures = args[4]
	DirAccess.make_dir_recursive_absolute(out)
	DirAccess.make_dir_recursive_absolute(fixtures)
	root.size = Vector2i(640,360)
	root.content_scale_size = Vector2i(640,360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	await process_frame
	app = root.get_node("AppState")
	app.set_process(false)
	SaveStore.root_path = "user://music-root-check"
	ck("windowed-render-context",DisplayServer.get_name() != "headless")
	originals = JSON.parse_string(FileAccess.get_file_as_string(ASSETS.path_join(Music.MANIFEST_FILE)))
	for context in ["city","field","ruins","battle"]:
		var stream = Music.select(context,1)
		ck(context+"-valid-selected-stream",stream != null)
		var raw = FileAccess.get_file_as_bytes(ASSETS.path_join(Music.WAV_FILES[context]))
		ck(context+"-raw-pcm-exact",stream.data == raw.slice(44))
		ck(context+"-stream-format",stream.format == AudioStreamWAV.FORMAT_16_BITS and stream.stereo and stream.mix_rate == 24000)
		ck(context+"-full-loop",stream.loop_mode == AudioStreamWAV.LOOP_FORWARD and stream.loop_begin == 0 and stream.loop_end == raw.slice(44).size()/4)
		ck(context+"-off-before-IO",Music.select(context,0,"/missing/no-read") == null)
	ck("automatic-default-off",Music.select("city",-1) == null)
	ck("unknown-override-off",Music.select("city",9) == null)
	ck("unknown-context-fallback",Music.select("unknown",1) == null)
	for context in Music.WAV_FILES:
		var name: String = Music.WAV_FILES[context]
		ck("copy-fixture-"+context,DirAccess.copy_absolute(ProjectSettings.globalize_path(ASSETS.path_join(name)),fixtures.path_join(name)) == OK)
	negative("top-array",[])
	var m = originals.duplicate(true)
	m.tracks = {}
	negative("tracks-map",m)
	m = originals.duplicate(true)
	m.tracks.pop_back()
	negative("missing-track",m)
	m = originals.duplicate(true)
	m.tracks[1] = m.tracks[0].duplicate(true)
	negative("duplicate-track",m)
	for value in [null,{},[],true,"16",16.5,-1]:
		m = originals.duplicate(true)
		m.tracks[0].bars = value
		negative("bars-"+str(value),m)
	for value in [null,{},[],true,"76",0,-1,401]:
		m = originals.duplicate(true)
		m.tracks[0].tempo_bpm = value
		negative("tempo-"+str(value),m)
	for field in ["bytes","sha256","path"]:
		for value in [null,{},[],true,1.5,"../missing.wav"]:
			m = originals.duplicate(true)
			m.tracks[0].files.wav[field] = value
			negative("wav-"+field+"-"+str(value),m)
	for field in ["frames","sample_rate_hz","channels","bit_depth"]:
		m = originals.duplicate(true)
		m.tracks[0].wav[field] = {}
		negative("wav-meta-map-"+field,m)
	put(fixtures.path_join(Music.MANIFEST_FILE),"{ invalid".to_utf8_buffer())
	ck("invalid-json-fallback",Music.select("city",1,fixtures) == null)
	put_manifest(originals)
	var original_wav = FileAccess.get_file_as_bytes(ASSETS.path_join(Music.WAV_FILES.city))
	for alteration in ["riff","riff-length","format","channels","rate","byte-rate","block-align","bits","odd-data","trailing"]:
		var raw = original_wav.duplicate()
		if alteration == "riff": raw[0] = 0
		elif alteration == "riff-length": raw.encode_u32(4,raw.size())
		elif alteration == "format": raw.encode_u16(20,3)
		elif alteration == "channels": raw.encode_u16(22,1)
		elif alteration == "rate": raw.encode_u32(24,22050)
		elif alteration == "byte-rate": raw.encode_u32(28,1)
		elif alteration == "block-align": raw.encode_u16(32,2)
		elif alteration == "bits": raw.encode_u16(34,8)
		elif alteration == "odd-data": raw.encode_u32(40,raw.size()-45)
		elif alteration == "trailing":
			raw.append(0)
			raw.append(0)
			raw.encode_u32(4,raw.size()-8)
		put(fixtures.path_join(Music.WAV_FILES.city),raw)
		m = originals.duplicate(true)
		m.tracks[0].files.wav.sha256 = digest(raw)
		m.tracks[0].files.wav.bytes = raw.size()
		negative("container-"+alteration,m)
	put(fixtures.path_join(Music.WAV_FILES.city),original_wav)
	put_manifest(originals)
	var cases = []
	for destination in ["scifi.city","scifi.outskirts","scifi.ruins"]:
		cases.append({"kind":"area","destination":destination,"room":1})
		for room in [1,2]: cases.append({"kind":"annex","destination":destination,"room":room})
	cases.append({"kind":"battle","destination":"scifi.city","room":1})
	var master = AudioServer.get_bus_index("Master")
	for item in cases:
		var label: String = item.kind+"-"+item.destination.trim_prefix("scifi.")+"-r"+str(item.room)
		var images = []
		var streams = []
		var traces = []
		for mode in ["baseline","off","on"]:
			var script: Script = baseline[item.kind] if mode == "baseline" else candidate[item.kind]
			var scene = setup(script,item.kind,item.destination,item.room,1 if mode == "on" else -1)
			await process_frame
			var ps = players(scene)
			ck(label+"-"+mode+"-no-doubled-players",ps.size() == (1 if item.kind == "battle" else 2))
			var player: AudioStreamPlayer = ps[0]
			ck(label+"-"+mode+"-playing-and-master",player.playing and player.bus == "Master")
			ck(label+"-"+mode+"-unchanged-player-gain",player.volume_db == (-13.0 if item.kind == "battle" else (-12.0 if item.kind == "annex" else -11.0)))
			streams.append(stream_description(player.stream))
			if mode == "on":
				var context: String = "battle" if item.kind == "battle" else {"scifi.city":"city","scifi.outskirts":"field","scifi.ruins":"ruins"}[item.destination]
				ck(label+"-selected-context",player.stream.data == Music.select(context,1).data)
				app.settings.set_master_volume(35,false)
				ck(label+"-settings-gain",not AudioServer.is_bus_mute(master) and absf(AudioServer.get_bus_volume_db(master)-linear_to_db(.35)) < .0001)
				app.settings.set_master_volume(0,false)
				ck(label+"-settings-mute",AudioServer.is_bus_mute(master))
				app.settings.set_master_volume(100,false)
				ck(label+"-settings-resume",not AudioServer.is_bus_mute(master) and absf(AudioServer.get_bus_volume_db(master)) < .0001 and player.playing)
			var trace = []
			for tick in 120:
				scene._process(1.0/60.0)
				trace.append(scene_state(scene,item.kind))
			traces.append(trace)
			images.append(await picture(scene,label+"-"+mode))
			await dispose(scene)
		ck(label+"-default-off-original-stream-identical",streams[0] == streams[1])
		ck(label+"-default-off-zero-render-difference",images[0].get_data() == images[1].get_data())
		ck(label+"-on-zero-render-difference",images[0].get_data() == images[2].get_data())
		for tick in 120:
			ck(label+"-off-state-parity-"+str(tick),traces[0][tick] == traces[1][tick])
			ck(label+"-on-state-parity-"+str(tick),traces[0][tick] == traces[2][tick])
		for fallback in ["missing","invalid"]:
			if fallback == "invalid": put_manifest({"schema":"bad"})
			var scene = setup(candidate[item.kind],item.kind,item.destination,item.room,1,fixtures if fallback == "invalid" else fixtures.path_join("missing"))
			await process_frame
			ck(label+"-"+fallback+"-fallback-stream-exact",stream_description(players(scene)[0].stream) == streams[0])
			ck(label+"-"+fallback+"-fallback-player-count",players(scene).size() == (1 if item.kind == "battle" else 2))
			await dispose(scene)
	put_manifest(originals)
	var failed = checks.filter(func(row):return not row["pass"])
	var source_hashes = {}
	for path in ["res://scripts/battle_arena.gd","res://scripts/scifi_exploration_area.gd","res://scripts/survey_annex.gd","res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd"]:
		source_hashes[path] = FileAccess.get_sha256(path)
	var report = {"tag":TAG,"count":checks.size(),"checks":checks,"failed":failed,"sourceRawSha256":source_hashes,"listened":false,"creatorApproved":false,"backend":AudioServer.get_driver_name(),"limitations":["Windowed real scene/player/PCM/settings checks with Dummy audio backend; no audible playback, mix or aesthetic quality claim.","All new themes remain off by default and pending listening/creator approval."]}
	put(out.path_join("rpg-2-star-ocean-the-second_themed-music_runtime-report_v01_"+TAG+".json"),JSON.stringify(report,"  ").to_utf8_buffer())
	print("THEMED_MUSIC_RUNTIME ",checks.size()-failed.size(),"/",checks.size()," PASS" if failed.is_empty() else " FAIL")
	quit(0 if failed.is_empty() else 1)
