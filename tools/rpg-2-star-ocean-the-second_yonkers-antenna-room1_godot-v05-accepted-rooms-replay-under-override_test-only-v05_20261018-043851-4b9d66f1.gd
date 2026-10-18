extends "res://../tools/rpg-2-star-ocean-the-second_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd"

# Yonkers antenna corridor room 1 v05 (UNAPPROVED, TEST-ONLY): the existing accepted-rooms replay (NYC room 1, NYC room 2,
# Yonkers room 2, exactly as their acceptance harnesses captured them) run with the v05 room-1 textures already taking
# over the v03 res:// paths in memory, the same way the v05 capture harness does. The three accepted rooms must still
# render byte-identically to their acceptance captures, i.e. the v05 override cannot leak outside room 1.
# Pixel comparison is done by the v05 capture pixel check. Nothing in the project is written.
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id> <absolute v05 nonruntime-exports dir>
const V05_HARNESS := preload("res://../tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v05-texture-override-capture-and-check_test-only-v05_20261018-043851-4b9d66f1.gd")

var v05_textures: Array[ImageTexture] = []


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3 or ResourceLoader.has_cached(V05_HARNESS.V03_RES["plate"]):
		_fail("v05 override not installed (third argument: absolute v05 nonruntime-exports dir)")
		return
	for key in V05_HARNESS.V03_RES:
		var image := Image.load_from_file(String(args[2]).path_join(V05_HARNESS.V05_FILES[key]))
		if image == null or image.is_empty():
			_fail("cannot load v05 export " + key)
			return
		var texture := ImageTexture.create_from_image(image)
		texture.take_over_path(V05_HARNESS.V03_RES[key])
		v05_textures.append(texture)
	print("ACCEPTED_REPLAY_V05_OVERRIDE in-memory textures=%d" % v05_textures.size())
	super._initialize()
