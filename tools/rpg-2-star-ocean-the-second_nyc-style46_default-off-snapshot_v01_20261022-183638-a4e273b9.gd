extends "res://../tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v13-texture-override-harness_test-only-unapproved-v13_20261018-100938-075675cf.gd"
func _initialize() -> void:
 call_deferred("_run")
func _run() -> void:
 var output:=""
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--style46-control-out="):output=a.trim_prefix("--style46-control-out=")
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.content_scale_size=Vector2i(640,360)
 root.size=Vector2i(640,360)
 Engine.max_fps=60
 SaveStore.root_path="user://test-saves/style46-control"
 app=root.get_node("AppState")
 v12=load(V12_SELECTOR);r1=load(R1_SELECTOR);r2=load(R2_SELECTOR)
 var result:={}
 for dest in ["scifi.city","scifi.outskirts","scifi.ruins"]:
  result[dest]=await _probe(dest,"")
 var f=FileAccess.open(output,FileAccess.WRITE)
 f.store_string(JSON.stringify(result,"  ")+"\n")
 print("STYLE46_CONTROL_SNAPSHOT_OK")
 quit()
