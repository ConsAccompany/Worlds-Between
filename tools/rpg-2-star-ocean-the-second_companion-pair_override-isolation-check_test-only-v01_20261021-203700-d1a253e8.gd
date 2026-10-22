extends SceneTree
# Declared render-binding fixture, not recruitment/input/approval evidence.
const LIANG = "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd"
const ZHAO = "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
var failed := false
var checks := 0
var arena
var L
var Z
func ck(ok: bool,label: String) -> void:
 checks += 1
 failed = failed or not ok
 print("PAIR_ISOLATION ","PASS " if ok else "FAIL ",label)
func _initialize() -> void:
 call_deferred("run")
func check_binding(member: String, path: String, expected: String) -> void:
 arena.companion_combat_member_override=member
 arena.companion_combat_index_override=path
 var host=load("res://scenes/battle_arena.tscn").instantiate()
 root.add_child(host)
 host.set_process(false)
 var members: Dictionary=host.companion_sets_by_member
 ck(members.is_empty() if expected=="" else members.size()==1 and members.has(expected),"explicit pair limits member to "+expected)
 ck(host.combat_sprite_sets!=null and host.combat_sprite_sets.has_set(0),"explicit pair preserves hero")
 ck(host.companion_sprite_sets==null if expected=="" else host.companion_sprite_sets==members[expected],"explicit pair compatibility alias")
 host.free()
func run() -> void:
 var app=root.get_node("AppState")
 app.begin_new_run()
 app.hero_appearance="male"
 app.recruit_member("liang-xu")
 app.recruit_member("zhao-ling")
 L=load(LIANG);Z=load(ZHAO);arena=load("res://scripts/battle_arena.gd")
 ck(L.DEFAULT_ADOPTED == OS.get_cmdline_user_args().has("--expect-default-adopted") and Z.DEFAULT_ADOPTED,"expected adoption scopes preserved")
 L.enabled_override=1
 check_binding("zhao-ling",Z.combat_index_path(),"zhao-ling")
 check_binding("liang-xu",L.combat_index_path(),"liang-xu")
 var loader=load(L.COMBAT_LOADER_PATH)
 var fixture:="user://rpg-2-star-ocean-the-second_companions_extra-member-index_test-only-v01_20261021-203700-d1a253e8.json"
 var file=FileAccess.open(fixture,FileAccess.WRITE)
 file.store_string(JSON.stringify({"schema":"worlds-between.combat-sprite-set-index/1","sets":{
  "liang-xu":loader.load_index(L.combat_index_path()).sets["liang-xu"],
  "zhao-ling":loader.load_index(Z.combat_index_path()).sets["zhao-ling"]}}))
 file.close()
 check_binding("liang-xu",fixture,"")
 check_binding("unknown-member",L.combat_index_path(),"")
 arena.companion_combat_member_override=""
 arena.companion_combat_index_override=""
 L.enabled_override=-1
 var absolute:=ProjectSettings.globalize_path(fixture)
 ck(absolute.begins_with(ProjectSettings.globalize_path("user://")),"fixture cleanup stays inside isolated user directory")
 if absolute.begins_with(ProjectSettings.globalize_path("user://")):
  ck(DirAccess.remove_absolute(absolute)==OK,"owned fixture removed")
 print("PAIR_ISOLATION_PASS checks=" if not failed else "PAIR_ISOLATION_FAIL checks=",checks)
 quit(1 if failed else 0)
