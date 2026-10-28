extends RefCounted
## Stable names plus read-only state for each original scoped latch.
static func install(host) -> void:
	for latch in host.cells.latches:
		if str(latch.link_id)=="left/return-catch":latch.gate_body.name="left_return_catch_gate"
		if str(latch.link_id)=="right/return-catch":latch.gate_body.name="right_return_catch_gate"
static func snapshot(host) -> Dictionary:
	var values: Dictionary={}
	for latch in host.cells.latches:
		var key: String=str(latch.link_id)
		if key not in ["left/return-catch","right/return-catch"]:continue
		var supported: bool=false
		for i in host.motor.get_slide_collision_count():
			var collision: KinematicCollision2D=host.motor.get_slide_collision(i)
			if collision.get_collider()==latch.gate_body and collision.get_normal().y<-.7:supported=true
		values[key]={"open":latch.is_open,"collision_layer":latch.gate_body.collision_layer,"shape_disabled":latch.gate_shape.disabled,"real_top_support":supported,"clock":latch.get("_clock"),"opened_at":latch.get("_opened_at"),"open_seconds":latch.open_seconds}
	return values
