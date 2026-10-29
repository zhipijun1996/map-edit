extends "ideas_runner_v6.gd"
## Read the real capped enemy velocity; the orbit target's cosine is not its speed.
func condition_met(state: String) -> bool:
	if state=="chain_setup":
		var first:=observed_enemy("enemy-1");var second:=observed_enemy("enemy-2")
		return first!=null and second!=null and motor.is_on_floor() and first.attack_behavior.state==&"idle" and first.attack_behavior.cooldown<=.000001 and second.attack_behavior.state==&"idle" and second.motor.position.x<=287 and second.motor.velocity.x<0
	return super.condition_met(state)
