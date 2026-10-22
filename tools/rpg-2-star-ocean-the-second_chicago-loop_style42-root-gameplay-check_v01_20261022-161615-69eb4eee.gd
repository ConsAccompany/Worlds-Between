extends SceneTree
const OLD_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const LOOP_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const POLICY := "res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd"
var folder := ""
var candidate := ""
var lang := "en"
var app: Node
var host: Node
var real_packed: PackedScene
var preview_packed: PackedScene
var total := 0
var captured: Array[String] = []
func _initialize() -> void: run.call_deferred()
func ck(value: bool, label: String) -> void:
 total += 1
 if not value: push_error("STYLE42_FAIL " + label)
func frames(n: int) -> void:
 for i in n: await process_frame
func cap(label: String) -> void:
 await frames(2)
 await RenderingServer.frame_post_draw
 var im := root.get_texture().get_image()
 ck(im.get_size() == Vector2i(640,360), "native capture size")
 var path := folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_style42-actual-gameplay_" + lang + "-" + label + "_20261022-161615-69eb4eee.png")
 ck(im.save_png(path)==OK,"capture " + label)
 captured.append(path)
func press(action: String) -> void:
 var e := InputEventAction.new()
 e.action = action
 e.pressed = true
 Input.parse_input_event(e)
 await frames(2)
 e = InputEventAction.new()
 e.action = action
 e.pressed = false
 Input.parse_input_event(e)
 await frames(1)
func run() -> void:
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--candidate="): candidate=a.substr(12)
  elif a.begins_with("--outdir="): folder=a.substr(9)
  elif a.begins_with("--lang="): lang=a.substr(7)
 ck(candidate!="" and folder!="", "arguments")
 DirAccess.make_dir_recursive_absolute(folder)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.content_scale_size=Vector2i(640,360)
 root.size=Vector2i(640,360)
 app=root.get_node("AppState")
 app.begin_new_run()
 app.show_initial_guide=false
 app.hero_appearance="female"
 app.language=lang
 ck(not load(POLICY).default_on(load(POLICY).CHICAGO),"ordinary default policy still off")
 var old_node=load(OLD_SCENE).instantiate()
 var original: Script=old_node.get_script()
 old_node.free()
 var packed: PackedScene=load(candidate)
 real_packed=load(OLD_SCENE)
 preview_packed=packed
 var detached=packed.instantiate()
 var revised: Script=detached.get_script()
 var oldc: Dictionary=original.get_script_constant_map()
 var newc: Dictionary=revised.get_script_constant_map()
 for k in ["WALK","BLOCKS","SPAWN","SITES","KIOSK_RADIUS","YSORT_PROPS","STREET_LABELS","SITE_TEXT","MOVE_SPEED"]:
  ck(oldc[k]==newc[k],"exact original constant "+k)
 detached.free()
 preview_packed.take_over_path(OLD_SCENE)
 load(POLICY).preview_override[load(POLICY).CHICAGO]=true
 change_scene_to_file(MAP_SCENE)
 await frames(5)
 var map: Node=current_scene
 map.select_place("earth.us.il.chicago")
 await frames(3)
 var before: int=app.calendar_minutes
 map.depart_button.pressed.emit()
 await frames(10)
 host=current_scene
 ck(host.get_script()==revised,"real map flight selects test-only in-memory candidate script")
 ck(app.current_destination_id=="scifi.loop" and app.calendar_minutes>before,"existing flight charges time and arrives Chicago")
 ck(host.hero.position==newc["SPAWN"] and host.sprite_pilot!=null,"unchanged spawn and authorized ordinary heroine")
 host.set_process(false)
 for y in range(360):
  for x in range(640):
   if original.walkable(Vector2(x,y)) != revised.walkable(Vector2(x,y)): ck(false,"walk geometry at "+str(Vector2(x,y))); quit(1); return
 ck(true,"all230400 collision samples exact")
 ck(host.title_label.text==("Chicago · The Loop" if lang=="en" else "芝加哥 · 卢普区"),"localized title")
 ck(host.badge_label.text.contains("not accepted") if lang=="en" else host.badge_label.text.contains("未验收"),"art not accepted badge")
 await cap("entry")
 var time_before: int=app.calendar_minutes
 host.hero.position=Vector2(565,220)
 Input.action_press("move_left")
 for i in 110:
  host._process(1.0/60.0)
  ck(revised.walkable(host.hero.position),"held input stays in walk lane")
 Input.action_release("move_left")
 ck(host.hero.position.x<320 and host.hero.position.x>300,"held input traverses under rail")
 var stopped: Vector2=host.hero.position
 host._process(1.0/60.0)
 ck(host.hero.position==stopped and app.calendar_minutes==time_before,"immediate physical stop, no walking calendar charge")
 await cap("walk-lane")
 for site in newc["SITES"]:
  var approach := "move_left" if site[0]=="pylon" else "move_up"
  host.hero.position=site[1]+(Vector2(36,0) if site[0]=="pylon" else Vector2(0,36))
  ck(revised.walkable(host.hero.position),"declared approach start walkable "+site[0])
  Input.action_press(approach)
  for i in 6: host._process(1.0/60.0)
  Input.action_release(approach)
  host._process(1.0/60.0)
  ck(revised.site_at(host.hero.position)==site[0],"input approach reaches "+site[0])
  await press("interact")
  ck(host.info_panel.visible and host.active_site==site[0] and host.info_label.text==newc["SITE_TEXT"][site[0]][lang],"actual interact opens localized "+site[0])
  await cap("clue-"+site[0])
  await press("interact")
  ck(not host.info_panel.visible,"actual interact closes "+site[0])
 host.hero.position=Vector2(140,182)
 host.reveal_strength=0.0
 host._update_reveal(0.0)
 ck(host.needs_reveal(host.hero.position),"unchanged west-column reveal point")
 await cap("column-occlusion")
 host._update_reveal(1.0)
 ck(host.reveal_strength==1.0,"same reveal transition")
 await cap("column-reveal")
 for item in [["west-tree",Vector2(198,256)],["east-tree",Vector2(432,256)]]:
  host.hero.position=item[1]
  ck(revised.walkable(host.hero.position),"tree inspection position walkable "+item[0])
  host.reveal_strength=0.0
  host._update_reveal(0.0)
  await cap(item[0]+"-occlusion")
  host._update_reveal(1.0)
  ck(host.reveal_strength==(1.0 if host.needs_reveal(host.hero.position) else 0.0),"unchanged tree reveal rule "+item[0])
  await cap(item[0]+"-reveal")
 ck(not app.areas_visited.has("scifi.loop"),"no extra survey goal credit")
 load(POLICY).clear_preview()
 real_packed.take_over_path(OLD_SCENE)
 host.back_button.pressed.emit()
 await frames(5)
 ck(current_scene.scene_file_path==MAP_SCENE,"actual return button opens existing world map")
 await cap("returned-map")
 var f=FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_style42-root-gameplay-result_"+lang+"_20261022-161615-69eb4eee.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify({"passed":true,"checks":total,"language":lang,"candidate":candidate,"captures":captured,"fixture":"declared test-only in-memory candidate handover + policy preview, fresh new run + three isolated approach starting positions; actual map departure, held movement and interaction/back signals; not ordinary default use or human playthrough","native":[640,360]},"  ")+"\n")
 print("STYLE42_CANDIDATE_RUNTIME_OK checks=",total)
 quit(0)
