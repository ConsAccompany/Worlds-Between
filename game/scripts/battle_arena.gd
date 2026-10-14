extends Node2D

const ENEMIES := {
	"patrol": {"name": "enemy_patrol", "max_hp": 64, "damage": 12, "speed": 55.0, "windup": 0.65, "cooldown": 1.35, "color": Color("#ab5b52")},
	"sentry": {"name": "enemy_sentry", "max_hp": 96, "damage": 18, "speed": 68.0, "windup": 0.48, "cooldown": 1.10, "color": Color("#96516f")},
}
const MOVE_SPEED := 168.0
const DODGE_COST := 12
const GUARD_HIT_COST := 6

var enemy_id := "patrol"
var enemy: Dictionary
var enemy_x := 493.0
var enemy_hp := 0
var enemy_cooldown := 0.6
var enemy_windup := 0.0
var enemy_target_index := 0
var enemy_attack_count := 0
var player_attack_count := 0
var fighters: Array[Dictionary] = []
var controlled_index := 0
var auto_mode := false
var paused := false
var queued_skill := false
var selected_order_id := ""
var next_attack_bonus := 0
var battle_finished := false
var battle_won := false
var feedback_key := "battle_ready"
var feedback_message := ""

var title_label: Label
var help_label: Label
var feedback_label: Label
var hp_label: Label
var energy_label: Label
var enemy_hp_label: Label
var hp_bar: ProgressBar
var energy_bar: ProgressBar
var enemy_bar: ProgressBar
var telegraph_label: Label
var party_buttons: Array[Button] = []
var auto_button: Button
var quick_skill_button: Button
var pause_overlay: ColorRect
var pause_title: Label
var pause_skill_button: Button
var pause_target_label: Label
var pause_order_feedback: Label
var pause_policy_button: Button
var pause_target_buttons: Array[Button] = []
var pause_order_buttons: Dictionary = {}
var pause_resume_button: Button
var result_overlay: ColorRect
var result_title: Label
var result_note: Label
var result_button: Button


func _ready() -> void:
	enemy_id = AppState.battle_enemy_id if ENEMIES.has(AppState.battle_enemy_id) else "patrol"
	enemy = ENEMIES[enemy_id]
	enemy_hp = int(enemy["max_hp"])
	for index in AppState.active_party_ids.size():
		fighters.append({"id": AppState.active_party_ids[index], "x": 135.0 + index * 36.0, "attack_cooldown": 0.0, "dodge_cooldown": 0.0, "dodge_time": 0.0, "dodge_direction": -1.0, "skill_cooldown": 0.0, "command": "default", "guard": false, "boost": 0})
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	AppState.last_battle_transition_ms = float(Time.get_ticks_usec() - AppState.battle_transition_started_usec) / 1000.0
	print("BATTLE_TRANSITION_MS %.2f" % AppState.last_battle_transition_ms)


func _process(delta: float) -> void:
	if battle_finished or paused:
		return
	for fighter in fighters:
		fighter["attack_cooldown"] = maxf(0.0, float(fighter["attack_cooldown"]) - delta)
		fighter["dodge_cooldown"] = maxf(0.0, float(fighter["dodge_cooldown"]) - delta)
		fighter["dodge_time"] = maxf(0.0, float(fighter["dodge_time"]) - delta)
		fighter["skill_cooldown"] = maxf(0.0, float(fighter["skill_cooldown"]) - delta)
		if float(fighter["dodge_time"]) > 0.0:
			fighter["x"] = clampf(float(fighter["x"]) + float(fighter["dodge_direction"]) * 420.0 * delta, 28.0, 612.0)
	if not auto_mode and _is_alive(controlled_index):
		var current: Dictionary = fighters[controlled_index]
		current["guard"] = Input.is_action_pressed("battle_guard")
		if Input.is_action_just_pressed("battle_attack"):
			_try_attack()
		if Input.is_action_just_pressed("battle_dodge"):
			_try_dodge()
		if Input.is_action_just_pressed("battle_skill"):
			_use_skill()
		if float(current["dodge_time"]) == 0.0:
			current["x"] = clampf(float(current["x"]) + Input.get_axis("move_left", "move_right") * MOVE_SPEED * delta, 28.0, 612.0)
	for index in fighters.size():
		if battle_finished:
			break
		if auto_mode or index != controlled_index:
			_update_ai(index, delta)
	if not battle_finished:
		_update_enemy(delta)
	_update_hud()
	queue_redraw()


func _is_alive(index: int) -> bool:
	return index >= 0 and index < fighters.size() and int(AppState.member_state(String(fighters[index]["id"]))["hp"]) > 0


func _nearest_living() -> int:
	var best := -1
	var distance := INF
	for index in fighters.size():
		if not _is_alive(index):
			continue
		var current := absf(enemy_x - float(fighters[index]["x"]))
		if current < distance:
			best = index
			distance = current
	return best


func _update_ai(index: int, delta: float) -> void:
	if not _is_alive(index) or battle_finished:
		return
	var fighter: Dictionary = fighters[index]
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	var definition: Dictionary = AppState.MEMBER_DEFS[String(fighter["id"])]
	var separation := absf(enemy_x - float(fighter["x"]))
	var command: String = fighter["command"]
	var policy: String = member.get("ai_policy", "balanced")
	fighter["guard"] = (command == "defend" or (command == "default" and policy == "cautious")) and enemy_windup > 0.0 and separation < 85.0
	if enemy_windup > 0.0 and separation < 85.0 and command != "focus" and command != "defend" and policy != "aggressive" and policy != "cautious":
		if int(member["energy"]) >= DODGE_COST and float(fighter["dodge_cooldown"]) == 0.0:
			_try_dodge(index)
			return
	if float(fighter["dodge_time"]) > 0.0:
		return
	if (command == "skill" or (command == "default" and policy == "aggressive")) and float(fighter["skill_cooldown"]) == 0.0 and int(member["energy"]) >= 14:
		if _use_skill(index):
			return
	if separation > float(definition["attack_range"]) - 8.0:
		fighter["x"] = clampf(float(fighter["x"]) + signf(enemy_x - float(fighter["x"])) * MOVE_SPEED * 0.72 * delta, 28.0, 612.0)
	elif float(fighter["attack_cooldown"]) == 0.0:
		_try_attack(index)


func _update_enemy(delta: float) -> void:
	if enemy_windup > 0.0:
		enemy_windup = maxf(0.0, enemy_windup - delta)
		if enemy_windup == 0.0:
			_apply_enemy_hit()
			enemy_cooldown = float(enemy["cooldown"])
		return
	if enemy_cooldown > 0.0:
		enemy_cooldown = maxf(0.0, enemy_cooldown - delta)
	var target := _nearest_living()
	if target < 0:
		_finish_battle(false)
		return
	var separation := absf(enemy_x - float(fighters[target]["x"]))
	if separation > 53.0:
		enemy_x = clampf(enemy_x + signf(float(fighters[target]["x"]) - enemy_x) * float(enemy["speed"]) * delta, 28.0, 612.0)
	elif enemy_cooldown == 0.0:
		enemy_target_index = target
		enemy_windup = float(enemy["windup"])


func _try_attack(index: int = -1) -> bool:
	if index < 0:
		index = controlled_index
	if battle_finished or not _is_alive(index):
		return false
	var fighter: Dictionary = fighters[index]
	if float(fighter["attack_cooldown"]) > 0.0:
		return false
	fighter["attack_cooldown"] = 0.43
	player_attack_count += 1
	var definition: Dictionary = AppState.MEMBER_DEFS[String(fighter["id"])]
	if absf(enemy_x - float(fighter["x"])) > float(definition["attack_range"]):
		if index == controlled_index:
			feedback_message = ""
			feedback_key = "battle_far"
		return false
	var damage := int(definition["attack_damage"]) + int(fighter["boost"]) + next_attack_bonus
	fighter["boost"] = 0
	next_attack_bonus = 0
	enemy_hp = maxi(0, enemy_hp - damage)
	feedback_message = ""
	feedback_key = "battle_hit"
	if enemy_hp == 0:
		_finish_battle(true)
	return true


func _try_dodge(index: int = -1) -> bool:
	if index < 0:
		index = controlled_index
	if battle_finished or not _is_alive(index):
		return false
	var fighter: Dictionary = fighters[index]
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	if float(fighter["dodge_cooldown"]) > 0.0:
		return false
	if int(member["energy"]) < DODGE_COST:
		feedback_message = ""
		feedback_key = "battle_no_energy"
		return false
	member["energy"] = int(member["energy"]) - DODGE_COST
	fighter["dodge_cooldown"] = 0.75
	fighter["dodge_time"] = 0.27
	var axis := Input.get_axis("move_left", "move_right") if index == controlled_index and not auto_mode else 0.0
	fighter["dodge_direction"] = axis if axis != 0.0 else signf(float(fighter["x"]) - enemy_x)
	return true


func _use_skill(index: int = -1) -> bool:
	if index < 0:
		index = controlled_index
	if battle_finished or not _is_alive(index):
		return false
	var fighter: Dictionary = fighters[index]
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	var member_id: String = fighter["id"]
	var cost := 16 if member_id == "liang-xu" else 14
	if member_id == "hero":
		cost = 12
	if int(member["energy"]) < cost:
		feedback_message = ""
		feedback_key = "battle_no_energy"
		return false
	if float(fighter["skill_cooldown"]) > 0.0:
		return false
	member["energy"] = int(member["energy"]) - cost
	fighter["skill_cooldown"] = 2.2
	match member_id:
		"hero":
			next_attack_bonus += 5
		"liang-xu":
			for ally in fighters:
				if ally != fighter and int(AppState.member_state(String(ally["id"]))["hp"]) > 0:
					ally["command"] = "focus"
					ally["boost"] = int(ally["boost"]) + 4
		"zhao-ling":
			next_attack_bonus += 8
		"ji-cheng":
			enemy_windup += 0.65 if enemy_windup > 0.0 else 0.0
			enemy_cooldown += 0.65
	feedback_message = AppState.text_for("battle_skill_used") % [AppState.member_name(member_id), AppState.text_for(String(AppState.MEMBER_DEFS[member_id]["skill_key"]))]
	return true


func _apply_enemy_hit() -> void:
	enemy_attack_count += 1
	var index := enemy_target_index if _is_alive(enemy_target_index) else _nearest_living()
	if index < 0:
		_finish_battle(false)
		return
	var fighter: Dictionary = fighters[index]
	if absf(enemy_x - float(fighter["x"])) > 69.0:
		return
	if float(fighter["dodge_time"]) > 0.0:
		feedback_message = ""
		feedback_key = "battle_dodge_feedback"
		return
	var member: Dictionary = AppState.member_state(String(fighter["id"]))
	var damage: int = int(enemy["damage"])
	feedback_message = ""
	if bool(fighter["guard"]) or (index == controlled_index and not auto_mode and Input.is_action_pressed("battle_guard")):
		if int(member["energy"]) >= GUARD_HIT_COST:
			member["energy"] = int(member["energy"]) - GUARD_HIT_COST
			damage = maxi(1, ceili(float(damage) * 0.30))
			feedback_key = "battle_guard_feedback"
		else:
			feedback_key = "battle_hurt"
	else:
		feedback_key = "battle_hurt"
	member["hp"] = maxi(0, int(member["hp"]) - damage)
	if int(member["hp"]) == 0:
		feedback_message = AppState.text_for("battle_member_down") % AppState.member_name(String(fighter["id"]))
		if index == controlled_index:
			_select_next_living()
		if _nearest_living() < 0:
			_finish_battle(false)


func _select_next_living() -> void:
	for offset in range(1, fighters.size() + 1):
		var next := (controlled_index + offset) % fighters.size()
		if _is_alive(next):
			controlled_index = next
			return


func _switch_control() -> void:
	if paused or battle_finished:
		return
	_select_next_living()
	auto_mode = false
	feedback_message = ""
	_refresh_text()


func _toggle_auto() -> void:
	if paused or battle_finished:
		return
	auto_mode = not auto_mode
	_refresh_text()


func _toggle_pause() -> void:
	if battle_finished:
		return
	paused = not paused
	pause_overlay.visible = paused
	if paused:
		selected_order_id = ""
		for fighter in fighters:
			if String(fighter["id"]) != String(fighters[controlled_index]["id"]) and int(AppState.member_state(String(fighter["id"]))["hp"]) > 0:
				selected_order_id = fighter["id"]
				break
		_refresh_text()
		pause_resume_button.grab_focus()
	else:
		if queued_skill:
			queued_skill = false
			_use_skill(controlled_index)
		_refresh_text()


func _queue_skill() -> void:
	queued_skill = true
	_refresh_text()


func _select_order_target(member_id: String) -> void:
	selected_order_id = member_id
	_refresh_text()


func _issue_order(command: String) -> void:
	for fighter in fighters:
		if String(fighter["id"]) == selected_order_id:
			fighter["command"] = command
			feedback_key = "battle_" + ("skill_order" if command == "skill" else command)
			break
	_refresh_text()


func _cycle_ai_policy() -> void:
	if selected_order_id == "":
		return
	var member: Dictionary = AppState.member_state(selected_order_id)
	var policies := ["balanced", "aggressive", "cautious"]
	var current: String = member.get("ai_policy", "balanced")
	member["ai_policy"] = policies[(policies.find(current) + 1) % policies.size()]
	_refresh_text()


func _finish_battle(won: bool) -> void:
	if battle_finished:
		return
	battle_finished = true
	paused = false
	pause_overlay.visible = false
	battle_won = won
	if won:
		for fighter in fighters:
			var member_id: String = fighter["id"]
			var recovered := BattleRules.recover_after_battle(AppState.member_state(member_id))
			if member_id == "hero":
				AppState.hero_state = recovered
			else:
				AppState.member_states[member_id] = recovered
		AppState.enemy_cleared_for_return = true
		AppState.returning_from_battle = true
	else:
		AppState.enemy_cleared_for_return = false
		AppState.returning_from_battle = false
		get_tree().create_timer(2.0).timeout.connect(_return_to_menu)
	result_overlay.visible = true
	_refresh_text()
	result_button.grab_focus()
	queue_redraw()


func _return_after_result() -> void:
	if battle_won:
		AppState.battle_enemy_id = ""
		get_tree().change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	else:
		_return_to_menu()


func _return_to_menu() -> void:
	if not is_inside_tree():
		return
	AppState.battle_enemy_id = ""
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("battle_pause") or (paused and event.is_action_pressed("ui_cancel")):
		_toggle_pause()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("battle_switch"):
		_switch_control()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("battle_auto"):
		_toggle_auto()
		get_viewport().set_input_as_handled()


func _draw() -> void:
	var backdrop := Color("#2b4050") if enemy_id == "patrol" else Color("#463b4a")
	draw_rect(Rect2(0, 0, 640, 360), Color("#101a27"))
	draw_rect(Rect2(0, 89, 640, 213), backdrop)
	for x in range(0, 640, 40):
		draw_rect(Rect2(x, 248, 22, 3), Color("#8ca5a4"))
	draw_rect(Rect2(0, 268, 640, 34), Color("#718883"))
	draw_rect(Rect2(0, 296, 640, 6), Color("#394f55"))
	for x in range(35, 640, 120 if enemy_id == "patrol" else 150):
		draw_rect(Rect2(x, 101, 12 if enemy_id == "patrol" else 25, 145), Color("#334f5d") if enemy_id == "patrol" else Color("#766b63"))
	for index in fighters.size():
		_draw_fighter(fighters[index], index)
	if enemy_hp > 0:
		_draw_enemy()


func _draw_fighter(fighter: Dictionary, index: int) -> void:
	var x: float = fighter["x"]
	var member_id: String = fighter["id"]
	var color: Color = AppState.MEMBER_DEFS[member_id]["color"]
	if not _is_alive(index):
		draw_rect(Rect2(x - 12, 263, 24, 5), Color("#56636d"))
		return
	if index == controlled_index and not auto_mode:
		draw_circle(Vector2(x, 272), 13.0, Color("#f5e1a6"))
	if float(fighter["dodge_time"]) > 0.0:
		color = color.lightened(0.25)
	draw_circle(Vector2(x, 239), 15.0, Color(0.09, 0.18, 0.21, 0.50))
	draw_rect(Rect2(x - 9, 223, 18, 39), color)
	draw_circle(Vector2(x, 215), 10.0, Color("#e5c594"))
	match member_id:
		"hero":
			draw_rect(Rect2(x - 9, 203, 18, 5), Color("#273f47"))
		"liang-xu":
			draw_rect(Rect2(x - 10, 202, 19, 5), Color("#c3c4c2"))
			draw_circle(Vector2(x + 11, 207), 5.0, Color("#b3b9ba"))
			draw_rect(Rect2(x + 6, 233, 8, 14), Color("#9b8162"))
		"zhao-ling":
			draw_rect(Rect2(x - 10, 202, 19, 5), Color("#293743"))
			draw_circle(Vector2(x - 10, 215), 4.0, Color("#65c5dc"))
			draw_circle(Vector2(x + 10, 215), 4.0, Color("#65c5dc"))
		"ji-cheng":
			draw_rect(Rect2(x - 10, 202, 14, 6), Color("#abb7b7"))
			draw_rect(Rect2(x + 5, 207, 5, 14), Color("#303a42"))
	draw_rect(Rect2(x - 9, 262, 7, 9), Color("#263e4a"))
	draw_rect(Rect2(x + 2, 262, 7, 9), Color("#263e4a"))
	if bool(fighter["guard"]):
		draw_rect(Rect2(x + (13 if enemy_x > x else -20), 217, 6, 35), Color("#a7d7ee"))
	if float(fighter["attack_cooldown"]) > 0.30:
		draw_rect(Rect2(x + (19 if enemy_x > x else -42), 225, 23, 5), Color("#e3ecde"))


func _draw_enemy() -> void:
	var color: Color = enemy["color"]
	if enemy_windup > 0.0:
		draw_circle(Vector2(enemy_x, 240), 30.0, Color(1.0, 0.23, 0.20, 0.28))
	draw_circle(Vector2(enemy_x, 241), 20.0, Color(0.14, 0.14, 0.21, 0.55))
	draw_rect(Rect2(enemy_x - 17, 217, 34, 41), color)
	draw_rect(Rect2(enemy_x - 11, 227, 22, 9), Color("#f4b293"))
	draw_rect(Rect2(enemy_x - 17, 257, 10, 12), Color("#343a43"))
	draw_rect(Rect2(enemy_x + 7, 257, 10, 12), Color("#343a43"))


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 90)
	canvas.add_child(header)
	title_label = _label(canvas, Vector2(16, 4), 18, Color("#eef7ef"))
	quick_skill_button = Button.new()
	quick_skill_button.position = Vector2(430, 6)
	quick_skill_button.size = Vector2(194, 27)
	quick_skill_button.add_theme_font_size_override("font_size", 11)
	quick_skill_button.pressed.connect(func(): _use_skill())
	canvas.add_child(quick_skill_button)
	hp_label = _label(canvas, Vector2(16, 38), 11, Color("#f2c8ad"))
	energy_label = _label(canvas, Vector2(228, 38), 11, Color("#9edbd9"))
	enemy_hp_label = _label(canvas, Vector2(438, 38), 11, Color("#e4adad"))
	hp_bar = _bar(canvas, Vector2(62, 39), Vector2(146, 11), Color("#d6736d"))
	energy_bar = _bar(canvas, Vector2(282, 39), Vector2(141, 11), Color("#62c9ce"))
	enemy_bar = _bar(canvas, Vector2(505, 39), Vector2(119, 11), Color("#bb6174"))
	for slot in AppState.PARTY_CAPACITY:
		var button := Button.new()
		button.position = Vector2(15 + slot * 103, 65)
		button.size = Vector2(98, 20)
		button.add_theme_font_size_override("font_size", 10)
		button.pressed.connect(_choose_control.bind(slot))
		canvas.add_child(button)
		party_buttons.append(button)
	auto_button = Button.new()
	auto_button.position = Vector2(535, 65)
	auto_button.size = Vector2(91, 20)
	auto_button.add_theme_font_size_override("font_size", 10)
	auto_button.pressed.connect(_toggle_auto)
	canvas.add_child(auto_button)
	telegraph_label = _label(canvas, Vector2(350, 186), 13, Color("#ffe0bf"))
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 302)
	footer.size = Vector2(640, 58)
	canvas.add_child(footer)
	feedback_label = _label(canvas, Vector2(16, 309), 12, Color("#f5d5a7"))
	help_label = _label(canvas, Vector2(16, 332), 11, Color("#aac6c6"))
	_build_pause_overlay(canvas)
	_build_result_overlay(canvas)


func _label(parent: Node, position: Vector2, font_size: int, font_color: Color) -> Label:
	var label := Label.new()
	label.position = position
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", font_color)
	parent.add_child(label)
	return label


func _bar(parent: Node, position: Vector2, size: Vector2, fill: Color) -> ProgressBar:
	var bar := ProgressBar.new()
	bar.position = position
	bar.size = size
	bar.show_percentage = false
	bar.add_theme_stylebox_override("background", _style(Color("#273744")))
	bar.add_theme_stylebox_override("fill", _style(fill))
	parent.add_child(bar)
	return bar


func _style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	return style


func _build_pause_overlay(canvas: CanvasLayer) -> void:
	pause_overlay = ColorRect.new()
	pause_overlay.color = Color(0.04, 0.07, 0.12, 0.89)
	pause_overlay.size = Vector2(640, 360)
	pause_overlay.visible = false
	canvas.add_child(pause_overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(55, 43)
	panel.size = Vector2(530, 265)
	panel.color = Color("#263945")
	pause_overlay.add_child(panel)
	pause_title = _label(pause_overlay, Vector2(78, 57), 19, Color("#f2e7c8"))
	pause_skill_button = Button.new()
	pause_skill_button.position = Vector2(78, 99)
	pause_skill_button.size = Vector2(270, 36)
	pause_skill_button.pressed.connect(_queue_skill)
	pause_overlay.add_child(pause_skill_button)
	pause_resume_button = Button.new()
	pause_resume_button.position = Vector2(385, 99)
	pause_resume_button.size = Vector2(169, 36)
	pause_resume_button.pressed.connect(_toggle_pause)
	pause_overlay.add_child(pause_resume_button)
	pause_target_label = _label(pause_overlay, Vector2(78, 151), 12, Color("#bfd7d3"))
	pause_order_feedback = _label(pause_overlay, Vector2(78, 272), 11, Color("#d8c99f"))
	pause_policy_button = Button.new()
	pause_policy_button.position = Vector2(365, 144)
	pause_policy_button.size = Vector2(189, 27)
	pause_policy_button.add_theme_font_size_override("font_size", 11)
	pause_policy_button.pressed.connect(_cycle_ai_policy)
	pause_overlay.add_child(pause_policy_button)
	for slot in 4:
		var button := Button.new()
		button.position = Vector2(78 + slot * 119, 176)
		button.size = Vector2(111, 28)
		button.add_theme_font_size_override("font_size", 10)
		pause_overlay.add_child(button)
		pause_target_buttons.append(button)
	for command in ["focus", "defend", "skill"]:
		var button := Button.new()
		button.position = Vector2(78 + pause_order_buttons.size() * 160, 226)
		button.size = Vector2(148, 37)
		button.pressed.connect(_issue_order.bind(command))
		pause_overlay.add_child(button)
		pause_order_buttons[command] = button


func _build_result_overlay(canvas: CanvasLayer) -> void:
	result_overlay = ColorRect.new()
	result_overlay.color = Color(0.04, 0.07, 0.12, 0.88)
	result_overlay.size = Vector2(640, 360)
	result_overlay.visible = false
	canvas.add_child(result_overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(112, 99)
	panel.size = Vector2(416, 171)
	panel.color = Color("#263945")
	result_overlay.add_child(panel)
	result_title = _label(result_overlay, Vector2(139, 117), 22, Color("#f2e7c8"))
	result_note = _label(result_overlay, Vector2(139, 158), 12, Color("#c6dcda"))
	result_note.size = Vector2(355, 50)
	result_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	result_button = Button.new()
	result_button.position = Vector2(333, 219)
	result_button.size = Vector2(168, 33)
	result_button.pressed.connect(_return_after_result)
	result_overlay.add_child(result_button)


func _choose_control(index: int) -> void:
	if paused or battle_finished or not _is_alive(index):
		return
	controlled_index = index
	auto_mode = false
	_refresh_text()


func _refresh_text() -> void:
	title_label.text = AppState.text_for("battle_title") % AppState.text_for(String(enemy["name"]))
	hp_label.text = AppState.text_for("battle_hp")
	energy_label.text = AppState.text_for("battle_energy")
	enemy_hp_label.text = AppState.text_for("battle_enemy_hp")
	help_label.text = AppState.text_for("battle_help")
	telegraph_label.text = AppState.text_for("battle_telegraph")
	auto_button.text = AppState.text_for("battle_auto_on" if auto_mode else "battle_auto_off")
	pause_title.text = AppState.text_for("battle_pause_title") % AppState.member_name(String(fighters[controlled_index]["id"]))
	var skill_key: String = AppState.MEMBER_DEFS[String(fighters[controlled_index]["id"])]["skill_key"]
	quick_skill_button.text = "Q · " + AppState.text_for(skill_key)
	pause_skill_button.text = AppState.text_for("battle_skill_use") + " · " + AppState.text_for(skill_key) + (" ✓" if queued_skill else "")
	pause_resume_button.text = AppState.text_for("battle_resume")
	pause_target_label.text = AppState.text_for("battle_target") % (AppState.member_name(selected_order_id) if selected_order_id != "" else "—")
	pause_policy_button.disabled = selected_order_id == ""
	pause_policy_button.text = AppState.text_for("ai_policy_" + String(AppState.member_state(selected_order_id).get("ai_policy", "balanced"))) if selected_order_id != "" else "AI —"
	pause_order_feedback.text = ""
	for fighter in fighters:
		if String(fighter["id"]) == selected_order_id:
			var order: String = fighter["command"]
			pause_order_feedback.text = AppState.member_name(selected_order_id) + " · " + AppState.text_for("battle_" + ("skill_order" if order == "skill" else order))
			break
	for command in pause_order_buttons:
		pause_order_buttons[command].text = AppState.text_for("battle_" + ("skill_order" if command == "skill" else command))
		pause_order_buttons[command].disabled = selected_order_id == ""
	var targets: Array[String] = []
	for fighter in fighters:
		if String(fighter["id"]) != String(fighters[controlled_index]["id"]) and int(AppState.member_state(String(fighter["id"]))["hp"]) > 0:
			targets.append(String(fighter["id"]))
	for slot in pause_target_buttons.size():
		var button: Button = pause_target_buttons[slot]
		button.visible = slot < targets.size()
		if slot < targets.size():
			button.text = AppState.member_name(targets[slot])
			if not button.pressed.is_connected(_select_order_target.bind(targets[slot])):
				for connection in button.pressed.get_connections():
					button.pressed.disconnect(connection["callable"])
				button.pressed.connect(_select_order_target.bind(targets[slot]))
	result_title.text = AppState.text_for("battle_win" if battle_won else "battle_loss")
	result_note.text = AppState.text_for("battle_win_note" if battle_won else "battle_loss_note")
	result_button.text = AppState.text_for("battle_continue" if battle_won else "battle_menu")
	_update_hud()


func _update_hud() -> void:
	var member_id: String = fighters[controlled_index]["id"]
	var member: Dictionary = AppState.member_state(member_id)
	hp_bar.max_value = int(member["max_hp"])
	hp_bar.value = int(member["hp"])
	energy_bar.max_value = int(member["max_energy"])
	energy_bar.value = int(member["energy"])
	enemy_bar.max_value = int(enemy["max_hp"])
	enemy_bar.value = enemy_hp
	feedback_label.text = "%s  %d/%d · %d/%d · %s" % [AppState.member_name(member_id), int(member["hp"]), int(member["max_hp"]), int(member["energy"]), int(member["max_energy"]), feedback_message if feedback_message != "" else AppState.text_for(feedback_key)]
	quick_skill_button.disabled = battle_finished or paused or auto_mode or not _is_alive(controlled_index)
	telegraph_label.visible = enemy_windup > 0.0 and not battle_finished
	for slot in AppState.PARTY_CAPACITY:
		var button: Button = party_buttons[slot]
		button.disabled = slot >= fighters.size() or (slot < fighters.size() and not _is_alive(slot))
		button.text = "%d %s" % [slot + 1, AppState.member_name(String(fighters[slot]["id"]))] if slot < fighters.size() else "%d —" % [slot + 1]
