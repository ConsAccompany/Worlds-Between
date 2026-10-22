extends "res://../tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v13-texture-override-harness_test-only-unapproved-v13_20261018-100938-075675cf.gd"
# Reuse existing real held-input/records/battle/result loop. Only the new flag/asset contract changes.
var checks := 0
var control := false
var router_path := ""
var package: Dictionary = {}
const NEW_FMT := "rpg-2-star-ocean-the-second_wdc-capitol-west_%s_style45-%s_20261022-182109-a780b895"
func _initialize() -> void:
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--style45-contract="):contract=JSON.parse_string(FileAccess.get_file_as_string(a.trim_prefix("--style45-contract=")))
  elif a.begins_with("--style45-package="):package=JSON.parse_string(FileAccess.get_file_as_string(a.trim_prefix("--style45-package=")))
  elif a.begins_with("--style45-out="):out_dir=a.trim_prefix("--style45-out=");cap_dir=out_dir
  elif a.begins_with("--style45-router="):router_path=a.trim_prefix("--style45-router=")
  elif a=="--style45-control":control=true
 tag="control" if control else "flag"
 DirAccess.make_dir_recursive_absolute(out_dir)
 call_deferred("_run")
func ck(v: bool,label: String) -> void:
 checks+=1
 if not v:push_error("STYLE45_RUNTIME_FAIL "+label)
func _run() -> void:
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.content_scale_size=Vector2i(640,360)
 root.size=Vector2i(640,360)
 Engine.max_fps=60
 ck(not contract.is_empty() and out_dir!="" and router_path!="","required arguments")
 report["saves"]["real_before"]=_tree_hashes(REAL_SAVES)
 SaveStore.root_path="user://test-saves/style45"
 app=root.get_node("AppState")
 v12=load(V12_SELECTOR);r1=load(R1_SELECTOR);r2=load(R2_SELECTOR)
 if control:
  for destination in ["scifi.city","scifi.outskirts","scifi.ruins"]:
   var a: Dictionary=await _probe(destination,"")
   var b: Dictionary=await _probe(destination,"res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd")
   ck(a["entry"]==b["entry"],"off-flag exact entry "+destination)
   ck(a["after"]==b["after"] and a["positions"]==b["positions"],"off-flag exact movement+render "+destination)
   ck(a["v12_active"]==b["v12_active"],"off-flag same art activity "+destination)
 else:
  ck(OS.get_cmdline_user_args().has("--wdc-common-style45"),"actual opt-in flag present")
  for lang in ["zh","en"]:
   await _language_run(lang)
   validate_run(lang)
 report["saves"]["real_after"]=_tree_hashes(REAL_SAVES)
 ck(report["saves"]["real_before"]==report["saves"]["real_after"],"real user saves unchanged")
 ck(report["errors"].is_empty(),"inherited walk/encounter/capture errors absent")
 report["checks"]=checks
 report["declaredFixture"]="fresh run, explicit opt-in, defined pose placements, real held route, sentry HP lowered to12 and real auto-toggle/result input; not ordinary default or human timed play"
 var f=FileAccess.open(out_dir.path_join(NEW_FMT%["runtime-result",tag]+".json"),FileAccess.WRITE)
 f.store_string(JSON.stringify(report,"  ")+"\n")
 print("STYLE45_RUNTIME_OK mode=",tag," checks=",checks)
 quit()
func _language_run(lang: String) -> void:
 await super(lang)
 var checkpoint=FileAccess.open(out_dir.path_join("rpg-2-star-ocean-the-second_wdc-style45_"+lang+"-checkpoint_v01_20261022-182109-a780b895.json"),FileAccess.WRITE)
 checkpoint.store_string(JSON.stringify({"scene":current_scene.scene_file_path,"run":report["runs"].get(lang,{}),"r2":current_scene.get("r2_active")},"  ")+"\n")
 var run: Dictionary=report["runs"][lang]
 if run.has("traversal"):
  var before: String=run["traversal"]["file"]
  var after: String=NEW_FMT%["rt640-"+lang+"-traversal",tag]+".png"
  ck(DirAccess.rename_absolute(cap_dir.path_join(before),cap_dir.path_join(after))==OK,"traversal capture named with actual run "+lang)
  run["traversal"]["file"]=after
func _capture(name: String,scene) -> Dictionary:
 var im:=root.get_texture().get_image()
 var file:=NEW_FMT%[name,tag]+".png"
 ck(im.get_size()==Vector2i(640,360),"native640x360 "+name)
 ck(im.save_png(cap_dir.path_join(file))==OK,"capture "+name)
 return {"file":file,"size":[640,360],"state":_state(scene),"base_layer":_base_layer(scene)}
func _base_layer(scene) -> Dictionary:
 var result: Dictionary=super(scene)
 var paths: Dictionary={}
 for purpose in ["rt-base","rt-fg","rt-walk","rt-ys-mast","rt-ys-tripod","rt-ys-beacon","rt-ys-elm"]:paths[purpose]=scene._v12_path(purpose)
 result["paths"]=paths
 result["actual_script"]=scene.get_script().resource_path
 result["walk_sha256"]=_sha(scene.v12_walk.get_data())
 return result
func validate_run(lang: String) -> void:
 var run: Dictionary=report["runs"][lang]
 ck(run["entry"]["base_layer"]["found"],"base loaded "+lang)
 ck(run["entry"]["base_layer"]["actual_script"]==router_path,"real shared-scene flag router "+lang)
 ck(run["entry"]["base_layer"]["image_sha256"]==package["expected_base_rgba_sha256"],"new pixels actually rendered "+lang)
 ck(run["traversal_walk"]["ok"],"held-input original walk route "+lang)
 ck(run["records_checked"]["state"]["records_checked"],"real records interaction "+lang)
 ck(run["approach"]["walk_ok"] and run["approach"]["scene_changed"],"held-input sentry encounter "+lang)
 ck(run["encounter"]["battle_won"] and run["encounter"]["auto_mode_by_input"],"real battle won with declared12HP fixture "+lang)
 ck(run.has("battle_return"),"actual result returns "+lang)
 if run.has("battle_return"):
  var ret: Dictionary=run["battle_return"]
  ck(ret["equals_return_texel"] and ret["camera_current"],"exact return position + current camera "+lang)
  ck(ret["base_layer"]["actual_script"]==router_path and ret["base_layer"]["image_sha256"]==package["expected_base_rgba_sha256"],"new scene remains on battle return "+lang)

# Current authored heroine results may hold the result button while the victory clip finishes.
# Complete that existing wait and any normal mandatory growth choice through actual UI input.
func _press_action(action: String) -> void:
 if action=="ui_accept" and current_scene.scene_file_path==BATTLE_PATH:
  var waited:=0
  while (current_scene.get("patrol_result_pending")==true or current_scene.get("heroine_result_pending")==true or current_scene.get("heroine_defeat_result_pending")==true) and waited<360:
   await process_frame
   waited+=1
  ck(waited<360,"authored result becomes ready without bypass")
  current_scene.result_button.grab_focus()
 await super(action)
 if action=="ui_accept":
  await _settle(10)
  if current_scene.scene_file_path=="res://scenes/growth_screen.tscn":
   var rounds:=0
   while app.has_pending_job_choice() and rounds<12:
    if current_scene.stay_button.disabled:
     for button in current_scene.member_buttons:
      if button.visible and not button.disabled and "!" in button.text:
       button.grab_focus()
       await super("ui_accept")
       break
    ck(not current_scene.stay_button.disabled,"normal stay-choice available")
    current_scene.stay_button.grab_focus()
    await super("ui_accept")
    rounds+=1
   ck(not app.has_pending_job_choice(),"normal required growth choices resolved")
   current_scene.back_button.grab_focus()
   await super("ui_accept")
   await _settle(10)
