extends SceneTree
# Independent UNSCORED probe. Compare actual Callable objects on the SAME original
# Button instances; target/method/bound argument summaries are reporting only.
const HELPER := preload("res://scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd")
const SKIN_DIR := "res://assets/ui/battle-skin-v01"
const SCRIPTS := {"exploration":"res://scripts/scifi_exploration_area.gd","annex":"res://scripts/survey_annex.gd","map":"res://scripts/scifi_world_map.gd"}
const SCENES := {"exploration":"res://scenes/scifi_exploration_area.tscn","annex":"res://scenes/survey_annex.tscn","map":"res://scenes/scifi_world_map.tscn"}
var app: Node
var rows:=[]
func _initialize() -> void:call_deferred("run")
func settle() -> void:
 for i in 4:await process_frame
 await RenderingServer.frame_post_draw
func nodes(node: Node) -> Array:
 var out:=[]
 for child in node.get_children():
  if String(child.name).begins_with("NavigationUiSkinPilotPlate"):continue
  out.append(child);out.append_array(nodes(child))
 return out
func callback_snapshot(node: Node) -> Dictionary:
 var out:={}
 for item in nodes(node):
  if not item is Button:continue
  var signals:={}
  for signal_info in item.get_signal_list():
   var connections:=[]
   for connection in item.get_signal_connection_list(signal_info.name):connections.append([connection.callable,connection.flags])
   if not connections.is_empty():signals[String(signal_info.name)]=connections
  out[item.get_instance_id()]=signals
 return out
func callback_summary(snapshot: Dictionary) -> Dictionary:
 var out:={}
 for instance_id in snapshot:
  var signals:={}
  for signal_name in snapshot[instance_id]:
   var summaries:=[]
   for row: Array in snapshot[instance_id][signal_name]:
    var c: Callable=row[0]
    summaries.append({"targetId":c.get_object_id(),"method":String(c.get_method()),"boundArgs":var_to_str(c.get_bound_arguments()),"unboundCount":c.get_unbound_arguments_count(),"flags":row[1]})
   signals[signal_name]=summaries
  out[str(instance_id)]=signals
 return out
func control_snapshot(node: Node) -> Array:
 var out:=[]
 for item in nodes(node):
  if not item is Control:continue
  var row: Array=[item.get_instance_id(),item.get_global_rect(),item.get_combined_minimum_size(),item.visible,item.focus_mode,item.mouse_filter,item.get_theme_font("font"),item.get_theme_font_size("font_size")]
  if item.get("text")!=null:row.append(item.text)
  if item is BaseButton:row.append(item.disabled)
  out.append(row)
 return out
func bytes_sha(data: PackedByteArray) -> String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(data);return h.finish().hex_encode()
func audio_snapshot(node: Node) -> Dictionary:
 var out:={}
 for item in nodes(node):
  if not(item is AudioStreamPlayer or item is AudioStreamPlayer2D or item is AudioStreamPlayer3D):continue
  var entry: Dictionary={"id":item.get_instance_id(),"streamId":item.stream.get_instance_id() if item.stream!=null else 0,"bus":item.bus,"volumeDb":item.volume_db}
  if item.stream is AudioStreamWAV:
   var wav: AudioStreamWAV=item.stream
   entry.merge({"pcmSha256":bytes_sha(wav.data),"rate":wav.mix_rate,"format":wav.format,"stereo":wav.stereo,"loopMode":wav.loop_mode,"loopBegin":wav.loop_begin,"loopEnd":wav.loop_end})
   if wav.loop_mode==AudioStreamWAV.LOOP_FORWARD:entry["loopPlaying"]=item.playing
  out[str(item.get_instance_id())]=entry
 return out
func selected_music_matches(node: Node,kind: String) -> bool:
 var local:=audio_snapshot(node)
 if kind=="map":return local.is_empty()
 if local.size()!=2:return false
 var selector=load("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd")
 var expected: AudioStreamWAV=selector.select("city",1)
 if expected==null:return false
 var count:=0
 for entry in local.values():
  if entry.get("loopMode",-1)==AudioStreamWAV.LOOP_FORWARD and entry.get("pcmSha256","")==bytes_sha(expected.data):count+=1
 return count==1
func open_context(node: Node,context: String) -> void:
 match context:
  "explore":node._open_dialogue()
  "annex":app.survey_clues[node._clue_key(0)]=true;node._inspect_clue(0)
  "field":node._open_field_log()
  "company":node.open_commerce()
  "credits":node.open_map_credits()
  "route":
   var here: String=node.route_adapter.current_place_id()
   for place in node.places:
    if String(place.id)!=here:node.select_place(String(place.id));break
func run() -> void:
 app=root.get_node("AppState")
 assert(app.settings.load_status=="missing")
 SaveStore.root_path="user://test-saves/nav-exact-callbacks"
 app.begin_new_run()
 root.size=Vector2i(640,360)
 for language in ["en","zh"]:
  for context in ["explore","annex","map","field","company","credits","route"]:
   var kind: String="exploration" if context=="explore" else ("annex" if context=="annex" else "map")
   app.language=language;app.current_destination_id="scifi.city";app.current_annex_room=1;app.show_initial_guide=false;app.returning_from_battle=false;app.resume_area_pending=false;app.resume_annex_pending=false
   load(SCRIPTS[kind]).navigation_ui_skin_override=0
   var node: Node=load(SCENES[kind]).instantiate();root.add_child(node)
   await settle();open_context(node,context);await settle()
   var before_calls:=callback_snapshot(node);var before_controls:=control_snapshot(node)
   var before_audio:=audio_snapshot(root)
   var correct_music:=selected_music_matches(node,kind)
   var helper=HELPER.new(SKIN_DIR);var applied: bool=helper.apply(node)
   await settle()
   var after_calls:=callback_snapshot(node);var after_controls:=control_snapshot(node)
   var after_audio:=audio_snapshot(root)
   helper.revert();await settle()
   var reverted_calls:=callback_snapshot(node);var reverted_controls:=control_snapshot(node)
   var reverted_audio:=audio_snapshot(root)
   rows.append({"language":language,"context":context,"applied":applied,"error":helper.last_error,"originalButtonCount":before_calls.size(),"correctSelectedMusicAndPlayerCount":correct_music,"audioUnchangedAfterApply":before_audio==after_audio,"audioUnchangedAfterRevert":before_audio==reverted_audio,"audioBefore":before_audio,"audioAfter":after_audio,"audioReverted":reverted_audio,"exactCallableObjectsAfterApply":before_calls==after_calls,"exactCallableObjectsAfterRevert":before_calls==reverted_calls,"originalControlsAfterApply":before_controls==after_controls,"originalControlsAfterRevert":before_controls==reverted_controls,"before":callback_summary(before_calls),"after":callback_summary(after_calls),"reverted":callback_summary(reverted_calls)})
   detach_audio(node)
   root.remove_child(node);node.free();await process_frame
 var failures:=rows.filter(func(r):return not(r.applied and r.exactCallableObjectsAfterApply and r.exactCallableObjectsAfterRevert and r.originalControlsAfterApply and r.originalControlsAfterRevert and r.correctSelectedMusicAndPlayerCount and r.audioUnchangedAfterApply and r.audioUnchangedAfterRevert))
 for kind in SCRIPTS:load(SCRIPTS[kind]).navigation_ui_skin_override=-1
 var source_hashes:={}
 for path in SCRIPTS.values():source_hashes[path]=FileAccess.get_sha256(path)
 source_hashes["helper"]=FileAccess.get_sha256("res://scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd")
 var report:={"extraUnscored":true,"method":"Same original Button instances; direct equality of actual Callable objects+flags, not connection counts or string signatures. All original Controls include hidden ones. Map native frame/route dressing intentionally untouched.","cases":rows,"failed":failures.size(),"sourceRawSha256":source_hashes,"scriptRawSha256":FileAccess.get_sha256(get_script().resource_path)}
 var f:=FileAccess.open(OS.get_cmdline_user_args()[0],FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close()
 print("NAV_EXACT_CALLBACKS cases=",rows.size()," failed=",failures.size())
 for row in failures:print("NAV_EXACT_CALLBACK_FAILURE ",row.language,"/",row.context," applied=",row.applied," ",row.error)
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
