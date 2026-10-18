extends SceneTree

# TEST-ONLY four-person party capture at any integer multiple of the 640x360 logical viewport, for the UNAPPROVED,
# NONRUNTIME female side-view battle idle STATIC candidate v12. Copy of the v11 any-size script (which stays unchanged);
# v12 changes the test save path and manifest labels and adds an optional 8th arg "draw-order":
#   overlay    (7 args, default) exactly the v11 method: the candidate is a child overlay drawn ABOVE every fighter, with
#              the 0.65-scaled 23.4 contact shadow, fighter 0 parked off-screen (v11 captures are reproduced byte-for-byte)
#   draw-order (8th arg)  the runtime path: fighter 0 stays at x 300 and the real battle_arena._draw_fighter draws the
#              candidate, because the idle entries of the female frame script's static texture cache are pointed at the
#              candidate (translated by (-2, +5) so its pin (32, 68) lands on HERO_COMBAT_ANCHOR (30, 73); pure texel
#              translation, no resampling). Real shadows (radius 18), real fighter order (fighter 0 first, companions over
#              it). auto_mode is set after the HUD update so the yellow controlled-fighter disc is not drawn; the battle is
#              paused, so the HUD text is unchanged. The no-sprite frame injects a fully transparent texture instead (the
#              real shadow stays). No game/ file is edited; the cache lives only in this process.
# Inherited v11 notes follow.
# v11 copy of the v10 any-size script (which stays unchanged);
# v11 changes the test save path and manifest labels, and adds one measurement: after the no-sprite grab the sentry is
# parked off-screen for one more grab, so the sentry's own pixels (no-sprite minus no-enemy) give the screen gap between
# the candidate's right edge and the sentry's left edge. The scene is then restored and re-grabbed (must equal the first
# capture). Inherited v10 / v09 notes follow.
# v10: HEAD_X (crown columns searched on 24-47, because the v10 head leans 4 texels forward).
# Copy of the committed v07r1 clean-clone helper (which stays unchanged and is
# still used for the 1280x720 captures); the only change is a 7th arg "<W>x<H>" naming the window size the run was started
# with (Godot --resolution <W>x<H>), so a 640x360 window (1 screen px per logical px) can be captured and measured too:
#   - the capture must be exactly W x H, W/640 == H/360 must be a whole number k, and every texel must be a k x k block
#   - companion masks, texture origin and screen-px measures use k instead of the literal 2
# At 1280x720 it draws exactly what v07r1 draws. Inherited v07r1 notes follow.
#
# Clean-clone repair (r1) of the v07 capture script; the v06/v07 scripts stay as committed. Same method, with two changes so
# it also runs against the committed battle_arena.gd, which has no arena bands:
#   - arena_override is set only if the scene declares it. Otherwise the run records arenaMode "head-geometric-backdrop":
#     HEAD's own backdrop is drawn, the 5th arg cannot pick a band, and no contact shadow is drawn (HEAD draws none).
#   - the floor line is a local 272.0 (HEAD's literal; the band build's ARENA_FLOOR_Y has the same value).
# With a band-capable battle_arena.gd the PNGs are byte-identical to the v06/v07 script output. Inherited v04-v07 settings:
#   - the yellow controlled-fighter disc is a test-only overlay and is NOT drawn (review capture only; sprite untouched)
#   - 5th arg selects the arena band through the scene's own arena_override (e.g. ruins = bright paving, outskirts = darker)
#   - 6th arg: path for the matching no-sprite capture (used offline for figure/floor value-contrast measurement)
# The candidate is authored natively at the owner-approved 0.65 on-screen size (1 texel = 1 logical px), so it is drawn at node
# scale 1.0: every texel is an exact 2x2 screen block like the companions. Same real battle_arena.tscn (band from arg 5, sentry),
# same party lineup/x positions and 0.65-scaled contact shadow (23.4) as the v01 0.65
# display-scale capture, so the two screenshots compare directly.
# Lives in tools/ (outside res://) so no game/ file is added or edited; run windowed (not --headless):
#   Godot --path game --resolution <W>x<H> -s <absolute path of this file> -- <candidate png> <sha256> <out png> <out json>
#         <arena id> <no-sprite png> <W>x<H>
# Measurement: capture with the sprite, without it, and with it again (must be identical); the sprite mask is every pixel
# that differs from the no-sprite capture. The first capture and the no-sprite capture are saved.
const BATTLE_SCENE_PATH := "res://scenes/battle_arena.tscn"
const PIN := Vector2(32, 68)
const CELL := Vector2i(68, 72)
const CROWN_ROW := 7
const HEAD_X := Vector2i(24, 47)          # crown columns are measured on the head only (v10 head spans x28-46)
const NODE_SCALE := 1.0
const LOGICAL := Vector2i(640, 360)
const SHADOW_RADIUS := 23.4               # 18 * 0.65 / 0.5, as in the v01 0.65 capture
const DISC_RADIUS := 16.9                 # 13 * 0.65 / 0.5
const HERO_X := 300.0
const ENEMY_X := 430.0
const OFFSCREEN_X := -1000.0
const SPACING := [0.0, -48.0, -96.0, -150.0]
const FLOOR_Y := 272.0
const HEAD_ARENA_IDS := ["ruins", "outskirts", "city-terrace", "archive"]   # ids the band build accepts; HEAD can draw none
const FEMALE_FRAMES_PATH := "res://scripts/rpg-2-star-ocean-the-second_protagonist-female_sideview-combat-frames_m8-prototype_20261014-143330-d94057ea.gd"
const RUNTIME_ANCHOR := Vector2i(30, 73)  # battle_arena.HERO_COMBAT_ANCHOR (checked at run time)


class CandidateOverlay extends Node2D:
	var texture: Texture2D
	var hero_x := 300.0
	var disc := false
	var sprite := true

	func _draw() -> void:
		var arena: Node2D = get_parent()
		if arena.get("arena_texture") != null:
			draw_set_transform(Vector2(roundf(hero_x), FLOOR_Y), 0.0, Vector2(1.0, 0.28))
			draw_circle(Vector2.ZERO, SHADOW_RADIUS, Color(0.02, 0.03, 0.05, 0.42))
			draw_set_transform(Vector2.ZERO)
		if disc:
			draw_circle(Vector2(hero_x, 272), DISC_RADIUS, Color("#f5e1a6"))
		if sprite:
			draw_texture(texture, Vector2(roundf(hero_x) - PIN.x, FLOOR_Y - PIN.y))


var app: Node
var args: PackedStringArray
var image: Image
var palette := {}
var companions := {}
var size := Vector2i.ZERO
var SCREEN_PER_LOGICAL := 0.0


func _initialize() -> void:
	call_deferred("_run")


func _fail(msg: String) -> void:
	push_error("CAPTURE FAIL: " + msg)
	print("CAPTURE FAIL: " + msg)
	quit(1)


func _run() -> void:
	args = OS.get_cmdline_user_args()
	if args.size() != 7 and not (args.size() == 8 and args[7] == "draw-order"):
		_fail("expected 7 user args (+ optional 8th 'draw-order')")
		return
	var draw_order := args.size() == 8
	var wh := args[6].split("x")
	if wh.size() != 2 or int(wh[0]) % LOGICAL.x != 0 or int(wh[0]) / LOGICAL.x != int(wh[1]) / LOGICAL.y \
			or int(wh[1]) % LOGICAL.y != 0 or int(wh[0]) < LOGICAL.x:
		_fail("7th arg must be an integer multiple of 640x360")
		return
	size = Vector2i(int(wh[0]), int(wh[1]))
	SCREEN_PER_LOGICAL = float(size.x / LOGICAL.x)
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	app = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m8-female-sideview-native-0p65-capture-v12"
	if FileAccess.get_sha256(args[0]) != args[1]:
		_fail("candidate sha256 mismatch")
		return
	image = Image.load_from_file(args[0])
	if image == null or image.get_size() != CELL:
		_fail("candidate size")
		return
	image.convert(Image.FORMAT_RGBA8)
	for y in image.get_height():
		for x in image.get_width():
			var c := image.get_pixel(x, y)
			if c.a >= 0.5:
				palette[c.to_html(false)] = true
	app.begin_new_run()
	app.hero_appearance = "female"
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination("scifi.ruins")
	app.begin_battle("sentry", Vector2(330, 215))
	var battle: Node2D = load(BATTLE_SCENE_PATH).instantiate()
	var band_capable := _has_property(battle, "arena_override")
	if band_capable:
		battle.set("arena_override", args[4])
	elif not HEAD_ARENA_IDS.has(args[4]):
		_fail("unknown arena id")
		return
	root.add_child(battle)
	current_scene = battle
	await process_frame
	await process_frame
	var arena_ok: bool = battle.get("arena_id") == args[4] if band_capable else battle.get("arena_texture") == null
	if not (arena_ok and battle.get("enemy_id") == "sentry" and battle.fighters.size() == 4):
		_fail("requested arena band (or HEAD backdrop), sentry, 4-member party")
		return
	var arena_mode := "arena-override-band" if band_capable else "head-geometric-backdrop"
	battle.paused = true
	battle.enemy_cooldown = 99.0
	battle.enemy_windup = 0.0
	battle.enemy_x = ENEMY_X
	for index in battle.fighters.size():
		battle.fighters[index]["x"] = HERO_X + SPACING[index]
		battle.fighters[index]["visual_action"] = ""
	_measure_companions(battle)
	var overlay := CandidateOverlay.new()
	var cache: Dictionary = {}
	var idle_paths: Array = []
	var runtime_tex: ImageTexture
	var empty_tex: ImageTexture
	if draw_order:
		if Vector2i(battle.HERO_COMBAT_ANCHOR) != RUNTIME_ANCHOR or String(battle.fighters[0]["id"]) != "hero" \
				or app.hero_appearance != "female":
			_fail("runtime anchor / fighter 0 / appearance not as expected")
			return
		var frames_script: Script = load(FEMALE_FRAMES_PATH)
		cache = frames_script.get("_texture_cache")
		idle_paths = frames_script.get("FRAMES")["idle"]
		var shift := Vector2i(RUNTIME_ANCHOR.x - int(PIN.x), RUNTIME_ANCHOR.y - int(PIN.y))   # (-2, +5)
		var padded := Image.create(CELL.x, CELL.y + shift.y, false, Image.FORMAT_RGBA8)
		for y in CELL.y:
			for x in CELL.x:
				var c := image.get_pixel(x, y)
				if c.a < 0.5:
					continue
				if x + shift.x < 0:
					_fail("candidate texel left of the runtime translation")
					return
				padded.set_pixel(x + shift.x, y + shift.y, c)
		runtime_tex = ImageTexture.create_from_image(padded)
		empty_tex = ImageTexture.create_from_image(Image.create(CELL.x, CELL.y + shift.y, false, Image.FORMAT_RGBA8))
		for p in idle_paths:
			cache[p] = runtime_tex
		battle.fighters[0]["x"] = HERO_X
		battle._update_hud()
		battle.auto_mode = true           # no controlled-fighter disc; paused, so the HUD text is not refreshed
	else:
		battle.fighters[0]["x"] = OFFSCREEN_X
		overlay.texture = ImageTexture.create_from_image(image)
		overlay.hero_x = HERO_X
		overlay.disc = false                  # test-only indicator removed from the review capture
		battle.add_child(overlay)
		battle._update_hud()
	battle.queue_redraw()
	var with_sprite := await _grab()
	if with_sprite.get_width() != size.x or with_sprite.get_height() != size.y:
		_fail("capture is %dx%d, not %dx%d" % [with_sprite.get_width(), with_sprite.get_height(), size.x, size.y])
		return
	if draw_order:
		for p in idle_paths:
			cache[p] = empty_tex
		battle.queue_redraw()
	else:
		overlay.sprite = false
		overlay.queue_redraw()
	var without_sprite := await _grab()
	battle.enemy_x = 4000.0
	battle.queue_redraw()
	var without_enemy := await _grab()
	battle.enemy_x = ENEMY_X
	battle.queue_redraw()
	if draw_order:
		for p in idle_paths:
			cache[p] = runtime_tex
		battle.queue_redraw()
	else:
		overlay.sprite = true
		overlay.queue_redraw()
	var again := await _grab()
	if again.get_data() != with_sprite.get_data():
		_fail("scene not static")
		return
	var m := _measure(with_sprite, without_sprite)
	var enemy_left := 99999
	var enemy_right := -1
	var enemy_px := 0
	for y in size.y:
		for x in size.x:
			if not without_sprite.get_pixel(x, y).is_equal_approx(without_enemy.get_pixel(x, y)):
				enemy_px += 1
				enemy_left = mini(enemy_left, x)
				enemy_right = maxi(enemy_right, x)
	var bb: Dictionary = m["spriteBBoxScreen"]
	m["enemyScreenPixels"] = enemy_px
	m["enemyLeftScreenX"] = enemy_left
	m["candidateRightToEnemyLeftGapScreenPx"] = enemy_left - int(bb["rightInclusive"]) - 1
	if enemy_px == 0:
		_fail("sentry pixels not found")
		return
	if int(m["spritePixels"]) == 0 or int(m["offPaletteSpritePixels"]) != 0 or float(m["nearestPredictionMatchRatio"]) < 1.0:
		_fail("sprite pixels not exact candidate texels: %s" % JSON.stringify(m))
		return
	if with_sprite.save_png(args[2]) != OK or without_sprite.save_png(args[5]) != OK:
		_fail("save png")
		return
	if FileAccess.get_sha256(args[0]) != args[1]:
		_fail("candidate changed during run")
		return
	var comp := {}
	for id in companions:
		var d: Dictionary = companions[id].duplicate()
		d.erase("_mask")
		comp[id] = d
	var manifest := {
		"project": "rpg-2-star-ocean-the-second",
		"subject": "female protagonist side-view battle idle STATIC candidate (native 0.65 on-screen size), four-person party capture, arena %s" % (args[4] if band_capable else "none (HEAD geometric backdrop)"),
		"status": "UNAPPROVED, NONRUNTIME test-only capture of a static candidate (v12 capture script); not runtime-integrated; no Game Bible, tracker or acceptance change",
		"artAcceptanceCount": 0,
		"createdAt": Time.get_datetime_string_from_system(),
		"engine": "Godot %s, canvas_items stretch (integer), 640x360 logical at %dx%d (--resolution)" % [Engine.get_version_info()["string"], size.x, size.y],
		"captureScript": "tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture-any-size_unapproved-v12_20261017-224530-2eb05ad9.gd",
		"captureMode": "draw-order" if draw_order else "overlay",
		"candidatePng": args[0].replace("\\", "/"),
		"candidateSha256": args[1],
		"capturePng": args[2].replace("\\", "/"),
		"captureSha256": FileAccess.get_sha256(args[2]),
		"width": with_sprite.get_width(),
		"height": with_sprite.get_height(),
		"nodeScale": NODE_SCALE,
		"equivalentToV01NodeScale": 0.65,
		"arena": args[4] if band_capable else "",
		"requestedArena": args[4],
		"arenaMode": arena_mode,
		"arenaBandDrawn": band_capable,
		"battleArenaScriptSha256Bytes": FileAccess.get_sha256("res://scripts/battle_arena.gd"),
		"controlledFighterDiscDrawn": false,
		"method": ("real battle_arena.tscn (arena_override band, sentry)" if band_capable else "real battle_arena.tscn as committed (no arena_override: HEAD geometric sentry backdrop, no band, no contact shadows)") + ", party hero/liang-xu/zhao-ling/ji-cheng at x 300/252/204/150; " + ("candidate drawn by the real battle_arena._draw_fighter as fighter 0 (female idle frame-cache entries pointed at the candidate translated (-2,+5) onto HERO_COMBAT_ANCHOR), real radius-18 contact shadows, runtime fighter order" if draw_order else "candidate drawn by a test-only child overlay in fighter 0's slot (fighter 0 parked off-screen) at node scale 1.0; " + ("0.65-scaled contact shadow 23.4 logical" if band_capable else "no contact shadow (HEAD draws none)")) + "; yellow controlled-fighter disc NOT drawn; sprite mask = capture with sprite minus capture without sprite",
		"drawOrderCaveat": "none: runtime order (shadows, fighter 0, then companions over it); candidate texels hidden by companions = expectedSpritePixels - spritePixels" if draw_order else "the overlay is a child node so it draws above every fighter; at runtime fighter 0 draws first (beneath companions)",
		"language": app.language,
		"companionsRuntimeFrames": comp,
		"measurement": m,
	}
	var f := FileAccess.open(args[3], FileAccess.WRITE)
	if f == null:
		_fail("manifest open")
		return
	f.store_string(JSON.stringify(manifest, "  ") + "\n")
	f.close()
	print("CAPTURE PASS arenaMode=%s %s" % [arena_mode, JSON.stringify(m)])
	quit(0)


func _has_property(object: Object, property: String) -> bool:
	for p in object.get_property_list():
		if p["name"] == property:
			return true
	return false


func _grab() -> Image:
	await process_frame
	await process_frame
	await process_frame
	var img := root.get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGBA8)
	return img


func _measure_companions(battle: Node2D) -> void:
	for index in range(1, battle.fighters.size()):
		var f: Dictionary = battle.fighters[index]
		var tex: Texture2D
		match String(f["id"]):
			"liang-xu":
				tex = battle._liang_combat_texture(f, index)
			"zhao-ling":
				tex = battle._zhao_combat_texture(f, index)
			"ji-cheng":
				tex = battle._ji_combat_texture(f, index)
		if tex == null:
			continue
		var img := tex.get_image()
		img.convert(Image.FORMAT_RGBA8)
		var used := img.get_used_rect()
		var anchor: Vector2 = battle.HERO_COMBAT_ANCHOR
		var ox: float = roundf(float(f["x"])) - anchor.x
		var oy: float = 272.0 - anchor.y
		var k := int(SCREEN_PER_LOGICAL)
		var mask := {}
		for y in img.get_height():
			for x in img.get_width():
				if img.get_pixel(x, y).a >= 0.5:
					for dy in k:
						for dx in k:
							mask[Vector2i(int((ox + x) * k) + dx, int((oy + y) * k) + dy)] = true
		companions[f["id"]] = {
			"x": f["x"],
			"usedRectTexels": [used.position.x, used.position.y, used.size.x, used.size.y],
			"heightLogicalPx": used.size.y,
			"soleScreenYInclusive": int((oy + used.end.y) * k) - 1,
			"rightScreenXInclusive": int((ox + used.end.x) * k) - 1,
			"_mask": mask,
		}


func _measure(a: Image, b: Image) -> Dictionary:
	var k := NODE_SCALE * SCREEN_PER_LOGICAL
	var ox := (roundf(HERO_X) - PIN.x * NODE_SCALE) * SCREEN_PER_LOGICAL
	var oy := (272.0 - PIN.y * NODE_SCALE) * SCREEN_PER_LOGICAL
	var head_cols := {}
	for x in range(HEAD_X.x, HEAD_X.y + 1):
		if image.get_pixel(x, CROWN_ROW).a < 0.5:
			continue
		var clear := true
		for y in CROWN_ROW:
			if image.get_pixel(x, y).a >= 0.5:
				clear = false
				break
		if clear:
			head_cols[x] = true
	var sprite_px := 0
	var off_palette := 0
	var predicted := 0
	var top := 99999
	var bottom := -1
	var left := 99999
	var right := -1
	var crown := 99999
	var mask := {}
	var col_hits := {}
	var row_hits := {}
	for y in range(int(oy) - 2, int(oy + CELL.y * k) + 2):
		for x in range(int(ox) - 2, int(ox + CELL.x * k) + 2):
			var ca := a.get_pixel(x, y)
			if ca.is_equal_approx(b.get_pixel(x, y)):
				continue
			sprite_px += 1
			mask[Vector2i(x, y)] = true
			if not palette.has(ca.to_html(false)):
				off_palette += 1
			var tx := int(floorf((x + 0.5 - ox) / k))
			var ty := int(floorf((y + 0.5 - oy) / k))
			if tx >= 0 and ty >= 0 and tx < CELL.x and ty < CELL.y:
				var c := image.get_pixel(tx, ty)
				if c.a >= 0.5 and c.to_html(false) == ca.to_html(false):
					predicted += 1
				col_hits[tx] = col_hits.get(tx, {})
				col_hits[tx][x] = true
				row_hits[ty] = row_hits.get(ty, {})
				row_hits[ty][y] = true
				if head_cols.has(tx):
					crown = mini(crown, y)
			top = mini(top, y)
			bottom = maxi(bottom, y)
			left = mini(left, x)
			right = maxi(right, x)
	var col_widths := {}
	for tx in col_hits:
		var w: int = col_hits[tx].size()
		col_widths[str(w)] = int(col_widths.get(str(w), 0)) + 1
	var row_heights := {}
	for ty in row_hits:
		var h: int = row_hits[ty].size()
		row_heights[str(h)] = int(row_heights.get(str(h), 0)) + 1
	var overlap := {}
	for id in companions:
		var cm: Dictionary = companions[id]["_mask"]
		var shared := 0
		for p in mask:
			if cm.has(p):
				shared += 1
		overlap[id] = {
			"opaqueOnOpaqueScreenPx": shared,
			"bboxGapScreenPx": left - int(companions[id]["rightScreenXInclusive"]) - 1,
			"crownToSoleRatioVsCompanionUsedHeight": float(bottom - crown + 1) / float(int(companions[id]["heightLogicalPx"]) * k),
			"soleOffsetScreenPx": bottom - int(companions[id]["soleScreenYInclusive"]),
		}
	var expected := 0
	for y in CELL.y:
		for x in CELL.x:
			if image.get_pixel(x, y).a >= 0.5:
				expected += int(k * k)
	return {
		"screenScaleFactor": k,
		"integerScreenScale": is_equal_approx(k, roundf(k)),
		"textureOriginScreenPx": [ox, oy],
		"spritePixels": sprite_px,
		"expectedSpritePixels": expected,
		"offPaletteSpritePixels": off_palette,
		"nearestPredictionMatchPx": predicted,
		"nearestPredictionMatchRatio": float(predicted) / maxf(1.0, float(sprite_px)),
		"spriteBBoxScreen": {"left": left, "top": top, "rightInclusive": right, "bottomInclusive": bottom},
		"ponytailTipScreenY": top,
		"crownScreenY": crown,
		"soleScreenYInclusive": bottom,
		"crownToSoleScreenPx": bottom - crown + 1,
		"crownToSoleLogicalPx": float(bottom - crown + 1) / SCREEN_PER_LOGICAL,
		"withPonytailLogicalPx": float(bottom - top + 1) / SCREEN_PER_LOGICAL,
		"widthScreenPx": right - left + 1,
		"texelColumnScreenWidths": col_widths,
		"texelRowScreenHeights": row_heights,
		"companionOverlap": overlap,
	}
