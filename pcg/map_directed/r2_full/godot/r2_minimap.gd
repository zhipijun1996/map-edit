extends Control
## Read-only whole-world minimap. All history samples are real Motor positions.
var case_data: Dictionary = {}
var motor: PlayerMotor
var bounds := Rect2()
var map_box := Rect2(10, 29, 280, 214)
var geometry: ImageTexture
var marks: Array = []
var history: Array[Vector2] = []
var projected_history: PackedVector2Array = PackedVector2Array()
var scale_factor := 1.0
var map_origin := Vector2.ZERO
var physics_samples := 0

func setup(data: Dictionary, actor: PlayerMotor) -> void:
	case_data = data
	motor = actor
	var raw: Array = data.world_bounds
	bounds = Rect2(raw[0], raw[1], raw[2], raw[3])
	size = Vector2(300, 270)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	process_physics_priority = 1200
	scale_factor = minf(map_box.size.x / bounds.size.x, map_box.size.y / bounds.size.y)
	map_origin = map_box.position + (map_box.size - bounds.size * scale_factor) * .5
	var image := Image.create(600, 540, false, Image.FORMAT_RGBA8)
	image.fill(Color(0, 0, 0, 0))
	var one_way: Dictionary = {}
	for index: Variant in data.get("one_way_platform_indices", []): one_way[int(index)] = true
	for index: int in data.platforms.size():
		var platform: Array = data.platforms[index]
		var start := project(Vector2(platform[0], platform[1])) * 2.0
		var extent := Vector2(platform[2], platform[3]) * scale_factor * 2.0
		var painted := Rect2i(floori(start.x), floori(start.y), maxi(1, ceili(extent.x)), maxi(1, ceili(extent.y)))
		painted = painted.intersection(Rect2i(0, 0, 600, 540))
		if painted.has_area():
			image.fill_rect(painted, Color("688a89") if one_way.has(index) else Color("b7b16b"))
	geometry = ImageTexture.create_from_image(image)
	for node: Dictionary in data.get("r2_semantics", {}).get("nodes", []):
		marks.append({"id": node.id, "at": project(Vector2(node.target.position[0], node.target.position[1])),
			"reward": float(node.get("reward", 0)) > 0})
	for challenge: Dictionary in data.get("r2_optional_challenges", []):
		marks.append({"id": challenge.id,
			"at": project(Vector2(challenge.target.position[0], challenge.target.position[1])), "reward": true})
	history.clear(); projected_history.clear(); physics_samples = 0
	queue_redraw()

func project(point: Vector2) -> Vector2:
	return map_origin + (point - bounds.position) * scale_factor

func _physics_process(_delta: float) -> void:
	if not is_instance_valid(motor): return
	physics_samples += 1
	var observed := motor.global_position
	history.append(observed)
	projected_history.append(project(observed))
	queue_redraw()

func _process(_delta: float) -> void:
	var view := get_viewport_rect().size
	position = Vector2(maxf(0, view.x - size.x - 14.0), maxf(0, view.y - size.y - 14.0))

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(.025, .035, .05, .94))
	draw_rect(Rect2(Vector2.ZERO, size), Color("748b8e"), false, 1.0)
	draw_string(ThemeDB.fallback_font, Vector2(10, 19),
		"完整地图 · %d 场所" % case_data.get("r2_semantics", {}).get("nodes", []).size(),
		HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("dbe8e2"))
	if geometry != null:
		draw_texture_rect(geometry, Rect2(Vector2.ZERO, size), false)
	if projected_history.size() >= 2:
		draw_polyline(projected_history, Color("58c7c4"), 1.8, true)
	for mark: Dictionary in marks:
		draw_circle(mark.at, 2.6 if mark.reward else 1.8, Color("eac366") if mark.reward else Color("c9d9cf"))
	if not projected_history.is_empty():
		draw_circle(projected_history[0], 3.0, Color("83c989"))
		draw_circle(projected_history[-1], 4.2, Color("fff2cf"))
		draw_arc(projected_history[-1], 6.0, 0, TAU, 20, Color("e4986f"), 1.3, true)
	draw_string(ThemeDB.fallback_font, Vector2(10, 260), "青：实际轨迹   金：奖励   ●：当前位置",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("b6cec8"))

func receipt() -> Dictionary:
	return {"scope": "read-only cache of actual static platforms plus real Motor history, no physics writes",
		"platforms": case_data.get("platforms", []).size(),
		"nodes": case_data.get("r2_semantics", {}).get("nodes", []).size(),
		"physics_samples": physics_samples, "world_bounds": [bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y],
		"first_position": [history[0].x, history[0].y] if not history.is_empty() else [],
		"last_position": [history[-1].x, history[-1].y] if not history.is_empty() else []}
