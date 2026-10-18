extends "res://../tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-texture-override-capture-and-check_test-only-v06_20261018-084726-c8f0d900.gd"

# Reuse the exact v06 interaction/collision/occlusion protocol instead of copying its 400-line runner.
# Its YK1_V06_* diagnostics name the inherited protocol, not the tested asset version. V07_INJECTED and pixels bind v07.
# Args: absolute capture directory, unique capture stamp, absolute final v07 manifest.
func _override_with_v06(manifest_path: String) -> bool:
 if ResourceLoader.has_cached(V03_RES["plate"]):return false
 var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
 var repo:=ProjectSettings.globalize_path("res://..").simplify_path()
 var exports: Dictionary=manifest.runtime_exports
 var files: Dictionary={"plate":exports.plate.file,"foreground":exports.foreground.file}
 for index in 3:
  files[["antenna-a-lattice-yagi","antenna-b-dish","antenna-c-guyed-whip"][index]]=exports.antennas[index].runtime_png.file
 for key in V03_RES:
  var image:=Image.load_from_file(repo.path_join(files[key]))
  if image==null:return false
  var texture:=ImageTexture.create_from_image(image)
  texture.take_over_path(V03_RES[key]);v06_textures[key]=texture
  if key=="plate":v06_plate_image=image
 print("YK1_V07_INJECTED manifest="+manifest_path+" (v06 check protocol, v07 candidate pixels)")
 return true


func _shot(language: String, at: Vector2, label: String) -> bool:
 app.language=language;_place(at);host._refresh_text()
 var image: Image=await _grab()
 if image.get_size()!=Vector2i(640,360):return false
 var file:=folder.path_join("rpg-2-star-ocean-the-second_yonkers-antenna-room1_v07-test-only-godot-%s-%s-640x360_%s.png" % [language,label,stamp])
 if image.save_png(file)!=OK:return false
 print("YK1_V07_CAPTURE "+file+" at="+str(at))
 return true
