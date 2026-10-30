extends "revision062_runner_v10.gd"
func condition_met(state: String) -> bool:
 if state=='r062_s09_return_shot':
  if motor.is_on_floor() or motor.position.x>154 or motor.position.x<138 or motor.position.y<250 or motor.position.y>320 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  plan[plan_index].direction=[.35,sqrt(1-.35*.35)];return true
 return super.condition_met(state)
