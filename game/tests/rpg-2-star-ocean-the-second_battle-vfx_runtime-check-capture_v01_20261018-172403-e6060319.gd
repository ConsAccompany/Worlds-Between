extends SceneTree
const Helper := preload("res://scripts/rpg-2-star-ocean-the-second_battle-vfx_transient-event-layer_pilot-v01_20261018-172229-71d0d38e.gd")
var Arena: GDScript
const SELF_PATH := "res://tests/rpg-2-star-ocean-the-second_battle-vfx_runtime-check-capture_v01_20261018-172403-e6060319.gd"
var app: Node
var passes := 0
var output_dir := ""
var stamp := ""
var run_id := ""
var captures := []
var report := {}

func _initialize() -> void:
	call_deferred("_run")

func _check(ok: bool, label: String) -> bool:
	if not ok:
		push_error("FAIL " + label)
		quit(1)
		return false
	passes += 1
	print("PASS " + label)
	return true

func _run() -> void:
	app = root.get_node("AppState")
	Arena = load("res://scripts/battle_arena.gd")
	SaveStore.root_path = "user://test-saves/vfx-capability"
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % (randi() & 0xffffffff)
	output_dir = ProjectSettings.globalize_path("res://../outputs/vfx-capability_%s-%s" % [stamp, run_id])
	DirAccess.make_dir_recursive_absolute(output_dir)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture-dir="):
			output_dir = arg.trim_prefix("--capture-dir=")
	DirAccess.make_dir_recursive_absolute(output_dir)
	if not _check(app.settings.load_status == "missing", "isolated fresh profile") or not _unit():
		return
	if not await _hooks() or not await _parity():
		return
	if DisplayServer.get_name() != "headless" and not await _captures():
		return
	var sources := {}
	for path in ["res://scripts/battle_arena.gd", "res://scripts/rpg-2-star-ocean-the-second_battle-vfx_transient-event-layer_pilot-v01_20261018-172229-71d0d38e.gd", SELF_PATH]:
		sources[path] = FileAccess.get_file_as_string(path).replace("\r\n", "\n").sha256_text()
	var data := {"task": "code.runtime.vfx-system", "status": "technical capability only; opt-in, provisional source-drawn accents", "createdAt": Time.get_datetime_string_from_system(), "checks": passes, "sourceHashAlgorithm": "sha256-text-lf-v1", "sources": sources, "report": report, "captures": captures, "artApproved": false, "healLimitation": "Presentation API tested. Current battle/GrowthRules have no healing gameplay; no healing mechanic added."}
	var path := output_dir.path_join("rpg-2-star-ocean-the-second_battle-vfx_capability-report_v01_%s-%s.json" % [stamp, run_id])
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "  ") + "\n")
	file.close()
	print("REPORT " + path)
	print("BATTLE_VFX PASS checks=%d captures=%d" % [passes, captures.size()])
	Arena.battle_vfx_override = -1
	quit(0)

func _unit() -> bool:
	var layer := Helper.new()
	if not _check(not layer.emit("unknown", Vector2.ZERO) and not layer.emit("hit", Vector2(NAN, 1)), "invalid events reject without mutation"):
		return false
	for kind in Helper.DURATIONS:
		if not _check(layer.emit(kind, Vector2(100, 200)), kind + " event accepted"):
			return false
	layer.advance(-1.0)
	if not _check(layer.events.size() == 5 and layer.events[0]["age"] == 0.0, "negative delta ignored"):
		return false
	layer.advance(0.60)
	if not _check(layer.events.is_empty(), "all five event lifetimes clean up by 600ms"):
		return false
	for index in 100:
		layer.emit("hit", Vector2(index, 200))
	if not _check(layer.events.size() == 24 and layer.emitted == 105 and layer.events[0]["origin"].x == 76.0, "24-event cap drops oldest; no unbounded queue"):
		return false
	for kind in Helper.DURATIONS:
		var a := Helper.new()
		var b := Helper.new()
		a.emit(kind, Vector2(123.4, 211.7), -1)
		b.emit(kind, Vector2(123.4, 211.7), -1)
		for tick in 3:
			a.advance(1.0 / 30.0)
		for tick in 6:
			b.advance(1.0 / 60.0)
		if not _check(a.events.size() == b.events.size() and is_equal_approx(a.events[0]["age"], b.events[0]["age"]) and a.events[0]["origin"] == Vector2(123, 212), kind + " advances by elapsed time at 30/60fps; stable pixel origin"):
			return false
	return true

func _prepare() -> void:
	app.begin_new_run()
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination("scifi.outskirts")
	app.member_state("ji-cheng")["ai_policy"] = "cautious"
	app.member_state("zhao-ling")["ai_policy"] = "aggressive"

func _open(vfx: int = 1, enemy: String = "patrol", sentry: int = 0, backdrop: int = 0) -> Node2D:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await process_frame
	_prepare()
	Arena.battle_vfx_override = vfx
	Arena.sentry_v2_override = sentry
	Arena.battle_backdrop_override = backdrop
	Arena.combat_sprite_set_override = 0
	app.begin_battle(enemy, Vector2(330, 215))
	var battle: Node2D = load("res://scenes/battle_arena.tscn").instantiate()
	battle.paused = true
	root.add_child(battle)
	current_scene = battle
	await process_frame
	await process_frame
	return battle

func _position(battle: Node2D) -> void:
	for index in 4:
		battle.fighters[index]["x"] = 170.0 + 90 * index
	battle.enemy_x = 200.0
	battle.enemy_hp = 1000
	battle.enemy_target_index = 0

func _hooks() -> bool:
	Arena.battle_vfx_override = -1
	if not _check(not OS.get_cmdline_user_args().has("--battle-vfx-pilot"), "test launches without VFX opt-in flag"):
		return false
	var off: Node2D = await _open(-1)
	if not _check(off.battle_vfx == null, "no VFX helper with default selection"):
		return false
	var battle: Node2D = await _open()
	_position(battle)
	battle.fighters[0]["x"] = 50.0
	if not _check(not battle._try_attack(0) and battle.battle_vfx.events.is_empty(), "missed out-of-range attack emits no contact effect"):
		return false
	battle.fighters[0]["x"] = 170.0
	battle.fighters[0]["attack_cooldown"] = 0.0
	if not _check(battle._try_attack(0) and battle.battle_vfx.events[-1]["kind"] == "attack", "successful normal attack contact emits once"):
		return false
	var count: int = battle.battle_vfx.emitted
	battle._try_attack(0)
	if not _check(battle.battle_vfx.emitted == count, "cooldown-rejected attack does not emit"):
		return false
	if not _check(battle._try_dodge(0) and battle.battle_vfx.events[-1]["kind"] == "dodge", "successful normal dodge emits once"):
		return false
	count = battle.battle_vfx.emitted
	battle._try_dodge(0)
	if not _check(battle.battle_vfx.emitted == count, "cooldown-rejected dodge does not emit"):
		return false
	count = battle.battle_vfx.emitted
	battle._apply_enemy_hit()
	if not _check(battle.battle_vfx.emitted == count, "enemy contact evaded during real dodge emits no hit or guard"):
		return false
	battle.fighters[0]["dodge_time"] = 0.0
	battle.fighters[0]["guard"] = true
	var energy: int = app.member_state("hero")["energy"]
	battle._apply_enemy_hit()
	if not _check(battle.battle_vfx.events[-1]["kind"] == "guard" and app.member_state("hero")["energy"] == energy - 6, "actual energy-funded blocked contact emits guard"):
		return false
	battle.fighters[0]["guard"] = false
	var hp: int = app.member_state("hero")["hp"]
	battle._apply_enemy_hit()
	if not _check(battle.battle_vfx.events[-1]["kind"] == "hit" and app.member_state("hero")["hp"] < hp, "actual damage contact emits hit"):
		return false
	battle.fighters[0]["guard"] = true
	app.member_state("hero")["energy"] = 0
	battle._apply_enemy_hit()
	if not _check(battle.battle_vfx.events[-1]["kind"] == "hit", "guard with insufficient energy emits damage hit, not blocked-contact cue"):
		return false
	hp = app.member_state("hero")["hp"]
	energy = app.member_state("hero")["energy"]
	if not _check(battle.show_heal_vfx(0) and battle.battle_vfx.events[-1]["kind"] == "heal" and app.member_state("hero")["hp"] == hp and app.member_state("hero")["energy"] == energy, "heal presentation API emits without inventing healing or energy changes"):
		return false
	if not _check(not battle.show_heal_vfx(-1) and not battle.show_heal_vfx(99), "invalid heal target rejected"):
		return false
	var before := JSON.stringify(battle.battle_vfx.events)
	battle._process(0.40)
	if not _check(JSON.stringify(battle.battle_vfx.events) == before, "pause freezes VFX elapsed time and lifetime"):
		return false
	battle.battle_finished = true
	battle.paused = false
	count = battle.battle_vfx.emitted
	for tick in 60:
		battle._process(1.0 / 60.0)
	battle.paused = true
	return _check(battle.battle_vfx.events.is_empty() and battle.battle_vfx.emitted == count, "one second of normal updates clears events without per-frame emission spam")

func _trace_row(battle: Node2D) -> String:
	var row := "%.4f|%d|%.4f|%.4f|%d|%d|%d|%d|%d|%s|%d" % [battle.enemy_x, battle.enemy_hp, battle.enemy_windup, battle.enemy_cooldown, battle.enemy_attack_count, battle.enemy_target_index, battle.player_attack_count, battle.controlled_index, int(battle.battle_finished), battle.feedback_key, battle.next_attack_bonus]
	for fighter in battle.fighters:
		var member: Dictionary = app.member_state(String(fighter["id"]))
		row += "|%s|%.4f|%.4f|%.4f|%.4f|%.4f|%s|%d|%d|%s|%.4f|%d|%d" % [fighter["id"], fighter["x"], fighter["attack_cooldown"], fighter["dodge_cooldown"], fighter["dodge_time"], fighter["skill_cooldown"], fighter["command"], int(fighter["guard"]), int(fighter["boost"]), fighter["visual_action"], fighter["visual_elapsed"], int(member["hp"]), int(member["energy"])]
	return row

func _simulate(vfx: int, combo: Array) -> Dictionary:
	var battle: Node2D = await _open(vfx, combo[0], combo[1], combo[2])
	battle.enemy_hp = 600
	battle.auto_mode = true
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	for step in 600:
		battle.paused = false
		battle._process(1.0 / 60.0)
		battle.paused = true
		context.update((_trace_row(battle) + "\n").to_utf8_buffer())
	var snapshot: Dictionary = app.make_snapshot("area", Vector2(330, 215), "vfx-parity")
	snapshot.erase("playTimeSeconds")
	for event in snapshot["playtestEvents"]:
		event.erase("atSeconds")
	return {"trace": context.finish().hex_encode(), "snapshot": JSON.stringify(snapshot), "effects": battle.battle_vfx.emitted if battle.battle_vfx != null else 0, "hits": battle.enemy_attack_count}

func _parity() -> bool:
	var pairs := []
	for combo in [["patrol", 0, 0], ["sentry", 0, 0], ["sentry", 1, 1]]:
		var on := await _simulate(1, combo)
		var off := await _simulate(0, combo)
		if not _check(on["trace"] == off["trace"] and on["snapshot"] == off["snapshot"] and on["effects"] > 0 and off["effects"] == 0 and on["hits"] > 0, "%s sentry%d/backdrop%d: 600-step simulation/save parity with effects emitted only on" % combo):
			return false
		pairs.append({"enemy": combo, "traceSha256": on["trace"], "steps": 600, "onEffects": on["effects"], "snapshotsEqual": true})
	report["simulationParity"] = pairs
	return true

func _capture_image(battle: Node2D) -> Image:
	battle._refresh_text()
	battle.queue_redraw()
	await process_frame
	await process_frame
	return root.get_viewport().get_texture().get_image()

func _captures() -> bool:
	root.size = Vector2i(640, 360)
	for kind in Helper.DURATIONS:
		for language in ["zh", "en"]:
			var battle: Node2D = await _open()
			if app.language != language:
				app.toggle_language()
			_position(battle)
			match kind:
				"attack": battle._try_attack(0)
				"dodge": battle._try_dodge(0)
				"guard":
					battle.fighters[0]["guard"] = true
					battle._apply_enemy_hit()
				"hit": battle._apply_enemy_hit()
				"heal": battle.show_heal_vfx(0)
			if not _check(battle.battle_vfx.events.size() == 1 and battle.battle_vfx.events[0]["kind"] == kind, "%s/%s capture has exactly its tested event" % [kind, language]):
				return false
			var on := await _capture_image(battle)
			var events: Array[Dictionary] = battle.battle_vfx.events.duplicate(true)
			battle.battle_vfx.events.clear()
			var off := await _capture_image(battle)
			battle.battle_vfx.events = events
			var changed := 0
			var outside := 0
			for y in 360:
				for x in 640:
					if on.get_pixel(x, y) != off.get_pixel(x, y):
						changed += 1
						if not Rect2i(0, 205, 640, 80).has_point(Vector2i(x, y)):
							outside += 1
			if not _check(on.get_size() == Vector2i(640, 360) and changed > 0 and changed <= 160 and outside == 0, "%s/%s local thin accents: %d changed pixels, none outside battle body/feet strip" % [kind, language, changed]):
				return false
			var name := "rpg-2-star-ocean-the-second_battle-vfx_%s-%s-640_test-only-v01_%s-%s.png" % [kind, language, stamp, run_id]
			var path := output_dir.path_join(name)
			on.save_png(path)
			captures.append({"case": kind, "language": language, "file": name, "sha256": FileAccess.get_sha256(path), "changedPixels": changed, "outsidePixels": outside, "healIsPresentationApiOnly": kind == "heal"})
	return true
