extends SceneTree

# Independent check of the outskirts/ruins quantized-pilot QA report: re-hashes every capture
# and candidate, re-reads PNG sizes, and counts box-vs-lanczos window pixel differences.
# Image comparison only; renders nothing. Run headless:
# Godot_v4.7.2-stable_win64_console.exe --headless --path game --script res://tests/<this>.gd -- --report=<abs path>


func _init() -> void:
	var report_path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--report="):
			report_path = arg.trim_prefix("--report=")
	var report: Variant = JSON.parse_string(FileAccess.get_file_as_string(report_path))
	if typeof(report) != TYPE_DICTIONARY:
		push_error("cannot parse report " + report_path)
		quit(1)
		return
	var failures := 0
	var images := {}
	for entry in report["captures"]:
		var image := Image.load_from_file(entry["capture"])
		var hash_ok: bool = FileAccess.get_sha256(entry["capture"]) == entry["capture_sha256"]
		var pilot_ok: bool = FileAccess.get_sha256(ProjectSettings.globalize_path(entry["pilot_source"])) == entry["pilot_source_sha256"]
		var size_ok := image != null and image.get_size() == Vector2i(1280, 720)
		var diff: Dictionary = entry["pilot_window_diff_bounds_measured"]
		var height_ok := int(diff["h"]) == int(round(float(entry["pilot_visible_window_expected"][1])))
		if not (hash_ok and pilot_ok and size_ok and height_ok):
			failures += 1
		image.convert(Image.FORMAT_RGBA8)
		images[entry["area"] + ":" + entry["variant"]] = image
		print("CHECK %s %s size_ok=%s capture_sha_ok=%s pilot_sha_ok=%s diff_h=%d expected_h=%.1f" % [entry["area"], entry["variant"], size_ok, hash_ok, pilot_ok, int(diff["h"]), float(entry["pilot_visible_window_expected"][1])])
	for area in ["scifi.outskirts", "scifi.ruins"]:
		var a: Image = images[area + ":boxquant"]
		var b: Image = images[area + ":lanczosquant"]
		var count := 0
		var bounds := Rect2i()
		for y in a.get_height():
			for x in a.get_width():
				if a.get_pixel(x, y) != b.get_pixel(x, y):
					count += 1
					bounds = Rect2i(x, y, 1, 1) if count == 1 else bounds.expand(Vector2i(x, y)).merge(Rect2i(x, y, 1, 1))
		print("VARIANT_DIFF %s pixels=%d bounds=%s" % [area, count, str(bounds)])
		if count == 0:
			failures += 1
	print("RESULT " + ("PASS" if failures == 0 else "FAIL %d" % failures))
	quit(0 if failures == 0 else 1)
