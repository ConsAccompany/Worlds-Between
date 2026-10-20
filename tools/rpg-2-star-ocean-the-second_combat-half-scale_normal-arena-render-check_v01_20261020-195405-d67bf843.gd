extends SceneTree
# Actual normal arena/helper draw; synthetic diagnostic pixels, not character art.
func _initialize()->void:call_deferred("_run")
func _run()->void:
 var a:=OS.get_cmdline_user_args()
 assert(a.size()==1)
 var out: String=a[0]
 root.size=Vector2i(1280,720)
 await process_frame
 var app: Node=root.get_node("AppState")
 app.begin_new_run()
 app.hero_appearance="female"
 app.recruit_member("liang-xu")
 app.recruit_member("zhao-ling")
 app.ji_records_checked=true
 app.recruit_member("ji-cheng")
 app.begin_battle("patrol",Vector2(330,215))
 var arena_script: GDScript=load("res://scripts/battle_arena.gd")
 arena_script.combat_sprite_set_override=1
 arena_script.combat_sprite_set_index_override="res://tests/fixtures/csp-half-scale-v01_7d4bddce/rpg-2-star-ocean-the-second_combat-half-scale_fixture-index_not-art-v01_20261020-154048-7d4bddce.json"
 var arena: Node2D=arena_script.new()
 root.add_child(arena)
 current_scene=arena
 arena.set_process(false)
 arena.set_process_input(false)
 arena.set_process_unhandled_input(false)
 await process_frame
 # Declared isolated synthetic fixture setup: avoid overlap by later-drawn party sprites.
 arena.fighters[0]["x"]=70.0
 var h: RefCounted=arena.combat_sprite_sets
 assert(h.has_set(0) and h.set_status(0)=="loaded")
 var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/csp-half-scale-v01_7d4bddce/rpg-2-star-ocean-the-second_combat-half-scale_fixture_not-art-v01_20261020-154048-7d4bddce.json"))
 var cell:=Vector2i(int(manifest["cell_size"][0]),int(manifest["cell_size"][1]))
 var pivot:=Vector2i(int(manifest["pivot"][0]),int(manifest["pivot"][1]))
 var results: Array=[]
 for facing in [1,-1]:
  h.states[0]["facing"]=facing
  h.states[0]["action"]="idle"
  h.states[0]["clock"]=0.0
  var cf: Dictionary=h.current_frame(0)
  var g: Dictionary=h.frame_geometry(0,float(arena.fighters[0]["x"]),272.)
  var logical_w:=cell.x/2
  var logical_h:=cell.y/2
  var expected_x:=roundi(float(arena.fighters[0]["x"]))-pivot.x/2 if facing==1 else roundi(float(arena.fighters[0]["x"]))-(logical_w-1-pivot.x/2)
  var expected_y:=272-pivot.y/2
  assert(g["dest"]==Rect2(expected_x,expected_y,logical_w,logical_h))
  var original: Image=h.sets[0]["texture"].get_image()
  var source: Image=original.get_region(Rect2i(cf["origin"],cell))
  if facing==-1:source.flip_x()
  source.convert(Image.FORMAT_RGBA8)
  arena.queue_redraw()
  await process_frame
  await RenderingServer.frame_post_draw
  var capture: Image=root.get_texture().get_image()
  capture.convert(Image.FORMAT_RGBA8)
  assert(capture.get_size()==Vector2i(1280,720))
  var actual: Image=capture.get_region(Rect2i(expected_x*2,expected_y*2,cell.x,cell.y))
  var matched:=0
  for y in cell.y:
   for x in cell.x:
    var v:=source.get_pixel(x,y)
    if v.a>0.999:
     var r:=actual.get_pixel(x,y)
     if absf(v.r-r.r)>=0.0001 or absf(v.g-r.g)>=0.0001 or absf(v.b-r.b)>=0.0001:
      print("TEXEL_MISMATCH facing=",facing," xy=",x,",",y," expected=",v," actual=",r," geometry=",g["dest"])
     assert(absf(v.r-r.r)<0.0001 and absf(v.g-r.g)<0.0001 and absf(v.b-r.b)<0.0001,"Native source texel must map1:1 to physical backing pixel")
     matched+=1
  assert(matched>500)
  var file:=out.path_join("rpg-2-star-ocean-the-second_combat-half-scale_normal-arena-native-texel-%s_diagnostic-v01_20261020-195405-d67bf843.png"%("right" if facing==1 else "left"))
  assert(capture.save_png(file)==OK)
  results.append({"facing":facing,"opaqueSourcePixelsExact":matched,"file":file.get_file(),"sha256":FileAccess.get_sha256(file),"expectedLogicalRect":[expected_x,expected_y,logical_w,logical_h],"backing":[1280,720],"sourceCell":[136,144],"normalArenaHelperDraw":true,"declaredFixtureHeroX":70,"otherPartyDefaultPositionsUnchanged":true})
 var f:=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_combat-half-scale_normal-arena-render-proof_v01_20261020-195405-d67bf843.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify({"syntheticNotArt":true,"results":results,"defaultArtAdoption":false,"helperSha256":FileAccess.get_sha256("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd")},"  ")+"\n")
 f.close()
 print("HALF_NATIVE_TEXEL_RENDER_PASS facings=2")
 current_scene=null
 arena.queue_free()
 await process_frame
 call_deferred("quit",0)
