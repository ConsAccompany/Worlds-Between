@tool
extends EditorPlugin
var raw_png_export
func _enter_tree() -> void:
    raw_png_export = preload("res://addons/raw-png-export-v01/rpg-2-star-ocean-the-second_export-pack_raw-input-hook_v08_20261019-231503-7f42cbb8.gd").new()
    add_export_plugin(raw_png_export)
func _exit_tree() -> void:
    remove_export_plugin(raw_png_export)
    raw_png_export = null
