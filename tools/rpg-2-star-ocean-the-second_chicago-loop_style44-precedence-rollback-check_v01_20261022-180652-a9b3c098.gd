extends SceneTree
const MAP := "res://scenes/scifi_world_map.tscn"
const POLICY := "res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd"
const V13 := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd"
var expected := ""
var report := ""
var count := 0
var host: Node
func _initialize() -> void: run.call_deferred()
func ck(ok: bool, label: String) -> void:
 count+=1
 if not ok:push_error("STYLE44_PRECEDENCE_FAIL "+label)
func frames(n: int) -> void:
 for i in n:await process_frame
func run() -> void:
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--expect-scene="):expected=a.substr(15)
  elif a.begins_with("--report="):report=a.substr(9)
 ck(not expected.is_empty(),"declared expected path")
 var policy=load(POLICY)
 ck(policy.CITY_V06_DEFAULT==false and policy.RUINS_V13_DEFAULT==false and policy.RECORDS_ROOM2_DEFAULT==false,"other three defaults untouched")
 ck(policy.preview_override.is_empty(),"no test policy overrides")
 ck(not load(V13).v13_enabled(),"Washington remains off without flag")
 var app=root.get_node("AppState")
 app.begin_new_run()
 app.hero_appearance="female"
 app.language="en"
 app.show_initial_guide=false
 change_scene_to_file(MAP)
 await frames(5)
 current_scene.select_place("earth.us.il.chicago")
 await frames(3)
 var before: int=app.calendar_minutes
 current_scene.depart_button.pressed.emit()
 await frames(10)
 host=current_scene
 ck(host.scene_file_path==expected,"actual selected scene is "+expected+"; got "+host.scene_file_path)
 ck(app.current_destination_id=="scifi.loop" and app.calendar_minutes>before,"normal existing flight and destination")
 ck(host.sprite_pilot!=null and host.hero.scale==Vector2(0.5,0.5),"authorized ordinary heroine still attached")
 ck(host.hero.position==host.SPAWN,"original spawn")
 ck(host.title_label.text=="Chicago · The Loop","existing localized UI")
 var selected=host.scene_file_path
 var game_script=host.get_script().resource_path
 host.back_button.pressed.emit()
 await frames(5)
 ck(current_scene.scene_file_path==MAP,"return to original world map")
 if report!="":
  var f=FileAccess.open(report,FileAccess.WRITE)
  f.store_string(JSON.stringify({"passed":true,"checks":count,"scene":selected,"script":game_script,"chicagoDefault":policy.CHICAGO_V05_DEFAULT,"userArgs":OS.get_cmdline_user_args(),"policyPreviewEmpty":policy.preview_override.is_empty()},"  ")+"\n")
 print("STYLE44_PRECEDENCE_OK checks=",count)
 quit()
