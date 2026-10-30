extends "ideas_runner_v3.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="accepted_shot_burst":command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="accepted_shot_burst":return motor.recoil_burst_remaining>0 and controller.shoot_ability.cooldown_remaining>0
	if state=="chain_final" and plan[plan_index].has("final_x"):
		if absf(motor.position.x-float(plan[plan_index].final_x))>3:return false
	return super.condition_met(state)
