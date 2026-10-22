extends "res://../tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v13-texture-override-harness_test-only-unapproved-v13_20261018-100938-075675cf.gd"
func _initialize() -> void:call_deferred("_run")
func ck(v: bool,label: String) -> void:
 if not v:push_error("STYLE47_PRECEDENCE_FAIL "+label)
func _run() -> void:
 var cfg:={}
 var out:=""
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--config="):cfg=JSON.parse_string(FileAccess.get_file_as_string(a.trim_prefix("--config=")))
  if a.begins_with("--out="):out=a.trim_prefix("--out=")
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.content_scale_size=Vector2i(640,360);root.size=Vector2i(640,360);Engine.max_fps=60
 SaveStore.root_path="user://test-saves/style47-precedence"
 app=root.get_node("AppState");v12=load(V12_SELECTOR);r1=load(R1_SELECTOR);r2=load(R2_SELECTOR)
 var v13=load("res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd")
 var mode: String=cfg["mode"]
 if mode=="rollback":v13.v13_override=0
 var baseline=JSON.parse_string(FileAccess.get_file_as_string(cfg["baseline"]))
 var result:={}
 for dest in ["scifi.city","scifi.outskirts"]:
  var run: Dictionary=await _probe(dest,"")
  ck(run["entry"]==baseline[dest]["entry"] and run["after"]==baseline[dest]["after"] and run["positions"]==baseline[dest]["positions"],"unaffected destination "+dest)
  result[dest]=run
 result["ruins"]=await _probe("scifi.ruins","")
 var layer: Dictionary=_base_layer(current_scene)
 if mode=="rollback":ck(not result["ruins"]["v12_active"],"explicit rollback reaches original placeholder")
 else:
  ck(layer["found"] and layer["image_sha256"]==cfg["expectedBase"],"explicit selected art bytes")
  ck(result["ruins"]["v12_active"],"selected art active")
 ck(current_scene.get_script().resource_path==cfg["router"],"real shared scene uses default router")
 result["mode"]=mode;result["base"]=layer
 var f=FileAccess.open(out,FileAccess.WRITE);f.store_string(JSON.stringify(result,"  ")+"\n")
 print("STYLE47_PRECEDENCE_OK ",mode)
 quit()
