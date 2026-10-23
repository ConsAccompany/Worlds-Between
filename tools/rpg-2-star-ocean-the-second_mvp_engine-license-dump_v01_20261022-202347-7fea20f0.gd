extends SceneTree
## Writes the engine's own embedded license/copyright data. No legal text is authored here.
## Usage: godot --headless --path <empty project> --script <this> -- <out_dir> <timestamp-id>

func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("LICENSE_DUMP_BAD_ARGS %s" % [args])
		quit(2)
		return
	var out_dir: String = args[0]
	var stamp: String = args[1]
	var methods := ["get_license_text", "get_license_info", "get_copyright_info"]
	for m in methods:
		if not Engine.has_method(m):
			push_error("LICENSE_DUMP_MISSING_METHOD %s" % m)
			quit(3)
			return
	var text: String = Engine.get_license_text()
	var info: Dictionary = Engine.get_license_info()
	var copyright: Array = Engine.get_copyright_info()
	if text.is_empty() or info.is_empty() or copyright.is_empty():
		push_error("LICENSE_DUMP_EMPTY")
		quit(4)
		return
	var version := Engine.get_version_info()
	var files := {
		"rpg-2-star-ocean-the-second_godot-4-7-2_engine-license-text_embedded_%s.txt" % stamp: text,
		"rpg-2-star-ocean-the-second_godot-4-7-2_thirdparty-license-info_embedded_%s.json" % stamp: JSON.stringify(info, "  ", true),
		"rpg-2-star-ocean-the-second_godot-4-7-2_copyright-info_embedded_%s.json" % stamp: JSON.stringify({"engineVersion": version, "copyrightInfo": copyright}, "  ", true),
	}
	for name in files:
		var f := FileAccess.open(out_dir.path_join(name), FileAccess.WRITE)
		if f == null:
			push_error("LICENSE_DUMP_WRITE_FAILED %s %d" % [name, FileAccess.get_open_error()])
			quit(5)
			return
		f.store_string(files[name])
		f.close()
	print("LICENSE_DUMP_OK %s" % JSON.stringify({"licenses": info.size(), "copyrightParts": copyright.size(), "textChars": text.length(), "version": version.get("string", "")}))
	quit(0)
