extends SceneTree

# Focused check + capture for the opt-in battle backdrop loader (`-- --battle-backdrop-pilot`; TECHNICAL capability only, every
# band UNAPPROVED, no default adoption). Run windowed with `-s <absolute path to this file>` against a project tree that holds
# the candidate battle_arena.gd. User args:
#   (none)                                        default mode: real encounters must stay geometric
#   --battle-backdrop-pilot [--sentry-v2-pilot]   CLI mode: real encounters use the loader; with both flags the battles are
#                                                 played to the result screen
#   --battle-backdrop-arena=<id>                  CLI arena pick; the destination-mapping section is skipped in this mode
#   --capture-dir=<absolute dir> --stamp=<YYYYMMDD-HHMMSS-id8> --capture-cases=<destination>:<enemy>[,...]
#                                                 640x360 zh/en captures of each real encounter case, plus a JSON manifest
# Static-override sections (selection, fallback, pixels, layout, gameplay trace) run in every mode and restore -1 / "" after.
const BATTLE_SCENE_PATH := "res://scenes/battle_arena.tscn"
const AREA_SCENE_PATH := "res://scenes/scifi_exploration_area.tscn"
const BATTLE_SCRIPT_PATH := "res://scripts/battle_arena.gd"
const PREFIX := "rpg-2-star-ocean-the-second_battle-backdrop-pilot"
const BAND_SHA256 := {
	"archive": "c840e071e126510cf301e8deafde2d085c759415c00c57ba88140da12c916f4b",
	"outskirts": "feea6297f1e859c64daffe0771e1ac5beadaffb0595066944b3b473cff82a4aa",
}
const UNSUPPORTED_IMAGE := "res://assets/environments/rpg-2-star-ocean-the-second_scifi-battle-arena_environment-background_m8-candidate_20261014-142723-7442fd01.png"
const MISSING_IMAGE := "res://assets/environments/rpg-2-star-ocean-the-second_battle-backdrop-pilot_missing-band-probe.png"
const WINDOWS := {"640": Vector2i(640, 360), "1280": Vector2i(1280, 720)}

var app: Node
var battle_script: GDScript
var passed := 0
var failed := 0
var results := []
var nearest_offset := -1
var traces := {}
var captures := []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail_now("windowed run required")
		return
	app = root.get_node("AppState")
	battle_script = load(BATTLE_SCRIPT_PATH)
	SaveStore.root_path = "user://test-saves/battle-backdrop-pilot-check"
	var cli_on := OS.get_cmdline_user_args().has(battle_script.BATTLE_BACKDROP_CLI_FLAG)
	var cli_sentry := OS.get_cmdline_user_args().has(battle_script.SENTRY_V2_CLI_FLAG)
	var cli_arena := _arg("--battle-backdrop-arena=")
	_check(not battle_script.BATTLE_BACKDROP_ART_APPROVED, "BATTLE_BACKDROP_ART_APPROVED is false (no band is approved)")
	await _resize("640")
	await _check_real_encounters(cli_on, cli_sentry, cli_arena)
	if cli_arena == "":
		await _check_selection()
	else:
		results.append({"pass": true, "label": "destination-mapping section skipped: CLI arena pick %s given" % cli_arena})
	await _check_fallbacks()
	await _check_pixels_and_layout()
	await _check_gameplay_trace()
	if _arg("--capture-dir=") != "":
		await _run_captures(cli_on, cli_sentry, cli_arena)
	battle_script.battle_backdrop_override = -1
	battle_script.battle_backdrop_arena_override = ""
	battle_script.sentry_v2_override = -1
	var summary := "BATTLE_BACKDROP_CHECK %s passed=%d failed=%d mode=%s nearest_offset=%d captures=%d" % ["OK" if failed == 0 else "FAIL", passed, failed, "cli" if cli_on else "default", nearest_offset, captures.size()]
	if _arg("--capture-dir=") != "":
		_write_manifest(cli_on, cli_sentry, cli_arena, summary)
	print(summary)
	quit(0 if failed == 0 else 1)


func _arg(prefix: String) -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(prefix):
			return argument.trim_prefix(prefix)
	return ""


func _prepare_party(destination: String, language: String = "zh") -> void:
	app.begin_new_run()
	app.hero_appearance = "male"
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination(destination)
	if app.language != language:
		app.toggle_language()


func _open_battle(enemy_id: String, settings: Dictionary = {}) -> Node2D:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await process_frame
	app.begin_battle(enemy_id, Vector2(330, 215))
	var battle: Node2D = load(BATTLE_SCENE_PATH).instantiate()
	for key in settings:
		battle.set(key, settings[key])
	root.add_child(battle)
	current_scene = battle
	await process_frame
	await process_frame
	return battle


# The normal game path: the exploration area's own encounter call changes scene to the battle.
func _open_encounter(destination: String, language: String = "zh") -> Node2D:
	_prepare_party(destination, language)
	change_scene_to_file(AREA_SCENE_PATH)
	for i in 3:
		await process_frame
	var area: Node = current_scene
	if area == null or not area.has_method("_open_encounter"):
		return null
	area.call("_open_encounter")
	for i in 4:
		await process_frame
	var battle := current_scene as Node2D
	return battle if battle != null and battle.get_script() == battle_script else null


func _check_real_encounters(cli_on: bool, cli_sentry: bool, cli_arena: String) -> void:
	_check(battle_script.battle_backdrop_override == -1 and battle_script.battle_backdrop_enabled() == cli_on, "static override untouched (-1); the loader is %s exactly as the CLI flag says" % ("on" if cli_on else "off"))
	for destination in ["scifi.outskirts", "scifi.ruins"]:
		var battle := await _open_encounter(destination)
		if not _check(battle != null, "%s encounter opens the battle through the exploration area's change_scene" % destination):
			continue
		var arena: String = cli_arena if cli_arena != "" else battle_script.BATTLE_ARENA_BY_DESTINATION[destination]
		var expect_status := "off"
		if cli_on:
			expect_status = "loaded" if battle_script.BATTLE_BACKDROP_BANDS.has(arena) else "no_band"
		_check(battle.battle_backdrop_status == expect_status and battle.battle_backdrop_arena_id == (arena if cli_on else ""), "%s encounter (%s): status %s arena '%s' (expected %s '%s')" % [destination, battle.enemy_id, battle.battle_backdrop_status, battle.battle_backdrop_arena_id, expect_status, arena if cli_on else ""])
		_check((battle.battle_backdrop_texture != null) == (expect_status == "loaded"), "%s encounter: band texture present only when loaded" % destination)
		_check((battle.get("enemy_texture") != null) == (cli_sentry and battle.enemy_id == "sentry"), "%s encounter: sentry v2 sprite only with its own flag on the sentry" % destination)
		if cli_on and cli_sentry:
			await _play_to_result(battle, destination)


func _play_to_result(battle: Node2D, destination: String) -> void:
	# Full-auto combat at a fixed step until the result screen, through the battle's own _process and _finish_battle.
	battle.paused = true
	battle.auto_mode = true
	var steps := 0
	while not battle.battle_finished and steps < 60 * 180:
		battle.paused = false
		battle._process(1.0 / 60.0)
		battle.paused = true
		steps += 1
	battle.paused = false
	await process_frame
	_check(battle.battle_finished and battle.battle_won and battle.result_overlay.visible, "%s battle with both flags played to the result screen: won=%s after %d steps (%.1f s)" % [destination, battle.battle_won, steps, steps / 60.0])


func _check_selection() -> void:
	battle_script.battle_backdrop_override = 1
	var cases := [
		["scifi.outskirts", "", "outskirts", "loaded"],
		["scifi.ruins", "", "ruins", "no_band"],
		["scifi.city", "", "city-terrace", "no_band"],
		["scifi.loop", "", "", "no_band"],
		["scifi.ruins", "archive", "archive", "loaded"],
		["scifi.ruins", "outskirts", "outskirts", "loaded"],
		["scifi.outskirts", "ruins", "ruins", "no_band"],
		["scifi.outskirts", "nope", "nope", "no_band"],
		["scifi.outskirts", "../outskirts", "../outskirts", "no_band"],
	]
	for entry in cases:
		_prepare_party(entry[0])
		battle_script.battle_backdrop_arena_override = entry[1]
		var battle := await _open_battle("patrol" if entry[0] == "scifi.outskirts" else "sentry")
		var ok: bool = battle.battle_backdrop_status == entry[3] and battle.battle_backdrop_arena_id == entry[2] and (battle.battle_backdrop_texture != null) == (entry[3] == "loaded")
		_check(ok, "selection %s + arena override '%s' -> arena '%s' status %s (got '%s' %s)" % [entry[0], entry[1], entry[2], entry[3], battle.battle_backdrop_arena_id, battle.battle_backdrop_status])
		if ok and entry[3] == "loaded":
			_check_band_texture(battle, entry[2])
	battle_script.battle_backdrop_arena_override = ""
	battle_script.battle_backdrop_override = 0
	_prepare_party("scifi.outskirts")
	battle_script.battle_backdrop_arena_override = "archive"
	var off := await _open_battle("patrol")
	_check(off.battle_backdrop_status == "off" and off.battle_backdrop_texture == null and off.battle_backdrop_arena_id == "", "override 0 wins over an arena pick: geometric, status off")
	battle_script.battle_backdrop_arena_override = ""
	battle_script.battle_backdrop_override = -1


func _check_band_texture(battle: Node2D, arena: String) -> void:
	var path: String = battle_script.BATTLE_BACKDROP_BANDS[arena]
	_check(FileAccess.get_sha256(ProjectSettings.globalize_path(path)) == BAND_SHA256[arena], "%s band is the tracked file (sha256-bytes %s...)" % [arena, BAND_SHA256[arena].left(8)])
	var source := Image.load_from_file(ProjectSettings.globalize_path(path))
	source.convert(Image.FORMAT_RGBA8)
	var band: Image = battle.battle_backdrop_texture.get_image()
	band.convert(Image.FORMAT_RGBA8)
	if not _check(source.get_size() == Vector2i(1280, 424) and band.get_size() == Vector2i(640, 212), "%s band: source 1280x424 drawn as a 640x212 logical texture" % arena):
		return
	# Every logical pixel must be one exact source texel (nearest, no blend) at a fixed 2x offset.
	var offset := -1
	for candidate in [0, 1]:
		var exact := true
		for y in 212:
			for x in 640:
				if band.get_pixel(x, y) != source.get_pixel(x * 2 + candidate, y * 2 + candidate):
					exact = false
					break
			if not exact:
				break
		if exact:
			offset = candidate
			break
	nearest_offset = offset
	_check(offset >= 0, "%s band: all 135680 logical pixels equal source texel (2x+%d, 2y+%d), nearest with no blending" % [arena, offset, offset])


func _check_fallbacks() -> void:
	battle_script.battle_backdrop_override = 0
	_prepare_party("scifi.outskirts")
	var reference := await _frame(await _open_battle("patrol", {"paused": true}))
	battle_script.battle_backdrop_override = 1
	var cases := [
		[MISSING_IMAGE, "missing", "missing file"],
		[UNSUPPORTED_IMAGE, "unsupported", "1672x941 image (not a multiple of 640x212)"],
		[BATTLE_SCENE_PATH, "unsupported", "non-texture resource"],
	]
	for entry in cases:
		_prepare_party("scifi.outskirts")
		var battle := await _open_battle("patrol", {"paused": true, "battle_backdrop_path_override": entry[0]})
		var ok: bool = battle.battle_backdrop_status == entry[1] and battle.battle_backdrop_texture == null
		_check(ok, "fallback %s -> status %s, no band (got %s)" % [entry[2], entry[1], battle.battle_backdrop_status])
		_check(_same(await _frame(battle), reference), "fallback %s renders the geometric backdrop pixel for pixel" % entry[2])
	for arena in ["ruins", "city-terrace", "nope"]:
		_prepare_party("scifi.outskirts")
		battle_script.battle_backdrop_arena_override = arena
		var battle := await _open_battle("patrol", {"paused": true})
		_check(battle.battle_backdrop_status == "no_band" and _same(await _frame(battle), reference), "arena '%s' (no tracked band / invalid key) renders the geometric backdrop pixel for pixel" % arena)
	battle_script.battle_backdrop_arena_override = ""
	battle_script.battle_backdrop_override = -1


func _check_pixels_and_layout() -> void:
	for window_key in WINDOWS:
		await _resize(window_key)
		var k: int = WINDOWS[window_key].x / 640
		for language in ["zh", "en"]:
			battle_script.battle_backdrop_override = 0
			_prepare_party("scifi.outskirts", language)
			var off_battle := await _open_battle("patrol", {"paused": true})
			_place(off_battle)
			var off := await _frame(off_battle)
			battle_script.battle_backdrop_override = 1
			_prepare_party("scifi.outskirts", language)
			var battle := await _open_battle("patrol", {"paused": true})
			_place(battle)
			var on := await _frame(battle)
			var band: Image = battle.battle_backdrop_texture.get_image()
			band.convert(Image.FORMAT_RGBA8)
			var tag := "%s %s" % [language, window_key]
			# Columns 0-109 hold no fighter, enemy or label, so the frame shows the band texels there exactly (k x k blocks).
			var exact := true
			for y in range(90 * k, 302 * k):
				for x in range(0, 110 * k):
					if on.get_pixel(x, y) != band.get_pixel(x / k, y / k - 90):
						exact = false
						break
				if not exact:
					break
			_check(exact, "%s: band shown nearest at the 640 logical scale (empty columns equal the band texels in %dx%d blocks)" % [tag, k, k])
			_check(_rows_same(on, off, 0, 90 * k) and _rows_same(on, off, 302 * k, 360 * k), "%s: header rows 0-89 and footer rows 302-359 identical to the default (HUD above the band, nothing covered)" % tag)
			_check(not _rows_same(on, off, 90 * k, 302 * k), "%s: the play band itself changed (band visible)" % tag)
			_check_layout(battle, tag)
			_check(_fighters_visible(on, off, battle, k), "%s: every fighter and the enemy are still drawn over the band (their pixels differ from the bare band)" % tag)
	battle_script.battle_backdrop_override = -1
	await _resize("640")


func _check_layout(battle: Node2D, tag: String) -> void:
	var inside := true
	var notes := []
	for fighter in battle.fighters:
		var x: float = fighter["x"]
		# Combat frames anchor at (30, 73) on the 272 floor; the selection ring reaches 285.
		if x - 30.0 < 0.0 or x + 30.0 > 640.0 or 272.0 - 73.0 < 90.0 or 285.0 > 302.0:
			inside = false
			notes.append("fighter %s x=%.0f" % [fighter["id"], x])
	if battle.enemy_x - 20.0 < 0.0 or battle.enemy_x + 20.0 > 640.0:
		inside = false
		notes.append("enemy x=%.0f" % battle.enemy_x)
	_check(inside, "%s: fighters (199-285) and enemy sit inside the 90-302 play band and the 640 width %s" % [tag, notes])
	var labels := {"title": battle.title_label, "feedback": battle.feedback_label, "help": battle.help_label, "hp": battle.hp_label, "energy": battle.energy_label, "enemy_hp": battle.enemy_hp_label}
	var clipped := []
	for key in labels:
		var rect: Rect2 = labels[key].get_global_rect()
		if rect.position.x < 0.0 or rect.end.x > 640.0 or rect.end.y > 360.0:
			clipped.append("%s %s" % [key, rect])
	for key in ["feedback", "help"]:
		if labels[key].get_global_rect().position.y < 302.0:
			clipped.append("%s above footer" % key)
	_check(clipped.is_empty(), "%s: footer console (feedback, help) and header labels inside 640x360, console inside the footer %s" % [tag, clipped])


func _fighters_visible(on: Image, off: Image, battle: Node2D, k: int) -> bool:
	# Each fighter's 8 px column above its feet must show sprite pixels: not the bare band texel there.
	var band: Image = battle.battle_backdrop_texture.get_image()
	band.convert(Image.FORMAT_RGBA8)
	var xs := []
	for fighter in battle.fighters:
		xs.append(roundi(float(fighter["x"])))
	xs.append(roundi(battle.enemy_x))
	for x in xs:
		var drawn := 0
		for y in range(230, 268):
			for dx in range(-4, 4):
				if on.get_pixel((x + dx) * k, y * k) != band.get_pixel(x + dx, y - 90):
					drawn += 1
		if drawn < 40:
			return false
	return true


func _check_gameplay_trace() -> void:
	# Ten seconds of fixed-step full-auto combat must match bit for bit with the backdrop and the sentry pilot in all four combinations.
	for setup in [["scifi.outskirts", "patrol"], ["scifi.ruins", "sentry"]]:
		var reference := ""
		for combo in [[0, 0], [1, 0], [0, 1], [1, 1]]:
			battle_script.battle_backdrop_override = combo[0]
			battle_script.battle_backdrop_arena_override = "archive"
			battle_script.sentry_v2_override = combo[1]
			_prepare_party(setup[0])
			var battle := await _open_battle(setup[1], {"paused": true})
			var loaded: bool = battle.battle_backdrop_texture != null
			battle.auto_mode = true
			# The same extra HP in every run keeps the fight going long enough for both sides to strike.
			battle.enemy_hp = 600
			var trace := PackedStringArray()
			for step in 600:
				battle.paused = false
				battle._process(1.0 / 60.0)
				battle.paused = true
				var row := "%.4f|%d|%.4f|%.4f|%d|%d|%d|%d|%s" % [battle.enemy_x, battle.enemy_hp, battle.enemy_windup, battle.enemy_cooldown, battle.enemy_target_index, battle.enemy_attack_count, battle.player_attack_count, int(battle.battle_finished), battle.feedback_key]
				for fighter in battle.fighters:
					var state: Dictionary = app.member_state(String(fighter["id"]))
					row += "|%.4f|%d|%d|%.4f|%.4f|%.4f|%s" % [fighter["x"], int(state["hp"]), int(state["energy"]), fighter["attack_cooldown"], fighter["dodge_time"], fighter["skill_cooldown"], fighter["visual_action"]]
				trace.append(row)
			var digest := "\n".join(trace).sha256_text()
			var key := "%s backdrop=%d sentry=%d" % [setup[1], combo[0], combo[1]]
			traces[key] = {"sha256": digest, "bandLoaded": loaded, "enemyHpEnd": battle.enemy_hp, "enemyAttacks": battle.enemy_attack_count, "playerAttacks": battle.player_attack_count, "finished": battle.battle_finished}
			_check(loaded == (combo[0] == 1), "%s: band loaded only with the backdrop on" % key)
			if reference == "":
				reference = digest
			else:
				_check(digest == reference, "%s: 600-step gameplay trace identical to backdrop=0 sentry=0 (%s...)" % [key, digest.left(12)])
		_check(int(traces["%s backdrop=1 sentry=1" % setup[1]]["enemyAttacks"]) > 0 and int(traces["%s backdrop=1 sentry=1" % setup[1]]["playerAttacks"]) > 0, "%s trace has real exchanges (both sides attacked)" % setup[1])
	battle_script.battle_backdrop_override = -1
	battle_script.battle_backdrop_arena_override = ""
	battle_script.sentry_v2_override = -1


func _run_captures(cli_on: bool, cli_sentry: bool, cli_arena: String) -> void:
	var capture_dir := _arg("--capture-dir=")
	var stamp := _arg("--stamp=")
	if not _check(RegEx.create_from_string("^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$").search(stamp) != null, "--stamp=YYYYMMDD-HHMMSS-<8 hex> given for captures"):
		return
	DirAccess.make_dir_recursive_absolute(capture_dir)
	await _resize("640")
	for case in _arg("--capture-cases=").split(",", false):
		var parts := case.split(":")
		var destination := "scifi." + parts[0]
		for language in ["zh", "en"]:
			var battle := await _open_encounter(destination, language)
			if not _check(battle != null and battle.enemy_id == parts[1], "capture %s %s: real %s encounter" % [case, language, parts[1]]):
				continue
			battle.paused = true
			_place(battle)
			battle.enemy_x = 353.0
			battle.enemy_windup = 0.2
			if battle.get("enemy_animation_texture") != null:
				battle.set("enemy_visual_state", "windup")
				battle.set("enemy_visual_clock", 0.05)
			battle._update_hud()
			battle._refresh_text()
			var image := await _frame(battle)
			var arena: String = battle.battle_backdrop_arena_id
			var name := "%s_%s-%s-%s-windup-%s-640_%s.png" % [PREFIX, arena if arena != "" else "none", battle.battle_backdrop_status, parts[1], language, stamp]
			var path := capture_dir.path_join(name)
			if not _check(image.get_size() == Vector2i(640, 360) and image.save_png(path) == OK, "capture %s saved at 640x360" % name):
				continue
			var band_path: String = battle_script.BATTLE_BACKDROP_BANDS.get(arena, "")
			captures.append({
				"file": name,
				"sha256Bytes": FileAccess.get_sha256(path),
				"size": [image.get_width(), image.get_height()],
				"destination": destination,
				"enemy": parts[1],
				"language": language,
				"state": "windup (paused, fixed layout)",
				"backdropArena": arena,
				"backdropStatus": battle.battle_backdrop_status,
				"backdropBand": band_path if battle.battle_backdrop_status == "loaded" else "",
				"backdropBandSha256Bytes": BAND_SHA256.get(arena, "") if battle.battle_backdrop_status == "loaded" else "",
				"sentryV2SpriteShown": battle.get("enemy_texture") != null,
				"openedThrough": "scifi_exploration_area._open_encounter -> change_scene_to_packed (real encounter path, CLI flags, no static override)",
			})


func _write_manifest(cli_on: bool, cli_sentry: bool, cli_arena: String, summary: String) -> void:
	# One manifest per run of a stamp: the tag names the CLI flags of the run.
	var run_tag := ("cli" if cli_on else "default") + ("-sentry" if cli_sentry else "") + ("-arena-" + cli_arena if cli_arena != "" else "")
	var path := _arg("--capture-dir=").path_join("%s_capture-manifest-%s_%s.json" % [PREFIX, run_tag, _arg("--stamp=")])
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"project": "rpg-2-star-ocean-the-second",
		"subject": "battle backdrop loader pilot (opt-in --battle-backdrop-pilot)",
		"status": "TECHNICAL capability evidence only; every band UNAPPROVED candidate art, acceptance 0, not default",
		"artApproved": false,
		"defaultAdoption": false,
		"godot": Engine.get_version_info()["string"],
		"battleScriptSha256Bytes": FileAccess.get_sha256(BATTLE_SCRIPT_PATH),
		"cmdlineUserArgs": OS.get_cmdline_user_args(),
		"cliBackdropFlag": cli_on,
		"cliSentryFlag": cli_sentry,
		"cliArena": cli_arena,
		"nearestSourceOffset": nearest_offset,
		"summary": summary,
		"gameplayTraces": traces,
		"captures": captures,
		"checks": results,
	}, "  ") + "\n")
	file.close()


func _place(battle: Node2D) -> void:
	var spacing := [0.0, -48.0, -96.0, -150.0]
	for i in battle.fighters.size():
		var fighter: Dictionary = battle.fighters[i]
		fighter["x"] = 300.0 + spacing[i]
		fighter["visual_action"] = ""
		fighter["visual_elapsed"] = 0.0
		fighter["visual_loop_kind"] = "idle"
		fighter["visual_loop_clock"] = 0.0
		fighter["visual_moving"] = false
		fighter["attack_cooldown"] = 0.0
	battle.enemy_cooldown = 99.0
	battle.enemy_windup = 0.0
	battle.enemy_x = 430.0


func _frame(battle: Node2D) -> Image:
	battle._update_hud()
	battle.queue_redraw()
	await process_frame
	await process_frame
	var image := root.get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	return image


func _resize(window_key: String) -> void:
	root.size = WINDOWS[window_key]
	for i in 4:
		await process_frame


func _same(a: Image, b: Image) -> bool:
	return a.get_size() == b.get_size() and a.get_data() == b.get_data()


func _rows_same(a: Image, b: Image, from_y: int, to_y: int) -> bool:
	if a.get_size() != b.get_size():
		return false
	var width := a.get_width()
	var da := a.get_data()
	var db := b.get_data()
	return da.slice(from_y * width * 4, to_y * width * 4) == db.slice(from_y * width * 4, to_y * width * 4)


func _check(condition: bool, label: String) -> bool:
	results.append({"pass": condition, "label": label})
	if condition:
		passed += 1
		print("PASS " + label)
	else:
		failed += 1
		push_error("FAIL " + label)
	return condition


func _fail_now(message: String) -> void:
	push_error("FAIL " + message)
	quit(1)
