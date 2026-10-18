extends SceneTree

# Exploration sprite set pilot: targeted logic checks (no scene, no capture). Run WITHOUT the pilot flags:
#   Godot --path game -s <this file> -- <report json path>   (windowed: frame checks read texture pixels)
# Covers: flag off reads nothing; default registry lists no set; actor-id selection and unknown actors;
# session cache (no file IO after the first load, none per draw); every malformed/missing input rejects the
# whole set (atomic fallback) while a valid set in the same registry still loads; time-based cadence at
# 30/60/144 fps and through a hitch; idle/walk/facing transitions. Malformed manifests and registries are
# written to user:// (run with an isolated APPDATA). The fixtures are diagnostic, not art.
const Pilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const FIX := "res://tests/fixtures/spriteset-diag-test-only-9f31902d/"
const REGISTRY := FIX + "rpg-2-star-ocean-the-second_spriteset-diag_fixture-registry_20261018-153932-9f31902d.json"
const FEMALE := FIX + "rpg-2-star-ocean-the-second_spriteset-diag_female-set-manifest_20261018-153932-9f31902d.json"
const MALE := FIX + "rpg-2-star-ocean-the-second_spriteset-diag_male-set-manifest_20261018-153932-9f31902d.json"
const BAD := FIX + "rpg-2-star-ocean-the-second_spriteset-diag_invalid-%s_20261018-153932-9f31902d.png"
const TMP := "user://ssp-logic-9f31902d/"

var results := []


func _initialize() -> void:
	call_deferred("_run")


func _check(name: String, ok: bool, detail = null) -> void:
	results.append({"check": name, "ok": ok, "detail": detail})
	print("SSP_LOGIC %s %s %s" % ["PASS" if ok else "FAIL", name, "" if detail == null else str(detail)])


func _json(path: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func _write(name: String, text: String) -> String:
	var file := FileAccess.open(TMP + name, FileAccess.WRITE)
	file.store_string(text)
	file.close()
	return TMP + name


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(TMP)
	var cli_flag := OS.get_cmdline_user_args().has(Pilot.FLAG)
	_check("L00 run without the pilot flag on the command line", not cli_flag)

	# Flag off: attach returns null before touching any file.
	Pilot.clear_cache()
	var probe := Sprite2D.new()
	root.add_child(probe)
	var legacy_texture := ImageTexture.create_from_image(Image.create(32, 48, false, Image.FORMAT_RGBA8))
	probe.texture = legacy_texture
	probe.offset = Vector2(0, -20)
	var off = Pilot.attach(probe, "protagonist-female", "south")
	_check("L01 flag off: attach returns null, sprite untouched, zero manifest reads and texture loads",
		off == null and probe.texture == legacy_texture and probe.offset == Vector2(0, -20) and probe.scale == Vector2.ONE
		and Pilot.manifest_reads == 0 and Pilot.texture_loads == 0 and probe.get_child_count() == 0)

	# Flag on with the shipped default registry: valid, lists no set, every actor keeps legacy textures.
	Pilot.enabled_override = 1
	var default_registry := Pilot.load_registry(Pilot.registry_path())
	var none_attached := true
	for actor in ["protagonist-female", "protagonist-male"]:
		if Pilot.attach(probe, actor, "south") != null:
			none_attached = false
	_check("L02 flag on, default registry: valid, empty, no actor attaches, sprite untouched",
		Pilot.registry_path() == Pilot.DEFAULT_REGISTRY and default_registry["ok"] and default_registry["actors"].is_empty()
		and none_attached and probe.texture == legacy_texture and Pilot.texture_loads == 0, default_registry["errors"])

	# Fixture registry: actor ids pick their own sets; unknown or unlisted actors fall back.
	Pilot.registry_override = REGISTRY
	var female_sprite := Sprite2D.new()
	var male_sprite := Sprite2D.new()
	var other_sprite := Sprite2D.new()
	for s in [female_sprite, male_sprite, other_sprite]:
		root.add_child(s)
	var female = Pilot.attach(female_sprite, "protagonist-female", "south")
	var loads_after_female := Pilot.texture_loads
	var male = Pilot.attach(male_sprite, "protagonist-male", "north")
	var unknown_ok := Pilot.attach(other_sprite, "liang-xu", "south") == null and Pilot.attach(other_sprite, "protagonist-", "south") == null \
		and Pilot.attach(other_sprite, "", "south") == null and other_sprite.texture == null
	_check("L03 actor ids select their own set; unknown/unlisted ids attach nothing",
		female != null and male != null and female.state()["set_id"] == "spriteset-diag-female-hd2-test-only-v01"
		and male.state()["set_id"] == "spriteset-diag-male-hd2-test-only-v01" and male.state()["facing"] == "north" and unknown_ok,
		[female.state() if female else null, male.state() if male else null])
	_check("L04 48 logical display: scale 1/density, pin floor line 1 logical px under the node (offset (0,-46))",
		female_sprite.scale == Vector2(0.5, 0.5) and female_sprite.offset == Vector2(0, -46)
		and female_sprite.texture.get_size() == Vector2(80, 112), [female_sprite.scale, female_sprite.offset])

	# Cache: a second attach and many frames of play read no file.
	var loads := Pilot.texture_loads
	var reads := Pilot.manifest_reads
	var again = Pilot.attach(other_sprite, "protagonist-female", "west")
	for i in 600:
		female.advance(1.0 / 60.0)
		if i % 90 < 50:
			female.walk()
		else:
			female.idle()
		if i % 120 == 0:
			female.face(Pilot.DIRECTIONS[(i / 120) % 4])
	_check("L05 cache: 24 texture loads per set, none on re-attach or during 600 frames of play",
		loads_after_female == 24 and loads == 48 and Pilot.texture_loads == loads and Pilot.manifest_reads == reads and again != null,
		{"after_female": loads_after_female, "after_male": loads, "after_play": Pilot.texture_loads, "manifest_reads": Pilot.manifest_reads})
	again.get_parent().remove_child(again)
	again.free()

	# Malformed inputs: each mutation of the valid female manifest must reject the whole set.
	var base := _json(FEMALE)
	var cases := {
		"missing frame file": func(m): m["actions"]["walk"]["east"][2]["file"] = "does-not-exist.png",
		"wrong frame size": func(m): m["actions"]["walk"]["east"][2]["file"] = BAD % "wrong-size",
		"partial alpha": func(m): m["actions"]["idle"]["south"][0]["file"] = BAD % "partial-alpha",
		"opaque cell border": func(m): m["actions"]["walk"]["north"][1]["file"] = BAD % "opaque-border",
		"idle not on the floor line": func(m): m["actions"]["idle"]["west"][1]["file"] = BAD % "floating-idle",
		"non-texture resource": func(m): m["actions"]["walk"]["south"][0]["file"] = FEMALE,
		"missing direction": func(m): m["actions"]["walk"].erase("east"),
		"unknown direction": func(m): m["actions"]["idle"]["northeast"] = m["actions"]["idle"]["north"],
		"extra action": func(m): m["actions"]["run"] = m["actions"]["walk"],
		"missing action": func(m): m["actions"].erase("idle"),
		"one-frame walk": func(m): m["actions"]["walk"]["west"] = [m["actions"]["walk"]["west"][0]],
		"zero duration": func(m): m["actions"]["walk"]["west"][1]["duration_ms"] = 0,
		"fractional duration": func(m): m["actions"]["idle"]["east"][0]["duration_ms"] = 12.5,
		"string duration": func(m): m["actions"]["idle"]["east"][0]["duration_ms"] = "470",
		"density 1": func(m): m["density"] = 1,
		"density 5": func(m): m["density"] = 5,
		"pivot outside frame": func(m): m["pivot"] = [40, 120],
		"pivot off the soles": func(m): m["pivot"] = [40, 100],
		"declared size differs": func(m): m["frame_size"] = [80, 120],
		"actor id mismatch": func(m): m["actor_id"] = "protagonist-male",
		"wrong schema": func(m): m["schema"] = "worlds-between.exploration-sprite-set.v0",
	}
	var rejected := {}
	for label in cases:
		var mutated: Dictionary = base.duplicate(true)
		cases[label].call(mutated)
		var outcome := Pilot.validate_set(mutated, FEMALE.get_base_dir(), "protagonist-female")
		rejected[label] = {"ok": outcome["ok"], "first_error": outcome["errors"][0] if outcome["errors"].size() else ""}
	var all_rejected := rejected.values().all(func(r): return not r["ok"] and r["first_error"] != "")
	var valid := Pilot.validate_set(base.duplicate(true), FEMALE.get_base_dir(), "protagonist-female")
	_check("L06 %d malformed/missing cases each reject the set; the unmutated manifest passes" % cases.size(),
		all_rejected and valid["ok"], rejected)

	# Atomic fallback through the real registry path: one bad walk frame -> that actor keeps legacy textures,
	# the other actor's valid set in the same registry still attaches.
	var partial: Dictionary = base.duplicate(true)
	for action in ["idle", "walk"]:
		for direction in Pilot.DIRECTIONS:
			for entry in partial["actions"][action][direction]:
				entry["file"] = FIX + entry["file"]
	partial["actions"]["walk"]["east"][3]["file"] = BAD % "wrong-size"
	var partial_path := _write("rpg-2-star-ocean-the-second_spriteset-diag_partial-female-set_20261018-153932-9f31902d.json", JSON.stringify(partial))
	var mixed_registry := _write("rpg-2-star-ocean-the-second_spriteset-diag_mixed-registry_20261018-153932-9f31902d.json", JSON.stringify(
		{"schema": Pilot.REGISTRY_SCHEMA, "actors": {"protagonist-female": partial_path, "protagonist-male": MALE}}))
	Pilot.registry_override = mixed_registry
	var legacy_sprite := Sprite2D.new()
	legacy_sprite.texture = legacy_texture
	legacy_sprite.offset = Vector2(0, -20)
	root.add_child(legacy_sprite)
	var partial_driver = Pilot.attach(legacy_sprite, "protagonist-female", "south")
	var male_sprite_2 := Sprite2D.new()
	root.add_child(male_sprite_2)
	var male_driver = Pilot.attach(male_sprite_2, "protagonist-male", "south")
	var partial_record: Dictionary = Pilot._sets[partial_path + "|protagonist-female"]
	_check("L07 partial set (23/24 valid frames) is rejected whole; sprite keeps legacy texture/offset/scale; other actor still loads",
		partial_driver == null and legacy_sprite.texture == legacy_texture and legacy_sprite.offset == Vector2(0, -20)
		and legacy_sprite.scale == Vector2.ONE and legacy_sprite.get_child_count() == 0 and not partial_record["ok"]
		and male_driver != null, partial_record["errors"])

	# Registry-level failures fall back for everyone.
	var bad_registries := {
		"missing file": TMP + "rpg-2-star-ocean-the-second_spriteset-diag_absent-registry_20261018-153932-9f31902d.json",
		"invalid json": _write("rpg-2-star-ocean-the-second_spriteset-diag_broken-registry_20261018-153932-9f31902d.json", "{\"schema\": "),
		"wrong schema": _write("rpg-2-star-ocean-the-second_spriteset-diag_old-registry_20261018-153932-9f31902d.json", JSON.stringify({"schema": "v0", "actors": {}})),
		"non-string entry": _write("rpg-2-star-ocean-the-second_spriteset-diag_bad-entry-registry_20261018-153932-9f31902d.json", JSON.stringify({"schema": Pilot.REGISTRY_SCHEMA, "actors": {"protagonist-female": 7}})),
		"absolute os path": "C:/not-a-resource-path/registry.json",
		"set file missing": _write("rpg-2-star-ocean-the-second_spriteset-diag_dangling-registry_20261018-153932-9f31902d.json", JSON.stringify({"schema": Pilot.REGISTRY_SCHEMA, "actors": {"protagonist-female": "res://tests/none.json"}})),
	}
	var fallbacks := {}
	for label in bad_registries:
		Pilot.registry_override = bad_registries[label]
		var s := Sprite2D.new()
		root.add_child(s)
		fallbacks[label] = Pilot.attach(s, "protagonist-female", "south") == null and s.texture == null
	_check("L08 missing/invalid/unknown registry or set path -> no attach (legacy)", fallbacks.values().all(func(v): return v), fallbacks)

	# Timing: frame index is a function of elapsed time only (30/60/144 fps agree with the analytic frame
	# including exact boundaries), and a 0.75 s hitch lands on the analytic frame.
	Pilot.registry_override = REGISTRY
	var timing := {}
	var worst := 0
	for clip_key in [["walk", "east"], ["idle", "south"]]:
		for fps in [30, 60, 144]:
			var s2 := Sprite2D.new()
			root.add_child(s2)
			var d = Pilot.attach(s2, "protagonist-female", "east")
			d.set_process(false)
			var clip: Dictionary = d.sprite_set["clips"][clip_key[0]][clip_key[1]]
			if clip_key[0] == "walk":
				d.walk()
			else:
				d.face(clip_key[1])
				d.idle()
			var mismatches := 0
			var near := 0
			var seen := {}
			for n in range(1, fps * 3 + 1):
				d.advance(1.0 / fps)
				if clip_key[0] == "walk":
					d.walk()
				else:
					d.idle()
				var t_us := int(round(n * 1000000.0 / fps))
				var durations := [130000, 130000, 130000, 130000] if clip_key[0] == "walk" else [470000, 410000]
				var want := _expected_frame(durations, t_us)
				if d.frame != want or s2.texture != clip["textures"][want] or d.clock_us != t_us:
					mismatches += 1
				seen[d.frame] = true
			timing["%s/%s@%d" % [clip_key[0], clip_key[1], fps]] = {"mismatches": mismatches, "boundary_samples_skipped": 0, "frames_seen": seen.size()}
			worst = maxi(worst, mismatches)
			s2.queue_free()
	var hitch_sprite := Sprite2D.new()
	root.add_child(hitch_sprite)
	var h = Pilot.attach(hitch_sprite, "protagonist-female", "east")
	h.set_process(false)
	h.walk()
	h.advance(0.75)
	h.walk()
	var walk_clip: Dictionary = h.sprite_set["clips"]["walk"]["east"]
	timing["hitch_0.75s"] = {"frame": h.frame, "want": 1}
	_check("L09 time-based cadence: every sample including exact boundaries at 30/60/144 fps; independent expected frames and elapsed clock; hitch",
		worst == 0 and h.frame == 1 and timing["walk/east@30"]["frames_seen"] == 4 and timing["idle/south@30"]["frames_seen"] == 2, timing)

	# Independent 100ms clip: same elapsed wall time must show frame zero at
	# shared loop boundaries, including after action and facing resets.
	var boundaries := []
	var boundary_ok := true
	var literal_clip := {"ends_us": [100000, 200000, 300000, 400000], "cycle_us": 400000}
	for fps in [30, 60, 144]:
		for milliseconds in [400, 800, 2400, 10000]:
			var count := int(round(fps * milliseconds / 1000.0))
			if absi(count * 1000 - fps * milliseconds) > 0:
				continue # Only shared, exactly representable tick times.
			var driver = Pilot.new()
			for tick in count:
				driver.advance(1.0 / fps)
			var expected_clock: int = milliseconds * 1000
			var actual_frame := Pilot.frame_at(literal_clip, driver.clock_us)
			var expected_frame := _expected_frame([100000, 100000, 100000, 100000], expected_clock)
			boundary_ok = boundary_ok and driver.clock_us == expected_clock and actual_frame == expected_frame
			boundaries.append({"fps": fps, "milliseconds": milliseconds, "clock_us": driver.clock_us, "frame": actual_frame, "expected_frame": expected_frame})
			driver.free()
	_check("L11 shared elapsed 400/800/2400ms and 10s boundaries, no tolerance or skipped boundary samples", boundary_ok, boundaries)

	# Transitions.
	var t := Sprite2D.new()
	root.add_child(t)
	var p = Pilot.attach(t, "protagonist-female", "south")
	p.set_process(false)
	var log := []
	p.idle()
	log.append(["start idle", p.state()["action"], p.state()["facing"], p.frame, p.clock_us])
	p.advance(0.5)
	p.idle()
	log.append(["idle 0.5 s", p.state()["action"], p.state()["facing"], p.frame, p.clock_us])
	p.face("east")
	p.walk()
	log.append(["turn east + walk", p.state()["action"], p.state()["facing"], p.frame, p.clock_us])
	p.advance(0.27)
	p.walk()
	log.append(["walk 0.27 s", p.state()["action"], p.state()["facing"], p.frame, p.clock_us])
	p.face("north")
	p.walk()
	log.append(["turn north while walking", p.state()["action"], p.state()["facing"], p.frame, p.clock_us])
	p.advance(0.2)
	p.idle()
	log.append(["stop", p.state()["action"], p.state()["facing"], p.frame, p.clock_us])
	p.face("bogus")
	p.idle()
	log.append(["unknown facing ignored", p.state()["action"], p.state()["facing"], p.frame, p.clock_us])
	var want_log := [["start idle", "idle", "south", 0, 0], ["idle 0.5 s", "idle", "south", 1, 500000], ["turn east + walk", "walk", "east", 0, 0],
		["walk 0.27 s", "walk", "east", 2, 270000], ["turn north while walking", "walk", "north", 0, 0], ["stop", "idle", "north", 0, 0],
		["unknown facing ignored", "idle", "north", 0, 0]]
	_check("L10 transitions: idle cycles; turn or start/stop restarts at frame 0; unknown facing ignored; texture follows state",
		log == want_log and t.texture == p.sprite_set["clips"]["idle"]["north"]["textures"][0], log)

	Pilot.enabled_override = -1
	Pilot.registry_override = ""
	var failed := results.filter(func(r): return not r["ok"]).size()
	var out := FileAccess.open(OS.get_cmdline_user_args()[0], FileAccess.WRITE)
	out.store_string(JSON.stringify({"checks": results, "passed": results.size() - failed, "total": results.size()}, " ", false) + "\n")
	out.close()
	print("SSP_LOGIC_DONE %d/%d" % [results.size() - failed, results.size()])
	quit(1 if failed else 0)


# Deliberately independent of the runtime's frame_at and clock accumulation.
func _expected_frame(durations: Array, elapsed_us: int) -> int:
	var total := 0
	for duration in durations:
		total += int(duration)
	var remaining := elapsed_us % total
	for index in durations.size():
		if remaining < int(durations[index]):
			return index
		remaining -= int(durations[index])
	return durations.size() - 1
