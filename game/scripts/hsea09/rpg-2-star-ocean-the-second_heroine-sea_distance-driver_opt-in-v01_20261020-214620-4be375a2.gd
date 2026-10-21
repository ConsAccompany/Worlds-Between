extends Node

# Presentation-only opt-in. The host supplies actual post-collision movement through step().
# No clock process, position/speed/collision mutation, interpolation, default adoption or art approval.
const FLAG := "--heroine-sea-distance-pilot"
const MODEL_PATH := "res://scripts/rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_v01_20261020-174416-39e12f18.gd"
const TRANSITION_PATH := "res://data/hsea-gait11/rpg-2-star-ocean-the-second_heroine-sea_explore-stop-transition-manifest_unapproved-v06_20261020-175838-408e8b21.json"
const TRANSITION_SHA256 := "a05df1930f3423cbdbe9f822cfe01acfcac900bb413dbf6667033f4cb9739a94"
const SOURCE_SET_SHA256 := "8c5cca3c43ece810955573744b7586981fe86525025166c12eb12c4c3a1e50b5"
const PROVENANCE_PATH := "res://data/hsea-gait11/rpg-2-star-ocean-the-second_hero-female_exploration-source-package-provenance_v01_20261020-175959-4806a4f6.json"
const PROVENANCE_SHA256 := "52a61c70b9ca94b091fde76c60b7e0e184b4d014557afbe40c681c9b09513f45"
# Exact, coordinator-inspected package profiles. Never infer a bridge/provenance path from untrusted JSON.
const ADDITIONAL_SOURCE_PROFILES := {
 "3ccf615a536fef4938dafa869ea7f454860a3dca72fdb0c6c566e03f4fea3fa1": {"transition_path": "res://data/hsea-front17/rpg-2-star-ocean-the-second_heroine-sea_explore-stop-transition-manifest_unapproved-front17-v01_20261021-022403-cabad530.json", "transition_sha256": "90c76f29573b37151b4016899351124d4a5e636c19b1fda72c4047959f372172", "provenance_path": "res://data/hsea-front17/rpg-2-star-ocean-the-second_hero-female_exploration-source-package-provenance_v01_20261020-222654-045bcd59.json", "provenance_sha256": "73629644b4f63d3486d7b44012b378d4c9fda260f5b4714e8a8960a4ddae468e", "phase_aware_stop": true, "phase_directions": ["south", "west", "north", "east"], "source_set_sha256": "5a644d10a94f5a7a56084f7c914c23d135c443150986fb97486c8f01fa112b7c"},
 "2a0953d1cbfa9fdf9700abce4d7ee8c59c2eeb6b59b9e5764d64b7704583bb24": {"transition_path": "res://data/hsea-stop15/rpg-2-star-ocean-the-second_heroine-sea_explore-stop-transition-manifest_unapproved-stop15-v01_20261021-015000-f141d653.json", "transition_sha256": "1d8b5dbad470ce33508073517641eabc8663dc142a866d15aadfa0ac7b598657", "provenance_path": "res://data/hsea-stop15/rpg-2-star-ocean-the-second_hero-female_exploration-source-package-provenance_v01_20261020-215528-cf35a07b.json", "provenance_sha256": "76bcfce2e4abfc088e964ad23bc7a521ddc440252209a04a1dcef471fc3f556a", "phase_aware_stop": true, "source_set_sha256": "2311c4a5e904b2501fb2fd09c9d7bfc0fd416a7298ec81877cde9a2ae04550ba"},
 "b0c2b02764dcb19020a21bd2538633125e79a5399d521b33e6f2286671ce902e": {
  "transition_path": "res://data/hsea-arms12/rpg-2-star-ocean-the-second_heroine-sea_explore-stop-transition-manifest_unapproved-v08_20261020-222336-0ad0e3f5.json",
  "transition_sha256": "23905e6976028f9e01d2beab5bcaded2e6a2cc181a4b4bbdb8bd70c63db6dc64",
  "provenance_path": "res://data/hsea-arms12/rpg-2-star-ocean-the-second_hero-female_exploration-source-package-provenance_v01_20261020-182605-7f130933.json",
  "provenance_sha256": "1a307cc178c939437ed77a2f8e1cad78e10ceffd329088468a26ba7c991c3f3c"
 }
}

static func _profile_for_set(set_hash: String) -> Dictionary:
	if set_hash == SOURCE_SET_SHA256:
		return {"transition_path": TRANSITION_PATH, "transition_sha256": TRANSITION_SHA256,
			"provenance_path": PROVENANCE_PATH, "provenance_sha256": PROVENANCE_SHA256}
	return ADDITIONAL_SOURCE_PROFILES.get(set_hash, {}).duplicate(true)

static var enabled_override := -1
var sprite: Sprite2D
var sprite_set := {}
var actor_id := "protagonist-female"
var model: RefCounted
var action := "idle"
var facing := "south"
var frame := 0
var last_state := {}
var bridges := {}

static func enabled() -> bool:
	return enabled_override == 1 if enabled_override >= 0 else OS.get_cmdline_user_args().has(FLAG)

static func attach(target: Sprite2D, actor: String, initial_facing: String) -> Node:
	if not enabled() or target == null or actor != "protagonist-female" or initial_facing not in ["south","west","north","east"]:
		return null
	# Dynamic lookup avoids circular preloads with the unchanged generic validator.
	var loader = load("res://scripts/exploration_sprite_set_pilot.gd")
	var registry: Dictionary = loader.load_registry(loader.registry_path())
	if not registry.get("ok", false):
		return null
	var set_path: String = registry["actors"].get(actor, "")
	if set_path.is_empty():
		return null
	if not FileAccess.file_exists(set_path):
		return null
	var profile := _profile_for_set(FileAccess.get_sha256(set_path))
	if profile.is_empty() or not _source_bytes_match(set_path.get_base_dir(), profile):
		return null
	var result: Dictionary = loader.load_set(set_path, actor)
	if not result.get("ok", false):
		return null
	var candidate: Dictionary = result["set"]
	# This specific pilot requires the four new 12-phase clips; old packages fall back whole.
	if int(candidate["density"]) != 2 or candidate["frame_size"] != Vector2(80, 112) or candidate["pivot"] != Vector2(40, 104):
		return null
	for direction in ["south", "west", "north", "east"]:
		if candidate["clips"]["walk"][direction]["textures"].size() != 12:
			return null
	var bridge_set := _load_bridges(loader, profile, candidate)
	if bridge_set.is_empty():
		return null
	var script = load(MODEL_PATH)
	if script == null:
		return null
	var state_model = script.new()
	state_model.reset(initial_facing)
	var driver = new()
	driver.sprite = target
	driver.sprite_set = candidate
	driver.model = state_model
	driver.bridges = bridge_set
	driver.facing = initial_facing
	target.scale = Vector2(0.5, 0.5)
	target.offset = Vector2(0, -46)
	target.add_child(driver)
	driver._apply({"action": "idle", "frame": 0, "facing": initial_facing})
	return driver

static func _source_bytes_match(base: String, profile: Dictionary) -> bool:
	var provenance_path: String = profile["provenance_path"]
	if not FileAccess.file_exists(provenance_path) or FileAccess.get_sha256(provenance_path) != profile["provenance_sha256"]:
		return false
	var data = JSON.parse_string(FileAccess.get_file_as_string(provenance_path))
	if not data is Dictionary or not data.get("source_pngs") is Array or data["source_pngs"].size() != 52:
		return false
	var seen := {}
	for entry in data["source_pngs"]:
		if not entry is Dictionary or not entry.get("output_file") is String or not entry.get("sha256") is String:
			return false
		var path: String = entry["output_file"]
		if not path.begins_with("png/") or path.contains("..") or path.contains("\\") or path.substr(4).contains("/") or not path.ends_with(".png") or seen.has(path):
			return false
		seen[path] = true
		var file := base.path_join(path)
		if not FileAccess.file_exists(file) or FileAccess.get_sha256(file) != entry["sha256"]:
			return false
	return true

static func _load_bridges(loader, profile: Dictionary, candidate: Dictionary = {}) -> Dictionary:
	var transition_path: String = profile["transition_path"]
	# Fixed source-bound supplemental file. Refuse all before changing any target field.
	if not FileAccess.file_exists(transition_path) or FileAccess.get_sha256(transition_path) != profile["transition_sha256"]:
		return {}
	var data = JSON.parse_string(FileAccess.get_file_as_string(transition_path))
	if not data is Dictionary or data.get("schema") != "worlds-between.exploration-stop-transition.supplemental.v1":
		return {}
	if not data.get("directions") is Dictionary:
		return {}
	var result := {}
	for direction in ["south", "west", "north", "east"]:
		var by_direction = data["directions"].get(direction)
		if not by_direction is Dictionary:
			return {}
		result[direction] = {}
		for contact in [0,6]:
			var spec = by_direction.get("contact" + str(contact))
			if not spec is Dictionary or spec.get("from_walk_frame") != contact or not spec.get("bridge") is Array or spec["bridge"].size() != 2:
				return {}
			var frames := []
			for entry in spec["bridge"]:
				if not entry is Dictionary or not entry.get("file") is String or not entry.get("sha256") is String:
					return {}
				var name: String = entry["file"]
				if name.is_empty() or name.contains("/") or name.contains("\\") or name.contains("..") or not name.ends_with(".png"):
					return {}
				var file := transition_path.get_base_dir().path_join(name)
				if not FileAccess.file_exists(file) or FileAccess.get_sha256(file) != entry["sha256"]:
					return {}
				frames.append({"file": name, "duration_ms": 40})
			var errors: Array[String] = []
			var clip: Dictionary = loader._clip(frames, direction + " bridge", "walk", transition_path.get_base_dir(),2,Vector2i(80,112),Vector2i(40,104),errors)
			if not errors.is_empty():
				return {}
			result[direction][contact] = clip["textures"]
	if profile.get("phase_aware_stop", false):
		if data.get("source_set_sha256") != profile.get("source_set_sha256"):
			return {}
		var phases := _load_phase_bridges(loader, transition_path, data, candidate, profile.get("phase_directions", ["east", "west"]))
		if phases.is_empty():
			return {}
		result["phase_bridges"] = phases
	return result

static func _load_phase_bridges(loader, manifest_path: String, data: Dictionary, candidate: Dictionary, allowed_directions: Array = ["east", "west"]) -> Dictionary:
	var listed = data.get("phase_bridges")
	if not listed is Dictionary or listed.size() != allowed_directions.size() or not listed.has_all(allowed_directions) or candidate.is_empty():
		return {}
	var result := {}
	for direction in allowed_directions:
		var by_direction = listed[direction]
		if not by_direction is Dictionary or by_direction.size() != 12:
			return {}
		result[direction] = {}
		for phase in range(12):
			var spec = by_direction.get("phase" + str(phase))
			if not spec is Dictionary or spec.get("from_walk_frame") != phase or not spec.get("bridge") is Array or spec["bridge"].size() != 4:
				return {}
			var frames := []
			for index in range(4):
				var entry = spec["bridge"][index]
				if not entry is Dictionary or not entry.get("file") is String or not entry.get("sha256") is String:
					return {}
				var name: String = entry["file"]
				if name.is_empty() or name.contains("/") or name.contains("\\") or name.contains("..") or not name.ends_with(".png"):
					return {}
				var file := manifest_path.get_base_dir().path_join(name)
				if not FileAccess.file_exists(file) or FileAccess.get_sha256(file) != entry["sha256"]:
					return {}
				# Endpoint equality is checked against the already validated protected walk/idle source bytes.
				if index == 0 or index == 3:
					var action_name := "walk" if index == 0 else "idle"
					var endpoint := phase if index == 0 else 0
					var original: String = candidate["clips"][action_name][direction]["paths"][endpoint]
					if FileAccess.get_sha256(original) != entry["sha256"]:
						return {}
				frames.append({"file": name, "duration_ms": 40})
			var errors: Array[String] = []
			var clip: Dictionary = loader._clip(frames, direction + " phase stop " + str(phase), "walk", manifest_path.get_base_dir(), 2, Vector2i(80,112), Vector2i(40,104), errors)
			if not errors.is_empty():
				return {}
			result[direction][phase] = clip["textures"]
	return result

static func _phase_bridge_index(progress: float) -> int:
	# Inclusive 120ms settle remains model-owned: four samples over the existing window.
	# At 30fps the three settle ticks show release/near-rest/idle; 60fps also holds the entry pose.
	if progress < 0.25:
		return 0
	if progress < 0.5:
		return 1
	if progress < 0.8:
		return 2
	return 3

func face(_next_facing: String) -> void:
	pass

func walk() -> void:
	pass

func idle() -> void:
	pass

func step(delta: float, previous: Vector2, actual: Vector2, direction: String) -> void:
	var next: Dictionary = model.step(delta, previous, actual, direction)
	if next.get("refused", false) or next.get("ok", true) == false:
		return
	_apply(next)

func _apply(next: Dictionary) -> void:
	last_state = next.duplicate(true)
	action = str(next.get("action", "idle"))
	facing = str(next.get("facing", facing))
	frame = int(next.get("frame", 0))
	var clip_action := "idle" if action == "idle" else "walk"
	var clip: Dictionary = sprite_set["clips"][clip_action][facing]
	frame = clampi(frame, 0, clip["textures"].size() - 1)
	sprite.texture = clip["textures"][frame]
	if action == "settle" and bridges.has("phase_bridges") and bridges["phase_bridges"].has(facing):
		var outgoing: int = int(next.get("settle_entry_frame", -1))
		if outgoing >= 0 and outgoing < 12:
			var phase_sample := _phase_bridge_index(float(next.get("settle_progress", 0.0)))
			sprite.texture = bridges["phase_bridges"][facing][outgoing][phase_sample]
			last_state["bridge_frame"] = phase_sample
			last_state["bridge_phase"] = outgoing
			return
	# The last half of the existing <=120ms settling window uses two authored bridges.
	# No extra post-stop timer and no alpha interpolation. The phase model stays authoritative
	# for a same-facing re-press. This does not assert continuous pose/foot identity.
	if action == "settle" and float(next.get("settle_progress",0.0)) >= 0.5:
		var diagnostics: Dictionary = next.get("diagnostics",{})
		var contact: int = int(diagnostics.get("settle_target_frame",0))
		if contact == 0 or contact == 6:
			var bridge_index := 0 if float(next["settle_progress"]) < 0.8 else 1
			sprite.texture = bridges[facing][contact][bridge_index]
			last_state["bridge_frame"] = bridge_index
			last_state["bridge_contact"] = contact

func state() -> Dictionary:
	var result := last_state.duplicate(true)
	result.merge({"actor_id": actor_id, "set_id": sprite_set["set_id"], "action": action, "facing": facing, "frame": frame}, true)
	return result
