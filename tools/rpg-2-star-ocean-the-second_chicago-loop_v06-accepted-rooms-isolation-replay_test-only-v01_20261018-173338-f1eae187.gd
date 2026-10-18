extends "res://../tools/rpg-2-star-ocean-the-second_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd"
# Reuse the accepted rooms' existing capture/interactions contract with Chicago v06 textures installed in memory.
# No scene, selector or game source file is edited. All six replacements are confined to Chicago's v05 art paths.
const ChicagoCapture := preload("res://../tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-godot-texture-override-capture_nonruntime-v06_20261018-155129-19790a70.gd")
var chicago_textures: Array[ImageTexture] = []
func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3:
		_fail("third argument must be v06 source directory")
		return
	for layer in ChicagoCapture.LAYERS:
		var image := Image.load_from_file(String(args[2]).path_join(ChicagoCapture.V06_FILE % layer))
		if image == null or image.is_empty():
			_fail("cannot load Chicago v06 layer " + layer)
			return
		var texture := ImageTexture.create_from_image(image)
		texture.take_over_path(ChicagoCapture.V05_ART % layer)
		chicago_textures.append(texture)
	print("ACCEPTED_REPLAY_CHICAGO_V06_OVERRIDE textures=%d" % chicago_textures.size())
	super._initialize()
