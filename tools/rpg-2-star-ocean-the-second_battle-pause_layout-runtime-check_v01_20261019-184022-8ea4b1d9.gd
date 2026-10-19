extends SceneTree
const TAG := "20261019-184022-8ea4b1d9"
var checks: Array=[]
var app: Node
var output: String
var current: Script
var frozen: Script
var old_skin: Script
func _initialize() -> void:call_deferred("run")
func ck(key: String, okay: bool) -> void:checks.append({"key":key,"pass":okay})
func setup(old: bool, skin: int, lang: String, member := 0) -> Node2D:
	app.begin_new_run();app.language=lang;app.hero_appearance="female"
	app.recruit_member("liang-xu");app.recruit_member("zhao-ling");app.ji_records_checked=true;app.recruit_member("ji-cheng")
	for id in app.active_party_ids:
		var state: Dictionary=app.member_state(id)
		state.job_stage=2;state.level=20;state.job_records[state.job_series]=GrowthRules.new_job_record(state.job_series,2)
	app.select_destination("scifi.city");app.begin_battle("patrol",Vector2(330,215))
	var script: Script=frozen if old else current
	script.battle_ui_skin_override=0 if old else skin
	script.battle_vfx_override=0;script.encounter_feedback_override=0;script.skill_vfx_override=0;script.sentry_v2_override=0;script.combat_sprite_set_override=0;script.themed_music_override=0
	seed(4832)
	var arena: Node2D=script.new();root.add_child(arena);current_scene=arena;arena.set_process(false)
	if old and skin==1:
		arena.battle_ui_skin=old_skin.new("res://assets/ui/battle-skin-v01")
		arena.battle_ui_skin_status="applied" if arena.battle_ui_skin.apply(arena) else "fallback"
	arena._choose_control(member)
	await process_frame;await process_frame
	return arena
func dispose(arena: Node2D) -> void:
	for sound in arena.find_children("*","AudioStreamPlayer",true,false):sound.stop();sound.stream=null
	arena.queue_free();await process_frame
func capture(label: String) -> Image:
	await process_frame;await RenderingServer.frame_post_draw
	var im:=root.get_texture().get_image();im.convert(Image.FORMAT_RGBA8)
	ck("capture-"+label,im.save_png(output.path_join("rpg-2-star-ocean-the-second_battle-pause_"+label+"_actual-640_v01_"+TAG+".png"))==OK)
	return im
func state(a: Node2D) -> Array:
	return [a.fighters.duplicate(true),a.enemy_hp,a.enemy_x,a.enemy_cooldown,a.enemy_windup,app.hero_state.duplicate(true),app.member_states.duplicate(true)]
func click(point: Vector2) -> void:
	var motion:=InputEventMouseMotion.new();motion.position=point;root.push_input(motion,true)
	for press in [true,false]:
		var event:=InputEventMouseButton.new();event.position=point;event.button_index=MOUSE_BUTTON_LEFT;event.pressed=press;root.push_input(event,true)
func layout(a: Node2D, label: String) -> void:
	var panel:=Rect2(55,43,530,286)
	var controls: Array=[a.pause_title,a.pause_skill_button,a.pause_resume_button,a.pause_target_label,a.pause_order_feedback,a.pause_policy_button]
	controls.append_array(a.pause_job_skill_buttons);controls.append_array(a.pause_target_buttons);controls.append_array(a.pause_order_buttons.values())
	for i in controls.size():
		var c: Control=controls[i]
		if not c.visible or (c is Label and c.text.is_empty()):continue
		var r:=c.get_global_rect()
		ck(label+"-inside-panel-"+str(i),panel.encloses(r))
		ck(label+"-minimum-fits-"+str(i),c.size.x>=c.get_combined_minimum_size().x and c.size.y>=c.get_combined_minimum_size().y)
		for j in range(i+1,controls.size()):
			var d: Control=controls[j]
			if d.visible and not (d is Label and d.text.is_empty()):ck(label+"-nonoverlap-"+str(i)+"-"+str(j),not r.intersects(d.get_global_rect()))
func run() -> void:
	output=OS.get_cmdline_user_args()[0];app=root.get_node("AppState")
	root.size=Vector2i(640,360);root.content_scale_size=Vector2i(640,360);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	await process_frame
	current=load("res://scripts/battle_arena.gd")
	frozen=load(output.path_join("rpg-2-star-ocean-the-second_battle-pause_arena-frozen-before-layout_v01_"+TAG+".gd"))
	old_skin=load(output.path_join("rpg-2-star-ocean-the-second_battle-pause_skin-helper-frozen-before-layout_v01_"+TAG+".gd"))
	for lang in ["en","zh"]:
		for skin in [0,1]:
			for mode in ["normal","victory","defeat"]:
				var old:=await setup(true,skin,lang)
				if mode!="normal":old._finish_battle(mode=="victory")
				var before:=await capture(lang+str(skin)+"-"+mode+"-before");await dispose(old)
				var fixed:=await setup(false,skin,lang)
				if mode!="normal":fixed._finish_battle(mode=="victory")
				var after:=await capture(lang+str(skin)+"-"+mode+"-after")
				ck(lang+str(skin)+mode+"-exact-render-parity",before.get_data()==after.get_data());await dispose(fixed)
			for member in 4:
				var a:=await setup(false,skin,lang,member)
				ck("skin-"+str(skin),a.battle_ui_skin_status==("applied" if skin==1 else "off"))
				a.enemy_x=float(a.fighters[member].x)+30.0
				a._toggle_pause();await process_frame
				var key: String=lang+str(skin)+"-member"+str(member)
				layout(a,key+"-plain")
				var paused_state:=state(a)
				for tick in 30:a._process(1.0/60.0)
				ck(key+"-paused-simulation-frozen",paused_state==state(a))
				var id: String=a.fighters[member].id
				var energy:=int(app.member_state(id).energy)
				click(a.pause_skill_button.get_global_rect().get_center());await process_frame
				ck(key+"-personal-click-queues-only",a.queued_skill and int(app.member_state(id).energy)==energy)
				layout(a,key+"-personal-checkmark")
				click(a.pause_resume_button.get_global_rect().get_center());await process_frame
				var cost:=12 if member==0 else (16 if member==1 else 14)
				ck(key+"-resume-executes-personal",not a.paused and not a.queued_skill and int(app.member_state(id).energy)==energy-cost)
				a.fighters[member].skill_cooldown=0.0
				a._toggle_pause();await process_frame
				for stage in 2:
					energy=int(app.member_state(id).energy)
					var button: Button=a.pause_job_skill_buttons[stage]
					ck(key+"-both-job-stages-visible-"+str(stage),button.visible)
					click(button.get_global_rect().get_center());await process_frame
					var series: String=app.member_state(id).job_series
					ck(key+"-job-click-"+str(stage),a.queued_job_skill and a.queued_job_skill_id==GrowthRules.SERIES[series].skills[stage] and int(app.member_state(id).energy)==energy)
					layout(a,key+"-job-checkmark"+str(stage))
					click(a.pause_resume_button.get_global_rect().get_center());await process_frame
					ck(key+"-resume-executes-job-"+str(stage),not a.paused and not a.queued_job_skill and int(app.member_state(id).energy)==energy-(10+3*(stage+1)))
					a.fighters[member].skill_cooldown=0.0
					a._toggle_pause();await process_frame
				if member==0:
					a.queued_skill=true;a.queued_job_skill_id=GrowthRules.SERIES.sword.skills[1];a._refresh_text();await process_frame
					await capture(lang+str(skin)+"-pause-two-rows")
				await dispose(a)
	# Let two actual audio mix boundaries drain after test-owned stopped/detached players.
	var age:=AudioServer.get_time_since_last_mix();var mixes:=0;var deadline:=Time.get_ticks_usec()+500000
	while mixes<2 and Time.get_ticks_usec()<deadline:
		await create_timer(0.002).timeout
		var now:=AudioServer.get_time_since_last_mix()
		if now<age:mixes+=1
		age=now
	ck("two-real-audio-mix-drain",mixes>=2)
	var failed:=checks.filter(func(row):return not row.pass)
	var report: Dictionary={"passed":checks.size()-failed.size(),"total":checks.size(),"failures":failed,"checks":checks,"arenaRawSha256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"skinRawSha256":FileAccess.get_sha256("res://scripts/rpg-2-star-ocean-the-second_battle-ui_skin-helper_root-v02_20261019-172332-dc55a291.gd"),"artApproved":false,"audioMixes":mixes}
	var f:=FileAccess.open(output.path_join("rpg-2-star-ocean-the-second_battle-pause_layout-runtime-report_v01_"+TAG+".json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
	for row in failed:print("FAILED "+row.key)
	print("PAUSE_LAYOUT_DONE ",report.passed,"/",report.total);quit(0 if failed.is_empty() else 1)
