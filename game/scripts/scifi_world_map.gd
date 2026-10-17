extends Node2D

# Global Earth map. Land and coast come from Natural Earth geodata, places from the
# world-map registry, both projected from real lon/lat (world_geo_projection.gd).
# Two layers share one interaction model: the whole-Earth view (plate carrée, 110m
# land) and a regional view (equidistant cylindrical at the region's latitude, 50m
# land plus approximate roads). The party never walks here; picking a place opens
# a route card, and travel numbers come only from the AppState route API. Every marker
# uses the travel data's coordinates (see world_map_route_adapter.gd). Leaving for another
# place always goes through confirm_travel(); without the route API nobody can depart.

# Default walkable scene; AppState.area_scene_path() names the scene for each destination.
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const GeoProjection := preload("res://scripts/world_geo_projection.gd")
const MapData := preload("res://scripts/world_map_data.gd")
const MapText := preload("res://scripts/world_map_text.gd")
const RouteAdapter := preload("res://scripts/world_map_route_adapter.gd")

const MAP_RECT := Rect2(0, 44, 640, 268)
const CARD_RECT := Rect2(424, 48, 210, 238)
# Where a region's places are framed, in map-local pixels, clear of the route card.
const REGION_FRAME := Rect2(150, 44, 230, 116)
# Map-status line (open regions, or the region name) in the map's top-left corner.
const STATUS_POS := Vector2(6, 4)
const STATUS_MAX_TEXT_WIDTH := 264.0
# Scale bar in the regional view, below the lowest framed marker and right of the view buttons.
const SCALE_BAR_ORIGIN := Vector2(200, 258)
# Space the scale bar and its "100 km" text may take; labels and the route inset keep clear of it.
const SCALE_BAR_RECT := Rect2(199, 250, 140, 14)
# Clear pixels kept between a marker label and fixed controls, other labels or other markers.
const LABEL_GAP := 3.0
# Label slots tried after the place's own label_side, in this order. Diagonal slots sit off the marker's corner.
const LABEL_SLOTS := ["right", "left", "below", "above", "above_right", "below_right", "above_left", "below_left"]
# Two-endpoint route inset, shown left of the route card when the trip's origin is outside the regional view.
const INSET_SIZE := Vector2(190, 94)
const GLOBAL_ZOOM_RANGE := 7.0
const REGION_ZOOM_RANGE := 6.0
const WHEEL_STEP := 1.25

const COLOR_BACKDROP := Color("#0a121b")
const COLOR_OCEAN := Color("#123544")
const COLOR_LAND := Color("#566f58")
const COLOR_COAST := Color("#a9c6a4")
const COLOR_GRID := Color(0.16, 0.36, 0.43, 0.75)
const COLOR_EQUATOR := Color(0.22, 0.47, 0.54, 0.9)
const COLOR_ROAD := Color(0.89, 0.77, 0.5, 0.7)
const COLOR_ROAD_MINOR := Color(0.75, 0.68, 0.5, 0.35)
const COLOR_MARKER := Color("#79cfc0")
const COLOR_MARKER_EDGE := Color("#0b1c24")
const COLOR_HERE := Color("#f0d68a")
const COLOR_LABEL_BG := Color(0.04, 0.08, 0.12, 0.88)
const COLOR_TEXT := Color("#f2f7f2")
const COLOR_SUBTEXT := Color("#a9c7c4")
const COLOR_INSET_BG := Color(0.04, 0.08, 0.12, 0.94)
const COLOR_INSET_RULE := Color(0.15, 0.25, 0.29)
const COLOR_ROUTE_LINE := Color("#e8f6ff")
const COLOR_ROUTE_EDGE := Color(0.03, 0.07, 0.1, 0.9)

static var last_mode := "global"

var title_label: Label
var help_label: Label
var back_button: Button
var growth_button: Button
var save_button: Button
var field_button: Button
var field_status: Label
var field_overlay: ColorRect
var field_title: Label
var field_body: RichTextLabel
var field_close: Button
var talk_button: Button
# City company panel. Opens only while the party is at a discovered place of type "city".
var commerce_button: Button
var commerce_overlay: ColorRect
var commerce_title: Label
var commerce_body: RichTextLabel
var commerce_member_buttons: Array[Button] = []
var commerce_member_ids: Array[String] = []
var commerce_recall_button: Button
var commerce_rest_button: Button
var commerce_close: Button
# Last action message as [text key, format args], so a language switch re-renders it.
var commerce_feedback: Array = []
# Scene destination ID -> place Button. Kept under the old name for existing flows.
var destination_buttons: Dictionary = {}
var place_buttons: Dictionary = {}
var region_buttons: Dictionary = {}

var mode := "global"
# Set in _ready from the party's current place (else the first display region).
var active_region_id := ""
var global_view: GeoProjection
# The active region's projection and land layer; one of each per region in region_views/region_layers.
var region_view: GeoProjection
var region_views: Dictionary = {}
var view: GeoProjection
var route_adapter: RouteAdapter
var route_state: Dictionary = {}
# Places shown on the map, with coordinates, names and scene links from the travel data.
var places: Array = []
var selected_place_id := ""
var selected_option_id := ""

var map_frame: Control
var underlay: Node2D
var global_layer: Node2D
var region_layer: Node2D
var region_layers: Dictionary = {}
var overlay: Node2D
var zoom_in_button: Button
var zoom_out_button: Button
var globe_button: Button
var region_button: Button
var legend_label: Label
var legend_backing: PanelContainer
var calendar_label: Label
var route_card: PanelContainer
var card_title: Label
var card_subtitle: Label
var card_kind: Label
var card_coords: Label
var card_from: Label
var card_route: Label
var card_options: VBoxContainer
var depart_button: Button
var cancel_button: Button
var route_inset: RouteInset
var dragging := false

var _global_coast: Array = []
# Region ID -> projected coast rings / road lines in that region's own projection.
var _region_coasts: Dictionary = {}
var _region_roads: Dictionary = {}


func _ready() -> void:
	AppState.record_playtest_event("location")
	route_adapter = RouteAdapter.new(AppState)
	var problems := route_adapter.api_problems()
	if not problems.is_empty():
		# Developer diagnostic only; players see a disabled Depart button with a short reason.
		push_warning("World map: route API unavailable, departures disabled: " + "; ".join(problems))
	places = route_adapter.places()
	active_region_id = _initial_region_id()
	_build_views()
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	if last_mode == "region":
		enter_region(active_region_id)
	else:
		enter_global()
	_refresh_text()
	if AppState.show_initial_guide:
		AppState.show_initial_guide = false
		call_deferred("_open_field_log")


func _initial_region_id() -> String:
	var here := find_place(route_adapter.current_place_id())
	if not here.is_empty() and not MapData.geo_region(String(here["geo_region_id"])).is_empty():
		return String(here["geo_region_id"])
	if not MapData.geo_region(active_region_id).is_empty():
		return active_region_id
	var regions := MapData.geo_regions()
	return String(regions[0]["id"]) if not regions.is_empty() else ""


func _build_views() -> void:
	var local_rect := Rect2(Vector2.ZERO, MAP_RECT.size)
	global_view = GeoProjection.new(0.0, 0.0)
	global_view.configure(local_rect, Rect2(-180, -90, 360, 180), false, GLOBAL_ZOOM_RANGE)
	for region in MapData.geo_regions():
		var projection := GeoProjection.new(region["central_meridian"], region["standard_parallel"])
		projection.configure(local_rect, projection.project_bbox(region["pan_bbox_wsen"]), true, REGION_ZOOM_RANGE)
		region_views[region["id"]] = projection
	region_view = region_views.get(active_region_id)
	view = global_view


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	_build_map_frame(canvas)

	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, MAP_RECT.position.y)
	canvas.add_child(header)
	title_label = _label(canvas, Vector2(12, 3), 15, Color("#eef8f5"))
	help_label = _label(canvas, Vector2(12, 25), 10, Color("#a4c1c3"))
	save_button = _button(canvas, Rect2(296, 6, 100, 32), 12, _open_save)
	growth_button = _button(canvas, Rect2(402, 6, 118, 32), 11, _open_growth)
	back_button = _button(canvas, Rect2(526, 6, 102, 32), 12, _return_to_menu)

	_build_route_card(canvas)

	var strip := ColorRect.new()
	strip.color = Color("#0d1723")
	strip.position = Vector2(0, 313)
	strip.size = Vector2(640, 47)
	canvas.add_child(strip)
	field_status = _label(canvas, Vector2(17, 319), 11, Color("#e9d9a8"))
	# Wraps instead of running under the company button on the right.
	field_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	field_status.size = Vector2(388, 0)
	field_button = _button(canvas, Rect2(521, 317, 103, 37), 0, _open_field_log)
	commerce_button = _button(canvas, Rect2(412, 317, 103, 37), 0, open_commerce)
	commerce_button.name = "CommerceButton"
	_build_field_log(canvas)
	_build_commerce(canvas)


func _build_map_frame(canvas: CanvasLayer) -> void:
	map_frame = Control.new()
	map_frame.name = "MapFrame"
	map_frame.position = MAP_RECT.position
	map_frame.size = MAP_RECT.size
	map_frame.clip_contents = true
	map_frame.mouse_filter = Control.MOUSE_FILTER_STOP
	map_frame.gui_input.connect(_on_map_input)
	canvas.add_child(map_frame)

	underlay = Node2D.new()
	underlay.draw.connect(_draw_underlay)
	map_frame.add_child(underlay)
	global_layer = _land_layer(MapData.global_land_rings(), global_view)
	_global_coast = _unit_rings(MapData.global_land_rings(), global_view)
	for region_id in region_views:
		var projection: GeoProjection = region_views[region_id]
		var key := MapData.geodata_key(region_id)
		region_layers[region_id] = _land_layer(MapData.region_land_rings(key), projection)
		region_layers[region_id].visible = false
		_region_coasts[region_id] = _unit_rings(MapData.region_land_rings(key), projection)
		var roads := []
		for road in MapData.region_roads(key):
			var points := PackedVector2Array()
			for p in road["points"]:
				points.append(projection.project(p.x, p.y))
			roads.append({"major": road["major"], "points": points})
		_region_roads[region_id] = roads
	region_layer = region_layers.get(active_region_id)
	overlay = Node2D.new()
	overlay.draw.connect(_draw_overlay)
	map_frame.add_child(overlay)

	for region in MapData.geo_regions():
		var button := _marker_button(map_frame)
		button.name = region["id"] + "_region_button"
		button.pressed.connect(enter_region.bind(region["id"]))
		region_buttons[region["id"]] = button
	for place in places:
		var button := _marker_button(map_frame)
		button.name = String(place["scene_destination_id"]).replace(".", "_").replace("-", "_") + "_button"
		button.pressed.connect(select_place.bind(place["id"]))
		place_buttons[place["id"]] = button
		destination_buttons[place["scene_destination_id"]] = button
	route_inset = RouteInset.new()
	route_inset.visible = false
	map_frame.add_child(route_inset)

	_build_status_backing()
	calendar_label = _label(map_frame, Vector2(392, 249), 10, COLOR_HERE)
	calendar_label.size = Vector2(240, 16)
	calendar_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	zoom_in_button = _button(map_frame, Rect2(8, 196, 26, 24), 14, _zoom_button.bind(WHEEL_STEP))
	zoom_out_button = _button(map_frame, Rect2(8, 222, 26, 24), 14, _zoom_button.bind(1.0 / WHEEL_STEP))
	zoom_in_button.text = "+"
	zoom_out_button.text = "−"
	globe_button = _button(map_frame, Rect2(38, 222, 54, 24), 10, enter_global)
	region_button = _button(map_frame, Rect2(96, 222, 96, 24), 10, _open_active_region)


# The status line sits on its own dark panel so coastlines and grid lines never run
# through the text. The panel hugs the text and wraps it only past STATUS_MAX_TEXT_WIDTH.
func _build_status_backing() -> void:
	legend_backing = PanelContainer.new()
	legend_backing.name = "StatusBacking"
	legend_backing.position = STATUS_POS
	legend_backing.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var style := StyleBoxFlat.new()
	style.bg_color = COLOR_LABEL_BG
	style.border_color = Color("#25404b")
	style.set_border_width_all(1)
	style.set_content_margin_all(1)
	style.content_margin_left = 5
	style.content_margin_right = 5
	legend_backing.add_theme_stylebox_override("panel", style)
	map_frame.add_child(legend_backing)
	legend_label = _label(legend_backing, Vector2.ZERO, 10, COLOR_SUBTEXT)


func _fit_status_backing() -> void:
	var font := legend_label.get_theme_font("font")
	var width := font.get_string_size(legend_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
	var wraps := width > STATUS_MAX_TEXT_WIDTH
	legend_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if wraps else TextServer.AUTOWRAP_OFF
	legend_label.custom_minimum_size.x = STATUS_MAX_TEXT_WIDTH if wraps else 0.0
	legend_backing.reset_size()


# The status panel's rectangle in map-local pixels.
func status_rect() -> Rect2:
	return Rect2(legend_backing.position, legend_backing.get_combined_minimum_size())


func _land_layer(rings: Array, projection: GeoProjection) -> Node2D:
	var layer := Node2D.new()
	map_frame.add_child(layer)
	for hole_pass in [false, true]:
		for ring in rings:
			if ring["hole"] != hole_pass:
				continue
			var polygon := Polygon2D.new()
			polygon.polygon = _project_points(ring["points"], projection)
			polygon.color = COLOR_OCEAN if hole_pass else COLOR_LAND
			layer.add_child(polygon)
	return layer


func _unit_rings(rings: Array, projection: GeoProjection) -> Array:
	var out := []
	for ring in rings:
		var points := _project_points(ring["points"], projection)
		points.append(points[0])
		out.append(points)
	return out


static func _project_points(points: PackedVector2Array, projection: GeoProjection) -> PackedVector2Array:
	var out := PackedVector2Array()
	out.resize(points.size())
	for i in points.size():
		out[i] = projection.project(points[i].x, points[i].y)
	return out


func _build_route_card(canvas: CanvasLayer) -> void:
	route_card = PanelContainer.new()
	route_card.name = "RouteCard"
	route_card.position = CARD_RECT.position
	route_card.custom_minimum_size = CARD_RECT.size
	route_card.size = CARD_RECT.size
	var style := StyleBoxFlat.new()
	# Opaque, so grid lines and degree labels never show through the card text.
	style.bg_color = Color(0.07, 0.13, 0.17, 1.0)
	style.border_color = COLOR_MARKER
	style.set_border_width_all(1)
	style.set_content_margin_all(8)
	route_card.add_theme_stylebox_override("panel", style)
	route_card.visible = false
	canvas.add_child(route_card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 3)
	route_card.add_child(box)
	card_title = _card_label(box, 14, COLOR_TEXT)
	card_subtitle = _card_label(box, 10, COLOR_SUBTEXT)
	card_kind = _card_label(box, 10, Color("#e9d9a8"))
	card_coords = _card_label(box, 9, COLOR_SUBTEXT)
	box.add_child(HSeparator.new())
	card_from = _card_label(box, 10, COLOR_TEXT)
	card_route = _card_label(box, 10, Color("#d8e6e2"))
	card_options = VBoxContainer.new()
	card_options.add_theme_constant_override("separation", 2)
	box.add_child(card_options)
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.add_child(spacer)
	var row := HBoxContainer.new()
	box.add_child(row)
	depart_button = Button.new()
	depart_button.name = "DepartButton"
	depart_button.custom_minimum_size = Vector2(0, 28)
	depart_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	depart_button.add_theme_font_size_override("font_size", 11)
	depart_button.pressed.connect(depart)
	row.add_child(depart_button)
	cancel_button = Button.new()
	cancel_button.name = "CancelButton"
	cancel_button.custom_minimum_size = Vector2(56, 28)
	cancel_button.add_theme_font_size_override("font_size", 11)
	cancel_button.pressed.connect(close_route_card)
	row.add_child(cancel_button)


func _build_field_log(canvas: CanvasLayer) -> void:
	field_overlay = ColorRect.new()
	field_overlay.color = Color(0.04, 0.08, 0.12, 0.93)
	field_overlay.size = Vector2(640, 360)
	field_overlay.visible = false
	canvas.add_child(field_overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(48, 39)
	panel.size = Vector2(544, 285)
	panel.color = Color("#25404b")
	field_overlay.add_child(panel)
	field_title = Label.new()
	field_title.position = Vector2(69, 53)
	field_title.add_theme_font_size_override("font_size", 20)
	field_title.add_theme_color_override("font_color", Color("#f0e3c5"))
	field_overlay.add_child(field_title)
	field_body = RichTextLabel.new()
	field_body.position = Vector2(69, 93)
	field_body.size = Vector2(500, 165)
	field_body.scroll_active = true
	field_body.add_theme_font_size_override("normal_font_size", 12)
	field_body.add_theme_color_override("font_color", Color("#e0eeeb"))
	field_overlay.add_child(field_body)
	talk_button = Button.new()
	talk_button.position = Vector2(69, 274)
	talk_button.size = Vector2(155, 34)
	talk_button.pressed.connect(_open_party_talk)
	field_overlay.add_child(talk_button)
	field_close = Button.new()
	field_close.position = Vector2(434, 274)
	field_close.size = Vector2(135, 34)
	field_close.pressed.connect(_close_field_log)
	field_overlay.add_child(field_close)


func _build_commerce(canvas: CanvasLayer) -> void:
	commerce_overlay = ColorRect.new()
	commerce_overlay.name = "CommerceOverlay"
	commerce_overlay.color = Color(0.04, 0.08, 0.12, 0.93)
	commerce_overlay.size = Vector2(640, 360)
	commerce_overlay.visible = false
	canvas.add_child(commerce_overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(48, 39)
	panel.size = Vector2(544, 285)
	panel.color = Color("#25404b")
	commerce_overlay.add_child(panel)
	commerce_title = Label.new()
	commerce_title.position = Vector2(69, 49)
	commerce_title.add_theme_font_size_override("font_size", 18)
	commerce_title.add_theme_color_override("font_color", Color("#f0e3c5"))
	commerce_overlay.add_child(commerce_title)
	commerce_body = RichTextLabel.new()
	commerce_body.position = Vector2(69, 78)
	commerce_body.size = Vector2(502, 144)
	commerce_body.scroll_active = true
	commerce_body.add_theme_font_size_override("normal_font_size", 11)
	commerce_body.add_theme_color_override("default_color", Color("#e0eeeb"))
	commerce_overlay.add_child(commerce_body)
	# One button per recruitable companion; only merchants who can be stationed are shown.
	for index in AppState.MEMBER_DEFS.size() - 1:
		var button := _button(commerce_overlay, Rect2(69 + index * 169, 228, 163, 30), 11, _commerce_station.bind(index))
		button.visible = false
		commerce_member_buttons.append(button)
	commerce_recall_button = _button(commerce_overlay, Rect2(69, 266, 150, 34), 11, _commerce_recall)
	commerce_rest_button = _button(commerce_overlay, Rect2(227, 266, 200, 34), 11, _commerce_rest)
	commerce_close = _button(commerce_overlay, Rect2(435, 266, 136, 34), 11, close_commerce)
	commerce_overlay.visibility_changed.connect(_sync_commerce_focus)


# --- View modes -------------------------------------------------------------

func enter_global() -> void:
	if _commerce_modal():
		return
	mode = "global"
	last_mode = mode
	view = global_view
	view.scale = view.min_scale
	view.center = view.bounds.get_center()
	view.clamp_center()
	close_route_card()
	_view_changed()


func enter_region(region_id: String) -> void:
	if _commerce_modal() or not region_views.has(region_id):
		return
	if region_id != active_region_id and route_card != null and route_card.visible:
		close_route_card()
	active_region_id = region_id
	mode = "region"
	last_mode = mode
	region_view = region_views[region_id]
	region_layer = region_layers[region_id]
	view = region_view
	var box := MapData.region_frame_bbox(region_id, places)
	view.frame_geo_box(box, region_frame_rect(region_id))
	_view_changed()


# Map-local pixels a region's places are fitted into: the registry's frame_px, else REGION_FRAME.
static func region_frame_rect(region_id: String) -> Rect2:
	var px: Variant = MapData.geo_region(region_id).get("frame_px")
	if typeof(px) == TYPE_ARRAY and px.size() == 4:
		return Rect2(float(px[0]), float(px[1]), float(px[2]), float(px[3]))
	return REGION_FRAME


func _open_active_region() -> void:
	enter_region(active_region_id)


func _zoom_button(factor: float) -> void:
	zoom_view(view.viewport.get_center(), factor)


# Zooming past the globe's limit over a region opens it; zooming out of a region returns.
func zoom_view(local_point: Vector2, factor: float) -> void:
	if _commerce_modal():
		return
	if mode == "global" and factor > 1.0 and view.scale * factor > view.max_scale + 0.001:
		var geo := view.screen_to_geo(local_point)
		# Neighbouring regions can share the margin; the one whose box centre is closest wins.
		var best_id := ""
		var best_distance := INF
		for region in MapData.geo_regions():
			var bbox: Array = region["global_zoom_bbox_wsen"]
			var near := Rect2(bbox[0] - 6.0, bbox[1] - 5.0, bbox[2] - bbox[0] + 12.0, bbox[3] - bbox[1] + 10.0)
			var distance := geo.distance_to(near.get_center())
			if near.has_point(geo) and distance < best_distance:
				best_id = String(region["id"])
				best_distance = distance
		if best_id != "":
			enter_region(best_id)
			return
	if mode == "region" and factor < 1.0 and view.scale * factor < view.min_scale - 0.001:
		var region := MapData.geo_region(active_region_id)
		enter_global()
		var bbox: Array = region["global_zoom_bbox_wsen"]
		view.scale = view.max_scale
		view.center = view.project((bbox[0] + bbox[2]) * 0.5, (bbox[1] + bbox[3]) * 0.5)
		view.clamp_center()
		_view_changed()
		return
	view.zoom_at(local_point, factor)
	_view_changed()


func _on_map_input(event: InputEvent) -> void:
	if _commerce_modal():
		return
	if event is InputEventMouseButton:
		var button := event as InputEventMouseButton
		if button.pressed and button.button_index == MOUSE_BUTTON_WHEEL_UP:
			zoom_view(button.position, WHEEL_STEP)
			map_frame.accept_event()
		elif button.pressed and button.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			zoom_view(button.position, 1.0 / WHEEL_STEP)
			map_frame.accept_event()
		elif button.button_index == MOUSE_BUTTON_LEFT:
			dragging = button.pressed
	elif event is InputEventMouseMotion and dragging:
		view.pan_pixels((event as InputEventMouseMotion).relative)
		_view_changed()
	elif event is InputEventMagnifyGesture:
		zoom_view((event as InputEventMagnifyGesture).position, (event as InputEventMagnifyGesture).factor)
	elif event is InputEventPanGesture:
		view.pan_pixels(-(event as InputEventPanGesture).delta * 8.0)
		_view_changed()


func _view_changed() -> void:
	var regional := mode == "region"
	global_layer.visible = not regional
	for region_id in region_layers:
		region_layers[region_id].visible = regional and region_id == active_region_id
	var layer := region_layer if regional else global_layer
	layer.transform = view.unit_transform()
	_layout_markers()
	_refresh_map_text()
	_sync_route_inset()
	underlay.queue_redraw()
	overlay.queue_redraw()


# --- Markers ----------------------------------------------------------------

func _marker_button(parent: Control) -> Button:
	var button := Button.new()
	button.focus_mode = Control.FOCUS_ALL
	button.add_theme_stylebox_override("normal", StyleBoxEmpty.new())
	button.add_theme_stylebox_override("pressed", StyleBoxEmpty.new())
	button.add_theme_stylebox_override("disabled", StyleBoxEmpty.new())
	var highlight := StyleBoxFlat.new()
	highlight.bg_color = Color(0, 0, 0, 0)
	highlight.border_color = COLOR_HERE
	highlight.set_border_width_all(1)
	highlight.set_corner_radius_all(3)
	button.add_theme_stylebox_override("hover", highlight)
	button.add_theme_stylebox_override("focus", highlight)
	var background := ColorRect.new()
	background.name = "LabelBackground"
	background.color = COLOR_LABEL_BG
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	button.add_child(background)
	for line in ["Primary", "Secondary"]:
		var label := Label.new()
		label.name = line
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label.add_theme_font_size_override("font_size", 10 if line == "Primary" else 9)
		label.add_theme_color_override("font_color", COLOR_TEXT if line == "Primary" else COLOR_SUBTEXT)
		button.add_child(label)
	parent.add_child(button)
	return button


func find_place(place_id: String) -> Dictionary:
	for entry in places:
		if entry["id"] == place_id:
			return entry
	return {}


func marker_position(place_id: String) -> Vector2:
	var place := find_place(place_id)
	return view.geo_to_screen(place["lon"], place["lat"])


func _region_anchor(region_id: String) -> Vector2:
	var box := MapData.region_places_bbox(region_id, places)
	return Vector2((box[0] + box[2]) * 0.5, (box[1] + box[3]) * 0.5)


# Markers never move: each dot sits on its travel-data coordinates. Labels are laid out one by one
# (cities first) into the first slot that stays clear of the fixed controls, the open route card,
# every other marker dot and the labels already placed, so neighbours such as New York City and
# Yonkers keep visibly separate name plates in both languages.
func _layout_markers() -> void:
	var language: String = AppState.language
	var other := MapText.other_language()
	var bounds := Rect2(Vector2(2, 2), view.viewport.size - Vector2(4, 4))
	var entries := []
	for region in MapData.geo_regions():
		var button: Button = region_buttons[region["id"]]
		button.visible = mode == "global"
		if not button.visible:
			continue
		var anchor := _region_anchor(region["id"])
		var count := MapData.places_in_region(region["id"], places).size()
		_set_marker_text(button, MapData.text(region, "name", language), MapText.t("region_sub") % count)
		entries.append([button, view.geo_to_screen(anchor.x, anchor.y), String(region.get("global_label_side", "right")), 0])
	for place in places:
		var button: Button = place_buttons[place["id"]]
		button.visible = mode == "region" and place["geo_region_id"] == active_region_id
		if not button.visible:
			continue
		_set_marker_text(button, MapData.text(place, "map_label", language), MapData.text(place, "map_label", other))
		entries.append([button, marker_position(place["id"]), String(place.get("label_side", "right")), _label_rank(place)])
	entries.sort_custom(func(a, b): return a[3] < b[3] if a[3] != b[3] else String(a[0].name) < String(b[0].name))
	var blocked := fixed_ui_rects()
	for entry in entries:
		blocked.append(_dot_rect(entry[1]))
	for entry in entries:
		var label_rect := _place_marker_button(entry[0], entry[1], entry[2], bounds, blocked, _dot_rect(entry[1]))
		blocked.append(label_rect.grow(LABEL_GAP))


# Cities claim their label slot first, then the other place kinds.
static func _label_rank(place: Dictionary) -> int:
	return 0 if String(place.get("kind", "")) == "city" else 1


static func _dot_rect(marker: Vector2) -> Rect2:
	return Rect2(marker - Vector2(9, 9), Vector2(18, 18))


# Map-local rectangles of the fixed map controls that labels and the route inset must not cover: the
# status panel, zoom and view buttons, the calendar date, the scale bar and, while open, the route card.
func fixed_ui_rects() -> Array:
	var out := [status_rect()]
	for control in [zoom_in_button, zoom_out_button, globe_button, region_button]:
		out.append(Rect2(control.position, control.size))
	# The calendar is right-aligned in a wide box; only its text is in the way.
	var font := calendar_label.get_theme_font("font")
	var width := font.get_string_size(calendar_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
	out.append(Rect2(calendar_label.position + Vector2(calendar_label.size.x - width, 0), Vector2(width, calendar_label.size.y)))
	if mode == "region":
		out.append(SCALE_BAR_RECT)
	if route_card != null and route_card.visible:
		out.append(_card_local_rect())
	var grown := []
	for rect in out:
		grown.append((rect as Rect2).grow(LABEL_GAP))
	return grown


func _card_local_rect() -> Rect2:
	return Rect2(CARD_RECT.position - MAP_RECT.position, CARD_RECT.size)


func _set_marker_text(button: Button, primary: String, secondary: String) -> void:
	(button.get_node("Primary") as Label).text = primary
	(button.get_node("Secondary") as Label).text = secondary
	button.tooltip_text = primary + " / " + secondary


# The button covers the marker dot and its label. The label takes its own side if that slot stays in
# the frame and clear of `blocked` (the marker's own dot excepted), else the first such slot in
# LABEL_SLOTS, else the first slot inside the frame. Returns the label rectangle.
func _place_marker_button(button: Button, marker: Vector2, side: String, bounds: Rect2, blocked: Array = [], own_dot := Rect2()) -> Rect2:
	var primary: Label = button.get_node("Primary")
	var secondary: Label = button.get_node("Secondary")
	var p_size := primary.get_combined_minimum_size()
	var s_size := secondary.get_combined_minimum_size()
	var label_size := Vector2(maxf(p_size.x, s_size.x) + 8.0, p_size.y + s_size.y - 2.0)
	var dot := _dot_rect(marker)
	var label_rect := Rect2()
	var in_frame := Rect2()
	for slot in [side] + LABEL_SLOTS:
		var candidate := _label_rect(marker, slot, label_size).abs()
		candidate.position = candidate.position.round()
		if not bounds.encloses(candidate):
			continue
		if not in_frame.has_area():
			in_frame = candidate
		var clear := true
		for other in blocked:
			if other != own_dot and candidate.intersects(other):
				clear = false
				break
		if clear:
			label_rect = candidate
			break
	if not label_rect.has_area():
		label_rect = in_frame if in_frame.has_area() else _label_rect(marker, side, label_size)
	var rect := dot.merge(label_rect)
	button.position = rect.position
	button.size = rect.size
	var label_local := label_rect.position - rect.position
	var background: ColorRect = button.get_node("LabelBackground")
	background.position = label_local
	background.size = label_size
	primary.position = label_local + Vector2(4, -1)
	secondary.position = label_local + Vector2(4, p_size.y - 3.0)
	return label_rect


static func _label_rect(marker: Vector2, side: String, label_size: Vector2) -> Rect2:
	match side:
		"left":
			return Rect2(marker + Vector2(-10.0 - label_size.x, -label_size.y * 0.5), label_size)
		"below":
			return Rect2(marker + Vector2(-label_size.x * 0.5, 10.0), label_size)
		"above":
			return Rect2(marker + Vector2(-label_size.x * 0.5, -10.0 - label_size.y), label_size)
		"above_right":
			return Rect2(marker + Vector2(9.0, -9.0 - label_size.y), label_size)
		"below_right":
			return Rect2(marker + Vector2(9.0, 9.0), label_size)
		"above_left":
			return Rect2(marker + Vector2(-9.0 - label_size.x, -9.0 - label_size.y), label_size)
		"below_left":
			return Rect2(marker + Vector2(-9.0 - label_size.x, 9.0), label_size)
	return Rect2(marker + Vector2(10.0, -label_size.y * 0.5), label_size)


# --- Drawing ----------------------------------------------------------------

func _draw_underlay() -> void:
	underlay.draw_rect(Rect2(Vector2.ZERO, MAP_RECT.size), COLOR_BACKDROP)
	var earth := view.unit_transform() * view.bounds
	underlay.draw_rect(earth, COLOR_OCEAN)


func _draw_overlay() -> void:
	var px := 1.0 / view.scale
	overlay.draw_set_transform_matrix(view.unit_transform())
	if mode == "global":
		for lon in range(-180, 181, 30):
			overlay.draw_line(view.project(lon, -90), view.project(lon, 90), COLOR_GRID, px)
		for lat in range(-60, 61, 30):
			overlay.draw_line(view.project(-180, lat), view.project(180, lat), COLOR_EQUATOR if lat == 0 else COLOR_GRID, px)
		for ring in _global_coast:
			overlay.draw_polyline(ring, COLOR_COAST, px)
		for region in MapData.geo_regions():
			var box := view.project_bbox(region["global_zoom_bbox_wsen"])
			overlay.draw_rect(box, COLOR_HERE, false, px * 1.5)
	else:
		var clip: Array = MapData.region_clip_bbox(MapData.geodata_key(active_region_id))
		for lon in range(ceili(clip[0]), floori(clip[2]) + 1):
			overlay.draw_line(view.project(lon, clip[1]), view.project(lon, clip[3]), COLOR_GRID, px)
		for lat in range(ceili(clip[1]), floori(clip[3]) + 1):
			overlay.draw_line(view.project(clip[0], lat), view.project(clip[2], lat), COLOR_GRID, px)
		for ring in _region_coasts.get(active_region_id, []):
			overlay.draw_polyline(ring, COLOR_COAST, px)
		var roads: Array = _region_roads.get(active_region_id, [])
		for road in roads:
			if not road["major"]:
				overlay.draw_polyline(road["points"], COLOR_ROAD_MINOR, px)
		for road in roads:
			if road["major"]:
				overlay.draw_polyline(road["points"], COLOR_ROAD, px)
	overlay.draw_set_transform_matrix(Transform2D.IDENTITY)
	if mode == "region":
		_draw_region_annotations()
		var here := route_adapter.current_place_id()
		for place in places:
			if place["geo_region_id"] == active_region_id:
				_draw_marker(marker_position(place["id"]), place["id"] == here, place["id"] == selected_place_id)
	else:
		for region in MapData.geo_regions():
			var anchor := _region_anchor(region["id"])
			_draw_marker(view.geo_to_screen(anchor.x, anchor.y), find_place(route_adapter.current_place_id()).get("geo_region_id", "") == region["id"], false)


func _draw_marker(at: Vector2, here: bool, selected: bool) -> void:
	if here:
		overlay.draw_arc(at, 8.5, 0.0, TAU, 24, COLOR_HERE, 2.0)
	if selected:
		overlay.draw_arc(at, 11.5, 0.0, TAU, 24, Color.WHITE, 1.5)
	overlay.draw_circle(at, 5.5, COLOR_MARKER_EDGE)
	overlay.draw_circle(at, 4.0, COLOR_MARKER)


func _draw_region_annotations() -> void:
	var font := ThemeDB.fallback_font
	for reference in MapData.reference_places():
		if reference["geo_region_id"] == active_region_id:
			var at := view.geo_to_screen(reference["lon"], reference["lat"])
			overlay.draw_rect(Rect2(at - Vector2(2, 2), Vector2(4, 4)), COLOR_SUBTEXT)
	for entry in annotation_label_rects():
		overlay.draw_string(font, entry["baseline"], entry["text"], HORIZONTAL_ALIGNMENT_LEFT, -1, 9, COLOR_SUBTEXT)
	# Scale bar: valid along meridians and the standard parallel.
	var km_per_px := view.km_per_pixel()
	var length_km := 10.0
	for candidate in [5.0, 10.0, 20.0, 25.0, 50.0, 100.0, 200.0]:
		if candidate / km_per_px <= 90.0:
			length_km = candidate
	var length_px := length_km / km_per_px
	var origin := SCALE_BAR_ORIGIN
	overlay.draw_line(origin, origin + Vector2(length_px, 0), COLOR_TEXT, 2.0)
	overlay.draw_line(origin + Vector2(0, -4), origin + Vector2(0, 2), COLOR_TEXT, 1.0)
	overlay.draw_line(origin + Vector2(length_px, -4), origin + Vector2(length_px, 2), COLOR_TEXT, 1.0)
	overlay.draw_string(font, origin + Vector2(length_px + 4, 4), "%d km" % int(length_km), HORIZONTAL_ALIGNMENT_LEFT, -1, 9, COLOR_TEXT)


# Degree and reference-place labels of the regional view, in map-local pixels. While the
# route card is open, latitude labels move to the card's left edge and any label that
# would touch the card or the route inset is left out, so no text sits half under either.
func annotation_label_rects() -> Array:
	var font := ThemeDB.fallback_font
	var clip: Array = MapData.region_clip_bbox(MapData.geodata_key(active_region_id))
	var visible := view.visible_geo_rect()
	var card := Rect2()
	if route_card != null and route_card.visible:
		card = _card_local_rect().grow(2)
	var inset := route_inset_rect().grow(2)
	var candidates := []
	# Longitude labels run in one row just below the status panel; other labels under it are left out.
	var status := status_rect().grow(1)
	var lon_baseline := maxf(26.0, status.end.y + font.get_ascent(9))
	for lon in range(ceili(clip[0]), floori(clip[2]) + 1):
		var x := view.geo_to_screen(lon, 0).x
		if x > 24 and x < view.viewport.size.x - 24:
			candidates.append([degree_text(lon, "E", "W"), Vector2(x + 2, lon_baseline)])
	for lat in range(ceili(clip[1]), floori(clip[3]) + 1):
		var y := view.geo_to_screen(visible.position.x, lat).y
		if y > 30 and y < view.viewport.size.y - 50:
			var text := degree_text(lat, "N", "S")
			var x := view.viewport.size.x - 34
			if card.has_area():
				x = card.position.x - font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9).x - 2
			candidates.append([text, Vector2(x, y - 2)])
	for reference in MapData.reference_places():
		if reference["geo_region_id"] == active_region_id:
			var at := view.geo_to_screen(reference["lon"], reference["lat"])
			candidates.append(["%s %s" % [MapData.text(reference, "name", "zh"), MapData.text(reference, "name", "en")], at + Vector2(5, 11)])
	var out := []
	for candidate in candidates:
		var size := font.get_string_size(candidate[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 9)
		var rect := Rect2(candidate[1] - Vector2(0, font.get_ascent(9)), size)
		if rect.intersects(status):
			continue
		if card.has_area() and rect.intersects(card):
			continue
		if inset.has_area() and rect.intersects(inset):
			continue
		out.append({"text": candidate[0], "baseline": candidate[1], "rect": rect})
	return out


# Whole-degree grid label: 74°W, 41°N, 0°E.
static func degree_text(value: int, positive: String, negative: String) -> String:
	return "%d°%s" % [absi(value), negative if value < 0 else positive]


# --- Route card -------------------------------------------------------------

func select_place(place_id: String) -> void:
	var place := find_place(place_id)
	if place.is_empty() or _commerce_modal():
		return
	if mode != "region" or active_region_id != place["geo_region_id"]:
		enter_region(place["geo_region_id"])
	selected_place_id = place_id
	route_state = route_adapter.preview(place_id)
	selected_option_id = route_state["selected"]
	route_card.visible = true
	# Labels that would sit under the card move to a free slot.
	_layout_markers()
	_refresh_route_card()
	overlay.queue_redraw()
	if not depart_button.disabled:
		depart_button.grab_focus()
	else:
		cancel_button.grab_focus()


# Cancelling never charges time: the core only settles a trip in confirm_travel().
func close_route_card() -> void:
	var had_place := selected_place_id
	if route_adapter != null and route_state.get("status", "") == "ready":
		route_adapter.cancel()
	selected_place_id = ""
	selected_option_id = ""
	route_state = {}
	if route_card != null:
		route_card.visible = false
	if route_inset != null:
		_sync_route_inset()
		_layout_markers()
	if overlay != null:
		overlay.queue_redraw()
	if not had_place.is_empty() and place_buttons.has(had_place) and place_buttons[had_place].visible:
		place_buttons[had_place].grab_focus()


# The only ways into a scene from the map: a confirmed trip (charged once by the core) or the
# place the party is already at (free). route_state is cleared first, so a second press is a no-op.
func depart() -> void:
	var place := find_place(selected_place_id)
	if place.is_empty() or _commerce_modal():
		return
	var status := String(route_state.get("status", ""))
	match status:
		"ready":
			route_state = {}
			var result := route_adapter.confirm(selected_place_id, selected_option_id)
			if not result["ok"] or String(result["scene_destination_id"]).is_empty():
				_show_departure_failed()
				return
			_enter_scene(result["scene_destination_id"])
		"same_place":
			route_state = {}
			if not route_adapter.enter_here():
				_show_departure_failed()
				return
			_enter_scene(place["scene_destination_id"])


func _choose_option(option_id: String) -> void:
	if _commerce_modal():
		return
	route_state = route_adapter.preview(selected_place_id, option_id)
	selected_option_id = route_state["selected"]
	_refresh_route_card()


# Kept as its own status so a language switch redraws the same message; no time was charged.
func _show_departure_failed() -> void:
	route_state = {"status": "failed"}
	_refresh_route_card()


func _refresh_route_card() -> void:
	var place := find_place(selected_place_id)
	if place.is_empty():
		return
	var language: String = AppState.language
	card_title.text = MapData.text(place, "map_label", language)
	var official := MapData.text(place, "name", language)
	card_subtitle.text = MapData.text(place, "map_label", MapText.other_language()) + ("" if official == card_title.text else "\n" + official)
	card_kind.text = MapText.t("kind_" + String(place.get("kind", "")))
	card_coords.text = GeoProjection.format_lat_lon(place["lon"], place["lat"])
	var origin := find_place(route_adapter.current_place_id())
	card_from.text = MapText.t("from") % (MapData.text(origin, "map_label", language) if not origin.is_empty() else "—")
	for child in card_options.get_children():
		card_options.remove_child(child)
		child.queue_free()
	card_options.visible = true
	depart_button.disabled = false
	var status: String = route_state.get("status", "pending_api")
	match status:
		"same_place":
			card_from.text = MapText.t("here")
			card_route.text = MapText.t("route_same")
			depart_button.text = MapText.t("enter_here")
		"ready":
			card_route.text = MapText.t("route_unverified") if not route_state["unverified"].is_empty() else ""
			card_route.visible = not card_route.text.is_empty()
			for option in route_state["options"]:
				var button := Button.new()
				button.name = "Route_" + String(option["option_id"]).validate_node_name()
				button.toggle_mode = true
				button.button_pressed = option["option_id"] == selected_option_id
				button.text = route_option_text(option)
				button.alignment = HORIZONTAL_ALIGNMENT_LEFT
				button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				button.add_theme_font_size_override("font_size", 10)
				button.pressed.connect(_choose_option.bind(option["option_id"]))
				card_options.add_child(button)
			depart_button.text = MapText.t("depart")
		"no_route":
			card_route.text = MapText.t("route_no_route")
			depart_button.text = MapText.t("route_pending_button")
			depart_button.disabled = true
		"failed":
			card_options.visible = false
			card_route.text = MapText.t("travel_failed")
			depart_button.text = MapText.t("route_pending_button")
			depart_button.disabled = true
		_:
			# Route API missing or mismatched: never offer an untimed trip to another place.
			card_route.text = MapText.t("route_pending_api")
			depart_button.text = MapText.t("route_pending_button")
			depart_button.disabled = true
	if status != "ready":
		card_route.visible = true
	cancel_button.text = MapText.t("cancel")
	_sync_route_inset()


# Formats one available route option: mode, approximate distance, whole-hour duration and arrival date.
# Every number and date comes from the route core; distances are only rounded for display.
static func route_option_text(option: Dictionary) -> String:
	var parts := [MapText.t("mode_" + String(option["mode"]))]
	if option["road_distance_km"] > 0.0:
		parts.append(MapText.t("road_km") % _km_text(option["road_distance_km"]))
	if option["air_distance_km"] > 0.0:
		parts.append(MapText.t("air_km") % _km_text(option["air_distance_km"]))
	parts.append(String(option["duration_text"]))
	var line := " · ".join(parts)
	if not String(option["arrival_text"]).is_empty():
		line += "\n" + MapText.t("arrival_text") % option["arrival_text"]
	if not option["via"].is_empty():
		line += "\n" + MapText.t("via") % ", ".join(option["via"])
	return line


static func _km_text(km: float) -> String:
	return str(WorldRouteRegistry.approximate_km(km))


# --- Route inset ----------------------------------------------------------------

func selected_route_option() -> Dictionary:
	for option in route_state.get("options", []):
		if option["option_id"] == selected_option_id:
			return option
	return {}


# The inset is wanted while the card offers a trip whose origin (the party's place) is not shown on this
# regional view: it sits in another region, or outside the part of the frame the card leaves free. The
# far place is then never drawn as a local marker; the inset shows both ends at their own coordinates.
func route_inset_wanted() -> bool:
	if route_card == null or not route_card.visible or mode != "region":
		return false
	if String(route_state.get("status", "")) != "ready" or selected_route_option().is_empty():
		return false
	var origin := find_place(route_adapter.current_place_id())
	if origin.is_empty() or origin["id"] == selected_place_id:
		return false
	if origin["geo_region_id"] != active_region_id:
		return true
	var free := Rect2(Vector2.ZERO, Vector2(_card_local_rect().position.x, MAP_RECT.size.y)).grow(-4)
	return not free.has_point(marker_position(origin["id"]))


# The inset's map-local rectangle while it is shown, else an empty Rect2.
func route_inset_rect() -> Rect2:
	if route_inset == null or not route_inset.visible:
		return Rect2()
	return Rect2(route_inset.position, route_inset.size)


# Shows, refreshes or hides the inset. It takes the lowest, then rightmost, slot left of the card and above
# the bottom row of controls that covers no marker, label or fixed control.
func _sync_route_inset() -> void:
	if route_inset == null:
		return
	if not route_inset_wanted():
		route_inset.visible = false
		return
	var slot := _route_inset_slot()
	if not slot.has_area():
		route_inset.visible = false
		return
	route_inset.position = slot.position
	var origin := find_place(route_adapter.current_place_id())
	var destination := find_place(selected_place_id)
	var option := selected_route_option()
	# The region's own land data when it covers both places, else the globe's.
	var key := MapData.geodata_key(active_region_id)
	var clip: Array = MapData.region_clip_bbox(key)
	var rings := MapData.region_land_rings(key)
	for place in [origin, destination]:
		if place["lon"] < clip[0] or place["lon"] > clip[2] or place["lat"] < clip[1] or place["lat"] > clip[3]:
			key = "global"
			rings = MapData.global_land_rings()
			clip = [-180.0, -90.0, 180.0, 90.0]
			break
	var language: String = AppState.language
	var air := String(option["mode"]) != "car"
	var km: float = option["air_distance_km"] if option["air_distance_km"] > 0.0 else option["road_distance_km"]
	var caption := MapText.t("mode_" + String(option["mode"]))
	if km > 0.0:
		caption += " · " + MapText.t("air_km" if option["air_distance_km"] > 0.0 else "road_km") % _km_text(km)
	route_inset.show_route(origin, destination, key, rings, clip, air,
		MapData.text(origin, "map_label", language), MapData.text(destination, "map_label", language), caption)
	route_inset.visible = true


func _route_inset_slot() -> Rect2:
	var blocked := fixed_ui_rects()
	for button in place_buttons.values():
		if button.visible:
			blocked.append(Rect2(button.position, button.size).grow(LABEL_GAP))
	var top := status_rect().end.y + 14.0
	var bottom := SCALE_BAR_RECT.position.y - LABEL_GAP - 1.0
	var right := _card_local_rect().position.x - 4.0
	var y := floorf(bottom - INSET_SIZE.y)
	while y >= top:
		var x := floorf(right - INSET_SIZE.x)
		while x >= 4.0:
			var candidate := Rect2(Vector2(x, y), INSET_SIZE)
			var clear := true
			for other in blocked:
				if candidate.intersects(other):
					clear = false
					break
			if clear:
				return candidate
			x -= 4.0
		y -= 4.0
	return Rect2()


# A small locator map for one trip: both places at their own coordinates on the same land data the map
# uses, the line between them (dashed great circle for a flight, dotted for a car trip, with no road
# geometry invented), the origin's party ring, the destination's selection ring, the trip mode and
# distance as on the card, and its own scale bar. Display only: it ignores the mouse.
class RouteInset:
	extends Control

	const CAPTION_HEIGHT := 14.0
	const DASH := 4.0
	const GAP := 3.0
	const DOT := 1.0
	const DOT_GAP := 3.0

	var area := Rect2()
	var projection: GeoProjection
	var land: Node2D
	var lines: Node2D
	var coasts: Array = []
	var arc := PackedVector2Array()
	var origin_pt := Vector2.ZERO
	var dest_pt := Vector2.ZERO
	var plane_pt := Vector2.ZERO
	var plane_dir := Vector2.LEFT
	var air := true
	var origin_label: Label
	var dest_label: Label
	var caption: Label
	var scale_km := 0.0
	var scale_px := 0.0
	var route_key := ""

	func _init() -> void:
		name = "RouteInset"
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		size = INSET_SIZE
		area = Rect2(Vector2(1, 1), Vector2(size.x - 2, size.y - CAPTION_HEIGHT - 2))
		var clip := Control.new()
		clip.position = area.position
		clip.size = area.size
		clip.clip_contents = true
		clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(clip)
		land = Node2D.new()
		clip.add_child(land)
		lines = Node2D.new()
		lines.draw.connect(_draw_lines)
		clip.add_child(lines)
		origin_label = _plate_label(10, COLOR_TEXT)
		dest_label = _plate_label(10, COLOR_TEXT)
		caption = _plate_label(9, COLOR_SUBTEXT)
		caption.remove_theme_stylebox_override("normal")
		caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	func _plate_label(font_size: int, color: Color) -> Label:
		var label := Label.new()
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label.add_theme_font_size_override("font_size", font_size)
		label.add_theme_color_override("font_color", color)
		label.add_theme_color_override("font_outline_color", COLOR_BACKDROP)
		label.add_theme_constant_override("outline_size", 3)
		var plate := StyleBoxFlat.new()
		plate.bg_color = COLOR_LABEL_BG
		plate.content_margin_left = 3
		plate.content_margin_right = 3
		label.add_theme_stylebox_override("normal", plate)
		add_child(label)
		return label

	# Rebuilds the geometry only when the trip changes; texts follow the language and the selected option.
	func show_route(origin: Dictionary, destination: Dictionary, land_key: String, rings: Array, clip_bbox: Array, is_air: bool,
			origin_text: String, dest_text: String, caption_text: String) -> void:
		var key := "%s>%s:%s:%s" % [origin["id"], destination["id"], land_key, is_air]
		if key != route_key:
			route_key = key
			air = is_air
			_build(origin, destination, rings, clip_bbox)
		origin_label.text = origin_text
		dest_label.text = dest_text
		caption.text = caption_text
		for label in [origin_label, dest_label, caption]:
			label.reset_size()
		# The northern place is labelled above its dot, the southern one below, so neither name sits on the line.
		var origin_north: bool = origin["lat"] >= destination["lat"]
		origin_label.position = _label_pos(origin_pt, "above" if origin_north else "below", origin_label.size)
		dest_label.position = _label_pos(dest_pt, "below" if origin_north else "above", dest_label.size)
		caption.position = Vector2(0, size.y - CAPTION_HEIGHT - 2)
		caption.size = Vector2(size.x - 6.0, CAPTION_HEIGHT)
		queue_redraw()
		lines.queue_redraw()

	func _build(origin: Dictionary, destination: Dictionary, rings: Array, clip_bbox: Array) -> void:
		for child in land.get_children():
			land.remove_child(child)
			child.queue_free()
		coasts.clear()
		projection = GeoProjection.new((origin["lon"] + destination["lon"]) * 0.5, (origin["lat"] + destination["lat"]) * 0.5)
		var local := Rect2(Vector2.ZERO, area.size)
		projection.configure(local, projection.project_bbox(clip_bbox), true, 60.0)
		# Both places fitted with room for one label row above and below the line.
		projection.frame_geo_box([minf(origin["lon"], destination["lon"]) - 1.7, minf(origin["lat"], destination["lat"]) - 1.3,
			maxf(origin["lon"], destination["lon"]) + 1.7, maxf(origin["lat"], destination["lat"]) + 1.3], local)
		var ocean := Polygon2D.new()
		ocean.polygon = PackedVector2Array([Vector2.ZERO, Vector2(local.size.x, 0), local.size, Vector2(0, local.size.y)])
		ocean.color = COLOR_OCEAN
		land.add_child(ocean)
		for hole_pass in [false, true]:
			for ring in rings:
				if ring["hole"] != hole_pass:
					continue
				var points := PackedVector2Array()
				for p in ring["points"]:
					points.append(projection.geo_to_screen(p.x, p.y))
				var polygon := Polygon2D.new()
				polygon.polygon = points
				polygon.color = COLOR_OCEAN if hole_pass else COLOR_LAND
				land.add_child(polygon)
				var closed := points.duplicate()
				closed.append(points[0])
				coasts.append(closed)
		origin_pt = projection.geo_to_screen(origin["lon"], origin["lat"])
		dest_pt = projection.geo_to_screen(destination["lon"], destination["lat"])
		arc = great_circle_points(origin["lon"], origin["lat"], destination["lon"], destination["lat"], 48, projection)
		var half := arc.size() / 2
		plane_pt = arc[half]
		plane_dir = (arc[half + 1] - arc[half - 1]).normalized()
		# Scale bar: the longest of these that fits in 48 px.
		var km_per_px := projection.km_per_pixel()
		scale_km = 0.0
		for candidate in [50.0, 100.0, 200.0, 250.0, 500.0, 1000.0, 2000.0]:
			if candidate / km_per_px <= 48.0:
				scale_km = candidate
		scale_px = scale_km / km_per_px

	# A label beside its dot, kept inside the inset's map area (it slides along the edge, never flips).
	func _label_pos(at: Vector2, side: String, s: Vector2) -> Vector2:
		var p := area.position + at
		var out := p + (Vector2(-s.x * 0.5, -6.0 - s.y) if side == "above" else Vector2(-s.x * 0.5, 4.0))
		out.x = clampf(out.x, area.position.x + 1.0, area.end.x - s.x - 1.0)
		out.y = clampf(out.y, area.position.y, area.end.y - s.y)
		return out.round()

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, size), COLOR_INSET_BG)
		draw_rect(Rect2(Vector2(0.5, 0.5), size - Vector2.ONE), COLOR_MARKER, false, 1.0)
		draw_line(Vector2(1, area.end.y + 0.5), Vector2(size.x - 1, area.end.y + 0.5), COLOR_INSET_RULE, 1.0)
		if scale_px > 0.0:
			var y := size.y - CAPTION_HEIGHT * 0.5 - 1.0
			var x0 := 6.0
			draw_line(Vector2(x0, y), Vector2(x0 + scale_px, y), COLOR_TEXT, 1.0)
			draw_line(Vector2(x0, y - 3), Vector2(x0, y + 1), COLOR_TEXT, 1.0)
			draw_line(Vector2(x0 + scale_px, y - 3), Vector2(x0 + scale_px, y + 1), COLOR_TEXT, 1.0)
			var font := get_theme_default_font()
			draw_string(font, Vector2(x0 + scale_px + 4.0, y + font.get_ascent(9) * 0.5 - 1.0), "%d km" % int(scale_km), HORIZONTAL_ALIGNMENT_LEFT, -1, 9, COLOR_SUBTEXT)

	func _draw_lines() -> void:
		for ring in coasts:
			lines.draw_polyline(ring, COLOR_COAST, 1.0)
		var segments := dashes(arc, DASH, GAP) if air else dashes(arc, DOT, DOT_GAP)
		for dash in segments:
			lines.draw_line(dash[0], dash[1], COLOR_ROUTE_EDGE, 3.0)
		for dash in segments:
			lines.draw_line(dash[0], dash[1], COLOR_ROUTE_LINE, 1.5)
		if air:
			# Generic aircraft wedge at mid-route, nose toward the destination.
			var f := plane_dir * 5.0
			var s := Vector2(-plane_dir.y, plane_dir.x)
			var body := PackedVector2Array([plane_pt + f, plane_pt - f * 0.7 + s * 3.6, plane_pt - f * 0.35, plane_pt - f * 0.7 - s * 3.6])
			lines.draw_colored_polygon(body, COLOR_ROUTE_EDGE)
			var inner := PackedVector2Array()
			for p in body:
				inner.append(plane_pt + (p - plane_pt) * 0.72)
			lines.draw_colored_polygon(inner, COLOR_ROUTE_LINE)
		# Origin: the party-here ring; destination: the selection ring. Same marks as the map markers.
		for at in [origin_pt, dest_pt]:
			lines.draw_circle(at, 4.0, COLOR_MARKER_EDGE)
			lines.draw_circle(at, 2.8, COLOR_MARKER)
		lines.draw_arc(origin_pt, 5.6, 0.0, TAU, 20, COLOR_HERE, 1.5)
		lines.draw_arc(dest_pt, 5.6, 0.0, TAU, 20, Color.WHITE, 1.2)

	# Segments along a polyline, `on` pixels drawn then `off` skipped, measured along the path.
	static func dashes(points: PackedVector2Array, on_px: float, off_px: float) -> Array:
		var out := []
		var on := true
		var left := on_px
		for i in points.size() - 1:
			var a := points[i]
			var b := points[i + 1]
			var length := a.distance_to(b)
			var t := 0.0
			while t < length - 0.001:
				var step := minf(left, length - t)
				if on:
					out.append([a.lerp(b, t / length), a.lerp(b, (t + step) / length)])
				t += step
				left -= step
				if left <= 0.001:
					on = not on
					left = on_px if on else off_px
		return out

	# True great-circle path (slerp on the unit sphere), projected into the inset.
	static func great_circle_points(lon_a: float, lat_a: float, lon_b: float, lat_b: float, n: int, proj: GeoProjection) -> PackedVector2Array:
		var a := _unit(lon_a, lat_a)
		var b := _unit(lon_b, lat_b)
		var omega := acos(clampf(a.dot(b), -1.0, 1.0))
		var out := PackedVector2Array()
		for i in n + 1:
			var t := float(i) / n
			var v := a.lerp(b, t) if omega < 1e-6 else (a * sin((1.0 - t) * omega) + b * sin(t * omega)) / sin(omega)
			out.append(proj.geo_to_screen(rad_to_deg(atan2(v.y, v.x)), rad_to_deg(asin(clampf(v.z, -1.0, 1.0)))))
		return out

	static func _unit(lon: float, lat: float) -> Vector3:
		var p := deg_to_rad(lat)
		var l := deg_to_rad(lon)
		return Vector3(cos(p) * cos(l), cos(p) * sin(l), sin(p))


# --- Text -------------------------------------------------------------------

func _refresh_map_text() -> void:
	help_label.text = MapText.t("help_region" if mode == "region" else "help_global")
	legend_label.text = MapText.t("boards_legend") if mode == "global" else MapData.text(MapData.geo_region(active_region_id), "name", AppState.language) + " · " + MapData.text(MapData.geo_region(active_region_id), "name", MapText.other_language())
	_fit_status_backing()
	calendar_label.text = route_adapter.calendar_text()
	globe_button.text = MapText.t("view_globe")
	# Names the region the button opens (the last one viewed, or where the party is).
	var region_name := MapData.text(MapData.geo_region(active_region_id), "short_name", AppState.language)
	region_button.text = region_name if region_name != "" else MapText.t("view_region")
	globe_button.disabled = mode == "global" and is_equal_approx(view.scale, view.min_scale)
	region_button.disabled = mode == "region"


func _refresh_text() -> void:
	title_label.text = MapText.t("title")
	back_button.text = AppState.text_for("map_back")
	growth_button.text = AppState.text_for("growth_open")
	save_button.text = AppState.text_for("save_open")
	_refresh_map_text()
	_layout_markers()
	if route_card.visible:
		_refresh_route_card()
	field_button.text = AppState.text_for("field_log")
	field_status.text = AppState.field_log_text()
	field_title.text = AppState.text_for("field_log")
	var lines := [AppState.text_for("field_log_hint"), "", AppState.field_log_text()]
	lines.append(AppState.survey_log_text())
	lines.append(AppState.field_assist_log_text())
	lines.append(AppState.field_trace_log_text())
	lines.append(AppState.play_time_text())
	for destination_id in AppState.DESTINATIONS:
		for index in 2:
			if AppState.field_traces.has("%s:%d" % [destination_id, index]):
				lines.append(AppState.text_for("field_trace_" + destination_id.trim_prefix("scifi.") + "_%d" % index))
	for destination_id in AppState.DESTINATIONS:
		if AppState.field_insights.has(destination_id):
			lines.append(AppState.text_for("field_assist_result_" + destination_id.trim_prefix("scifi.")))
	if AppState.relay_checked:
		lines.append(AppState.text_for("relay_record"))
	if AppState.ji_records_checked:
		lines.append(AppState.text_for("archive_record"))
	if AppState.machine_observed:
		lines.append(AppState.text_for("machine_record"))
	if AppState.can_submit_report():
		lines.append(AppState.text_for("report_ready"))
	field_body.text = "\n".join(lines)
	field_close.text = AppState.text_for("save_back")
	talk_button.text = AppState.text_for("talk_open")
	talk_button.disabled = AppState.recruited_members.is_empty()
	_refresh_commerce()
	overlay.queue_redraw()


# --- Existing flows -----------------------------------------------------------

func _open_field_log() -> void:
	if _commerce_modal():
		return
	_refresh_text()
	field_overlay.visible = true
	field_close.grab_focus()


func _close_field_log() -> void:
	field_overlay.visible = false
	field_button.grab_focus()


# --- City company -------------------------------------------------------------

# The party's current place when it can host a company (a discovered city), otherwise "".
func commerce_city_id() -> String:
	var city_id := String(AppState.current_location_id)
	return city_id if AppState.commerce_city_block_reason(city_id) == "" else ""


func open_commerce() -> void:
	# Never stacks over the field log; that overlay must be closed first.
	if commerce_city_id() == "" or field_overlay.visible:
		return
	if route_card.visible:
		close_route_card()
	commerce_feedback = []
	_refresh_commerce()
	commerce_overlay.visible = true
	commerce_close.grab_focus()


func close_commerce() -> void:
	commerce_overlay.visible = false
	commerce_button.grab_focus()


# The company panel is modal: while it is open the map, route card, header and bottom-strip actions do nothing.
func _commerce_modal() -> bool:
	return commerce_overlay != null and commerce_overlay.visible


# Keeps keyboard focus (Tab and arrow keys) inside the open company panel; restored when it hides by any path.
func _sync_commerce_focus() -> void:
	var behavior := Control.FOCUS_BEHAVIOR_DISABLED if commerce_overlay.visible else Control.FOCUS_BEHAVIOR_INHERITED
	for node in commerce_overlay.get_parent().get_children():
		if node is Control and node != commerce_overlay:
			(node as Control).focus_behavior_recursive = behavior


# Opens the company with this companion, or stations them at an NPC-run one. Either way they leave the party.
func _commerce_station(index: int) -> void:
	var city_id := commerce_city_id()
	if city_id == "" or index >= commerce_member_ids.size():
		return
	var member_id := commerce_member_ids[index]
	var existing: bool = AppState.commerce_ledger_state()["companies"].has(city_id)
	var result: Dictionary = AppState.assign_commerce_manager(city_id, member_id) if existing else AppState.open_commerce_company(city_id, member_id)
	commerce_feedback = [("commerce_assigned" if existing else "commerce_opened"), [AppState.member_name(member_id)]] if result["ok"] else ["commerce_failed", []]
	_refresh_commerce()
	_keep_commerce_focus()


func _commerce_recall() -> void:
	var result: Dictionary = AppState.recall_commerce_manager(commerce_city_id())
	if result["ok"]:
		commerce_feedback = [("commerce_recalled" if result["rejoined_active_party"] else "commerce_recalled_reserve"), [AppState.member_name(String(result["member_id"]))]]
	else:
		commerce_feedback = ["commerce_failed", []]
	_refresh_commerce()
	_keep_commerce_focus()


# Station and Recall hide the pressed button, which drops keyboard focus; move it to Back inside the panel.
func _keep_commerce_focus() -> void:
	if commerce_overlay.visible and get_viewport().gui_get_focus_owner() == null:
		commerce_close.grab_focus()


# Rest passes a week on the shared calendar; the ledger settles inside AppState.advance_calendar.
func _commerce_rest() -> void:
	var result: Dictionary = AppState.rest_one_week()
	AppState.write_auto_save("map", Vector2.ZERO, "commerce_rest")
	commerce_feedback = ["commerce_rested", [int(result["weeks_settled"]), int(result["units"])]]
	_refresh_map_text()
	_refresh_commerce()


func _refresh_commerce() -> void:
	var city_id := commerce_city_id()
	commerce_button.visible = city_id != ""
	commerce_button.text = AppState.text_for("commerce_open")
	commerce_rest_button.text = AppState.text_for("commerce_rest")
	commerce_close.text = AppState.text_for("save_back")
	if city_id == "":
		commerce_overlay.visible = false
		return
	commerce_title.text = AppState.text_for("commerce_title") % AppState.travel_location_name(city_id)
	var ledger := AppState.commerce_ledger_state()
	var companies: Dictionary = ledger["companies"]
	var here: Dictionary = companies.get(city_id, {})
	var lines: PackedStringArray = []
	if not commerce_feedback.is_empty():
		var args: Array = commerce_feedback[1]
		lines.append(AppState.text_for(String(commerce_feedback[0])) % args if not args.is_empty() else AppState.text_for(String(commerce_feedback[0])))
	lines.append(AppState.text_for("travel_date_line") % AppState.calendar_date_text())
	lines.append(AppState.text_for("commerce_ledger") % int(ledger["ledgerUnits"]))
	if here.is_empty():
		lines.append(AppState.text_for("commerce_none_here"))
	for company_city in companies:
		var company: Dictionary = companies[company_city]
		var manager := String(company["managerId"])
		var place := AppState.travel_location_name(String(company_city))
		if manager != "":
			var full_rate := AppState.commerce_companion_rate_percent(manager)
			lines.append(AppState.text_for("commerce_company_companion") % [place, AppState.member_name(manager), full_rate, int(company["weeksSettled"]), int(company["unitsEarned"])])
			# The shown rate is for full weeks; say so when the running week settles differently.
			var week_rate := AppState.commerce_current_week_rate_percent(String(company_city))
			if week_rate == 0:
				lines.append(AppState.text_for("commerce_week_opening") % full_rate)
			elif week_rate != full_rate:
				lines.append(AppState.text_for("commerce_week_partial") % [week_rate, full_rate])
		else:
			lines.append(AppState.text_for("commerce_company_npc") % [place, CommerceLedger.NPC_EFFICIENCY_PERCENT, int(company["weeksSettled"]), int(company["unitsEarned"])])
	lines.append(AppState.text_for("commerce_rule"))
	# One company per city: companions can be stationed only while this city's company has no companion.
	var can_station := here.is_empty() or String(here["managerId"]) == ""
	commerce_member_ids.clear()
	if can_station:
		commerce_member_ids.assign(AppState.commerce_station_candidates())
	if can_station and commerce_member_ids.is_empty():
		lines.append(AppState.text_for("commerce_no_merchant"))
	commerce_body.text = "\n".join(lines)
	for index in commerce_member_buttons.size():
		var button := commerce_member_buttons[index]
		button.visible = index < commerce_member_ids.size()
		if button.visible:
			button.text = AppState.text_for("commerce_open_with" if here.is_empty() else "commerce_assign") % AppState.member_name(commerce_member_ids[index])
	var stationed := "" if here.is_empty() else String(here["managerId"])
	commerce_recall_button.visible = stationed != ""
	commerce_recall_button.text = AppState.text_for("commerce_recall") % AppState.member_name(stationed) if stationed != "" else ""


func _open_party_talk() -> void:
	if AppState.recruited_members.is_empty() or _commerce_modal():
		return
	get_tree().change_scene_to_file("res://scenes/party_talk.tscn")


# Loads the area scene the core has already selected. The map itself never selects a scene,
# so it cannot move the party without travel settlement.
func _enter_scene(destination_id: String) -> void:
	if AppState.current_destination_id != destination_id:
		push_error("World map: scene %s is not the party's current scene %s" % [destination_id, AppState.current_destination_id])
		_show_departure_failed()
		return
	get_tree().change_scene_to_file(AppState.area_scene_path(destination_id))


func _return_to_menu() -> void:
	if _commerce_modal():
		return
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _open_growth() -> void:
	if _commerce_modal():
		return
	AppState.growth_return_scene = "res://scenes/scifi_world_map.tscn"
	get_tree().change_scene_to_file("res://scenes/growth_screen.tscn")


func _open_save() -> void:
	if _commerce_modal():
		return
	AppState.save_screen_mode = "save"
	AppState.save_return_scene = "res://scenes/scifi_world_map.tscn"
	AppState.save_return_position = Vector2.ZERO
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")


func _exit_tree() -> void:
	if route_adapter != null and route_state.get("status", "") == "ready":
		route_adapter.cancel()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		if commerce_overlay.visible:
			close_commerce()
		elif field_overlay.visible:
			_close_field_log()
		elif route_card.visible:
			close_route_card()
		else:
			_return_to_menu()


func _label(parent: Node, at: Vector2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = at
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", COLOR_BACKDROP)
	label.add_theme_constant_override("outline_size", 3)
	parent.add_child(label)
	return label


func _card_label(parent: Node, font_size: int, color: Color) -> Label:
	var label := _label(parent, Vector2.ZERO, font_size, color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size = Vector2(CARD_RECT.size.x - 16, 0)
	return label


func _button(parent: Node, rect: Rect2, font_size: int, callback: Callable) -> Button:
	var button := Button.new()
	button.position = rect.position
	button.size = rect.size
	if font_size > 0:
		button.add_theme_font_size_override("font_size", font_size)
	button.pressed.connect(callback)
	parent.add_child(button)
	return button
