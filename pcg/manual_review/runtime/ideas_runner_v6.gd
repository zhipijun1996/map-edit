extends "ideas_runner_v5.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="chain_setup":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state in ["chain_setup","chain_prepared"]:
		var first:=observed_enemy("enemy-1");var second:=observed_enemy("enemy-2")
		if first==null or second==null or not motor.is_on_floor():return false
		var a=first.attack_behavior;var b=second.attack_behavior
		if a==null or b==null or b.state!=&"idle":return false
		if state=="chain_setup":return a.state==&"idle" and a.cooldown<=.000001 and second.motor.position.x<=262 and cos(b.state_time*1.8)<=0
		return a.state==&"attack" and first.motor.position.y>=510 and a.state_time<=.32 and second.motor.position.x>=330 and second.motor.position.x<=365 and cos(b.state_time*1.8)>0
	return super.condition_met(state)
