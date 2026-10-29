extends "revision061_runner_v5.gd"
func condition_met(state: String) -> bool:
 if state=='r061_ellipse_board'and current_case.route_spec.from_port=='B':return motor.is_on_floor()and carrier('P').position.x>=390 and carrier('P').position.y>=360 and carrier('P').position.y<=385
 if state=='r061_q_exit':
  var p=carrier('Q');return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='Q'and p.position.y>=210 and p.position.y<=222 and p.definition.at_time(p.motion_clock+.05).y>p.position.y and controller.shoot_ability.cooldown_remaining<=.000001
 return super.condition_met(state)
