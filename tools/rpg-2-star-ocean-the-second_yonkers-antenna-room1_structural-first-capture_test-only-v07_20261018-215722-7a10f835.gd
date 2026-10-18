extends SceneTree

# Bounded first visual review: actual normal survey scene, candidate textures injected only in memory.
const RESOURCES := {
 "plate":"res://assets/environments/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-plate_unapproved-v03_20261017-224447-15709be4.png",
 "foreground":"res://assets/environments/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_foreground-occluder_unapproved-v03_20261017-224447-15709be4.png",
 "antenna-a-lattice-yagi":"res://assets/props/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_antenna-a-lattice-yagi_unapproved-v03_20261017-224447-15709be4.png",
 "antenna-b-dish":"res://assets/props/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_antenna-b-dish_unapproved-v03_20261017-224447-15709be4.png",
 "antenna-c-guyed-whip":"res://assets/props/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_antenna-c-guyed-whip_unapproved-v03_20261017-224447-15709be4.png"
}
var textures := []


func _initialize() -> void:
 call_deferred("_run")


func _run() -> void:
 var args := OS.get_cmdline_user_args()
 if args.size() < 3:
  push_error("Need manifest path, output folder, stamp");quit(1);return
 var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
 var repo := ProjectSettings.globalize_path("res://..").simplify_path()
 var exports: Dictionary = manifest.runtime_exports
 var files: Dictionary = {"plate":exports.plate.file,"foreground":exports.foreground.file}
 for index in 3:
  files[["antenna-a-lattice-yagi","antenna-b-dish","antenna-c-guyed-whip"][index]]=exports.antennas[index].runtime_png.file
 for key in RESOURCES:
  if ResourceLoader.has_cached(RESOURCES[key]):
   push_error("Candidate source cached before injection: "+key);quit(1);return
  var image := Image.load_from_file(repo.path_join(files[key]))
  if image == null:
   push_error("Missing candidate PNG: "+files[key]);quit(1);return
  var texture := ImageTexture.create_from_image(image)
  texture.take_over_path(RESOURCES[key]);textures.append(texture)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.content_scale_size=Vector2i(640,360);root.size=Vector2i(640,360)
 var app := root.get_node("AppState")
 SaveStore.root_path="user://test-saves/yk1-v07-"+args[2]
 app.begin_new_run();app.hero_appearance="female";app.select_destination("scifi.outskirts");app.current_annex_room=1
 var scene: Node = load("res://scenes/survey_annex.tscn").instantiate()
 root.add_child(scene);current_scene=scene
 await process_frame
 scene.set_process(false)
 scene.hero.texture=load("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
 scene.hero.scale=Vector2(0.5,0.5);scene.hero.offset=Vector2(0,-40);scene.hero.position=Vector2(87,261)
 DirAccess.make_dir_recursive_absolute(args[1])
 for language in ["zh","en"]:
  app.language=language;scene._refresh_text()
  await process_frame
  await process_frame
  await RenderingServer.frame_post_draw
  var image := root.get_viewport().get_texture().get_image()
  if image.get_size()!=Vector2i(640,360):push_error("Not native640x360");quit(1);return
  var file := args[1].path_join("rpg-2-star-ocean-the-second_yonkers-antenna-room1_structural-godot-"+language+"-entry-ref48_unapproved-v07_"+args[2]+".png")
  if image.save_png(file)!=OK:push_error("Capture failed");quit(1);return
  print("YK1_V07_FIRST_CAPTURE "+file)
 scene.queue_free()
 await process_frame
 print("YK1_V07_FIRST_CAPTURE_OK 2; test-only, reference heroine, art unapproved")
 quit()
