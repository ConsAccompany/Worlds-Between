extends SceneTree
# Defect reproducer: a successful reproduction is NOT a passing character QA gate.
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 SaveStore.root_path = "user://test-saves/xcheck36-contact-reproducer"
 var app = root.get_node("AppState")
 app.begin_new_run()
 app.set_process(false)
 app.hero_appearance = "male"
 app.current_destination_id = "scifi.outskirts"
 app.show_initial_guide = false
 var host = load("res://scenes/scifi_exploration_area.tscn").instantiate()
 root.add_child(host)
 host.set_process(false)
 var driver = host.sprite_pilot
 if driver == null or driver.actor_id != "protagonist-male":
  push_error("ordinary male package not attached"); quit(2); return
 driver.set_process(false)
 host.hero.position = Vector2(520,290)
 Input.action_press("move_left")
 driver.advance(1.0/60.0)
 host._process(1.0/60.0)
 var p0: Vector2 = host.hero.position
 var s0: Dictionary = driver.state()
 driver.advance(0.04)
 host._process(0.04)
 var p1: Vector2 = host.hero.position
 var s1: Dictionary = driver.state()
 Input.action_release("move_left")
 # Opaque heel x=32 at phase0 and x=36 at phase1, source-hash/PNG verified independently.
 var drift = (p1.x + (36.0-40.0)*0.5) - (p0.x + (32.0-40.0)*0.5)
 var reproduced = s0.action=="walk" and s0.frame==0 and s1.action=="walk" and s1.frame==1 and abs(p1.x-p0.x+5.6)<0.0001 and abs(drift+3.6)<0.0001
 print("MVP_CONTACT_ACTUAL ", JSON.stringify({"before":s0,"after":s1,"heroDeltaX":p1.x-p0.x,"footWorldDeltaX":drift,"zeroSlipPassed":abs(drift)<0.0001,"actualOrdinaryHostInput":true,"deltaSeconds":0.04}))
 host.free()
 if reproduced: print("MVP_CONTACT_REPRODUCED_NOT_QA_PASS")
 else: push_error("contact reproduction expectation mismatch")
 quit(0 if reproduced else 1)
