extends "review040_runner_v3.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="enemy_x_ready":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="enemy_x_ready":
		var q: Dictionary=plan[plan_index].enemy_position;var actor:=observed_enemy(str(q.id))
		return actor!=null and not actor.health.terminal and actor.motor.position.x>=float(q.minimum_x)
	if state=="enemy_below":
		if not super.condition_met(state):return false
		return motor.position.y>=float(plan[plan_index].enemy_window.get("minimum_actor_y",-100000))
	return super.condition_met(state)
