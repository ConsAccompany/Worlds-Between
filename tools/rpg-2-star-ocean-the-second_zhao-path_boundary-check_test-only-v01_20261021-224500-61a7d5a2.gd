extends SceneTree
# Actual host binding fixtures; no normal-input or artistic acceptance claim.
const POLICY := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
var config
var area
var arena
var app: Node
var failed := false
var count := 0
func ck(ok: bool,label: String) -> void:
 count+=1
 failed=failed or not ok
 print("ZPATH_BOUNDARY ","PASS " if ok else "FAIL ",label)
func _initialize() -> void:
 call_deferred("run")
func scene(kind: String) -> Node:
 var host: Node=load("res://scenes/"+kind+".tscn").instantiate()
 root.add_child(host)
 host.set_process(false)
 return host
func run() -> void:
 config=load(POLICY)
 area=load("res://scripts/scifi_exploration_area.gd")
 arena=load("res://scripts/battle_arena.gd")
 app=root.get_node("AppState")
 ck(not config.DEFAULT_ADOPTED,"creator adoption remains off")
 ck(config.configure(app,"en","male").get("ok",false),"whole candidate config valid")
 var host: Node=scene("scifi_exploration_area")
 ck(config.npc_attached(host),"valid field NPC binds full set")
 host.free()
 app.recruit_member("zhao-ling") # Explicit setup fixture for render binding, not recruitment evidence.
 host=scene("battle_arena")
 ck(host.companion_sprite_sets!=null,"valid companion combat binds")
 host.free()
 config.enabled_override=0
 host=scene("scifi_exploration_area")
 ck(not config.npc_attached(host),"own disable refuses existing NPC hook")
 host.free()
 host=scene("battle_arena")
 ck(host.companion_sprite_sets==null,"own disable refuses existing combat hook")
 ck(host.combat_sprite_sets!=null and host.combat_sprite_sets.has_set(0),"disabled companion preserves male default")
 host.free()
 config.enabled_override=1
 config.combat_index_override="user://missing-zpath27-combat-index.json"
 config.clear_cache()
 host=scene("scifi_exploration_area")
 ck(not config.npc_attached(host),"whole package invalid combat also refuses NPC")
 host.free()
 host=scene("battle_arena")
 ck(host.companion_sprite_sets==null,"whole package refusal keeps companion legacy")
 ck(host.combat_sprite_sets!=null and host.combat_sprite_sets.has_set(0),"whole refusal preserves male default")
 host.free()
 config.combat_index_override=""
 config.clear_cache()
 arena.combat_sprite_set_index_override="user://existing-explicit-combat-choice.json"
 host=scene("battle_arena")
 ck(host.companion_sprite_sets==null,"explicit index choice without pilot flag wins")
 host.free()
 arena.combat_sprite_set_index_override=""
 # Simulate the enabled ordinary-policy branch with no demonstration host overrides.
 area.field_npc_presenter_override=""
 arena.companion_combat_member_override=""
 arena.companion_combat_index_override=""
 host=scene("scifi_exploration_area")
 ck(config.npc_attached(host),"prepared ordinary NPC hook works without demo bindings")
 host.free()
 host=scene("battle_arena")
 ck(host.companion_sprite_sets!=null and host.companion_sprite_sets.loaded_count()==1,"prepared ordinary combat hook works without demo bindings")
 host.free()
 config.rollback()
 config.enabled_override=-1
 config.clear_cache()
 print("ZPATH_BOUNDARY_PASS checks=" if not failed else "ZPATH_BOUNDARY_FAILED checks=",count)
 quit(1 if failed else 0)
