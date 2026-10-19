extends SceneTree
# Actual normal .tscn path under only themed music+navigation CLI flags.
const SCRIPTS := {"exploration":"res://scripts/scifi_exploration_area.gd","annex":"res://scripts/survey_annex.gd","map":"res://scripts/scifi_world_map.gd"}
const SCENES := {"exploration":"res://scenes/scifi_exploration_area.tscn","annex":"res://scenes/survey_annex.tscn","map":"res://scenes/scifi_world_map.tscn"}
var rows:=[]
func _initialize() -> void:call_deferred("run")
func all_nodes(node: Node) -> Array:
 var out:=[]
 for child in node.get_children():out.append(child);out.append_array(all_nodes(child))
 return out
func sha(data: PackedByteArray) -> String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(data);return h.finish().hex_encode()
func run() -> void:
 var args:=OS.get_cmdline_user_args();var folder:=args[0];var report_path:=args[1]
 assert(args.has("--themed-music-pilot") and args.has("--navigation-ui-skin-pilot"))
 var app: Node=root.get_node("AppState");assert(app.settings.load_status=="missing");SaveStore.root_path="user://test-saves/nav-normal-scenes";app.begin_new_run();root.size=Vector2i(640,360)
 var stamp:=Time.get_datetime_string_from_system(true).replace("-","").replace(":","").replace("T","-")+"-7d2c965e"
 for language in ["en","zh"]:
  for kind in SCENES:
   app.language=language;app.current_destination_id="scifi.city";app.current_annex_room=1;app.show_initial_guide=false;app.returning_from_battle=false;app.resume_area_pending=false;app.resume_annex_pending=false
   var script=load(SCRIPTS[kind]);assert(script.navigation_ui_skin_override==-1)
   var node: Node=load(SCENES[kind]).instantiate();root.add_child(node)
   for i in 6:await process_frame
   await RenderingServer.frame_post_draw
   var plates:=all_nodes(node).filter(func(n):return String(n.name).begins_with("NavigationUiSkinPilotPlate"))
   var players:=all_nodes(node).filter(func(n):return n is AudioStreamPlayer or n is AudioStreamPlayer2D or n is AudioStreamPlayer3D)
   var music:={}
   for player in players:
    if player.stream is AudioStreamWAV and player.stream.loop_mode==AudioStreamWAV.LOOP_FORWARD:music={"pcmSha256":sha(player.stream.data),"playing":player.playing,"rate":player.stream.mix_rate,"loopEnd":player.stream.loop_end}
   var selector=load("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd");var expected: AudioStreamWAV=selector.select("city",1)
   var image:=root.get_texture().get_image();var file:="rpg-2-star-ocean-the-second_navigation-ui_normal-combined-%s-%s-640_pilot-unapproved-v01_%s.png"%[kind,language,stamp]
   var saved: bool=image.save_png(folder.path_join(file))==OK
   var back_rect:=Rect2(node.back_button.position,node.back_button.size) if kind!="map" else Rect2()
   rows.append({"kind":kind,"language":language,"normalScene":SCENES[kind],"navOverride":script.navigation_ui_skin_override,"helperApplied":node.navigation_ui_skin!=null and node.navigation_ui_skin.applied,"plateCount":plates.size(),"expectedPlateCount":5 if kind=="map" else 3,"playerCount":players.size(),"expectedPlayerCount":0 if kind=="map" else 2,"selectedMusicCorrect":music.is_empty() if kind=="map" else (music.get("pcmSha256","")==sha(expected.data) and music.get("playing",false)),"music":music,"native640":image.get_size()==Vector2i(640,360),"captureSaved":saved,"file":file,"pngSha256":FileAccess.get_sha256(folder.path_join(file)),"backRect":var_to_str(back_rect)})
   detach_audio(node)
   root.remove_child(node);node.free();await process_frame
 var failures:=rows.filter(func(r):return not(r.helperApplied and r.navOverride==-1 and r.plateCount==r.expectedPlateCount and r.playerCount==r.expectedPlayerCount and r.selectedMusicCorrect and r.native640 and r.captureSaved))
 var hashes:={}
 for path in SCRIPTS.values():hashes[path]=FileAccess.get_sha256(path)
 var report:={"extraUnscored":true,"flags":args,"sourceRawSha256":hashes,"cases":rows,"failed":failures.size(),"scriptRawSha256":FileAccess.get_sha256(get_script().resource_path),"artApproved":false}
 var f:=FileAccess.open(report_path,FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close()
 print("NAV_NORMAL_COMBINED cases=",rows.size()," failed=",failures.size())
 for row in failures:print(JSON.stringify(row))
 call_deferred("finish",failures.is_empty())

func detach_audio(node: Node) -> void:
 for child in node.get_children():
  if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:child.stop();child.stream=null
  detach_audio(child)
func finish(passed: bool) -> void:
 var previous_age:=AudioServer.get_time_since_last_mix()
 var mixes:=0
 var deadline:=Time.get_ticks_usec()+300000
 while mixes<2 and Time.get_ticks_usec()<deadline:
  await process_frame
  var age:=AudioServer.get_time_since_last_mix()
  if age<previous_age:mixes+=1
  previous_age=age
 print("AUDIO_CLEANUP_MIX_BOUNDARIES ",mixes)
 quit(0 if passed and mixes==2 else 1)
