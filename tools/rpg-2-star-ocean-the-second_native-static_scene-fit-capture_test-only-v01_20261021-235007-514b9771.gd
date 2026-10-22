extends SceneTree
# Generic source-fit render; no actor assignment, defaults, interaction or human-play credit.
func _initialize() -> void:
 call_deferred("run")
 create_timer(75).timeout.connect(func():push_error("STATIC_FIT_TIMEOUT");quit(2))
func quiet(node: Node) -> void:
 node.process_mode = Node.PROCESS_MODE_DISABLED
 if node is AudioStreamPlayer or node is AudioStreamPlayer2D or node is AudioStreamPlayer3D:
  node.stop()
  node.stream = null
 for child in node.get_children(): quiet(child)
func run() -> void:
 var args = OS.get_cmdline_user_args()
 if args.size()!=3: push_error("expected png_absolute outdir tag");quit(2);return
 var source = Image.load_from_file(args[0])
 if source==null or source.get_size()!=Vector2i(80,112): push_error("source80x112 missing");quit(2);return
 var texture = ImageTexture.create_from_image(source)
 var app = root.get_node("AppState")
 app.set_process(false)
 SaveStore.root_path = "user://test-saves/jiang37-source-fit"
 root.size = Vector2i(640,360)
 var files = []
 for destination in ["scifi.city","scifi.ruins"]:
  for language in ["en","zh"]:
   app.begin_new_run()
   app.hero_appearance="female"
   app.current_destination_id=destination
   app.language=language
   app.show_initial_guide=false
   app.run_active=false
   var host = load("res://scenes/scifi_exploration_area.tscn").instantiate()
   root.add_child(host)
   quiet(host)
   for tween in get_processed_tweens(): tween.kill()
   var candidate = Sprite2D.new()
   candidate.texture=texture
   candidate.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
   candidate.scale=Vector2(0.5,0.5)
   candidate.offset=Vector2(0,-46)
   candidate.position=Vector2(400,280)
   candidate.z_index=50
   host.add_child(candidate)
   var label=Label.new()
   label.text="JIANG LAN SOURCE FIT / TEST ONLY" if language=="en" else "蒋岚源帧适配 / 仅测试"
   label.position=Vector2(310,293)
   label.add_theme_font_size_override("font_size",10)
   label.z_index=51
   host.add_child(label)
   for i in 3: await process_frame
   await RenderingServer.frame_post_draw
   var png=root.get_texture().get_image()
   if png.get_size()!=Vector2i(640,360):push_error("wrong viewport size");quit(2);return
   var file="rpg-2-star-ocean-the-second_jiang-lan_source-fit-"+destination.replace("scifi.","")+"-"+language+"_test-only-640-v01_"+args[2]+".png"
   if png.save_png(args[1].path_join(file))!=OK:push_error("capture write failed");quit(2);return
   files.append({"file":file,"sha256":FileAccess.get_sha256(args[1].path_join(file)),"sourceSha256":FileAccess.get_sha256(args[0]),"destination":destination,"language":language,"candidatePosition":[400,280],"scale":0.5,"testOnly":true})
   quiet(host)
   host.free()
   await process_frame
 var report=FileAccess.open(args[1].path_join("rpg-2-star-ocean-the-second_jiang-lan_source-fit-manifest_test-only-v01_"+args[2]+".json"),FileAccess.WRITE)
 report.store_string(JSON.stringify({"captures":files,"runtimeAdopted":false,"artApproved":false,"inputKind":"direct deterministic source-fit overlay"},"  ")+"\n")
 report.close()
 print("JIANG37_SOURCE_FIT_PASS captures=",files.size())
 quit(0)
