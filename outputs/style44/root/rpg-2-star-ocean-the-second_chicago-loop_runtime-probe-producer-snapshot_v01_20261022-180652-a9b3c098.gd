extends SceneTree
const OLD_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const LOOP_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const POLICY := "res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd"
# Ordinary-default verifier: no candidate arg, no take_over_path, no preview_override. Expected paths are the
# style42 native-manifest scene.tscn/scene.script entries (outputs/style42/*native-manifest*), hardcoded.
const STYLE42_TSCN := "res://scenes/style42/rpg-2-star-ocean-the-second_chicago-loop-style42_state-lake-scene_unapproved-v01_20261022-161615-69eb4eee.tscn"
const STYLE42_GD := "res://scripts/style42/rpg-2-star-ocean-the-second_chicago-loop-style42_state-lake-scene_unapproved-v01_20261022-161615-69eb4eee.gd"
var folder := ""
var lang := "en"
var app: Node
var host: Node
var total := 0
var captured: Array[String] = []
func _initialize() -> void: run.call_deferred()
func ck(value: bool, label: String) -> void:
 total += 1
 if not value: push_error("STYLE44_FAIL " + label)
func frames(n: int) -> void:
 for i in n: await process_frame
func cap(label: String) -> void:
 await frames(2)
 await RenderingServer.frame_post_draw
 var im := root.get_texture().get_image()
 ck(im.get_size() == Vector2i(640,360), "native capture size")
 var path := folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_style44-ordinary-gameplay_" + lang + "-" + label + "_20261022-180652-a9b3c098.png")
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
 var extra := 0
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--outdir="): folder=a.substr(9)
  elif a.begins_with("--lang="): lang=a.substr(7)
  else: extra+=1
 ck(folder!="" and extra==0, "arguments only --lang/--outdir (no user flags)")
 DirAccess.make_dir_recursive_absolute(folder)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.content_scale_size=Vector2i(640,360)
 root.size=Vector2i(640,360)
 app=root.get_node("AppState")
 app.begin_new_run()
 app.show_initial_guide=false
 app.hero_appearance="female"
 app.language=lang
 var pol=load(POLICY)
 ck(pol.preview_override.is_empty(),"no policy preview override")
 ck(pol.CHICAGO_V05_DEFAULT and pol.default_on(pol.CHICAGO),"Chicago ordinary default bit true")
 ck(not pol.CITY_V06_DEFAULT and not pol.RUINS_V13_DEFAULT and not pol.RECORDS_ROOM2_DEFAULT,"other three default bits false")
 ck(not pol.default_on(pol.CITY) and not pol.default_on(pol.RUINS) and not pol.default_on(pol.RECORDS),"other three defaults resolve false")
 var map_scene: String=app.save_return_scene
 ck(map_scene==MAP_SCENE,"AppState resolves ordinary world map")
 var old_node=load(OLD_SCENE).instantiate()
 var original: Script=old_node.get_script()
 old_node.free()
 var revised: Script=load(STYLE42_GD)
 var oldc: Dictionary=original.get_script_constant_map()
 var newc: Dictionary=revised.get_script_constant_map()
 for k in ["WALK","BLOCKS","SPAWN","SITES","KIOSK_RADIUS","YSORT_PROPS","STREET_LABELS","SITE_TEXT","MOVE_SPEED"]:
  ck(oldc[k]==newc[k],"exact original constant "+k)
 change_scene_to_file(map_scene)
 await frames(5)
 var map: Node=current_scene
 map.select_place("earth.us.il.chicago")
 await frames(3)
 var before: int=app.calendar_minutes
 map.depart_button.pressed.emit()
 for i in 60:
  await process_frame
  if current_scene!=null and current_scene.scene_file_path==STYLE42_TSCN: break
 await frames(3)
 host=current_scene
 ck(host.scene_file_path==STYLE42_TSCN and host.get_script()==revised,"ordinary map flight lands in manifest style42 scene via default fallback")
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
 host.back_button.pressed.emit()
 await frames(5)
 ck(current_scene.scene_file_path==MAP_SCENE,"actual return button opens existing world map")
 ck(pol.preview_override.is_empty(),"still no policy preview override")
 await cap("returned-map")
 var f=FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_style44-ordinary-gameplay-result_"+lang+"_20261022-180652-a9b3c098.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify({"passed":true,"checks":total,"language":lang,"scene":STYLE42_TSCN,"script":STYLE42_GD,"captures":captured,"fixture":"ordinary default: no user flags, no take_over_path, no preview override; fresh new run + three isolated approach starting positions; actual map departure, held movement and interaction/back signals; not a human playthrough; art UNAPPROVED","native":[640,360]},"  ")+"\n")
 print("STYLE44_ORDINARY_RUNTIME_OK checks=",total)
 quit(0)
