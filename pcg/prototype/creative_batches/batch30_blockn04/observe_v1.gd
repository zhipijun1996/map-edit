extends RefCounted
## Existing real bodies only: stable name and read-only collision/timer snapshot.
static func install(host) -> void:
	for latch in host.cells.latches:
		if str(latch.link_id)=="return-catch":latch.gate_body.name="n04_return_catch_gate"
static func snapshot(host) -> Dictionary:
	for latch in host.cells.latches:
		if str(latch.link_id)!="return-catch":continue
		var supported:=false
		for i in host.motor.get_slide_collision_count():
			var collision: KinematicCollision2D=host.motor.get_slide_collision(i)
			if collision.get_collider()==latch.gate_body and collision.get_normal().y<-.7:supported=true
		return {"open":latch.is_open,"collision_layer":latch.gate_body.collision_layer,"shape_disabled":latch.gate_shape.disabled,"real_top_support":supported,"clock":latch.get("_clock"),"opened_at":latch.get("_opened_at"),"open_seconds":latch.open_seconds}
	return {}
