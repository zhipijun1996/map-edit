extends "refresh_resource_runner_v3.gd"
func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","")=="height_at_most":command.trigger.state="airborne"
	return super.validate_plan(translated)
func condition_met(state: String) -> bool:
	if state=="height_at_most":return not motor.is_on_floor() and motor.position.y<=float(plan[plan_index].height_threshold)
	return super.condition_met(state)
func control_plan(frame: int) -> Array:
	if plan_index>=plan.size() or not plan[plan_index].has("brake_target_y"):return super.control_plan(frame)
	var command: Dictionary=plan[plan_index];var target: float=command.brake_target_y
	var displacement: float=motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration
	var dy:=clampf((motor.position.y-target)/displacement,.0,.65)
	if command.op!="shoot" or not command.has("direction"):
		command.erase("brake_target_y")
		var omitted:=super.control_plan(frame)
		command.brake_target_y=target
		return omitted
	var side:=signf(float(command.direction[0]))
	command.direction=[side*sqrt(1-dy*dy),dy];command.erase("brake_target_y")
	var result:=super.control_plan(frame)
	command.brake_target_y=target
	return result
