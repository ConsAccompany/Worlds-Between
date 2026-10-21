extends SceneTree
# Deterministic manual-step simulation in actual arena; not normal-input play or artistic acceptance.
const POLICY := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const ACTIONS := ["move_left","move_right","battle_guard","battle_attack","battle_dodge","battle_skill"]
var checks: Array = []
var failed := false
var policy: GDScript
func ck(ok: bool, label: String) -> void:
 checks.append({"check":label,"passed":ok})
 if not ok:
  failed=true
  print("ZPATH_PARITY_FAIL ",label)
func _initialize() -> void:
 call_deferred("run")
 create_timer(40.0).timeout.connect(func():print("ZPATH_PARITY_TIMEOUT");quit(2))
func clear_input() -> void:
 for action in ACTIONS: Input.action_release(action)
func simulate(appearance: String, enabled: int) -> Array:
 clear_input()
 var app: Node=root.get_node("AppState")
 ck(policy.configure(app,"en",appearance).get("ok",false),"preview config validates %s/%s"%[appearance,enabled])
 if enabled==0: policy.rollback()
 app.recruit_member("liang-xu")
 app.recruit_member("zhao-ling")
 app.ji_records_checked=true
 app.recruit_member("ji-cheng")
 app.select_destination("outskirts")
 app.battle_enemy_id="patrol"
 policy.enabled_override=enabled
 policy.clear_cache()
 seed(127271)
 var scene: Node=load("res://scenes/battle_arena.tscn").instantiate()
 root.add_child(scene)
 scene.set_process(false)
 scene.set_physics_process(false)
 var slot: int=app.active_party_ids.find("zhao-ling")
 ck(scene.combat_sprite_sets!=null and scene.combat_sprite_sets.has_set(0),"hero default retained %s/%s"%[appearance,enabled])
 if scene.combat_sprite_sets!=null:
  ck(scene.combat_sprite_sets.sets[0].key=="hero:"+appearance,"hero identity %s/%s"%[appearance,enabled])
 var zhao_loaded := false
 for prop in scene.get_property_list():
  var value: Variant=scene.get(prop.name)
  if value is RefCounted and value.has_method("has_set") and value.has_set(slot):
   zhao_loaded=value.sets[slot].key=="zhao-ling"
 ck(zhao_loaded==(enabled==1),"only enabled Zhao model loads %s/%s"%[appearance,enabled])
 scene.controlled_index=slot
 var frames: Array=[]
 for i in 180:
  clear_input()
  if i<55: Input.action_press("move_right")
  elif i<80: Input.action_press("battle_guard")
  if i in [85,110,135,160]: scene._try_attack(slot)
  if i==92: scene._try_dodge(slot)
  if i==125: scene._use_skill(slot)
  scene._process(1.0/60.0)
  var hp: Array=[]
  var energy: Array=[]
  for id in app.active_party_ids:
   hp.append(app.member_state(id).hp)
   energy.append(app.member_state(id).energy)
  frames.append({"fighters":scene.fighters.duplicate(true),"enemyHp":scene.enemy_hp,"enemyX":scene.enemy_x,"hp":hp,"energy":energy,"finished":scene.battle_finished,"party":app.active_party_ids.duplicate()})
 scene.free()
 policy.rollback()
 clear_input()
 return frames
func run() -> void:
 var args:=OS.get_cmdline_user_args()
 if args.size()<2:
  quit(2);return
 policy=load(POLICY)
 ck(policy!=null,"integration policy loads")
 if policy==null:
  quit(1);return
 ck(not policy.DEFAULT_ADOPTED,"ordinary adoption remains pending")
 for appearance in ["male","female"]:
  var off:=simulate(appearance,0)
  var on:=simulate(appearance,1)
  ck(off.size()==180 and on.size()==180,"bounded parity frame count "+appearance)
  for i in 180:
   ck(off[i]==on[i],"mechanics identical %s/%s"%[appearance,i])
 policy.enabled_override=-1
 policy.clear_cache()
 var out: String=args[0]
 DirAccess.make_dir_recursive_absolute(out)
 var file=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_zhao-path_mechanical-parity-proof_test-only-v01_"+args[1]+".json"),FileAccess.WRITE)
 file.store_string(JSON.stringify({"scope":"deterministic manual-step simulation; not normal-input playtest","policySha256Raw":FileAccess.get_sha256(POLICY),"checks":checks,"passed":not failed},"  ")+"\n")
 print("ZPATH_PARITY_PASS" if not failed else "ZPATH_PARITY_FAILED")
 quit(1 if failed else 0)
