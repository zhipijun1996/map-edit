extends "review045_forest_runner_v1.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="falling_height":command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="falling_height":return not motor.is_on_floor() and motor.velocity.y>=0 and motor.position.y>=float(plan[plan_index].height_threshold)
	return super.condition_met(state)
