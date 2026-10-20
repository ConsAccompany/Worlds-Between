extends SceneTree
# TEST-ONLY staged playback/capture for the heroine-sea partial2 combat-motion pilot.
# In-memory subclass of the CURRENT battle_arena.gd overrides ONLY the hero draw:
# 136x144 source -> Rect2(round(x)-32, 204, 68, 72), pivot 32/68, nearest, no mipmaps.
# The arena process is frozen; each frame changes only the injected hero texture.
# Uses the manifest's authored 1/30 s tick durations. No Python compositing, no
# interpolation, no equal-frame retiming, no contact sheet.
# Usage: -- capture <manifest> <out> <lang> <fps> <outskirts|default>
#        -- probe   <manifest> <out>

const ARENA_SHA := "41548c86eb04fb12a988c211373601f7c08d579b408d4951aa6d0f03302cb197"
const BASE_SHA := "4ce65a7915c0c0270a4ca353152b45b7d68b42672cb1483dd4f3e9cf4ac9d5e6"
const PROBE_SOURCE := """extends "res://scripts/battle_arena.gd"
var candidate: Texture2D
var inject := false
func _draw_fighter(fighter: Dictionary, index: int) -> void:
	if not inject or String(fighter["id"]) != "hero":
		super._draw_fighter(fighter, index)
		return
	var x: float = fighter["x"]
	if _is_alive(index) and index == controlled_index and not auto_mode:
		draw_circle(Vector2(x, 272), 13.0, Color("#f5e1a6"))
	draw_texture_rect(candidate, Rect2(roundf(x) - 32., 272. - 68., 68., 72.), false)
"""

func _initialize() -> void:
	call_deferred("_run")

func _hash(image: Image) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(image.get_data())
	return h.finish().hex_encode()

func _capture(arena: Node2D, path: String, size: Vector2i) -> Image:
	arena.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	assert(image != null and image.get_size() == size, "Backing image must be the declared window size")
	image.convert(Image.FORMAT_RGBA8)
	if path != "":
		assert(image.save_png(path) == OK)
	return image

func _controls(arena: Node) -> Array:
	var out := []
	for node in arena.find_children("*", "Control", true, false):
		var c: Control = node
		if not c.is_visible_in_tree():
			continue
		var r := c.get_global_rect()
		out.append([String(arena.get_path_to(c)), snappedf(r.position.x, 0.01), snappedf(r.position.y, 0.01), snappedf(r.size.x, 0.01), snappedf(r.size.y, 0.01)])
	return out

func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	assert(f != null, "Cannot read " + path)
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	assert(parsed is Dictionary, "Manifest must be a JSON object")
	return parsed

func _pose_path(motion_root: String, manifest_dir: String, entry: Dictionary) -> String:
	if String(entry.get("path", "")) != "":
		return motion_root.path_join(String(entry["path"]))
	return manifest_dir.path_join(String(entry["name"]))

func _load_texture(motion_root: String, manifest_dir: String, entry: Dictionary) -> Texture2D:
	var path := _pose_path(motion_root, manifest_dir, entry)
	assert(FileAccess.file_exists(path), "Missing pose PNG " + path)
	assert(FileAccess.get_sha256(path) == String(entry["sha256"]), "Pose PNG hash mismatch " + path)
	var image := Image.load_from_file(path)
	assert(image != null and image.get_size() == Vector2i(136, 144), "Pose must be 136x144 native")
	assert(not image.has_mipmaps())
	return ImageTexture.create_from_image(image)

func _setup(language: String, plate: bool) -> Node2D:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/hsea-motion-capture-" + language + "-" + ("outskirts" if plate else "default")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination("scifi.outskirts" if plate else "scifi.city")
	if app.language != language:
		app.toggle_language()
	app.begin_battle("patrol" if plate else "sentry", Vector2(330, 215))
	var base_script: GDScript = load("res://scripts/battle_arena.gd")
	base_script.sentry_v2_override = 0
	base_script.battle_backdrop_override = 1 if plate else 0
	base_script.combat_sprite_set_override = 0
	var probe := GDScript.new()
	probe.source_code = PROBE_SOURCE
	assert(probe.reload() == OK)
	var arena: Node2D = probe.new()
	root.add_child(arena)
	current_scene = arena
	arena.set_process(false)
	arena.set_process_input(false)
	arena.set_process_unhandled_input(false)
	await process_frame
	assert(arena.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST)
	assert(arena.fighters.size() == 4)
	assert(arena.fighters[0]["id"] == "hero")
	var xs := []
	for fighter: Dictionary in arena.fighters:
		xs.append(float(fighter["x"]))
	assert(xs == [135., 171., 207., 243.], "Keep normal current-main party positions")
	if plate:
		assert(arena.battle_backdrop_status == "loaded" and arena.battle_backdrop_arena_id == "outskirts")
	return arena

func _pose_for_tick(frames: Array, tick: int) -> String:
	var acc := 0
	for fr in frames:
		acc += int(fr["ticks"])
		if tick < acc:
			return String(fr["pose"])
	return String(frames[-1]["pose"])

func _tick_pose(idle: Array, idle_ticks: int, attack: Array, tick: int) -> String:
	var local := tick % 102
	if local < 60:
		return _pose_for_tick(idle, local % idle_ticks)
	if local < 72:
		return _pose_for_tick(attack, local - 60)
	return _pose_for_tick(idle, (local - 72) % idle_ticks)

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	assert(args.size() >= 2, "capture/probe arguments required")
	var mode: String = args[0]
	assert(FileAccess.get_sha256("res://scripts/battle_arena.gd") == ARENA_SHA, "Bind raw current arena SHA")
	assert(FileAccess.get_sha256("res://project.godot") != "", "Project readable")
	var manifest_path: String = args[1]
	var out: String = args[2]
	assert(DirAccess.dir_exists_absolute(out), "Runner must create the fresh output folder")
	var manifest := _json(manifest_path)
	var motion_root: String = args[3] if mode == "capture" else ""
	var manifest_dir := manifest_path.get_base_dir()
	var base_entry: Dictionary = manifest["poseFiles"]["base"]
	var base_path := _pose_path(args[3], manifest_dir, base_entry)
	assert(FileAccess.get_sha256(base_path) == BASE_SHA, "Approved static source must remain byte-exact")
	assert(String(base_entry["sha256"]) == BASE_SHA)
	var textures := {}
	for pose_id in manifest["poseFiles"]:
		textures[pose_id] = _load_texture(args[3], manifest_dir, manifest["poseFiles"][pose_id])
	var target := Vector2i(1280, 720)
	root.size = target
	await process_frame
	await process_frame
	assert(root.size == target, "Backing window must be 1280x720")
	assert(root.content_scale_mode == Window.CONTENT_SCALE_MODE_CANVAS_ITEMS, "Project stretch mode must stay canvas_items")
	assert(root.content_scale_size == Vector2i(640, 360), "Logical game size must stay 640x360")
	var visible := root.get_visible_rect().size
	assert(visible == Vector2(640, 360), "Logical visible rect must stay 640x360")
	var final_xf := root.get_final_transform()
	assert(is_equal_approx(final_xf.get_scale().x, 2.0) and is_equal_approx(final_xf.get_scale().y, 2.0), "Canvas integer stretch factor must be 2")
	var save_tag: String = args[7] if mode == "capture" else "probe"
	if mode == "capture":
		assert(args.size() == 8, "capture <manifest> <out> <motion_root> <lang> <fps> <outskirts|default> <tag>")
		_capture_clip(args, manifest, manifest_dir, textures, base_entry, visible, save_tag)
	else:
		assert(args.size() == 4, "probe <manifest> <out> <motion_root>")
		_probe(args, manifest, manifest_dir, base_entry, visible)

func _capture_clip(args: PackedStringArray, manifest: Dictionary, manifest_dir: String, textures: Dictionary, base_entry: Dictionary, visible: Vector2, save_tag: String) -> void:
	var language: String = args[4]
	var fps: int = int(args[5])
	var plate: String = args[6]
	assert(language == "en" or language == "zh")
	assert(fps == 30 or fps == 60)
	assert(plate == "outskirts" or plate == "default")
	var plate_bool := plate == "outskirts"
	var arena: Node2D = await _setup(language, plate_bool)
	var idle: Array = manifest["clips"]["idle"]["frames"]
	var attack: Array = manifest["clips"]["attack"]["frames"]
	var idle_ticks := int(manifest["clips"]["idle"]["total_ticks"])
	var attack_ticks := int(manifest["clips"]["attack"]["total_ticks"])
	assert(idle_ticks == 28 and attack_ticks == 12, "Bind authored idle 28-tick / attack 12-tick durations")
	var total_ticks := 60 + attack_ticks + 30 + 60 + attack_ticks + 30
	assert(total_ticks == 204, "6.8 s at authored 1/30 s ticks")
	var total_frames: int = total_ticks * fps / 30
	var hero_x := roundf(float(arena.fighters[0]["x"]))
	var frames_dir: String = args[2].path_join("frames_%s_%d" % [language, fps])
	DirAccess.make_dir_recursive_absolute(frames_dir)
	# Verification at the identical frozen state: canonical baseline, injection, restore.
	var baseline: Image = await _capture(arena, args[2].path_join("verify-baseline_%s_%d.png" % [language, fps]), Vector2i(1280, 720))
	var controls_before := _controls(arena)
	arena.candidate = textures["base"]
	arena.inject = true
	var injected: Image = await _capture(arena, args[2].path_join("verify-injected-base_%s_%d.png" % [language, fps]), Vector2i(1280, 720))
	var controls_after := _controls(arena)
	assert(controls_before == controls_after, "Injection must not move UI controls")
	arena.inject = false
	var restored: Image = await _capture(arena, args[2].path_join("verify-restored_%s_%d.png" % [language, fps]), Vector2i(1280, 720))
	assert(restored.get_data() == baseline.get_data(), "Injection off re-renders identically")
	assert(_controls(arena) == controls_before, "Restore must not move UI controls")
	var original: Texture2D = arena._female_combat_texture(arena.fighters[0], 0)
	var original_rect := Rect2i(Vector2i(int(hero_x), 272) - Vector2i(arena.HERO_COMBAT_ANCHOR), Vector2i(original.get_size()))
	var candidate_rect := Rect2i(Vector2i(int(hero_x) - 32, 272 - 68), Vector2i(68, 72))
	var bounds := original_rect.merge(candidate_rect)
	var phys := Rect2i(bounds.position * 2, bounds.size * 2)
	var a := baseline.get_data()
	var b := injected.get_data()
	var changed := 0
	var outside := 0
	for y in 720:
		for x in 1280:
			var i := (y * 1280 + x) * 4
			if a[i] != b[i] or a[i + 1] != b[i + 1] or a[i + 2] != b[i + 2] or a[i + 3] != b[i + 3]:
				changed += 1
				if not phys.has_point(Vector2i(x, y)):
					outside += 1
	assert(changed > 0 and outside == 0, "Only the hero replacement bounds may change")
	var critical_ticks := {"base": 0, "anticipation": 62, "contact": 65, "recovery": 69}
	var critical := {}
	var frame_hashes := []
	var first_frame_sha := ""
	var last_frame_sha := ""
	for frame in total_frames:
		var tick := int(floor(float(frame) * 30.0 / float(fps) + 0.000001))
		var pose := _tick_pose(idle, idle_ticks, attack, tick)
		assert(textures.has(pose), "Pose texture present: " + pose)
		arena.candidate = textures[pose]
		arena.inject = true
		var frame_path := frames_dir.path_join("frame_%05d.png" % frame)
		var image: Image = await _capture(arena, frame_path, Vector2i(1280, 720))
		var fsha := FileAccess.get_sha256(frame_path)
		frame_hashes.append(fsha)
		if first_frame_sha == "":
			first_frame_sha = fsha
		last_frame_sha = fsha
		for label in critical_ticks:
			var ctick: int = critical_ticks[label]
			if tick == ctick and float(frame) == float(ctick) * float(fps) / 30.0:
				var cpath: String = args[2].path_join("rpg-2-star-ocean-the-second_heroine-sea-motion_v01_%s%d-%s_%s_staged-partialpilot_%s.png" % [language, fps, plate, label, save_tag])
				assert(image.save_png(cpath) == OK)
				critical[label] = {"pose": pose, "tick": tick, "t": snappedf(float(tick) / 30.0, 0.000001), "frame": frame, "file": cpath.get_file(), "sha256": FileAccess.get_sha256(cpath), "width": image.get_width(), "height": image.get_height()}
	arena.inject = false
	var final_restore: Image = await _capture(arena, "", Vector2i(1280, 720))
	assert(final_restore.get_data() == baseline.get_data(), "Final restore equals baseline at identical frozen state")
	assert(_controls(arena) == controls_before, "Final restore must not move UI controls")
	var pose_at_tick := []
	for tick in total_ticks:
		pose_at_tick.append(_tick_pose(idle, idle_ticks, attack, tick))
	var report := {
		"testOnly": true, "status": "STAGED partial pilot (partial2 action staged motion); NOT all 8 actions, NOT creator-approved, NOT continuous normal-input combat",
		"staged": true, "partialPilot": true, "processFrozen": true, "continuousNormalInputCombat": false,
		"language": language, "fps": fps, "plate": plate, "backing": [1280, 720], "logicalVisible": [visible.x, visible.y],
		"contentScaleMode": "canvas_items", "contentScaleSize": [640, 360], "stretchFactor": 2,
		"drawCall": "draw_texture_rect(candidate, Rect2(round(x)-32, 204, 68, 72), tile=false); 136x144 source, 68x72 logical, pivot 32/68, NEAREST, no mipmaps",
		"testedRevision": save_tag, "arenaSha256": FileAccess.get_sha256("res://scripts/battle_arena.gd"),
		"projectSha256": FileAccess.get_sha256("res://project.godot"),
		"captureToolSha256": FileAccess.get_sha256(get_script().resource_path),
		"manifestSha256": FileAccess.get_sha256(args[1]), "manifest": args[1],
		"authorTool": manifest["source"], "baseSource": base_entry, "baseSourceByteExact": FileAccess.get_sha256(_pose_path(args[3], manifest_dir, base_entry)) == BASE_SHA,
		"poseFiles": manifest["poseFiles"], "clips": manifest["clips"], "stagedContact": manifest["stagedContact"],
		"schedule": {"leadIdleSeconds": 2.0, "attackSeconds": 0.4, "tailIdleSeconds": 1.0, "attacks": 2, "cycleTicks": 102, "totalTicks": total_ticks, "totalSeconds": snappedf(float(total_ticks) / 30.0, 0.000001), "tickSeconds": 1.0 / 30.0, "fpsParity": "30 fps samples each authored tick once; 60 fps samples each authored tick twice; no retiming"},
		"verification": {"sameFrozenArenaInstance": true, "controlsLogical": controls_after, "controlsBeforeEqualsAfter": controls_before == controls_after, "restoredEqualsBaselineRgba": true, "finalRestoreEqualsBaselineRgba": true, "changedPixels": changed, "changedOutsideHeroBounds": outside, "heroLogicalUnionRect": [bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y], "candidateLogicalRect": [candidate_rect.position.x, candidate_rect.position.y, 68, 72], "candidatePhysicalRect": [candidate_rect.position.x * 2, candidate_rect.position.y * 2, 136, 144]},
		"frames": {"count": total_frames, "dir": frames_dir.get_file(), "firstSha256": first_frame_sha, "lastSha256": last_frame_sha, "sha256ListSha256": _sha_text("\n".join(frame_hashes)), "width": 1280, "height": 720},
		"critical": critical, "poseAtTick": pose_at_tick,
		"sampledPoseRule": "tick = floor(frame*30/fps); pose selected from manifest authored cumulative ticks",
		"screenshotCompositing": false, "pythonCompositing": false, "artAccepted": false, "motionApproved": false,
		"gameSourceEdited": false, "runtimeDefaultChanged": false, "cameraChanged": false, "partyX": [135.0, 171.0, 207.0, 243.0]
	}
	assert(critical.size() == 4, "Four separate critical full-size captures")
	var rf := FileAccess.open(args[2].path_join("raw-%s-%d.json" % [language, fps]), FileAccess.WRITE)
	rf.store_string(JSON.stringify(report, "  ") + "\n")
	rf.close()
	print("HSEA_MOTION_CAPTURE_OK mode=capture lang=", language, " fps=", fps, " plate=", plate, " frames=", total_frames, " outside=", outside)
	quit(0)

func _sha_text(text: String) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(text.to_utf8_buffer())
	return h.finish().hex_encode()

func _probe(args: PackedStringArray, manifest: Dictionary, manifest_dir: String, base_entry: Dictionary, visible: Vector2) -> void:
	var arena: Node2D = await _setup("en", false)
	var hero: Dictionary = arena.fighters[0]
	var definition: Dictionary = AppState.MEMBER_DEFS["hero"]
	var hero_x := float(hero["x"])
	# Declared single in-range setup: only the enemy position is set; no HP/timer/cooldown is injected.
	arena.enemy_x = hero_x + 60.0
	arena.queue_redraw()
	var before := {"enemyHp": arena.enemy_hp, "enemyMaxHp": int(arena.enemy["max_hp"]), "visualElapsed": float(hero["visual_elapsed"]), "visualAction": String(hero["visual_action"]), "attackCooldown": float(hero["attack_cooldown"]), "playerAttackCount": arena.player_attack_count, "feedbackKey": arena.feedback_key}
	assert(before["attackCooldown"] == 0.0, "Normal initial cooldown is zero; nothing is injected")
	assert(before["visualElapsed"] == 0.0 and before["visualAction"] == "", "Normal initial hero visual state")
	var before_img: Image = await _capture(arena, args[2].path_join("probe-before-attack.png"), Vector2i(1280, 720))
	var hit: bool = arena._try_attack(0)
	var after := {"enemyHp": arena.enemy_hp, "visualElapsed": float(hero["visual_elapsed"]), "visualAction": String(hero["visual_action"]), "attackCooldown": float(hero["attack_cooldown"]), "playerAttackCount": arena.player_attack_count, "feedbackKey": arena.feedback_key}
	var after_img: Image = await _capture(arena, args[2].path_join("probe-after-attack-0ms.png"), Vector2i(1280, 720))
	var contact_s := float(manifest["stagedContact"]["start_s"])
	var damage := int(before["enemyHp"]) - int(after["enemyHp"])
	assert(hit, "normal _try_attack must land in the declared in-range setup")
	assert(damage == int(definition["attack_damage"]), "Immediate damage equals normal member attack damage")
	assert(after["visualElapsed"] == 0.0, "Damage lands on the press frame, not the staged contact frame")
	var report := {
		"testOnly": true, "stagedProbe": false, "realAttackEventProbe": true, "continuousNormalInputCombat": false,
		"status": "REAL normal battle_arena._try_attack event probe; not synchronized with the staged visual contact",
		"language": "en", "plate": "default", "backing": [1280, 720], "logicalVisible": [visible.x, visible.y],
		"arenaSha256": FileAccess.get_sha256("res://scripts/battle_arena.gd"), "projectSha256": FileAccess.get_sha256("res://project.godot"),
		"captureToolSha256": FileAccess.get_sha256(get_script().resource_path), "manifestSha256": FileAccess.get_sha256(args[1]),
		"setup": {"heroX": hero_x, "enemyX": arena.enemy_x, "separation": 60.0, "heroAttackRange": float(definition["attack_range"]), "singlePress": true, "hpInjection": false, "timerInjection": false, "cooldownInjection": false, "enemyPositionSetForInRangeSetupOnly": true},
		"before": before, "after": after, "tryAttackReturned": hit, "immediateDamage": damage,
		"immediateGameDamageAtSeconds": 0.0, "stagedContactStartSeconds": contact_s,
		"deltaSeconds": snappedf(contact_s - 0.0, 0.000001), "mismatch": contact_s > 0.0, "synchronizedGameplayContact": false,
		"note": "The arena applies damage and hit VFX on the press frame (t=0); the manifest's staged contact is a visual timeline only. Do not claim synchronized gameplay contact.",
		"probeBeforeFile": "probe-before-attack.png", "probeBeforeSha256": FileAccess.get_sha256(args[2].path_join("probe-before-attack.png")),
		"probeAfterFile": "probe-after-attack-0ms.png", "probeAfterSha256": FileAccess.get_sha256(args[2].path_join("probe-after-attack-0ms.png")),
		"beforeRgbaSha256": _hash(before_img), "afterRgbaSha256": _hash(after_img)
	}
	var rf := FileAccess.open(args[2].path_join("raw-probe.json"), FileAccess.WRITE)
	rf.store_string(JSON.stringify(report, "  ") + "\n")
	rf.close()
	print("HSEA_MOTION_CAPTURE_OK mode=probe hit=", hit, " damage=", damage, " visualElapsed=", after["visualElapsed"], " stagedContact=", contact_s)
	quit(0)
