extends Node2D
## Concrete graph-state/one-way passage gates; never moves or refills the actor.
var controller: PlayerController
var opened_flags: Dictionary = {}
var specs: Array = []
var physical: Dictionary = {}
var armed: Dictionary = {}
var events: Array = []
var frame := -1

func configure(values: Array, actor: PlayerController, flags: Dictionary) -> void:
	controller = actor; opened_flags = flags; specs = values.duplicate(true)
	process_physics_priority = -150
	for spec: Dictionary in specs:
		var key := str(spec.edge_id)
		var raw: Array = spec.bounds
		var body := StaticBody2D.new(); body.name = "PassageGate_" + key
		body.position = Vector2(raw[0] + raw[2] / 2., raw[1] + raw[3] / 2.)
		var shape := CollisionShape2D.new(); var rectangle := RectangleShape2D.new()
		rectangle.size = Vector2(raw[2], raw[3]); shape.shape = rectangle
		body.add_child(shape); add_child(body)
		physical[key] = {"body": body, "shape": shape, "blocking": true}
		armed[key] = false
	queue_redraw()

func _physics_process(_delta: float) -> void:
	if not is_instance_valid(controller) or not is_instance_valid(controller.motor): return
	var position_now := controller.motor.global_position
	var actor_shape := controller.motor.get_node("CollisionShape2D") as CollisionShape2D
	var half := (actor_shape.shape as RectangleShape2D).size / 2.
	for spec: Dictionary in specs:
		var key := str(spec.edge_id); var record: Dictionary = physical[key]
		var values: Array = spec.bounds
		var bounds := Rect2(values[0], values[1], values[2], values[3])
		var flag: Variant = spec.get("switch")
		var enabled: bool = flag == null or str(flag).is_empty() or opened_flags.has(str(flag))
		var blocking := not enabled
		if enabled and spec.get("one_way", false):
			var normal_values: Array = spec.direction
			var normal := Vector2(normal_values[0], normal_values[1]).normalized()
			var relative := position_now - bounds.get_center()
			var along := relative.dot(normal)
			var across := absf(relative.dot(normal.orthogonal()))
			var depth := absf(normal.x) * half.x + absf(normal.y) * half.y
			var aperture := (bounds.size.y if absf(normal.x) > .5 else bounds.size.x) / 2.
			if not armed[key] and along < -depth - 6. and along > -100. and across < aperture - 4.:
				armed[key] = true
				events.append({"frame":frame,"edge_id":key,"event":"one_way_approach_from_allowed_side"})
			if armed[key] and (along > depth + 10. or along < -145.):
				armed[key] = false
			blocking = not armed[key]
		# Never close a collision shape through an overlapping body.
		if blocking and not record.blocking and bounds.grow(2.).intersects(Rect2(position_now - half, half * 2.)):
			blocking = false
		if blocking != bool(record.blocking):
			record.shape.set_deferred("disabled", not blocking)
			record.blocking = blocking
			events.append({"frame":frame,"edge_id":key,"event":"collision_closed" if blocking else "collision_opened"})
	queue_redraw()

func _draw() -> void:
	for spec: Dictionary in specs:
		var raw: Array = spec.bounds
		var bounds := Rect2(raw[0], raw[1], raw[2], raw[3])
		var blocking: bool = physical.get(str(spec.edge_id), {}).get("blocking", true)
		var color := Color("bc8463") if spec.get("one_way", false) else Color("b3b7df")
		draw_rect(bounds, Color(color, .9 if blocking else .12))
		draw_rect(bounds, color, false, 2.)
		if spec.get("one_way", false):
			var direction_values: Array = spec.direction
			var direction := Vector2(direction_values[0], direction_values[1]).normalized()
			var center := bounds.get_center(); var end := center + direction * 20.
			draw_line(center - direction * 14., end, Color.WHITE, 3.)
			draw_line(end, end - direction * 9. + direction.orthogonal() * 7., Color.WHITE, 3.)
			draw_line(end, end - direction * 9. - direction.orthogonal() * 7., Color.WHITE, 3.)
