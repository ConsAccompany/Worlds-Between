extends Node2D

const ENEMIES := {
	"patrol": {"name": "enemy_patrol", "max_hp": 64, "damage": 12, "speed": 55.0, "windup": 0.65, "cooldown": 1.35, "color": Color("#ab5b52")},
	"sentry": {"name": "enemy_sentry", "max_hp": 96, "damage": 18, "speed": 68.0, "windup": 0.48, "cooldown": 1.10, "color": Color("#96516f")},
}
const MOVE_SPEED := 168.0
const ATTACK_RANGE := 61.0
const ATTACK_DAMAGE := 19
const DODGE_COST := 12
const GUARD_HIT_COST := 6

var enemy_id := "patrol"
var enemy: Dictionary
var player_x := 135.0
var enemy_x := 493.0
var enemy_hp := 0
var attack_cooldown := 0.0
var dodge_cooldown := 0.0
var dodge_time := 0.0
var dodge_direction := -1.0
var enemy_cooldown := 0.6
var enemy_windup := 0.0
var enemy_attack_count := 0
var player_attack_count := 0
var battle_finished := false
var battle_won := false
var feedback_key := "battle_ready"

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
var result_overlay: ColorRect
var result_title: Label
var result_note: Label
var result_button: Button


func _ready() -> void:
	enemy_id = AppState.battle_enemy_id if ENEMIES.has(AppState.battle_enemy_id) else "patrol"
	enemy = ENEMIES[enemy_id]
	enemy_hp = int(enemy["max_hp"])
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	AppState.last_battle_transition_ms = float(Time.get_ticks_usec() - AppState.battle_transition_started_usec) / 1000.0
	print("BATTLE_TRANSITION_MS %.2f" % AppState.last_battle_transition_ms)


func _process(delta: float) -> void:
	if battle_finished:
		return
	attack_cooldown = maxf(0.0, attack_cooldown - delta)
	dodge_cooldown = maxf(0.0, dodge_cooldown - delta)
	dodge_time = maxf(0.0, dodge_time - delta)
	if Input.is_action_just_pressed("battle_attack"):
		_try_attack()
	if Input.is_action_just_pressed("battle_dodge"):
		_try_dodge()
	var axis := Input.get_axis("move_left", "move_right")
	if dodge_time > 0.0:
		player_x += dodge_direction * 420.0 * delta
	else:
		player_x += axis * MOVE_SPEED * delta
	player_x = clampf(player_x, 28.0, 612.0)
	_update_enemy(delta)
	_update_hud()
	queue_redraw()


func _update_enemy(delta: float) -> void:
	if enemy_windup > 0.0:
		enemy_windup = maxf(0.0, enemy_windup - delta)
		if enemy_windup == 0.0:
			_apply_enemy_hit()
			enemy_cooldown = float(enemy["cooldown"])
		return
	if enemy_cooldown > 0.0:
		enemy_cooldown = maxf(0.0, enemy_cooldown - delta)
	var separation := absf(enemy_x - player_x)
	if separation > 53.0:
		enemy_x += signf(player_x - enemy_x) * float(enemy["speed"]) * delta
		enemy_x = clampf(enemy_x, 28.0, 612.0)
	elif enemy_cooldown == 0.0:
		enemy_windup = float(enemy["windup"])


func _try_attack() -> bool:
	if battle_finished or attack_cooldown > 0.0:
		return false
	attack_cooldown = 0.37
	player_attack_count += 1
	if absf(enemy_x - player_x) > ATTACK_RANGE:
		feedback_key = "battle_far"
		_update_hud()
		return false
	enemy_hp = maxi(0, enemy_hp - ATTACK_DAMAGE)
	feedback_key = "battle_hit"
	_update_hud()
	queue_redraw()
	if enemy_hp == 0:
		_finish_battle(true)
	return true


func _try_dodge() -> bool:
	if battle_finished or dodge_cooldown > 0.0:
		return false
	if int(AppState.hero_state["energy"]) < DODGE_COST:
		feedback_key = "battle_no_energy"
		_update_hud()
		return false
	AppState.hero_state["energy"] = int(AppState.hero_state["energy"]) - DODGE_COST
	dodge_cooldown = 0.75
	dodge_time = 0.27
	var axis := Input.get_axis("move_left", "move_right")
	dodge_direction = axis if axis != 0.0 else signf(player_x - enemy_x)
	_update_hud()
	return true


func _apply_enemy_hit() -> void:
	enemy_attack_count += 1
	if absf(enemy_x - player_x) > 69.0:
		return
	if dodge_time > 0.0:
		feedback_key = "battle_dodge_feedback"
		return
	var damage: int = int(enemy["damage"])
	if Input.is_action_pressed("battle_guard") and int(AppState.hero_state["energy"]) >= GUARD_HIT_COST:
		AppState.hero_state["energy"] = int(AppState.hero_state["energy"]) - GUARD_HIT_COST
		damage = maxi(1, ceili(float(damage) * 0.30))
		feedback_key = "battle_guard_feedback"
	else:
		feedback_key = "battle_hurt"
	AppState.hero_state["hp"] = maxi(0, int(AppState.hero_state["hp"]) - damage)
	_update_hud()
	if int(AppState.hero_state["hp"]) == 0:
		_finish_battle(false)


func _finish_battle(won: bool) -> void:
	if battle_finished:
		return
	battle_finished = true
	battle_won = won
	if won:
		AppState.hero_state = BattleRules.recover_after_battle(AppState.hero_state)
		AppState.enemy_cleared_for_return = true
		AppState.returning_from_battle = true
	else:
		AppState.hero_state["hp"] = 0
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


func _draw() -> void:
	var backdrop := Color("#2b4050") if enemy_id == "patrol" else Color("#463b4a")
	draw_rect(Rect2(0, 0, 640, 360), Color("#101a27"))
	draw_rect(Rect2(0, 68, 640, 234), backdrop)
	for x in range(0, 640, 40):
		draw_rect(Rect2(x, 248, 22, 3), Color("#8ca5a4"))
	draw_rect(Rect2(0, 268, 640, 34), Color("#718883"))
	draw_rect(Rect2(0, 296, 640, 6), Color("#394f55"))
	if enemy_id == "patrol":
		for x in range(35, 640, 120):
			draw_rect(Rect2(x, 100, 12, 148), Color("#334f5d"))
	else:
		for x in range(40, 640, 150):
			draw_rect(Rect2(x, 90, 25, 155), Color("#766b63"))
	_draw_player()
	if enemy_hp > 0:
		_draw_enemy()


func _draw_player() -> void:
	var body := Color("#88d7d0") if dodge_time > 0.0 else Color("#5eb6af")
	if Input.is_action_pressed("battle_guard"):
		body = Color("#91bdf1")
	draw_circle(Vector2(player_x, 238), 15.0, Color(0.09, 0.18, 0.21, 0.50))
	draw_rect(Rect2(player_x - 9, 223, 18, 39), body)
	draw_circle(Vector2(player_x, 215), 10.0, Color("#e5c594"))
	draw_rect(Rect2(player_x - 9, 262, 7, 9), Color("#263e4a"))
	draw_rect(Rect2(player_x + 2, 262, 7, 9), Color("#263e4a"))
	if Input.is_action_pressed("battle_guard"):
		draw_rect(Rect2(player_x + (13 if enemy_x > player_x else -20), 217, 6, 35), Color("#a7d7ee"))
	if attack_cooldown > 0.23:
		var reach := 19.0 if enemy_x > player_x else -42.0
		draw_rect(Rect2(player_x + reach, 225, 23, 5), Color("#e3ecde"))


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
	header.size = Vector2(640, 68)
	canvas.add_child(header)
	title_label = _label(canvas, Vector2(16, 4), 18, Color("#eef7ef"))
	hp_label = _label(canvas, Vector2(16, 38), 11, Color("#f2c8ad"))
	energy_label = _label(canvas, Vector2(228, 38), 11, Color("#9edbd9"))
	enemy_hp_label = _label(canvas, Vector2(438, 38), 11, Color("#e4adad"))
	hp_bar = _bar(canvas, Vector2(62, 39), Vector2(146, 11), Color("#d6736d"))
	energy_bar = _bar(canvas, Vector2(282, 39), Vector2(141, 11), Color("#62c9ce"))
	enemy_bar = _bar(canvas, Vector2(505, 39), Vector2(119, 11), Color("#bb6174"))
	telegraph_label = _label(canvas, Vector2(350, 186), 13, Color("#ffe0bf"))
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 302)
	footer.size = Vector2(640, 58)
	canvas.add_child(footer)
	feedback_label = _label(canvas, Vector2(16, 309), 12, Color("#f5d5a7"))
	help_label = _label(canvas, Vector2(16, 332), 11, Color("#aac6c6"))
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


func _refresh_text() -> void:
	title_label.text = AppState.text_for("battle_title") % AppState.text_for(String(enemy["name"]))
	hp_label.text = AppState.text_for("battle_hp")
	energy_label.text = AppState.text_for("battle_energy")
	enemy_hp_label.text = AppState.text_for("battle_enemy_hp")
	help_label.text = AppState.text_for("battle_help")
	telegraph_label.text = AppState.text_for("battle_telegraph")
	result_title.text = AppState.text_for("battle_win" if battle_won else "battle_loss")
	result_note.text = AppState.text_for("battle_win_note" if battle_won else "battle_loss_note")
	result_button.text = AppState.text_for("battle_continue" if battle_won else "battle_menu")
	_update_hud()


func _update_hud() -> void:
	hp_bar.max_value = int(AppState.hero_state["max_hp"])
	hp_bar.value = int(AppState.hero_state["hp"])
	energy_bar.max_value = int(AppState.hero_state["max_energy"])
	energy_bar.value = int(AppState.hero_state["energy"])
	enemy_bar.max_value = int(enemy["max_hp"])
	enemy_bar.value = enemy_hp
	feedback_label.text = "%s  %d/%d · %s  %d/%d · %s" % [AppState.text_for("battle_hp"), int(AppState.hero_state["hp"]), int(AppState.hero_state["max_hp"]), AppState.text_for("battle_energy"), int(AppState.hero_state["energy"]), int(AppState.hero_state["max_energy"]), AppState.text_for(feedback_key)]
	telegraph_label.visible = enemy_windup > 0.0 and not battle_finished
