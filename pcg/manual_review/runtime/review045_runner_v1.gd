extends "review040_runner_v7.gd"
## Read-only position and burst guard. Previous registered programs stay frozen.
func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	if not trigger.has("migration_goal"):return true
	return rect(trigger.migration_goal).has_point(motor.position) and motor.recoil_burst_remaining<=0.000001
