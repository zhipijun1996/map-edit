extends "first40_game_air_v2.gd"

func condition_met(state: String) -> bool:
	if state=="grounded_shot_ready":
		if not super.condition_met(state):return false
		var trigger: Dictionary=plan[plan_index].get("trigger",{})
		return not trigger.has("migration_goal") or rect(trigger.migration_goal).has_point(motor.position)
	return super.condition_met(state)
