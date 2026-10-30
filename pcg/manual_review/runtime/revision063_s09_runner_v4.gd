extends "revision062_runner_v10.gd"
func condition_met(state: String) -> bool:
 if state=='r062_s09_return_shot':
  if motor.is_on_floor() or motor.position.x>192 or motor.position.x<176 or motor.position.y<240 or motor.position.y>280 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var up: float=clampf((motor.position.y-184)/154.,.1,.65)
  plan[plan_index].direction=[sqrt(1-up*up),up];return true
 return super.condition_met(state)
