extends "lift_runner_v9.gd"
func condition_met(state: String) -> bool:
	if state=="lift_finish" and str(plan[plan_index].lift_window.id)=="selected_upper":
		return super.condition_met(state) and lift_named(chosen_upper).position.y<=330
	return super.condition_met(state)
