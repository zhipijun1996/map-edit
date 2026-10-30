extends "revision061_runner_v6.gd"
func condition_met(state: String) -> bool:
 if state=='r061_orbit_right_shot':
  if motor.is_on_floor()or motor.position.y<100 or motor.position.y>125 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var up: float=clampf((motor.position.y-55)/154.,0,.7);plan[plan_index].direction=[-sqrt(1-up*up),up];return true
 return super.condition_met(state)
