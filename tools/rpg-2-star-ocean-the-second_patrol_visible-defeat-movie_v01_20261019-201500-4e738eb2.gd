extends SceneTree
var out = ""
var stamp = ""
var app
var arena
var failures = []
var clips = []
var sequence_frame = 0
var sequence_dir = ""
func _initialize():call_deferred("run")
func run():
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="):out=arg.trim_prefix("--out=")
        if arg.begins_with("--stamp="):stamp=arg.trim_prefix("--stamp=")
    root.size=Vector2i(640,360)
    sequence_dir=out.path_join("pseq-"+stamp.right(8))
    DirAccess.make_dir_recursive_absolute(sequence_dir)
    app=root.get_node("AppState")
    SaveStore.root_path="user://test-saves/patrol-visible-defeat-movie"
    arena=load("res://scripts/battle_arena.gd")
    arena.patrol_animation_override=-1
    arena.sentry_v2_override=-1
    for language in ["en","zh"]:
        app.begin_new_run()
        app.hero_appearance="male"
        app.recruit_member("liang-xu")
        app.recruit_member("zhao-ling")
        app.ji_records_checked=true
        app.recruit_member("ji-cheng")
        app.select_destination("scifi.outskirts")
        if app.language!=language:app.toggle_language()
        app.begin_battle("patrol",Vector2(330,215))
        var battle=load("res://scenes/battle_arena.tscn").instantiate()
        root.add_child(battle)
        current_scene=battle
        await process_frame
        var key=InputEventKey.new()
        key.physical_keycode=KEY_T
        key.pressed=true
        Input.parse_input_event(key)
        await process_frame
        key=InputEventKey.new()
        key.physical_keycode=KEY_T
        key.pressed=false
        Input.parse_input_event(key)
        if not battle.auto_mode:failures.append("normal T input did not enable auto "+language)
        var frames=0
        var visible_defeat_frames=0
        var shown_frames=0
        var captured=false
        var rows=[]
        while frames<600:
            await process_frame
            await RenderingServer.frame_post_draw
            frames+=1
            sequence_frame+=1
            var frame_image=root.get_texture().get_image()
            if frame_image.get_size()!=Vector2i(640,360):failures.append("native capture size mismatch")
            if frame_image.save_png(sequence_dir.path_join("rpg-2-star-ocean-the-second_patrol_frame-%04d_v01_%s.png" % [sequence_frame,stamp]))!=OK:failures.append("sequence frame save failed")
            var visible_death=battle.enemy_visual_state=="defeat" and not battle.result_overlay.visible
            if visible_death:
                visible_defeat_frames+=1
                if not captured and battle.enemy_visual_clock>=0.3:
                    var path=out.path_join("rpg-2-star-ocean-the-second_patrol_visible-defeat-%s_v01_%s.png" % [language,stamp])
                    var image=frame_image
                    if image.save_png(path)!=OK:failures.append("capture failed "+language)
                    captured=true
            if battle.result_overlay.visible:shown_frames+=1
            rows.append({"frame":frames,"gameSeconds":frames/60.0,"enemyHp":battle.enemy_hp,"enemyState":battle.enemy_visual_state,"enemyVisualClock":battle.enemy_visual_clock,"pending":battle.patrol_result_pending,"presentationElapsed":battle.patrol_result_elapsed,"panelVisible":battle.result_overlay.visible,"auto":battle.auto_mode})
            if shown_frames>=30:break
        if visible_defeat_frames<44 or not captured or shown_frames<30:failures.append("defeat not visibly held "+language)
        clips.append({"language":language,"frames":frames,"visibleDefeatFrames":visible_defeat_frames,"resultFrames":shown_frames,"criticalPngCaptured":captured,"rows":rows})
        battle.free()
        current_scene=null
        await process_frame
    var f=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_patrol_visible-defeat-report_v01_%s.json" % stamp),FileAccess.WRITE)
    f.store_string(JSON.stringify({"captureMode":"Native640x360 per-rendered-frame capture at fixed60 game simulation; one saved frame per1/60 game second, no resize/interpolation/HP/timer/stat/position manipulation. Physical T starts ordinary auto battle. Not a wall-clock60performance claim.","sequenceFrames":sequence_frame,"sequenceDirectory":sequence_dir,"clips":clips,"failures":failures},"  ")+"\n");f.close()
    print("PATROL_VISIBLE_DEFEAT_MOVIE_PASS" if failures.is_empty() else "PATROL_VISIBLE_DEFEAT_MOVIE_FAIL "+JSON.stringify(failures))
    arena=null
    await process_frame
    await process_frame
    quit(0 if failures.is_empty() else 1)
