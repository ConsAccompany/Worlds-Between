extends "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd"

# Washington, D.C. ruins (scifi.ruins): opt-in v12r1 amendment of the Capitol west v12 integration candidate
# (UNAPPROVED, art not accepted). Off by default: without `-- --wdc-capitol-west-v12r1` (or r1_override = 1)
# every override hands straight to the v12 selector, which itself is inert without `--wdc-capitol-west-v12`.
# v12r1 keeps v12's art layers, walk mask, clue anchors, interaction radii, encounter, bypass, annex and battle
# hand-offs. It changes only three bounded things:
#   1. Camera: an eased follow curve (scroll 0 at the dome, then a smooth ramp to 1.5 rows per walked row and a
#      smooth stop at the bottom) replaces v12's instant 0 -> 2x kink. The 48-row actor canvas stays inside the
#      play rows 62..317 at every foot row. The spawn moves 8 rows north so the dome is in full view at entry.
#   2. Screen-safe glyphs: a clue glyph whose circle would be cut by the header/footer is pinned inside the play
#      band (or hidden when it is far outside), so no half glyph peeks out of the footer.
#   3. Label layout: world labels pick the first free slot (v12 default, above, below, left, right) that stays
#      inside the play band and clears the other labels, the visible glyphs, the actors and the heroine.
# To remove the opt-in, point game/scenes/scifi_exploration_area.tscn back at the v12 selector (or the base).
# Checks: tools/rpg-2-star-ocean-the-second_wdc-capitol-west_integration-fix-check_unapproved-v12r1_20261018-034933-23596520.py

const R1_FLAG := "--wdc-capitol-west-v12r1"
const R1_SPAWN := Vector2(372, 238)
# Eased camera curve over foot rows: 0 up to R1_CAM_START, ease-in over R1_CAM_EASE rows to R1_CAM_RATE,
# hold, ease-out over R1_CAM_EASE rows into V12_SCROLL_MAX.
const R1_CAM_START := 238
const R1_CAM_EASE := 20.0
const R1_CAM_RATE := 1.5
# Glyph circles are drawn with radius 14; 15 keeps the anti-aliased rim inside the band.
const R1_GLYPH_RADIUS := 15.0
# Glyphs whose centre is within this many rows of the band are pinned inside it; farther ones are not drawn.
const R1_GLYPH_PIN_REACH := 44.0
const R1_LABEL_GAP := 1.0

static var r1_override := -1

var r1_active := false
var r1_slots := {}
var r1_drawn_signature := ""
var r1_layout_report := {}


static func r1_enabled() -> bool:
	if r1_override >= 0:
		return r1_override == 1
	return OS.get_cmdline_user_args().has(R1_FLAG)


static func r1_scroll_for(feet: float) -> int:
	# Sub-pixel foot position in, whole scroll row out (an integer foot row would add a rounding step).
	var d := feet - float(R1_CAM_START)
	var rise := 0.5 * R1_CAM_RATE * R1_CAM_EASE
	var hold := (float(V12_SCROLL_MAX) - 2.0 * rise) / R1_CAM_RATE
	var scroll := 0.0
	if d <= 0.0:
		scroll = 0.0
	elif d < R1_CAM_EASE:
		scroll = 0.5 * R1_CAM_RATE * d * d / R1_CAM_EASE
	elif d < R1_CAM_EASE + hold:
		scroll = rise + R1_CAM_RATE * (d - R1_CAM_EASE)
	elif d < 2.0 * R1_CAM_EASE + hold:
		var rest := 2.0 * R1_CAM_EASE + hold - d
		scroll = float(V12_SCROLL_MAX) - 0.5 * R1_CAM_RATE * rest * rest / R1_CAM_EASE
	else:
		scroll = float(V12_SCROLL_MAX)
	# Safety floor: the actor canvas bottom (feet + 3) never passes play row 317.
	var lowest := roundi(feet) + V12_CANVAS_BELOW - (V12_VIEW_BOTTOM - V12_VIEW_TOP)
	return clampi(maxi(roundi(scroll), lowest), 0, V12_SCROLL_MAX)


func _ready() -> void:
	if not r1_enabled():
		super()
		return
	var saved := v12_override
	v12_override = 1
	r1_active = true
	super()
	v12_override = saved
	r1_active = v12_active


func _draw() -> void:
	if not r1_active:
		super()
		return
	if enemy_visible:
		_draw_enemy()
	for glyph in _r1_glyphs():
		_draw_field_marker(glyph["at"], glyph["color"], glyph["kind"])


func _refresh_text() -> void:
	super()
	if r1_active and v12_labels != null:
		_r1_layout()


func _v12_install(resumed: bool) -> void:
	super(resumed)
	if not r1_active:
		return
	if not resumed:
		hero.position = R1_SPAWN
		safe_position = hero.position
	_v12_sync()


func _v12_sync() -> void:
	super()
	if not r1_active:
		return
	v12_scroll = r1_scroll_for(hero.position.y)
	if v12_camera != null:
		v12_camera.position = Vector2(0, v12_scroll - V12_VIEW_TOP)
		v12_camera.force_update_scroll()
	if v12_labels != null:
		_r1_layout()


func _r1_band() -> Vector2:
	# World rows shown in play rows 62..317 at the current scroll.
	return Vector2(v12_scroll, v12_scroll + V12_VIEW_BOTTOM - V12_VIEW_TOP)


func _r1_glyphs() -> Array:
	var specs := []
	if enemy_visible:
		specs.append(["bypass", V12_BYPASS_MARKER, Color("#8fd8cf"), "bypass"])
	if not AppState.ji_records_checked:
		specs.append(["records", V12_RECORDS, Color("#e5bb77"), "records"])
	specs.append(["survey", V12_SURVEY, Color("#80d0c4" if AppState.survey_solved.has(destination_id) else "#d8be7f"), "survey"])
	specs.append(["assist", V12_ASSIST, Color("#80d0c4" if AppState.field_insights.has(destination_id) else "#e3bf78"), "assist"])
	for index in 2:
		var recorded: bool = AppState.field_traces.has("%s:%d" % [destination_id, index])
		specs.append(["trace%d" % index, V12_TRACES[index], Color("#80d0c4" if recorded else "#f4ca81"), "trace"])
	var band := _r1_band()
	var glyphs := []
	for spec in specs:
		var world: Vector2 = spec[1]
		if world.y < band.x - R1_GLYPH_PIN_REACH or world.y > band.y + R1_GLYPH_PIN_REACH:
			continue
		var at := Vector2(clampf(world.x, R1_GLYPH_RADIUS, 639.0 - R1_GLYPH_RADIUS),
			clampf(world.y, band.x + R1_GLYPH_RADIUS, band.y - R1_GLYPH_RADIUS))
		if at != world and hero != null:
			# A pinned glyph steps aside instead of hiding under the heroine standing next to its real spot.
			var feet := Vector2(round(hero.position.x), round(hero.position.y))
			var hero_rect := Rect2(feet.x - 16, feet.y - V12_CANVAS_ABOVE, 32, V12_CANVAS_ABOVE + V12_CANVAS_BELOW + 1)
			if hero_rect.intersects(Rect2(at - Vector2(R1_GLYPH_RADIUS, R1_GLYPH_RADIUS), Vector2(2, 2) * R1_GLYPH_RADIUS)):
				var reach := 16.0 + R1_GLYPH_RADIUS + 2.0
				var side := 1.0 if at.x >= feet.x else -1.0
				if feet.x + side * reach > 639.0 - R1_GLYPH_RADIUS or feet.x + side * reach < R1_GLYPH_RADIUS:
					side = -side
				at.x = feet.x + side * reach
		glyphs.append({"key": spec[0], "world": world, "at": at, "pinned": at != world, "color": spec[2], "kind": spec[3]})
	return glyphs


func _r1_glyph_label(key: String) -> Label:
	match key:
		"records":
			return records_label
		"survey":
			return survey_label
		"assist":
			return assist_label
		"trace0":
			return trace_labels[0]
		"trace1":
			return trace_labels[1]
	return null


func _r1_layout() -> void:
	var band := _r1_band()
	var glyphs := _r1_glyphs()
	var signature := str(band) + str(glyphs)
	if signature != r1_drawn_signature:
		r1_drawn_signature = signature
		queue_redraw()
	# Obstacles every label must clear: visible glyph circles, the heroine canvas, Ji and the sentry.
	var feet := Vector2(round(hero.position.x), round(hero.position.y))
	var hero_rect := Rect2(feet.x - 16, feet.y - V12_CANVAS_ABOVE, 32, V12_CANVAS_ABOVE + V12_CANVAS_BELOW + 1)
	var blockers := []
	for glyph in glyphs:
		var at: Vector2 = glyph["at"]
		blockers.append(Rect2(at - Vector2(R1_GLYPH_RADIUS, R1_GLYPH_RADIUS), Vector2(2, 2) * R1_GLYPH_RADIUS))
	var npc_shown := field_npc != null and not AppState.recruited_members.has(recruit_id)
	if npc_shown:
		blockers.append(Rect2(npc_position.x - 16, npc_position.y - V12_CANVAS_ABOVE, 32, V12_CANVAS_ABOVE + V12_CANVAS_BELOW + 1))
	if enemy_visible:
		blockers.append(Rect2(enemy_position + Vector2(-24, -24), Vector2(48, 48)))
	# Labels to place, interactable clues first: [label, anchor, default offset, kind, shown, key].
	var jobs := []
	var defaults := {"records": Vector2(-25, -37), "survey": Vector2(-50, -42), "assist": Vector2(-46, -38),
		"trace0": Vector2(-23, -34), "trace1": Vector2(-23, -34)}
	var shown_glyphs := {}
	for glyph in glyphs:
		shown_glyphs[glyph["key"]] = glyph["at"]
	for key in ["records", "survey", "assist", "trace0", "trace1"]:
		var label := _r1_glyph_label(key)
		var logical: bool = key != "records" or not AppState.ji_records_checked
		jobs.append([label, shown_glyphs.get(key, Vector2.ZERO), defaults[key], "glyph", logical and shown_glyphs.has(key), key])
	var npc_in_band := npc_position.y >= band.x + 10.0 and npc_position.y <= band.y + 18.0
	jobs.append([npc_label, npc_position, Vector2(-38, -58), "npc", npc_shown and npc_in_band, "npc"])
	var enemy_in_band := enemy_position.y >= band.x + 10.0 and enemy_position.y <= band.y + 18.0
	jobs.append([enemy_label, enemy_position, Vector2(-39, -47), "enemy", enemy_visible and enemy_in_band, "enemy"])
	var placed := []
	r1_layout_report = {"band": [band.x, band.y], "labels": {}}
	for job in jobs:
		var label: Label = job[0]
		if not job[4]:
			label.visible = false
			continue
		var size := label.get_combined_minimum_size()
		var candidates := _r1_candidates(job[1], job[2], job[3], size)
		var choice := -1
		var clears_hero := true
		var previous: int = r1_slots.get(label.get_instance_id(), -1)
		for pass_index in 2:
			var avoid_hero := pass_index == 0
			if previous >= 0 and previous < candidates.size() and _r1_free(candidates[previous], band, placed, blockers, hero_rect, avoid_hero):
				choice = previous
			else:
				for index in candidates.size():
					if _r1_free(candidates[index], band, placed, blockers, hero_rect, avoid_hero):
						choice = index
						break
			if choice >= 0:
				clears_hero = avoid_hero
				break
		if choice < 0:
			label.visible = false
			r1_slots.erase(label.get_instance_id())
			r1_layout_report["labels"][job[5]] = {"slot": -1}
			continue
		var rect: Rect2 = candidates[choice]
		r1_slots[label.get_instance_id()] = choice
		label.position = rect.position
		label.visible = true
		placed.append(rect)
		r1_layout_report["labels"][job[5]] = {"slot": choice, "clears_hero": clears_hero}


func _r1_candidates(anchor: Vector2, default_offset: Vector2, kind: String, size: Vector2) -> Array:
	var w := size.x
	var h := size.y
	var spots := [anchor + default_offset]
	# Body box around the anchor that the label must sit outside of (glyph circle, sentry or Ji canvas).
	var body := Rect2(-R1_GLYPH_RADIUS, -R1_GLYPH_RADIUS, 2.0 * R1_GLYPH_RADIUS, 2.0 * R1_GLYPH_RADIUS)
	match kind:
		"enemy":
			body = Rect2(-24, -24, 48, 48)
		"npc":
			body = Rect2(-16, -V12_CANVAS_ABOVE, 32, V12_CANVAS_ABOVE + V12_CANVAS_BELOW + 1)
	var left := anchor.x + body.position.x - 2.0 - w
	var right := anchor.x + body.end.x + 2.0
	var above := anchor.y + body.position.y - 2.0 - h
	var below := anchor.y + body.end.y + 2.0
	var middle := anchor.y + body.get_center().y - h * 0.5
	var centre := anchor.x - w * 0.5
	# Above, below, the two sides, the four diagonals, then two higher rows that clear a heroine standing
	# right below the clue (her canvas is 48 rows tall).
	for spot in [Vector2(centre, above), Vector2(centre, below), Vector2(left, middle), Vector2(right, middle),
			Vector2(left, above), Vector2(right, above), Vector2(left, below), Vector2(right, below),
			Vector2(centre, above - h - 2.0), Vector2(centre, above - 2.0 * h - 4.0)]:
		spots.append(spot)
	# Last resort before overlapping the heroine: slide along the same rows, nearest columns first.
	for step in range(1, 21):
		for row in [above, middle, above - h - 2.0, below, above - 2.0 * h - 4.0]:
			spots.append(Vector2(centre - 8.0 * step, row))
			spots.append(Vector2(centre + 8.0 * step, row))
	var rects := []
	for spot in spots:
		var x := clampf(round(spot.x), 1.0, 639.0 - w)
		rects.append(Rect2(Vector2(x, round(spot.y)), size))
	return rects


func _r1_free(rect: Rect2, band: Vector2, placed: Array, blockers: Array, hero_rect: Rect2, avoid_hero: bool) -> bool:
	if rect.position.y < band.x + 1.0 or rect.end.y > band.y:
		return false
	var grown := rect.grow(R1_LABEL_GAP)
	for other in placed:
		if grown.intersects(other):
			return false
	for blocker in blockers:
		if grown.intersects(blocker):
			return false
	if avoid_hero and grown.intersects(hero_rect):
		return false
	return true
