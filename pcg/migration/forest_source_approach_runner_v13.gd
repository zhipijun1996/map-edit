extends "forest_feedback_runner_v9.gd"
## Original drive_drop input policy. Motor and one-way collision stay native.
var source_last_drop_frame:=-100
func make_fixture(case: Dictionary) -> void:
	source_last_drop_frame=-100
	await super.make_fixture(case)
func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	for command: Dictionary in raw:
		var t: Dictionary=command.get("trigger",{})
		if t.has("source_drop_until_y")and(not(t.source_drop_until_y is float or t.source_drop_until_y is int)or not is_finite(float(t.source_drop_until_y))or t.get("state","")!="grounded"or not t.has("migration_goal")):return "invalid_original_drop_route_target"
	return super.validate_plan(raw)
func control_plan(frame: int) -> Array:
	var requests:=super.control_plan(frame)
	if plan_index<plan.size():
		var trigger: Dictionary=plan[plan_index].get("trigger",{})
		if trigger.has("source_drop_until_y")and motor.is_on_floor()and motor.position.y<float(trigger.source_drop_until_y)-20.0 and frame-source_last_drop_frame>=20:
			controller.router.request_action(&"drop_through",Vector2.ZERO);source_last_drop_frame=frame;requests.append({"type":"drop_through","direction":[0,0],"plan_index":plan_index,"source_original_periodic_drop":true})
	return requests
