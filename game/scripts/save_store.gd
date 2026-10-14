extends RefCounted
class_name SaveStore

const SCHEMA_VERSION := 1
const MAX_AUTOS := 5
const MANUAL_SLOTS := 3
static var root_path := "user://saves"


static func write_entry(kind: String, slot: int, snapshot: Dictionary) -> String:
	if kind != "auto" and (kind != "manual" or slot < 1 or slot > MANUAL_SLOTS):
		return ""
	if DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(root_path)) != OK:
		return ""
	var sequence := 1
	for previous in list_entries():
		sequence = maxi(sequence, int(previous.get("sequence", 0)) + 1)
	var id := ("auto-%08d.json" % sequence) if kind == "auto" else ("manual-%d-%08d.json" % [slot, sequence])
	var entry := {
		"schemaVersion": SCHEMA_VERSION,
		"id": id,
		"kind": kind,
		"slot": slot if kind == "manual" else 0,
		"sequence": sequence,
		"savedAt": Time.get_datetime_string_from_system(),
		"snapshot": snapshot,
	}
	var file := FileAccess.open(root_path.path_join(id), FileAccess.WRITE)
	if file == null:
		return ""
	file.store_string(JSON.stringify(entry))
	file.flush()
	file.close()
	var check := _read_file(id)
	if check.is_empty() or int(check.get("sequence", 0)) != sequence:
		return ""
	_prune(kind, slot)
	return id


static func list_entries() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var directory := DirAccess.open(root_path)
	if directory == null:
		return result
	for name in directory.get_files():
		if not (name.begins_with("auto-") or name.begins_with("manual-")) or not name.ends_with(".json"):
			continue
		var entry := _read_file(name)
		if not entry.is_empty() and entry.get("kind", "") in ["auto", "manual"]:
			result.append(entry)
	result.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return int(a.get("sequence", 0)) > int(b.get("sequence", 0)))
	return result


static func read_entry(id: String) -> Dictionary:
	for entry in list_entries():
		if entry.get("id", "") == id:
			return entry
	return {}


static func _read_file(id: String) -> Dictionary:
	var file := FileAccess.open(root_path.path_join(id), FileAccess.READ)
	if file == null:
		return {}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if typeof(parsed) != TYPE_DICTIONARY or parsed.get("id", "") != id or typeof(parsed.get("snapshot")) != TYPE_DICTIONARY:
		return {}
	return parsed


static func _prune(kind: String, slot: int) -> void:
	var retained := 0
	for entry in list_entries():
		if entry.get("kind", "") != kind or (kind == "manual" and int(entry.get("slot", 0)) != slot):
			continue
		retained += 1
		if retained > (MAX_AUTOS if kind == "auto" else 1):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(root_path.path_join(String(entry["id"]))))
