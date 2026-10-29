extends "review040_runner_v5.gd"
func condition_met(state: String) -> bool:
	if state=="enemy_x_ready":
		if not super.condition_met(state):return false
		var q: Dictionary=plan[plan_index].enemy_position
		return observed_enemy(str(q.id)).motor.position.x<=float(q.get("maximum_x",100000))
	return super.condition_met(state)
