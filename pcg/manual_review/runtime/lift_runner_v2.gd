extends "lift_runner_v1.gd"
func condition_met(state: String) -> bool:
	if state=="lift_board":
		var p=lift_named(str(plan[plan_index].lift_window.id))
		if p==null or not motor.is_on_floor() or p.position.y<760 or p.definition.at_time(context.module.clock+.15).y>p.position.y:return false
		for dt: float in [.18,.3,.45,.6]:
			if saw_x("G1",dt)<205:return false
		return true
	return super.condition_met(state)
