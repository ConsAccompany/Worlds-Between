extends SceneTree

# TEST-ONLY actual normal-game run of the opt-in female complete-exploration pilot: the real host scene processes real
# action input (Input.action_press / action_release) through its own movement, collision, clamp, facing and y-sort.
# Nothing here sets a pose. Script: idle, east start/run/stop, same-facing re-press during the stop, reversal to west,
# north, south, two diagonals, a long push into the boundary (blocked), final idle. Records per frame the host position,
# host facing, the driver's model-mode flag versus the visible pose key, frame cost and memory, and writes a JSON.
#   Godot --path <checkout>/game -s <abs this file> [--write-movie <abs avi> --fixed-fps N] -- --out=<abs json>
#     --scene=city|annex --lang=en|zh [--mixed=1] [--female-complete-exploration-pilot]

const Driver := preload("res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd")
const PLAN := [["", 0.5], ["move_right", 1.0], ["", 0.5], ["move_right", 0.4], ["", 0.1], ["move_right", 0.3],
	["move_left", 0.8], ["move_up", 0.8], ["move_down", 0.8], ["move_right+move_up", 0.6], ["move_left+move_down", 0.6],
	["move_left", 3.0], ["", 1.2]]


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var opts := {"out": "", "scene": "city", "lang": "en", "mixed": "0"}
	for arg in OS.get_cmdline_user_args():
		for k in opts:
			if arg.begins_with("--%s=" % k):
				opts[k] = arg.substr(k.length() + 3)
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/fcx2-actual"
	app.begin_new_run()
	app.hero_appearance = "female"
	app.language = opts["lang"]
	app.select_destination("scifi.city")
	app.current_annex_room = 2
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var host: Node2D = load("res://scenes/scifi_exploration_area.tscn" if opts["scene"] == "city" else "res://scenes/survey_annex.tscn").instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	var pilot = host.sprite_pilot
	var attached: bool = pilot != null and pilot.has_method("step")
	var rng := RandomNumberGenerator.new()
	rng.seed = 1019
	var frames := []
	var mem0 := OS.get_static_memory_usage()
	var placeholder := 0
	var mismatch := 0
	for seg in PLAN:
		var actions: Array = [] if seg[0] == "" else String(seg[0]).split("+")
		for a in actions:
			Input.action_press(a)
		var t := 0.0
		while t < float(seg[1]):
			if opts["mixed"] == "1":
				OS.delay_usec([0, 0, 18000, 4000, 30000][rng.randi() % 5])
			await process_frame
			var dt := get_root().get_process_delta_time()
			t += dt
			var rec := {"seg": seg[0], "dt": snappedf(dt, 0.0001), "pos": [snappedf(host.hero.position.x, 0.001), snappedf(host.hero.position.y, 0.001)],
				"process_ms": snappedf(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0, 0.01)}
			if attached:
				var r: Dictionary = pilot.report()
				rec["facing"] = r["facing"]
				rec["mode_flag"] = r["model_mode"]
				rec["visible"] = "idle-%d" % r["idle_phase"] if r["showing_idle"] else "live"
				rec["step_us_max_so_far"] = r["step_us_max"]
				if String(r["model_mode"]) == "reverse-placeholder":
					placeholder += 1
				# The visible pose must agree with the mode flag: rest/idle -> idle loop, anything else -> live pose.
				var resting := String(r["model_mode"]) in ["idle", "rest"]
				if resting != bool(r["showing_idle"]):
					mismatch += 1
			frames.append(rec)
		if String(seg[0]) in ["move_up", "move_down"]:
			await RenderingServer.frame_post_draw
			var image := root.get_texture().get_image()
			assert(image.save_png(String(opts["out"]).get_base_dir().path_join("rpg-2-star-ocean-the-second_female-complete-explore_combined-city-"+String(seg[0]).replace("_","-")+"-critical_unapproved-v01_20261019-233242-ada4f7ad.png")) == OK)
		for a in actions:
			Input.action_release(a)
	var report := {"tool": "female-complete-explore actual game run v01", "opts": opts, "attached": attached,
		"flag_present": OS.get_cmdline_user_args().has(Driver.FLAG), "frames": frames.size(),
		"static_memory_delta_bytes": OS.get_static_memory_usage() - mem0, "reverse_placeholder_frames": placeholder,
		"mode_visible_mismatch_frames": mismatch}
	if attached:
		report["driver"] = pilot.report()
	var pm := []
	for f in frames:
		pm.append(float(f["process_ms"]))
	pm.sort()
	report["process_ms_p50"] = pm[pm.size() / 2]
	report["process_ms_p95"] = pm[int(pm.size() * 0.95)]
	report["process_ms_max"] = pm[-1]
	report["final_pos"] = frames[-1]["pos"]
	report["frame_log"] = frames
	var f := FileAccess.open(opts["out"], FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " "))
	f.close()
	var flag_on: bool = report["flag_present"]
	var ok: bool = (attached == flag_on) and placeholder == 0 and mismatch == 0
	if flag_on:
		ok = ok and String(report["driver"]["model_mode"]) in ["idle", "rest"] and bool(report["driver"]["showing_idle"])
	print("ATTACHED=%s FRAMES=%d P50=%.2f P95=%.2f MAX=%.2f FINAL=%s" % [attached, frames.size(), report["process_ms_p50"], report["process_ms_p95"], report["process_ms_max"], str(report["final_pos"])])
	for child in host.get_children():
		if child is AudioStreamPlayer:
			child.stop()
			child.stream = null
	host.queue_free()
	await process_frame
	Driver.clear_cache()
	print("FCX_ACTUAL_RUN_PASS" if ok else "FCX_ACTUAL_RUN_FAIL")
	var previous := AudioServer.get_time_since_last_mix()
	var mixes := 0
	var deadline := Time.get_ticks_usec() + 300000
	while mixes < 2 and Time.get_ticks_usec() < deadline:
		await process_frame
		var age := AudioServer.get_time_since_last_mix()
		if age < previous:
			mixes += 1
		previous = age
	quit(0 if ok and mixes == 2 else 1)
