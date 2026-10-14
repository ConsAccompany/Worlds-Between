extends SceneTree

# Read-only review-tool check: each source sheet loads into its visible TextureRect.
const GALLERY_SCENE := "res://scenes/rpg-2-star-ocean-the-second_character-source-gallery_m8-v01_20261014-144020-907ab4d1.tscn"
var captures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _settle() -> void:
	await process_frame
	await process_frame


func _check(ok: bool, detail: String) -> bool:
	if not ok:
		push_error("CHARACTER_GALLERY_CHECK_FAILED: " + detail)
		quit(1)
	return ok


func _capture(label: String) -> void:
	var directory := OS.get_environment("WB_GALLERY_EVIDENCE_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless":
		return
	DirAccess.make_dir_recursive_absolute(directory)
	await RenderingServer.frame_post_draw
	var frame := root.get_texture().get_image()
	if not _check(frame.get_size() == Vector2i(640, 360), "gallery viewport size"):
		return
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var filename := "rpg-2-star-ocean-the-second_character-source-gallery_in-engine-%s_m8-v01_%s-%08x.png" % [label, stamp, randi()]
	if _check(frame.save_png(directory.path_join(filename)) == OK, "save sample " + label):
		captures.append(filename)


func _run() -> void:
	change_scene_to_file(GALLERY_SCENE)
	await _settle()
	var gallery: Control = current_scene
	var entries: Array = gallery.get("entries")
	if not _check(entries.size() == 52, "52 source visual variants"):
		return
	var approved := 0
	var concept := 0
	var approved_index := -1
	for index in entries.size():
		var entry: Dictionary = entries[index]
		var approval := String(entry["source_portrait"]["approval"])
		if approval == "approved":
			approved += 1
			if approved_index == -1:
				approved_index = index
		elif approval == "concept":
			concept += 1
		else:
			if not _check(false, "unknown approval for " + String(entry["visual_id"])):
				return
		if not _check(gallery.show_index(index), "image loads " + String(entry["visual_id"])):
			return
		await process_frame
		var portrait: TextureRect = gallery.get("portrait")
		if not _check(portrait.is_visible_in_tree() and portrait.texture != null, "visible portrait " + String(entry["visual_id"])):
			return
		var image := portrait.texture.get_image()
		if not _check(not image.is_empty() and image.get_used_rect().has_area() and image.get_size() == gallery.get("current_image_size"), "drawable pixels " + String(entry["visual_id"])):
			return
		if not _check(portrait.get_rect().size == Vector2(608, 238), "single image viewport geometry"):
			return
		var status: Label = gallery.get("status_label")
		if not _check(status.text.contains("APPROVED") == (approval == "approved"), "approval label " + String(entry["visual_id"])):
			return
	if not _check(approved == 9 and concept == 43 and approved_index >= 0, "approved/concept totals 9/43"):
		return
	if not _check(String(gallery.get("source_label").text).contains("精灵未因此验收"), "source-only review disclaimer"):
		return
	gallery.show_index(0)
	gallery.get_node("NextButton").pressed.emit()
	if not _check(gallery.get("current_index") == 1, "next button navigates"):
		return
	gallery.get_node("PreviousButton").pressed.emit()
	if not _check(gallery.get("current_index") == 0, "previous button navigates"):
		return
	for sample in [{"index": 0, "label": "protagonist-concept"},
			{"index": approved_index, "label": "approved-source"},
			{"index": 51, "label": "final-companion-concept"}]:
		if not _check(gallery.show_index(int(sample["index"])), "sample selection"):
			return
		await _settle()
		await _capture(String(sample["label"]))
	var directory := OS.get_environment("WB_GALLERY_EVIDENCE_DIR")
	if not directory.is_empty() and captures.size() == 3:
		var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
		var filename := "rpg-2-star-ocean-the-second_character-source-gallery_visual-check-manifest_m8-v01_%s-%08x.json" % [stamp, randi()]
		var record := {"status": "source_portrait_review_only", "visual_variants": 52,
			"approved_source_portraits": 9, "concept_source_portraits": 43,
			"runtime_sprites_accepted_by_this_test": 0, "captures": captures}
		var file := FileAccess.open(directory.path_join(filename), FileAccess.WRITE)
		if _check(file != null, "open gallery manifest"):
			file.store_string(JSON.stringify(record, "\t") + "\n")
			file.close()
	print("CHARACTER_GALLERY_CHECK_OK entries=52 approved=9 concept=43 captures=%d" % captures.size())
	quit(0)
