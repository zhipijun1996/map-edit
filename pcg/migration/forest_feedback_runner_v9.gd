extends "forest_feedback_runner_v7.gd"
## A source-observed departure condition, never a position/velocity assignment.
func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	for command: Dictionary in raw:
		var trigger: Dictionary=command.get("trigger",{})
		if trigger.has("source_min_y") and (not(trigger.source_min_y is float or trigger.source_min_y is int) or not is_finite(float(trigger.source_min_y))):return "invalid_source_departure_y"
	return super.validate_plan(raw)

func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	return not trigger.has("source_min_y") or (not motor.is_on_floor() and motor.position.y>=float(trigger.source_min_y))
