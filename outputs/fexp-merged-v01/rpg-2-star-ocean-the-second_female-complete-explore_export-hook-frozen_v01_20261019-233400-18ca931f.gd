@tool
extends EditorExportPlugin
var counts := {"png":0,"gd":0,"wav":0}
func _get_name() -> String:
    return "worlds-between-exact-raw-input-export"
func _add_original(path: String) -> void:
    var bytes := FileAccess.get_file_as_bytes(path)
    if bytes.is_empty():
        push_error("raw export input empty: " + path)
        return
    add_file(path, bytes, false)
    counts[path.get_extension()] += 1
func _add_scripts(directory: String) -> void:
    for file in DirAccess.get_files_at(directory):
        if file.ends_with(".gd"):
            _add_original(directory.path_join(file))
    for child in DirAccess.get_directories_at(directory):
        _add_scripts(directory.path_join(child))
func _export_begin(_features: PackedStringArray, _is_debug: bool, _path: String, _flags: int) -> void:
    counts = {"png":0,"gd":0,"wav":0}
    _add_scripts("res://scripts")
func _export_file(path: String, _type: String, _features: PackedStringArray) -> void:
    if path.ends_with(".png") or path.ends_with(".wav"):
        _add_original(path)
func _export_end() -> void:
    print("RAW_INPUT_EXPORT_FILE_COUNTS "+JSON.stringify(counts))
