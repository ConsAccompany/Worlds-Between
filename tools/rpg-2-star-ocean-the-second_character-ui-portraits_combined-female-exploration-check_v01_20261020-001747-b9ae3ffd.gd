extends SceneTree
# Unscored combined normal CLI readiness only. No enabled overrides, fallback injection or art approval.
# Godot --path game --audio-driver Dummy --fixed-fps60 --script <this> -- <output-folder> <report-json>
#   --character-ui-portraits-pilot --female-complete-exploration-pilot
var TAG := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-") + "-" + Crypto.new().generate_random_bytes(4).hex_encode()
const DRIVER_PATH := "res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd"
const Driver := preload(DRIVER_PATH)
const SOURCE_PATHS := ["res://scripts/scifi_exploration_area.gd","res://scripts/exploration_sprite_set_pilot.gd",DRIVER_PATH,"res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_input-guard_v01_20261019-190507-a7d3e9b1.gd","res://scripts/rpg-2-star-ocean-the-second_character-ui-portraits_helper_v01_20261019-233832-b7c4e912.gd","res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_package_v01_20261019-184500-f2c0a7e1.json","res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_south-runtime_v01_20261019-184900-f2c0a7e1.json","res://assets/portraits/ui-kit-v02/rpg-2-star-ocean-the-second_character-ui-kit_manifest_v02_20261020-001030-9be4a34f.json"]
var checks:=[]
var captures:=[]
var rows:=[]
var sources_before:={}
var output_folder:=""
func _initialize() -> void:call_deferred("run")
func ck(key:String,okay:bool,detail:String="") -> void:checks.append({"key":key,"pass":okay,"detail":detail})
func settle() -> void:
 await process_frame
 await process_frame
 await RenderingServer.frame_post_draw
func click(control:Control) -> void:
 var point:=control.get_global_rect().get_center()
 var motion:=InputEventMouseMotion.new();motion.position=point;root.push_input(motion,true)
 for down in [true,false]:
  var event:=InputEventMouseButton.new();event.position=point;event.button_index=MOUSE_BUTTON_LEFT;event.pressed=down;root.push_input(event,true)
func detach_audio(node:Node) -> void:
 for child in node.get_children():
  if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:child.stop();child.stream=null
  detach_audio(child)
func capture(purpose:String,language:String) -> void:
 await RenderingServer.frame_post_draw
 var image:=root.get_texture().get_image()
 ck("native640-"+purpose+"-"+language,image.get_size()==Vector2i(640,360))
 var file:="rpg-2-star-ocean-the-second_character-ui-portraits_combined-female-"+purpose+"-"+language+"-640_unapproved-v01_"+TAG+".png"
 var path:=output_folder.path_join(file)
 ck("capture-"+purpose+"-"+language,image.save_png(path)==OK)
 captures.append({"purpose":purpose,"language":language,"file":file,"sha256":FileAccess.get_sha256(path)})
func run() -> void:
 var args:=OS.get_cmdline_user_args()
 assert(args.size()>=4 and args.has("--character-ui-portraits-pilot") and args.has("--female-complete-exploration-pilot"))
 output_folder=args[0];var report_path:=args[1]
 DirAccess.make_dir_recursive_absolute(output_folder)
 root.size=Vector2i(640,360);root.content_scale_size=Vector2i(640,360);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 for path in SOURCE_PATHS:sources_before[path]=FileAccess.get_sha256(path)
 var app:Node=root.get_node("AppState")
 var host_script:Script=load("res://scripts/scifi_exploration_area.gd")
 ck("actual-cli-no-overrides",host_script.character_ui_portraits_override==-1 and Driver.enabled_override==-1 and Driver.package_override.is_empty() and Driver.runtime_override.is_empty())
 for language in ["en","zh"]:
  app.begin_new_run();app.language=language;app.hero_appearance="female";app.current_destination_id="scifi.city"
  app.show_initial_guide=false;app.returning_from_battle=false;app.resume_area_pending=false
  var host:Node=load("res://scenes/scifi_exploration_area.tscn").instantiate();root.add_child(host);current_scene=host
  await settle()
  var pilot=host.sprite_pilot
  ck("normal-complete-driver-"+language,pilot!=null and pilot.get_script().resource_path==DRIVER_PATH,str(Driver.last_refusal))
  assert(pilot!=null and pilot.get_script().resource_path==DRIVER_PATH)
  var portraits:Control=host.character_ui_portraits
  ck("normal-dialogue-helper-"+language,portraits!=null)
  assert(portraits!=null)
  var before:Vector2=host.hero.position
  Input.action_press("move_right")
  for i in 25:await process_frame
  var running:Vector2=host.hero.position
  Input.action_release("move_right")
  for i in 24:await process_frame
  var rep:Dictionary=pilot.report()
  ck("real-host-movement-"+language,running.x>before.x+10.0)
  ck("real-host-stop-"+language,host.hero.position==running)
  ck("complete-driver-settled-"+language,rep.steps>=48 and rep.facing=="east" and rep.showing_idle and rep.oracle_mismatch==0)
  ck("complete-driver-display-"+language,host.hero.scale==Vector2(0.5,0.5) and host.hero.texture.get_size()==Vector2(80,112))
  await capture("movement-stop",language)
  # Interaction fixture places the hero at the unchanged existing NPC site; the real host interaction opens real dialogue.
  host.hero.position=host.npc_position
  var interact:=InputEventAction.new();interact.action="interact";interact.pressed=true;host._unhandled_input(interact)
  await settle()
  var full_text:String=app.text_for("recruit_"+String(host.recruit_id).split("-")[0])
  ck("normal-recruit-open-"+language,host.dialogue_open and host.dialogue_mode=="recruit")
  ck("correct-recruit-identity-"+language,host.recruit_id=="liang-xu" and portraits.get_dialogue_subject()=="liang-xu" and portraits.is_showing_dialogue())
  ck("full-original-text-"+language,not full_text.is_empty() and host.dialogue_text.text==full_text)
  ck("full-text-fits-"+language,portraits.get_text_fit())
  var methods:=[]
  for connection in host.invite_button.pressed.get_connections():methods.append(String(connection.callable.get_method()))
  ck("original-recruit-callback-"+language,methods.has("_dialogue_primary") and not host.invite_button.disabled)
  ck("portrait-does-not-consume-mouse-"+language,host.dialogue_panel.find_child("CharacterUiPortrait",true,false).mouse_filter==Control.MOUSE_FILTER_IGNORE)
  await capture("recruit-dialogue",language)
  click(host.invite_button);await settle()
  ck("real-recruit-click-"+language,app.recruited_members.has("liang-xu") and not host.dialogue_open and not portraits.is_showing_dialogue())
  ck("click-keeps-original-text-"+language,host.dialogue_text.text==full_text)
  ck("female-driver-survives-dialogue-"+language,host.sprite_pilot==pilot and pilot.get_script().resource_path==DRIVER_PATH and host.hero.scale==Vector2(0.5,0.5))
  rows.append({"language":language,"movementStart":var_to_str(before),"movementEnd":var_to_str(running),"driver":rep,"recruitId":host.recruit_id,"fullDialogueText":full_text,"portraitSubject":"liang-xu","recruited":app.recruited_members.has("liang-xu")})
  detach_audio(host);root.remove_child(host);host.free();pilot=null;portraits=null;current_scene=null;await process_frame
 Driver.clear_cache()
 var sources_after:={}
 for path in SOURCE_PATHS:sources_after[path]=FileAccess.get_sha256(path)
 ck("combined-source-bytes-unchanged",sources_before==sources_after)
 var failed:=checks.filter(func(row):return not row.pass)
 var report:={"passed":failed.is_empty(),"checks":checks,"failures":failed,"cases":rows,"captures":captures,"flags":args,"sourceRawSha256Before":sources_before,"sourceRawSha256After":sources_after,"probeRawSha256":FileAccess.get_sha256(get_script().resource_path),"normalCliCombined":true,"artOrApprovalOrExtraProgress":false,"positionFixture":"Only interaction setup places hero at unchanged NPC site; movement uses real input/host update"}
 var file:=FileAccess.open(report_path,FileAccess.WRITE);assert(file!=null);file.store_string(JSON.stringify(report,"  ")+"\n");file.close()
 var previous:=AudioServer.get_time_since_last_mix();var mixes:=0;var deadline:=Time.get_ticks_usec()+300000
 while mixes<2 and Time.get_ticks_usec()<deadline:
  await process_frame
  var age:=AudioServer.get_time_since_last_mix()
  if age<previous:mixes+=1
  previous=age
 for row in failed:print("COMBINED_UI_FEMALE_FAIL ",JSON.stringify(row))
 print("COMBINED_UI_FEMALE_EXPLORATION ",checks.size()-failed.size(),"/",checks.size())
 print("COMBINED_UI_FEMALE_AUDIO_MIX_BOUNDARIES ",mixes)
 quit(0 if failed.is_empty() and mixes==2 else 1)
