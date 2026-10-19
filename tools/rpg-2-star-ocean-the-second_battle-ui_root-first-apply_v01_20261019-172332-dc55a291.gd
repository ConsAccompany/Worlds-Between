extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var app=root.get_node("AppState")
 app.begin_new_run()
 app.recruit_member("liang-xu")
 app.recruit_member("zhao-ling")
 app.ji_records_checked=true
 app.recruit_member("ji-cheng")
 app.begin_battle("patrol",Vector2(330,215))
 var a=load("res://scenes/battle_arena.tscn").instantiate()
 root.add_child(a)
 a.set_process(false)
 await process_frame
 var s=load("res://scripts/rpg-2-star-ocean-the-second_battle-ui_skin-helper_root-v02_20261019-172332-dc55a291.gd").new("res://assets/ui/battle-skin-v01")
 print("APPLY_RESULT ",s.apply(a)," error=",s.last_error)
 s.revert()
 a.queue_free()
 await process_frame
 print("HUD_FIRST_APPLY_DONE")
 quit(0)
