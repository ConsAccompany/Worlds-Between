extends "res://../tools/rpg-2-star-ocean-the-second_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd"

# WDC Capitol west v13 (UNAPPROVED, TEST-ONLY): the existing accepted-rooms replay (NYC room 1, NYC room 2, Yonkers
# room 2, exactly as their acceptance harnesses captured them) run with the v13 rt-base already taking over the v12
# rt-base res:// path in memory, the same way the v13 texture-override harness does. The three accepted rooms must
# still render byte-identically to their acceptance captures, i.e. the override cannot leak outside the Capitol
# west opt-in. Pixel comparison is done by the v13 author/check tool. Nothing in the project is written.
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id> <absolute v13 rt-base PNG>
const V12_BASE_RES := "res://assets/environments/candidates/wdc-cw-v12_20261017-235608-66d00477/rpg-2-star-ocean-the-second_wdc-capitol-west_rt-base_unapproved-v12_20261017-235608-66d00477.png"

var v13_texture: ImageTexture


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3 or ResourceLoader.has_cached(V12_BASE_RES):
		_fail("v13 override not installed (third argument: absolute v13 rt-base PNG)")
		return
	var image := Image.load_from_file(String(args[2]))
	if image == null or image.is_empty():
		_fail("cannot load the v13 rt-base")
		return
	v13_texture = ImageTexture.create_from_image(image)
	v13_texture.take_over_path(V12_BASE_RES)
	print("ACCEPTED_REPLAY_V13_OVERRIDE in-memory textures=1 cached=%s" % ResourceLoader.has_cached(V12_BASE_RES))
	super._initialize()
