extends "ideas_runner_v8.gd"
## Spend the final empty recoil on descent, keeping the whole body in the TOP mouth.
func condition_met(state: String) -> bool:
	if state=="chain_final":
		return super.condition_met(state) and motor.position.y>=100 and motor.velocity.y>=0
	return super.condition_met(state)
