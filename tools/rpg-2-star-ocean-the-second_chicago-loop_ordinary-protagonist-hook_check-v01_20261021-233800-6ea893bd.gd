extends SceneTree
const SCENE = "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const LOADER = preload("res://scripts/exploration_sprite_set_pilot.gd")
var failed: Array[String] = []
var checks = 0
func ck(ok: bool, label: String) -> void:
 checks += 1
 if not ok: failed.append(label); print("LOOP_HERO_FAIL ", label)
func hash_texture(s: Sprite2D) -> String:
 var ctx = HashingContext.new()
 ctx.start(HashingContext.HASH_SHA256)
 ctx.update(s.texture.get_image().get_data())
 return ctx.finish().hex_encode()
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var app = root.get_node("AppState")
 app.set_process(false)
 for actor in ["female", "male"]:
  app.begin_new_run()
  app.hero_appearance = actor
  app.current_destination_id = "scifi.loop"
  app.show_initial_guide = false
  var node = load(SCENE).instantiate()
  root.add_child(node)
  node.set_process(false)
  ck(node.sprite_pilot != null, actor + " approved ordinary driver attached")
  var expected = Sprite2D.new()
  var driver = LOADER.attach(expected, "protagonist-" + actor, "south")
  ck(driver != null and node.sprite_pilot.get_script() == driver.get_script(), actor + " same shared driver")
  ck(node.hero.scale == expected.scale and node.hero.offset == expected.offset and hash_texture(node.hero) == hash_texture(expected), actor + " exact ordinary package scale pivot idle")
  expected.free()
  for pair in [["move_right", "east", Vector2.RIGHT], ["move_down", "south", Vector2.DOWN], ["move_left", "west", Vector2.LEFT], ["move_up", "north", Vector2.UP]]:
   node.hero.position = Vector2(320, 232)
   var start: Vector2 = node.hero.position
   Input.action_press(pair[0])
   for i in 10: node._process(1.0/60.0)
   Input.action_release(pair[0])
   ck(node.facing == pair[1], actor + " facing " + pair[1])
   ck(node.hero.position.distance_to(start + pair[2] * (140.0/6.0)) < 0.001, actor + " unchanged 140px movement " + pair[1])
   var stopped: Vector2 = node.hero.position
   for i in 30: node._process(1.0/60.0)
   ck(node.hero.position == stopped, actor + " physical stop " + pair[1])
   ck(node.sprite_pilot != null and node.hero.scale == Vector2(0.5,0.5), actor + " presenter retained " + pair[1])
  var resume: Vector2 = node.hero.position
  node.free()
  app.resume_area_pending = true
  app.resume_area_position = resume
  var again = load(SCENE).instantiate()
  root.add_child(again)
  again.set_process(false)
  ck(again.hero.position == resume and not app.resume_area_pending, actor + " resume position consumed once")
  ck(again.sprite_pilot != null, actor + " resume ordinary presenter")
  ck(not again.walkable(Vector2(-100,-100)) and again.walkable(again.safe_position(Vector2(-100,-100))), actor + " collision safe resume")
  again.free()
 print("LOOP_HERO_RESULT checks=",checks," failed=",failed.size())
 if failed.is_empty(): print("LOOP_HERO_PASS")
 quit(0 if failed.is_empty() else 1)
