extends Node2D
## Read-only labels at actual declared place targets, not a replacement graph.
var semantics: Dictionary = {}
var camera: Camera2D
var overview := false

func _process(_delta: float) -> void:
	queue_redraw()

func _draw() -> void:
	var scale := maxf(.01, camera.zoom.x) if is_instance_valid(camera) else 1.0
	var font_size := clampi(roundi((15.0 if overview else 16.0) / scale), 12, 192)
	for node: Dictionary in semantics.get("nodes", []):
		var raw: Array = node.target.position
		var position := Vector2(raw[0], raw[1])
		var color := Color("82c9c0")
		if float(node.get("reward", 0)) > 0: color = Color("e8c76a")
		if str(node.get("id", "")) == "boss": color = Color("cb9fd5")
		draw_circle(position, 3.0 / scale, color)
		var text := str(node.get("label", node.id))
		if overview: text = str(node.id) + " " + text
		draw_string(ThemeDB.fallback_font, position + Vector2(4.0 / scale, -8.0 / scale),
			text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)
