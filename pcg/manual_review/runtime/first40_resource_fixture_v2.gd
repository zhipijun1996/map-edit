extends "first40_resource_fixture_v1.gd"
## Aim is computed from observed height and the original weapon displacement.
## Only Router requests change; no actor, physics or resource values are written.
func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","") in ["shot_ready_below","shot_ready_above"]:command.trigger.state="shot_ready"
	return super.validate_plan(translated)

func condition_met(state: String) -> bool:
	if state in ["shot_ready_below","shot_ready_above"]:
		if not super.condition_met("shot_ready"):return false
		var command: Dictionary=plan[plan_index]
		return motor.position.y<=float(command.height_threshold) if state=="shot_ready_above" else motor.position.y>=float(command.height_threshold)
	return super.condition_met(state)

func control_plan(frame: int) -> Array:
	if plan_index<plan.size():
		var command: Dictionary=plan[plan_index]
		if command.op=="shoot" and command.has("brake_target_y"):
			var displacement: float=motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration
			var dy:=clampf((motor.position.y-float(command.brake_target_y))/displacement,.0,.65)
			command.direction=[-sqrt(1.0-dy*dy),dy]
	return super.control_plan(frame)
