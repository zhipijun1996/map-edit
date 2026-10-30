extends "revision062_runner_v7.gd"
func condition_met(state: String) -> bool:
 if state=='r062_s09_return_shot':
  if motor.is_on_floor()or absf(motor.position.x-230)>3 or motor.position.y<253 or motor.position.y>260 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var up: float=clampf((motor.position.y-204)/154.,.1,.6);plan[plan_index].direction=[sqrt(1-up*up),up];return true
 return super.condition_met(state)
