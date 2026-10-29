extends "ideas_runner_v9.gd"
## Observe the actual first diver's horizontal pose as well as attack phase.
## Random initial idle cooldown can put it far left at the same state time.
func condition_met(state: String) -> bool:
	if state=="chain_prepared":
		var first:=observed_enemy("enemy-1")
		return super.condition_met(state) and first!=null and first.motor.position.x>=130 and first.motor.position.x<=178
	return super.condition_met(state)
