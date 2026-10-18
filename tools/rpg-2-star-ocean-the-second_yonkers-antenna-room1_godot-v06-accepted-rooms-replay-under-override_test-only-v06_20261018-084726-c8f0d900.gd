extends "res://../tools/rpg-2-star-ocean-the-second_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd"

# Yonkers antenna corridor room 1 v06 (UNAPPROVED, TEST-ONLY): the existing accepted-rooms replay (NYC room 1, NYC room 2,
# Yonkers room 2, exactly as their acceptance harnesses captured them) run with the v06 room-1 textures already taking
# over the v03 res:// paths in memory, the same way the v06 capture harness does. The three accepted rooms must still
# render byte-identically to their acceptance captures, i.e. the v06 override cannot leak outside room 1.
# Pixel comparison is done by the v06 capture pixel check. Nothing in the project is written.
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id> <absolute v06 nonruntime-exports dir>
const V06_HARNESS := preload("res://../tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-texture-override-capture-and-check_test-only-v06_20261018-084726-c8f0d900.gd")

var v06_textures: Array[ImageTexture] = []


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3 or ResourceLoader.has_cached(V06_HARNESS.V03_RES["plate"]):
		_fail("v06 override not installed (third argument: absolute v06 nonruntime-exports dir)")
		return
	for key in V06_HARNESS.V03_RES:
		var image := Image.load_from_file(String(args[2]).path_join(V06_HARNESS.V06_FILES[key]))
		if image == null or image.is_empty():
			_fail("cannot load v06 export " + key)
			return
		var texture := ImageTexture.create_from_image(image)
		texture.take_over_path(V06_HARNESS.V03_RES[key])
		v06_textures.append(texture)
	print("ACCEPTED_REPLAY_V06_OVERRIDE in-memory textures=%d" % v06_textures.size())
	super._initialize()
