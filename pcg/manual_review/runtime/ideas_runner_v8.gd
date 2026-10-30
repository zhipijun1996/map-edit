extends "ideas_runner_v7.gd"
## Start the jump at the beginning of the actual dive, before body contact.
func condition_met(state: String) -> bool:
	if state=="chain_prepared":
		var first:=observed_enemy("enemy-1");var second:=observed_enemy("enemy-2")
		return first!=null and second!=null and motor.is_on_floor() and first.attack_behavior.state==&"attack" and first.attack_behavior.state_time>=.016 and first.attack_behavior.state_time<=.08 and second.attack_behavior.state==&"idle" and second.motor.position.x>=330 and second.motor.position.x<=365 and second.motor.velocity.x>0
	return super.condition_met(state)
