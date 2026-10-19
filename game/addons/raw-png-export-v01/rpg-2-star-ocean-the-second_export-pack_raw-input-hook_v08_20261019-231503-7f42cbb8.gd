@tool
extends EditorExportPlugin
var counts := {"png":0,"gd":0,"wav":0}
var added_paths := {}
const FEXP_RUNTIME := "res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_south-runtime_v01_20261019-184900-f2c0a7e1.json"
const FEXP_RUNTIME_SHA256 := "90fcf3ed873be0b67dec823cb09c596550db23553def89f6e899a4976a7a5da8"
func _get_name() -> String:
    return "worlds-between-exact-raw-input-export"
func _add_original(path: String) -> void:
    if added_paths.has(path):
        return
    var bytes := FileAccess.get_file_as_bytes(path)
    if bytes.is_empty():
        push_error("raw export input empty: " + path)
        return
    add_file(path, bytes, false)
    added_paths[path] = true
    counts[path.get_extension()] += 1
func _add_scripts(directory: String) -> void:
    for file in DirAccess.get_files_at(directory):
        if file.ends_with(".gd"):
            _add_original(directory.path_join(file))
    for child in DirAccess.get_directories_at(directory):
        _add_scripts(directory.path_join(child))
func _export_begin(_features: PackedStringArray, _is_debug: bool, _path: String, _flags: int) -> void:
    counts = {"png":0,"gd":0,"wav":0}
    added_paths = {}
    _add_scripts("res://scripts")
    _add_fexp_raw_parts()
func _export_file(path: String, _type: String, _features: PackedStringArray) -> void:
    if path.ends_with(".png") or path.ends_with(".wav"):
        _add_original(path)
func _export_end() -> void:
    print("RAW_INPUT_EXPORT_FILE_COUNTS "+JSON.stringify(counts))

# The 68 pinned SOUTH parts are deliberately under .gdignore; they never get import callbacks.
# Export their exact original bytes without changing import settings or runtime/default rendering.
func _add_fexp_raw_parts() -> void:
    if not FileAccess.file_exists(FEXP_RUNTIME) or FileAccess.get_sha256(FEXP_RUNTIME) != FEXP_RUNTIME_SHA256:
        push_error("raw export fexp runtime missing or unpinned")
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(FEXP_RUNTIME))
    if not parsed is Dictionary or not parsed.get("part_lists") is Array:
        push_error("raw export fexp part_lists invalid")
        return
    var paths := {}
    for pair in parsed.part_lists:
        if not pair is Array or pair.size() != 2 or not pair[0] is Array or not pair[1] is String:
            push_error("raw export fexp part tuple invalid")
            return
        var prefix: String = pair[1]
        if prefix not in ["res://assets/characters/run-v06-unapproved/", "res://assets/characters/run-v09-unapproved/", "res://assets/characters/run-v10-unapproved/"]:
            push_error("raw export fexp root invalid")
            return
        for part in pair[0]:
            if not part is Dictionary or not part.get("file") is String or not part.get("sha256") is String:
                push_error("raw export fexp part metadata invalid")
                return
            var file: String = part.file
            if file.is_empty() or file.get_file() != file or file.contains("\\") or file.contains(":") or file.contains("..") or not file.ends_with(".png"):
                push_error("raw export fexp part path invalid")
                return
            var path := prefix + file
            if paths.has(path) or not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != part.sha256:
                push_error("raw export fexp part missing, duplicate or hash mismatch: " + path)
                return
            if FileAccess.get_file_as_bytes(path).is_empty():
                push_error("raw export fexp part empty: " + path)
                return
            paths[path] = true
    if paths.size() != 68:
        push_error("raw export fexp exact part count invalid")
        return
    for path in paths:
        _add_original(path)
