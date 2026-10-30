extends "ideas_runner_v4.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="chain_prepared":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="chain_prepared":
		var first:=observed_enemy("enemy-1");var second:=observed_enemy("enemy-2")
		if first==null or second==null or not motor.is_on_floor():return false
		var a=first.attack_behavior;var b=second.attack_behavior
		return a!=null and b!=null and ((a.state==&"telegraph" and a.state_time>=.5) or (a.state==&"attack" and a.state_time<=.1)) and b.state==&"idle" and second.motor.position.x>=330 and second.motor.position.x<=410 and cos(b.state_time*1.8)>=0
	return super.condition_met(state)
