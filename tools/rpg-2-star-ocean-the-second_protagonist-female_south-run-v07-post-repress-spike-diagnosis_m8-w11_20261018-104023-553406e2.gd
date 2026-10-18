extends "rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd"

# TEST-ONLY headless DIAGNOSIS of the post-re-press pose-change "spike" reported as remaining defects 1-2 in the v07 QA note
# (30 fps 477-484 px vs the steady run's 473; 144 fps 374 vs 345).  Nothing is changed: this script EXTENDS the v07 capture
# tool (hash checked) and uses its compositor, its gait driver (Loco7) and the v06 art / manifest read-only.  The per-frame
# measure is the v06/v07 receipt's cell_silhouette_xor: at the 0.5 display scale in a 1280x720 window (640x360 logical) one
# cell texel is one window pixel, so the XOR of the composed cell alpha masks equals it (checked against the v07 receipt).
# Writes one JSON receipt with:
#   1. the v07 spike cases re-simulated (must equal the v07 receipt's numbers),
#   2. per frame: the drawn state against the manifest's steady per-px state at the same phase, and the XOR of the steady
#      per-px states at the same two phases (what the steady gait itself draws for that step),
#   3. the steady run's per-frame maximum over 24 sub-pixel start alignments at 30 / 60 / 144 fps (longer than v07's walk),
#   4. the steady per-px gait's own envelope: the largest XOR between per-px states 1, 2, 4, 5, 9 and 10 px apart, every phase.
# Run from the repository root (headless is fine; no window, no capture):
#   <Godot 4.7.2> --headless --path game -s res://../tools/<this file> -- --out=<absolute receipt path>

const V07_TOOL_FILE := "rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd"
const V07_TOOL_SHA256 := "1be872365334ffe57c91d33d2ad805fb2eb3b425fc98cb55ce9b1edfa8f37836"
# [fps, release frame, gap] -> v07 capture receipt: frame index after the re-press and its cell XOR
const V07_SPIKES := [[30, 6, 1, 4, 484], [30, 15, 1, 4, 480], [30, 5, 1, 5, 477], [144, 20, 12, 21, 374]]
const STEADY_V07 := {30: 473, 60: 371, 144: 345}


func _mask(r: Dictionary) -> Dictionary:
	var img: Image = v8_image if bool(r["show_v8"]) else comp.compose(r["state"])["image"]
	var m := {}
	for y in img.get_height():
		for x in img.get_width():
			if img.get_pixel(x, y).a8 != 0:
				m[Vector2i(x, y)] = true
	return m


func _steady_state(row: Dictionary) -> Dictionary:
	return {"show_v8": false, "state": {"bob": row["bob"], "hdy": 0, "sx": row["sx"], "csx": row["sx"], "arms": row["arms"], "feet": row["feet"]}}


func _deviation(stt: Dictionary, row: Dictionary) -> Array:
	var d := []
	for k in ["bob", "sx"]:
		if int(stt[k]) != int(row[k]):
			d.append("%s %d/%d" % [k, int(stt[k]), int(row[k])])
	if int(stt["csx"]) != int(row["sx"]):
		d.append("csx %d/%d" % [int(stt["csx"]), int(row["sx"])])
	if int(stt["hdy"]) != 0:
		d.append("hdy %d/0" % int(stt["hdy"]))
	for a in ["R", "L"]:
		if String(stt["arms"][a]) != String(row["arms"][a]):
			d.append("arm%s %s/%s" % [a, String(stt["arms"][a]), String(row["arms"][a])])
	for s in ["vl", "vr"]:
		for f in ["o", "lift", "kin"]:
			if int(stt["feet"][s][f]) != int(row["feet"][s][f]):
				d.append("%s.%s %d/%d" % [s, f, int(stt["feet"][s][f]), int(row["feet"][s][f])])
		if String(stt["feet"][s]["view"]) != String(row["feet"][s]["view"]):
			d.append("%s.view %s/%s" % [s, String(stt["feet"][s]["view"]), String(row["feet"][s]["view"])])
	return d


func _run() -> void:
	var out := _user_arg("out")
	var self_dir := (get_script() as Script).resource_path.get_base_dir()
	if _sha_text_lf(self_dir.path_join(V07_TOOL_FILE)) != V07_TOOL_SHA256 or _sha_text_lf(self_dir.path_join(V06_TOOL_FILE)) != V06_TOOL_SHA256:
		print("SPIKE_DIAG FAIL: v06 / v07 capture tools are not the pinned files")
		quit(1)
		return
	var mpath := ASSET_DIR + MANIFEST
	if _sha_text_lf(mpath) != V06_MANIFEST_SHA256:
		print("SPIKE_DIAG FAIL: v06 manifest is not the pinned file")
		quit(1)
		return
	manifest = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(mpath)))
	amend = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(V07_DIR + V07_AMEND)))
	manifest["restart"]["v07_rise_lock"] = bool(amend["restart_amendment"]["rise_lock"])
	v8_image = _load_rgba(V8_PATH)
	comp = PartCompositor.new()
	var err := comp.load_parts(manifest["parts"], ASSET_DIR, manifest["rig"])
	if err != "":
		print("SPIKE_DIAG FAIL: " + err)
		quit(1)
		return
	SDM = int(manifest["gait"]["stride_px"])
	var per_px: Array = manifest["metrics"]["nominal_per_px"]
	var n := per_px.size()
	var steady_masks := []
	for row in per_px:
		steady_masks.append(_mask(_steady_state(row)))
	var rep := {"tool": "tools/" + (get_script() as Script).resource_path.get_file(), "status": "UNAPPROVED / NONRUNTIME diagnosis only; nothing changed",
		"measure": "cell silhouette XOR between consecutive frames (composed cell alpha masks; 1 cell texel = 1 window px at the 0.5 display scale in a 1280x720 window of the 640x360 logical viewport)",
		"sources": {"v06_capture_tool": V06_TOOL_SHA256, "v07_capture_tool": V07_TOOL_SHA256, "v06_manifest": V06_MANIFEST_SHA256, "rise_lock": manifest["restart"]["v07_rise_lock"]},
		"cases": [], "steady_alignment_sweep": {}, "per_px_envelope": {}}
	var all_ok := true
	# 1 + 2: the v07 spike cases, frame by frame
	for c in V07_SPIKES:
		var fps: int = c[0]
		var dt := 1.0 / float(fps)
		var plan := _plan_walk(int(c[1]), fps)
		for i in int(c[2]):
			plan.append({"input": false, "dt": dt})
		for i in int(round(0.3 * fps)):
			plan.append({"input": true, "dt": dt})
		var loco := Loco7.new()
		var y_log := 165.0
		loco.setup(manifest, int(round(2.0 * y_log)))
		var rp: int = 1 + int(c[1]) + int(c[2])
		var prev := {}
		var prev_steady := {}
		var rows := []
		for k in plan.size():
			if bool(plan[k]["input"]):
				y_log += 140.0 * dt
			var r := loco.tick(bool(plan[k]["input"]), dt, int(round(2.0 * y_log)))
			var m := _mask(r)
			var ph := posmod(int(r["phase"]), n)
			var ms: Dictionary = steady_masks[ph]
			if k >= rp:
				var ev := []
				for e in r["events"]:
					ev.append(String(e[0]))
				rows.append({"frame_after_repress": k - rp, "phase": ph, "cell_xor": _xor(m, prev),
					"steady_per_px_xor_same_phases": _xor(ms, prev_steady) if not prev_steady.is_empty() else -1,
					"events": ev, "arms": r["state"]["arms"], "deviation_from_steady_per_px": _deviation(r["state"], per_px[ph])})
			prev = m
			prev_steady = ms
		var spike: Dictionary = rows[int(c[3])]
		var reproduced: bool = int(spike["cell_xor"]) == int(c[4])
		all_ok = all_ok and reproduced
		rep["cases"].append({"fps": fps, "release_frame": c[1], "gap": c[2], "v07_receipt_spike": {"frame_after_repress": c[3], "cell_xor": c[4]},
			"reproduced_exactly": reproduced, "spike_frame": spike, "frames": rows})
		print("SPIKE_DIAG case %s: frame +%d xor %d (v07 receipt %d), steady per-px same phases %d, deviations %s" % [str(c.slice(0, 3)), int(c[3]),
			int(spike["cell_xor"]), int(c[4]), int(spike["steady_per_px_xor_same_phases"]), str(spike["deviation_from_steady_per_px"])])
	# 3: steady runs at 24 sub-pixel start alignments (2.2 s each, measured after 1.5 strides)
	for fps in [30, 60, 144]:
		var dt := 1.0 / float(fps)
		var per := []
		for k in 24:
			var loco := Loco7.new()
			var y_log := 165.0 + float(k) / 48.0
			loco.setup(manifest, int(round(2.0 * y_log)))
			var prev := {}
			var mx := 0
			for f in int(2.2 * fps):
				y_log += 140.0 * dt
				var r := loco.tick(true, dt, int(round(2.0 * y_log)))
				var m := _mask(r)
				if not prev.is_empty() and int(r["dist"]) >= SDM * 3 / 2:
					mx = maxi(mx, _xor(m, prev))
				prev = m
			per.append(mx)
		var best: int = per.max()
		rep["steady_alignment_sweep"][str(fps)] = {"max": best, "per_alignment": per, "v07_receipt_steady_max": STEADY_V07[fps]}
		print("SPIKE_DIAG steady %d fps: max %d over 24 start alignments (v07 receipt steady %d)" % [fps, best, STEADY_V07[fps]])
	# 4: the steady per-px gait's own envelope
	for step in [1, 2, 4, 5, 9, 10]:
		var best := 0
		var at := -1
		var over := []
		for p0 in n:
			var x := _xor(steady_masks[(p0 + step) % n], steady_masks[p0])
			if x > best:
				best = x
				at = p0
			if x > 473:
				over.append([p0, (p0 + step) % n, x])
		rep["per_px_envelope"][str(step)] = {"max": best, "at_phases": [at, (at + step) % n], "pairs_over_473": over}
		print("SPIKE_DIAG per-px envelope step %d px: max %d at %d -> %d, pairs over 473: %d" % [step, best, at, (at + step) % n, over.size()])
	rep["all_v07_spikes_reproduced"] = all_ok
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		f.store_string(JSON.stringify(rep, "  ", true) + "\n")
		f.close()
	print("SPIKE_DIAG %s" % ("PASS (v07 spikes reproduced; receipt written)" if all_ok else "FAIL (a v07 spike was not reproduced)"))
	quit(0 if all_ok else 1)
