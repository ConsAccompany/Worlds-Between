extends CanvasLayer

# Settings overlay opened from the title screen's Settings button or F10 anywhere. Native basic
# controls only (functional UI; final UI art not approved). Built the first time it opens, so it adds
# nothing to any screen until requested. Every change applies and saves at once through GameSettings.

const PANEL_RECT := Rect2(60, 34, 520, 292)

var settings: GameSettings
var app: Node
var blocker: ColorRect
var title_label: Label
var status_label: Label
var language_label: Label
var zh_button: Button
var en_button: Button
var volume_label: Label
var volume_slider: HSlider
var volume_value: Label
var movement_label: Label
var default_button: Button
var arrows_button: Button
var note_label: Label
var current_label: Label
var reset_button: Button
var close_button: Button


func _ready() -> void:
	layer = 100
	app = settings.app
	_build_ui()
	app.language_changed.connect(_refresh)
	settings.settings_changed.connect(_refresh)
	visible = false


func show_overlay() -> void:
	_refresh()
	visible = true
	(en_button if app.language == "en" else zh_button).grab_focus()


func hide_overlay() -> void:
	visible = false


func _build_ui() -> void:
	blocker = ColorRect.new()
	blocker.color = Color(0.02, 0.04, 0.06, 0.72)
	blocker.size = Vector2(640, 360)
	blocker.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(blocker)

	var panel := Panel.new()
	panel.position = PANEL_RECT.position
	panel.size = PANEL_RECT.size
	var style := StyleBoxFlat.new()
	style.bg_color = Color("#13202d")
	style.border_color = Color("#54c4be")
	style.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", style)
	blocker.add_child(panel)

	var column := VBoxContainer.new()
	column.position = Vector2(14, 10)
	column.size = PANEL_RECT.size - Vector2(28, 20)
	column.add_theme_constant_override("separation", 8)
	panel.add_child(column)

	var header := HBoxContainer.new()
	column.add_child(header)
	title_label = _label(header, 18, Color("#eff9f6"))
	title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	status_label = _label(header, 12, Color("#9dbbc0"))

	var language_row := _row(column)
	language_label = _label(language_row, 14, Color("#d8ecea"), 120)
	var language_group := ButtonGroup.new()
	zh_button = _toggle(language_row, language_group, settings.set_language.bind("zh"))
	en_button = _toggle(language_row, language_group, settings.set_language.bind("en"))

	var volume_row := _row(column)
	volume_label = _label(volume_row, 14, Color("#d8ecea"), 120)
	volume_slider = HSlider.new()
	volume_slider.min_value = 0
	volume_slider.max_value = 100
	volume_slider.step = 5
	volume_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	volume_slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	volume_slider.value_changed.connect(func(value: float): settings.set_master_volume(int(value)))
	volume_row.add_child(volume_slider)
	volume_value = _label(volume_row, 14, Color("#eff9f6"), 48)
	volume_value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	var movement_row := _row(column)
	movement_label = _label(movement_row, 14, Color("#d8ecea"), 120)
	var preset_group := ButtonGroup.new()
	default_button = _toggle(movement_row, preset_group, settings.set_movement_preset.bind(GameSettings.PRESET_DEFAULT))
	arrows_button = _toggle(movement_row, preset_group, settings.set_movement_preset.bind(GameSettings.PRESET_ARROWS))

	note_label = _label(column, 12, Color("#9dbbc0"))
	note_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	current_label = _label(column, 12, Color("#eff9f6"))
	current_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(spacer)

	var buttons := _row(column)
	reset_button = _button(buttons, settings.reset_defaults)
	var gap := Control.new()
	gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	buttons.add_child(gap)
	close_button = _button(buttons, settings.close)


func _row(parent: Node) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	row.custom_minimum_size = Vector2(0, 30)
	parent.add_child(row)
	return row


func _label(parent: Node, font_size: int, color: Color, width := 0) -> Label:
	var label := Label.new()
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	if width > 0:
		label.custom_minimum_size = Vector2(width, 0)
	parent.add_child(label)
	return label


func _button(parent: Node, callback: Callable) -> Button:
	var button := Button.new()
	button.add_theme_font_size_override("font_size", 14)
	button.custom_minimum_size = Vector2(0, 30)
	button.pressed.connect(callback)
	parent.add_child(button)
	return button


func _toggle(parent: Node, group: ButtonGroup, callback: Callable) -> Button:
	var button := _button(parent, callback)
	button.toggle_mode = true
	button.button_group = group
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return button


func _refresh() -> void:
	if title_label == null:
		return
	title_label.text = app.text_for("settings_title")
	status_label.text = app.text_for("settings_status")
	language_label.text = app.text_for("settings_language")
	_set_choice(zh_button, "中文", app.language == "zh")
	_set_choice(en_button, "English", app.language == "en")
	volume_label.text = app.text_for("settings_volume")
	volume_slider.set_value_no_signal(settings.master_volume)
	volume_value.text = "%d%%" % settings.master_volume
	movement_label.text = app.text_for("settings_movement")
	_set_choice(default_button, app.text_for("settings_preset_default"), settings.movement_preset == GameSettings.PRESET_DEFAULT)
	_set_choice(arrows_button, app.text_for("settings_preset_arrows"), settings.movement_preset == GameSettings.PRESET_ARROWS)
	note_label.text = app.text_for("settings_preset_note")
	current_label.text = app.text_for("settings_current_help") % app.text_for("area_help")
	reset_button.text = app.text_for("settings_reset")
	close_button.text = app.text_for("settings_close")


# The default theme's pressed style is subtle, so the chosen option also carries a check mark.
func _set_choice(button: Button, label: String, chosen: bool) -> void:
	button.text = ("✓ " if chosen else "") + label
	button.set_pressed_no_signal(chosen)
