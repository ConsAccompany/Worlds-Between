extends RefCounted
# Presentation capability only; source-drawn accents are provisional, not approved final VFX art.
# No timers, random generators, game-state references, resources or input writes.
const DURATIONS := {"attack": 0.22, "dodge": 0.27, "guard": 0.30, "hit": 0.20, "heal": 0.55}
const MAX_EVENTS := 24
var events: Array[Dictionary] = []
var emitted := 0

func emit(kind: String, origin: Vector2, facing: float = 1.0) -> bool:
	if not DURATIONS.has(kind) or not is_finite(origin.x) or not is_finite(origin.y) or not is_finite(facing):
		return false
	if events.size() >= MAX_EVENTS:
		events.pop_front()
	events.append({"kind": kind, "origin": origin.round(), "facing": -1.0 if facing < 0.0 else 1.0, "age": 0.0, "duration": DURATIONS[kind]})
	emitted += 1
	return true

func advance(delta: float) -> void:
	if not is_finite(delta) or delta < 0.0:
		return
	for index in range(events.size() - 1, -1, -1):
		events[index]["age"] = float(events[index]["age"]) + delta
		if float(events[index]["age"]) + 0.000001 >= float(events[index]["duration"]):
			events.remove_at(index)

func draw(canvas: CanvasItem) -> void:
	for event in events:
		var progress: float = clampf(float(event["age"]) / float(event["duration"]), 0.0, 1.0)
		var fade: float = (1.0 - progress) * 0.68
		var origin: Vector2 = event["origin"]
		var facing: float = event["facing"]
		match event["kind"]:
			"attack", "hit":
				var color := Color("#e6b66a") if event["kind"] == "attack" else Color("#cf8b7f")
				color.a = fade
				# Small contact spokes; no solid flash covering the body or screen.
				for offset in [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
					var inner := 4.0 + progress * 4.0
					var outer := 8.0 + progress * 7.0
					canvas.draw_line((origin + offset * inner).round(), (origin + offset * outer).round(), color, 1.0, false)
			"dodge":
				var color := Color(0.44, 0.69, 0.75, fade * 0.8)
				for line in 3:
					var at := origin + Vector2(-facing * (4.0 + progress * 12.0), line * 3.0 - 3.0)
					canvas.draw_line(at.round(), (at + Vector2(-facing * (8.0 - progress * 4.0), 0)).round(), color, 1.0, false)
			"guard":
				var color := Color(0.49, 0.75, 0.81, fade)
				var points := PackedVector2Array()
				for step in 7:
					var angle := -PI * 0.40 + step * PI * 0.80 / 6.0
					points.append((origin + Vector2(cos(angle) * facing, sin(angle)) * (12.0 + progress * 3.0)).round())
				canvas.draw_polyline(points, color, 1.0, false)
			"heal":
				var color := Color(0.49, 0.79, 0.66, fade)
				for side in [-1.0, 1.0]:
					var at := (origin + Vector2(side * 12.0, -progress * 14.0)).round()
					canvas.draw_line(at - Vector2(2, 0), at + Vector2(2, 0), color, 1.0, false)
					canvas.draw_line(at - Vector2(0, 2), at + Vector2(0, 2), color, 1.0, false)
