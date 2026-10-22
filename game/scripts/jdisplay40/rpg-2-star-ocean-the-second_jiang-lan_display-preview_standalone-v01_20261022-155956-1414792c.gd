extends Control
# Standalone Jiang Lan character preview (test-only, explicit separate scene; not attached to ordinary flow).
# Portrait: exact display crop (UNAPPROVED). Actor: existing jexplore39 set at 0.5 through the generic
# exploration sprite set pilot with an explicit preview override; a bounded manual viewer of the same validated
# registry is used only when the pilot refuses (e.g. textures not imported in this checkout).

const Pilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const PORTRAIT := "res://assets/portraits/jiang-display40/rpg-2-star-ocean-the-second_jiang-lan_display-portrait-crop_v01_20261022-155956-1414792c.png"
const REGISTRY := "res://data/jexplore39/rpg-2-star-ocean-the-second_jiang-lan_explore-sprite-set-registry_unapproved-jexplore39-v01_20261022-154032-63facbc5.json"
const ACTOR := "jiang-lan"
const CARD := Vector2(640, 360)
const PORTRAIT_BOX := Rect2(16, 56, 180, 250)
const STAGE := Rect2(404, 64, 220, 220)
const SPEED := 40.0
const TEXT := {
	"en": {"title": "Character Preview", "pending": "Art pending", "name": "Jiang Lan",
		"career": "Engineering designer · 29",
		"identity": "Asymmetric tool vest,\norange cuffs, forehead goggles,\ntwo distinct waist devices",
		"idle": "Idle", "walk": "Walk", "hint": "Arrows: facing · WASD: move · Esc: exit"},
	"zh": {"title": "角色预览", "pending": "美术待定", "name": "蒋岚",
		"career": "工程设计师 · 29岁",
		"identity": "不对称工具背心、橙色袖口、\n额前护目镜、\n腰间两件不同装置",
		"idle": "待机", "walk": "行走", "hint": "方向键：朝向 · WASD：移动 · Esc：退出"},
}

var lang := "en"
var card: Control
var portrait: TextureRect
var actor: Sprite2D
var driver: Node = null
var binding := ""
var manual := {}
var manual_clock_us := 0
var facing := "south"
var action := "idle"
var held_walk := false
var actor_pos := Vector2.ZERO
var toggle_button: Button
var labels := {}


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--lang="):
			lang = "zh" if arg.substr(7) == "zh" else "en"
	var t: Dictionary = TEXT[lang]
	card = Control.new()
	card.size = CARD
	add_child(card)
	var bg := ColorRect.new()
	bg.color = Color(0.09, 0.11, 0.15)
	bg.size = CARD
	card.add_child(bg)
	labels["title"] = _label(t["title"], Vector2(16, 12), 18)
	labels["pending"] = _label(t["pending"], Vector2(520, 16), 12, Color(1.0, 0.72, 0.38))
	portrait = TextureRect.new()
	portrait.position = PORTRAIT_BOX.position
	portrait.size = PORTRAIT_BOX.size
	portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	portrait.texture = _load_texture(PORTRAIT)
	card.add_child(portrait)
	labels["name"] = _label(t["name"], Vector2(208, 64), 20)
	labels["career"] = _label(t["career"], Vector2(208, 96), 13)
	labels["identity"] = _label(t["identity"], Vector2(208, 124), 12, Color(0.8, 0.84, 0.9))
	var stage_bg := ColorRect.new()
	stage_bg.color = Color(0.16, 0.19, 0.24)
	stage_bg.position = STAGE.position
	stage_bg.size = STAGE.size
	stage_bg.clip_contents = true
	card.add_child(stage_bg)
	actor = Sprite2D.new()
	actor.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	actor_pos = STAGE.size * Vector2(0.5, 0.75)
	actor.position = actor_pos
	stage_bg.add_child(actor)
	_bind_actor()
	var y := STAGE.end.y + 8
	var x := STAGE.position.x
	for d in [["←", "west"], ["↑", "north"], ["↓", "south"], ["→", "east"]]:
		var b := _button(d[0], Vector2(x, y), Vector2(32, 24))
		b.name = "Face_" + d[1]
		b.pressed.connect(set_facing.bind(d[1]))
		x += 36
	toggle_button = _button(t["walk"], Vector2(x + 4, y), Vector2(68, 24))
	toggle_button.name = "ToggleAction"
	toggle_button.pressed.connect(toggle_action)
	labels["hint"] = _label(t["hint"], Vector2(16, 334), 11, Color(0.65, 0.7, 0.78))
	get_viewport().size_changed.connect(_fit)
	_fit()


func _fit() -> void:
	var vp := get_viewport_rect().size
	var s := minf(vp.x / CARD.x, vp.y / CARD.y)
	card.scale = Vector2(s, s)
	card.position = (vp - CARD * s) * 0.5


func _label(text: String, pos: Vector2, font_size: int, color := Color(0.93, 0.95, 0.98)) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	card.add_child(l)
	return l


func _button(text: String, pos: Vector2, sz: Vector2) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = sz
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", 12)
	card.add_child(b)
	return b


static func _load_texture(path: String) -> Texture2D:
	if ResourceLoader.exists(path, "Texture2D"):
		return ResourceLoader.load(path, "Texture2D") as Texture2D
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	return null if image == null or image.is_empty() else ImageTexture.create_from_image(image)


func _bind_actor() -> void:
	var saved_enabled := Pilot.enabled_override
	var saved_registry := Pilot.registry_override
	Pilot.enabled_override = 1
	Pilot.registry_override = REGISTRY
	Pilot.clear_cache()
	driver = Pilot.attach(actor, ACTOR, facing)
	Pilot.enabled_override = saved_enabled
	Pilot.registry_override = saved_registry
	if driver != null:
		binding = "pilot"
		return
	# Bounded manual viewer: same registry/set JSON, same frame timing rule, raw PNG pixels (no rescale/repaint).
	var reg = JSON.parse_string(FileAccess.get_file_as_string(REGISTRY))
	if typeof(reg) != TYPE_DICTIONARY or not reg.get("actors", {}).has(ACTOR):
		binding = "none"
		return
	var set_path: String = REGISTRY.get_base_dir().path_join(reg["actors"][ACTOR])
	var data = JSON.parse_string(FileAccess.get_file_as_string(set_path))
	if typeof(data) != TYPE_DICTIONARY or data.get("actor_id") != ACTOR:
		binding = "none"
		return
	var clips := {}
	for act in Pilot.ACTIONS:
		clips[act] = {}
		for dir in Pilot.DIRECTIONS:
			var textures := []
			var ends := []
			var total := 0
			for f in data["actions"][act][dir]:
				var tex := _load_texture(set_path.get_base_dir().path_join(f["file"]))
				if tex == null or Vector2i(tex.get_size()) != Vector2i(data["frame_size"][0], data["frame_size"][1]):
					binding = "none"
					return
				textures.append(tex)
				total += int(f["duration_ms"]) * 1000
				ends.append(total)
			clips[act][dir] = {"textures": textures, "ends_us": ends, "cycle_us": total}
	var density := int(data["density"])
	var frame_size := Vector2(data["frame_size"][0], data["frame_size"][1])
	var pivot := Vector2(data["pivot"][0], data["pivot"][1])
	actor.scale = Vector2.ONE / float(density)
	actor.offset = frame_size * 0.5 - pivot + Vector2(0.0, Pilot.FLOOR_DROP_LOGICAL * density)
	manual = {"set_id": data["set_id"], "density": density, "clips": clips}
	binding = "manual-viewer"
	_apply_manual()


func _apply_manual() -> void:
	if manual.is_empty():
		return
	var clip: Dictionary = manual["clips"][action][facing]
	actor.texture = clip["textures"][Pilot.frame_at(clip, manual_clock_us)]


func set_facing(next: String) -> void:
	if next == facing:
		return
	facing = next
	manual_clock_us = 0
	if driver != null:
		driver.face(next)
	_apply_manual()


func set_action(next: String) -> void:
	if next == action:
		return
	action = next
	manual_clock_us = 0
	if driver != null:
		if next == "walk":
			driver.walk()
		else:
			driver.idle()
	_apply_manual()
	toggle_button.text = TEXT[lang]["idle" if next == "walk" else "walk"]


func toggle_action() -> void:
	held_walk = action != "walk"
	set_action("walk" if held_walk else "idle")


func _process(delta: float) -> void:
	var move := Vector2(
		float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
		float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W)))
	if move != Vector2.ZERO:
		if absf(move.x) >= absf(move.y):
			set_facing("east" if move.x > 0 else "west")
		else:
			set_facing("south" if move.y > 0 else "north")
		set_action("walk")
		actor_pos = (actor_pos + move.normalized() * SPEED * delta).clamp(Vector2(20, 60), STAGE.size - Vector2(20, 8))
		actor.position = actor_pos.round()
	elif not held_walk:
		set_action("idle")
	if driver == null and not manual.is_empty():
		manual_clock_us += int(round(delta * 1000000.0))
		_apply_manual()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_ESCAPE: get_tree().quit()
			KEY_LEFT: set_facing("west")
			KEY_RIGHT: set_facing("east")
			KEY_UP: set_facing("north")
			KEY_DOWN: set_facing("south")


func state() -> Dictionary:
	return {"lang": lang, "binding": binding, "facing": facing, "action": action,
		"actor_scale": actor.scale, "actor_texture_size": actor.texture.get_size() if actor.texture else Vector2.ZERO,
		"portrait_size": portrait.texture.get_size() if portrait.texture else Vector2.ZERO}
