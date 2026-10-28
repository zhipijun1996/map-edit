extends Node2D
## Navigation marks only. All collision and actual actors remain original nodes.
var semantics: Dictionary = {}
var observer

func _process(_delta: float) -> void:
	queue_redraw()

func _draw() -> void:
	for point: Dictionary in semantics.get("checkpoints", []):
		var raw: Array = point.region
		var area := Rect2(raw[0], raw[1], raw[2], raw[3])
		var color := Color("72c9c0")
		if point.get("kind", "") == "reward": color = Color("efc566")
		if point.get("kind", "") == "rejoin": color = Color("a9b9f1")
		draw_rect(area, Color(color, .08)); draw_rect(area, color, false, 1.5)
		draw_string(ThemeDB.fallback_font, area.position + Vector2(-6, -12),
			str(point.get("label", point.id)), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, color)
	for raw: Dictionary in semantics.get("rewards", []):
		var values: Array = raw.region
		var at := Rect2(values[0], values[1], values[2], values[3]).get_center()
		var claimed: bool = observer != null and observer.services.has(str(raw.id)) and observer.services[str(raw.id)].claimed
		draw_circle(at + Vector2(0, -28), 11, Color("769271") if claimed else Color("f6ca56"))
		draw_string(ThemeDB.fallback_font, at + Vector2(-30, -48),
			"CLAIMED" if claimed else "+" + str(raw.amount), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("ffdf80"))
