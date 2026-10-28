extends "forest_region_runner_v12.gd"
## Original drive_drop inputs on actual OWP supports. No collider/motor edits.
var source_last_drop_frame:=-100
func make_fixture(case: Dictionary) -> void:
	source_last_drop_frame=-100
	await super.make_fixture(case)
func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	for command: Dictionary in raw:
		var t: Dictionary=command.get("trigger",{})
		if t.has("source_drop_until_y")and(not(t.source_drop_until_y is float or t.source_drop_until_y is int)or not(t.get("source_drop_mouth_x")is float or t.get("source_drop_mouth_x")is int)or not is_finite(float(t.source_drop_until_y))or not is_finite(float(t.source_drop_mouth_x))or t.get("state","")!="grounded"or not t.has("migration_goal")):return "invalid_original_drop_route_target"
	return super.validate_plan(raw)
func control_plan(frame: int) -> Array:
	var requests:=super.control_plan(frame)
	if plan_index<plan.size():
		var t: Dictionary=plan[plan_index].get("trigger",{})
		if t.has("source_drop_until_y")and motor.is_on_floor()and absf(motor.position.x-float(t.source_drop_mouth_x))<7.0 and motor.position.y<float(t.source_drop_until_y)-20.0 and frame-source_last_drop_frame>=20:
			controller.router.request_action(&"drop_through",Vector2.ZERO);source_last_drop_frame=frame;requests.append({"type":"drop_through","direction":[0,0],"plan_index":plan_index,"source_original_periodic_drop":true})
	return requests
