extends "review045_runner_v3.gd"
## Input-only wall climbing. Every contact action receives the registered jitter.
var climb_serial:=0
var climb_ready_frame:=-1
func make_fixture(data: Dictionary) -> void:
	climb_serial=0;climb_ready_frame=-1
	await super.make_fixture(data)
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")in ["climb_y","wall_launch","saw_exit_ready"]:command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="climb_y":return motor.position.y<=float(plan[plan_index].climb_target)
	if state=="saw_exit_ready":return motor.is_on_floor() and context.phase_condition({"kind":"saw_phase","id":"mouth-saw","window":[.28,.34]})
	if state=="wall_launch":
		var q: Array=plan[plan_index].wall_window
		return controller.traversal.state==&"wall_attach" and motor.position.y>=float(q[0]) and motor.position.y<=float(q[1]) and context.phase_condition({"kind":"saw_phase","id":"mouth-saw","window":[.28,.34]})
	return super.condition_met(state)
func control_plan(frame: int) -> Array:
	var climbing: bool=plan_index<plan.size() and plan[plan_index].get("trigger",{}).get("state","")=="climb_y"
	if climbing:
		settling=false
		var axis:=1.0
		for i: int in motor.get_slide_collision_count():
			var collision:=motor.get_slide_collision(i)
			if absf(collision.get_normal().x)>.7:axis=-collision.get_normal().x
		controller.router.set_move_axis(axis)
	var requests:=super.control_plan(frame)
	var ready: bool=climbing and plan_index<plan.size() and plan[plan_index].get("trigger",{}).get("state","")=="climb_y" and ((controller.traversal.state==&"wall_attach" and controller.action_resources.wall_ready) or motor.is_on_floor())
	if ready:
		var key:=10000+climb_serial
		if climb_ready_frame<0:climb_ready_frame=frame+maxi(0,1+timing_error(key))
		if frame>=climb_ready_frame:
			controller.router.request_action(&"jump",Vector2.ZERO)
			requests.append({"type":"jump","direction":[0,0],"plan_index":plan_index,"noise_key":key})
			climb_serial+=1;climb_ready_frame=-1
	else:climb_ready_frame=-1
	return requests
