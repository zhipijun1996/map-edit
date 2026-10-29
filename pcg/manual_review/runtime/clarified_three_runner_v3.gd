extends "clarified_three_runner_v2.gd"
## Input precedes original Controller.physics_tick, which advances cooldown
## before try_fire. Permit that next-tick window, without changing cooldown.
func condition_met(state: String) -> bool:
	if state=="shot_ready" and current_case.approved_implementation.reviewId=="171":
		for event: Dictionary in fired_commands:
			if int(event.frame)==clarified_input_frame and plan[int(event.index)].op=="shoot":return false
		return cells.enemies.size()==2 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=1./60.+.000001
	return super.condition_met(state)
