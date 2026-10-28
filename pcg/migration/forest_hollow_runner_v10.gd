extends "forest_feedback_runner_v9.gd"
## Observe the original elbow's full-body departure before casting; no motor edits.
func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	for command: Dictionary in raw:
		var trigger: Dictionary=command.get("trigger",{})
		if trigger.has("source_right_of") and (not(trigger.source_right_of is float or trigger.source_right_of is int)or not is_finite(float(trigger.source_right_of))):return "invalid_original_elbow_departure"
	return super.validate_plan(raw)
func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	return not trigger.has("source_right_of") or (not motor.is_on_floor()and motor.position.x>=float(trigger.source_right_of))
