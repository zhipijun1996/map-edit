extends "review045_runner_v2.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="descending_shot_height":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="descending_shot_height":
		return not motor.is_on_floor() and motor.velocity.y>=0 and motor.position.y>=float(plan[plan_index].height_threshold) and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
	if state=="enemy_below" and plan[plan_index].get("enemy_window",{}).has("maximum_actor_y"):
		if motor.position.y>float(plan[plan_index].enemy_window.maximum_actor_y):return false
	return super.condition_met(state)
