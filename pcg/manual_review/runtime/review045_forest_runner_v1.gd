extends "../../migration/forest_region_ui_runner_v16.gd"
## Preserve original hook, pickup and OR chest consumers; observe the real body.
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="observed_height":command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="observed_height":
		var q: Dictionary=plan[plan_index].observed_y
		return motor.position.y>=float(q.value) if q.direction=="gte" else motor.position.y<=float(q.value)
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	if not trigger.has("migration_goal"):return true
	return rect(trigger.migration_goal).has_point(motor.position) and motor.recoil_burst_remaining<=0.000001
