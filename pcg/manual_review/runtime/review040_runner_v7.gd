extends "review040_runner_v6.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="enemy_y_ready":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="enemy_y_ready":
		var q: Dictionary=plan[plan_index].enemy_position
		var actor:=observed_enemy(str(q.id))
		return actor!=null and not actor.health.terminal and actor.motor.position.y>=float(q.minimum_y)
	return super.condition_met(state)
