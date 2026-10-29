extends "review045_runner_v1.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="enemy_attack_ready":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="enemy_attack_ready":
		var actor:=observed_enemy(str(plan[plan_index].enemy_id))
		return actor!=null and not actor.health.terminal and actor.attack_behavior!=null and actor.attack_behavior.state==&"attack"
	return super.condition_met(state)
