extends "review040_runner_v4.gd"
func condition_met(state: String) -> bool:
	if state=="enemy_x_ready":
		if not super.condition_met(state):return false
		var q: Dictionary=plan[plan_index].enemy_position
		if not q.has("moving_side"):return true
		var actor:=observed_enemy(str(q.id))
		return actor.motor.velocity.x*float(q.moving_side)>0
	return super.condition_met(state)
