extends SceneTree

# Explicit unit fixture: invokes the real _finish_battle(true) without fighting.
# Tests localization and reward/save idempotence only, not natural victory or playtesting.
var checks: Array = []
var captures: Array = []
var out := ""
var tag := ""
var stage := ""
var failures := 0

func _initialize() -> void:
	call_deferred("run")

func ck(name: String, ok: bool, detail: Variant = null) -> void:
	checks.append({"name": name, "passed": ok, "detail": detail})
	print("RESULT_LOCALE ", "PASS " if ok else "FAIL ", name)
	if not ok:
		failures += 1

func save_ids() -> Array:
	return SaveStore.list_entries().map(func(v: Dictionary): return String(v["id"]))

func capture_result(arena: Node, name: String) -> void:
	arena.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	var path := out.path_join("rpg-2-star-ocean-the-second_battle-result_" + name + "_unit-" + stage + "_" + tag + ".png")
	ck(name + " actual viewport", image.get_size() == Vector2i(640, 360))
	ck(name + " capture saved", image.save_png(path) == OK)
	captures.append({"file": path, "sha256": FileAccess.get_sha256(path)})

func run() -> void:
	var args := OS.get_cmdline_user_args()
	assert(args.size() == 3)
	out = args[0]
	tag = args[1]
	stage = args[2]
	DirAccess.make_dir_recursive_absolute(out)
	root.size = Vector2i(640, 360)
	await process_frame
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://result-locale-unit/" + stage
	ck("isolated profile physically exists", DirAccess.dir_exists_absolute(OS.get_environment("APPDATA")))
	ck("not headless capture", DisplayServer.get_name() != "headless")
	var arena_script: GDScript = load("res://scripts/battle_arena.gd")
	for start_language in ["en", "zh"]:
		app.begin_new_run()
		if app.language != start_language:
			app.toggle_language()
		app.select_destination("scifi.outskirts")
		app.begin_battle("patrol", Vector2(330, 215))
		var arena: Node2D = arena_script.new()
		root.add_child(arena)
		arena.set_process(false)
		var before_saves := save_ids()
		var before_xp := int(app.hero_state["xp"])
		var before_jp := int(app.hero_state["jp"])
		arena._finish_battle(true)
		var awarded_xp := int(app.hero_state["xp"])
		var awarded_jp := int(app.hero_state["jp"])
		var after_saves := save_ids()
		ck(start_language + " real reward once", awarded_xp - before_xp == 26 and awarded_jp - before_jp == 12)
		ck(start_language + " exactly one new save", after_saves.size() == before_saves.size() + 1)
		var languages: Array = [start_language, "zh" if start_language == "en" else "en", start_language]
		for i in languages.size():
			var language: String = languages[i]
			if app.language != language:
				app.toggle_language()
			# Refresh is already wired to language_changed; repeat refresh to check idempotence.
			arena._refresh_text()
			var expected_reward := "Battle rewards: 26 XP / 12 JP; reserves earn 25%" if language == "en" else "战斗奖励：26 XP / 12 JP；候补获得 25%"
			var prefix: String = str(start_language) + "-" + str(i) + "-" + language
			ck(prefix + " localized title", arena.result_title.text == ("Victory" if language == "en" else "战斗胜利"), arena.result_title.text)
			ck(prefix + " localized button", arena.result_button.text == ("Keep exploring" if language == "en" else "继续探索"), arena.result_button.text)
			ck(prefix + " localized exact reward", arena.result_note.text.ends_with(expected_reward), arena.result_note.text)
			ck(prefix + " no repeated rewards", int(app.hero_state["xp"]) == awarded_xp and int(app.hero_state["jp"]) == awarded_jp)
			ck(prefix + " identical save IDs", save_ids() == after_saves)
			await capture_result(arena, prefix)
		arena._finish_battle(true)
		ck(start_language + " repeat finish idempotent", save_ids() == after_saves and int(app.hero_state["xp"]) == awarded_xp and int(app.hero_state["jp"]) == awarded_jp)
		arena.queue_free()
		await process_frame
	var report := {"fixture": "unit: direct real finish callback; no natural combat claim", "stage": stage, "sourceSha256": FileAccess.get_sha256("res://scripts/battle_arena.gd"), "testSha256": FileAccess.get_sha256(get_script().resource_path), "checks": checks, "failures": failures, "captures": captures}
	var report_path := out.path_join("rpg-2-star-ocean-the-second_battle-result_locale-unit-report_" + stage + "_" + tag + ".json")
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print("RESULT_LOCALE_UNIT_OK" if failures == 0 else "RESULT_LOCALE_UNIT_FAILED", " ", checks.size(), " checks; failures=", failures)
	quit(0 if failures == 0 else 1)
