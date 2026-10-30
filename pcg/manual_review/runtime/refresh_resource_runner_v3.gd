extends "first40_resource_fixture_v2.gd"
func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","")=="height_at_least":command.trigger.state="airborne"
	return super.validate_plan(translated)
func condition_met(state: String) -> bool:
	if state=="height_at_least":return not motor.is_on_floor() and motor.position.y>=float(plan[plan_index].height_threshold)
	return super.condition_met(state)
