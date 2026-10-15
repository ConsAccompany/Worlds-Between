extends SceneTree

# Export data inclusion smoke for the M2 global Earth map and travel calendar.
# Source mode checks that the Windows Desktop preset in export_presets.cfg would pack every
# JSON file the map, route core and calendar read at run time. Pack mode runs inside an
# exported .pck with no project folder on disk and checks that those files load from the pack.
# Source mode, from the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_20261015-033441-6e5c07b5.gd
# Pack mode, after `--export-pack "Windows Desktop" <dir>/game.pck`, run from <dir> without --path:
#   <godot> --headless --main-pack game.pck \
#     --script res://tests/rpg-2-star-ocean-the-second_global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_20261015-033441-6e5c07b5.gd -- --pack-mode

const MapData := preload("res://scripts/world_map_data.gd")
const RouteRegistry := preload("res://scripts/world_route_registry.gd")
const Calendar := preload("res://scripts/travel_calendar.gd")
const PRESETS_PATH := "res://export_presets.cfg"
const PRESET_NAME := "Windows Desktop"

var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var pack_mode := OS.get_cmdline_user_args().has("--pack-mode")
	var ok := _pack_checks() if pack_mode else _source_checks()
	if not ok:
		return
	if not _load_checks():
		return
	print("EXPORT_DATA_INCLUSION_SMOKE_OK mode=%s checks=%d" % ["pack" if pack_mode else "source", checks])
	quit(0)


# Every JSON path read by the map (display registry, geodata) and by the route core, which
# also supplies the calendar start. Taken from the scripts so a renamed file is caught.
func _data_paths() -> Array:
	return [RouteRegistry.DEFAULT_DATA_PATH, MapData.REGISTRY_PATH, MapData.GEODATA_PATH]


func _source_checks() -> bool:
	var config := ConfigFile.new()
	if not _check(config.load(PRESETS_PATH) == OK, "export_presets.cfg loads"):
		return false
	var section := ""
	for candidate in config.get_sections():
		if candidate.begins_with("preset.") and candidate.count(".") == 1 and config.get_value(candidate, "name", "") == PRESET_NAME:
			section = candidate
	if not _check(section != "", "preset named %s exists" % PRESET_NAME):
		return false
	if not _check(config.get_value(section, "platform", "") == "Windows Desktop", "preset targets Windows Desktop"):
		return false
	var export_filter := String(config.get_value(section, "export_filter", ""))
	var include_filters := _filters(config.get_value(section, "include_filter", ""))
	var exclude_filters := _filters(config.get_value(section, "exclude_filter", ""))
	var json_is_resource := ResourceLoader.get_recognized_extensions_for_type("JSON").has("json")
	if not _check(json_is_resource, "Godot recognises .json as a resource type"):
		return false
	for path in _data_paths():
		var relative := String(path).trim_prefix("res://")
		if not _check(FileAccess.file_exists(path), "data file exists: " + relative):
			return false
		if not _check(_ignored_by_gdignore(relative) == "", "data file is not under a .gdignore folder: " + relative):
			return false
		var included := _matches_any(relative, include_filters) or (export_filter == "all_resources" and json_is_resource)
		if not _check(included, "preset packs " + relative):
			return false
		if not _check(not _matches_any(relative, exclude_filters), "preset does not exclude " + relative):
			return false
	return true


# Inside an exported pack: res:// must not resolve to a project folder on disk, so a passing
# read can only come from the .pck.
func _pack_checks() -> bool:
	var on_disk := ProjectSettings.globalize_path("res://project.godot")
	if not _check(not FileAccess.file_exists(on_disk), "no project.godot on disk at " + on_disk):
		return false
	if not _check(not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path("res://data")), "no data folder on disk next to the pack"):
		return false
	for path in _data_paths():
		if not _check(FileAccess.file_exists(path), "pack contains " + String(path).trim_prefix("res://")):
			return false
	return true


# Same loads the game makes: route core (with the calendar start), map registry and geodata.
func _load_checks() -> bool:
	for path in _data_paths():
		var text := FileAccess.get_file_as_string(path)
		if not _check(typeof(JSON.parse_string(text)) == TYPE_DICTIONARY, "parses as a JSON object: " + String(path).get_file()):
			return false
	var registry: WorldRouteRegistry = RouteRegistry.load_default()
	if not _check(registry.is_valid(), "route core data is valid: " + ", ".join(registry.errors)):
		return false
	if not _check(registry.location_order.size() > 0 and registry.locations.has(registry.start_location_id), "route core has locations and a start location"):
		return false
	if not _check(registry.calendar_start_minutes > 0 and Calendar.iso_text(registry.calendar_start_minutes).length() == 16, "calendar start reads from the travel data: " + Calendar.iso_text(registry.calendar_start_minutes)):
		return false
	if not _check(MapData.display_places().size() > 0 and MapData.geo_regions().size() > 0, "map display registry has places and regions"):
		return false
	if not _check(MapData.global_land_rings().size() > 0, "geodata has global land rings"):
		return false
	return true


func _filters(raw: Variant) -> PackedStringArray:
	var result: PackedStringArray = []
	for part in String(raw).split(",", false):
		if part.strip_edges() != "":
			result.append(part.strip_edges())
	return result


func _matches_any(relative: String, filters: PackedStringArray) -> bool:
	for pattern in filters:
		if relative.matchn(pattern) or relative.get_file().matchn(pattern):
			return true
	return false


# Godot skips any folder holding a .gdignore file when it scans or exports the project.
func _ignored_by_gdignore(relative: String) -> String:
	var dir := "res://"
	for part in relative.get_base_dir().split("/", false):
		dir = dir.path_join(part)
		if FileAccess.file_exists(dir.path_join(".gdignore")):
			return dir
	return ""


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if not condition:
		push_error("EXPORT_DATA_INCLUSION_SMOKE_FAIL " + label)
		quit(1)
		return false
	return true
