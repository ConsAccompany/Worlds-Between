extends SceneTree
var arena
var frozen
var app
var out = ""
var errors = []
var checks = []
var images = []
func _initialize():
    call_deferred("run")
func expect(ok, label):
    checks.append({"check":label,"pass":ok})
    if not ok: errors.append(label)
func setup(enemy, language, old=false, patrol=1, sentry=0):
    if current_scene != null:
        current_scene.free()
        current_scene = null
    app.begin_new_run()
    app.hero_appearance = "male"
    app.recruit_member("liang-xu")
    app.recruit_member("zhao-ling")
    app.ji_records_checked = true
    app.recruit_member("ji-cheng")
    app.select_destination("scifi.ruins" if enemy == "sentry" else "scifi.outskirts")
    if app.language != language: app.toggle_language()
    app.begin_battle(enemy, Vector2(330,215))
    arena.patrol_animation_override = patrol
    arena.sentry_v2_override = sentry
    frozen.patrol_animation_override = patrol
    frozen.sentry_v2_override = sentry
    var b = load("res://scenes/battle_arena.tscn").instantiate()
    if old: b.set_script(frozen)
    b.set_process(false)
    root.add_child(b)
    current_scene = b
    return b
func combat(b):
    var a = [b.enemy_x,b.enemy_hp,b.enemy_windup,b.enemy_cooldown,b.enemy_attack_count,b.enemy_target_index,b.battle_finished,b.battle_won,app.enemy_cleared_for_return,app.returning_from_battle,app.hero_state.duplicate(true),app.member_states.duplicate(true)]
    for f in b.fighters: a.append([f["x"],f["attack_cooldown"],f["dodge_cooldown"],f["dodge_time"],f["skill_cooldown"]])
    return var_to_str(a)
func shot():
    current_scene.queue_redraw()
    await process_frame
    await process_frame
    return root.get_texture().get_image()
func timing_case(deltas, tag):
    var b = setup("patrol","en")
    b.enemy_hp = 0
    var save_before = SaveStore.list_entries().size()
    var xp_before = int(app.hero_state["xp"])
    var jp_before = int(app.hero_state["jp"])
    b._finish_battle(true)
    expect(b.battle_finished and b.battle_won and not b.result_overlay.visible and b.patrol_result_pending, tag+" victory immediately committed but panel hidden")
    expect(b.result_button.disabled and b.result_button.focus_mode == Control.FOCUS_NONE and not b.result_button.has_focus(), tag+" hidden button inert and unfocused")
    expect(SaveStore.list_entries().size() == save_before+1 and int(app.hero_state["xp"]) == xp_before+26 and int(app.hero_state["jp"]) == jp_before+12, tag+" reward and autosave immediate once")
    var save_after = SaveStore.list_entries().duplicate(true)
    var state = combat(b)
    b._return_after_result()
    b.result_button.pressed.emit()
    expect(current_scene == b and app.battle_enemy_id == "patrol", tag+" premature direct and button return blocked")
    var elapsed = 0.0
    for d in deltas:
        elapsed += d
        b._process(d)
        var should_show = elapsed + 0.000000001 >= 0.75
        expect(b.result_overlay.visible == should_show, tag+" exact visibility at %.12f" % elapsed)
        expect(combat(b) == state, tag+" no combat/reward state drift %.12f" % elapsed)
    b._finish_battle(true)
    expect(SaveStore.list_entries() == save_after and combat(b) == state, tag+" no duplicate save or reward after finish retry")
    expect(b.result_overlay.visible and not b.result_button.disabled and b.result_button.focus_mode == Control.FOCUS_ALL and b.result_button.has_focus(),tag+" result becomes usable")
func run():
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="):out=arg.trim_prefix("--out=")
    DirAccess.make_dir_recursive_absolute(out)
    app = root.get_node("AppState")
    SaveStore.root_path="user://test-saves/patrol-victory-visibility"
    root.size=Vector2i(640,360)
    arena=load("res://scripts/battle_arena.gd")
    frozen=GDScript.new()
    frozen.source_code=FileAccess.get_file_as_string("C:/Users/hkzha/Documents/Codex/2026-10-12/rpg-2-star-ocean-the-second/work/max0840-sentry-sync/outputs/patrol-victory-v01/rpg-2-star-ocean-the-second_patrol_pre-result-fix-arena_v01_20261019-201344-e7f7d7a0.gd")
    expect(frozen.reload()==OK,"frozen arena compiles")
    var d30=[]
    for i in 22:d30.append(1.0/30.0)
    d30.append(1.0/30.0)
    timing_case(d30,"30fps")
    var d60=[]
    for i in 45:d60.append(1.0/60.0)
    timing_case(d60,"60fps")
    timing_case([0.749999,0.000001],"boundary-minus-one-microsecond")
    timing_case([0.75],"exact-boundary")
    for language in ["en","zh"]:
        for spec in [["patrol",0,0],["sentry",0,0],["sentry",0,1],["sentry",1,1]]:
            var old=setup(spec[0],language,true,spec[1],spec[2])
            old.enemy_hp=0
            old._finish_battle(true)
            var oldstate=combat(old)
            var a=await shot()
            var b=setup(spec[0],language,false,spec[1],spec[2])
            b.enemy_hp=0
            b._finish_battle(true)
            var bb=await shot()
            var label="%s p%d s%d %s" % [spec[0],spec[1],spec[2],language]
            expect(a.get_data()==bb.get_data(),"default/Sentry result pixels exact "+label)
            expect(combat(b)==oldstate,"default/Sentry result state exact "+label)
        var loss=setup("patrol",language)
        loss._finish_battle(false)
        expect(loss.result_overlay.visible and not loss.patrol_result_pending,"loss result immediate "+language)
    if current_scene != null:current_scene.free();current_scene=null
    var f=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_patrol_victory-boundary-report_v01_20261019-201431-6f92cfae.json"),FileAccess.WRITE)
    f.store_string(JSON.stringify({"checks":checks,"errors":errors},"  ")+"\n");f.close()
    print("PATROL_RESULT_PRESENTATION_PASS checks=",checks.size()) if errors.is_empty() else print("PATROL_RESULT_PRESENTATION_FAIL ",JSON.stringify(errors))
    frozen=null;arena=null
    await process_frame
    await process_frame
    quit(0 if errors.is_empty() else 1)
