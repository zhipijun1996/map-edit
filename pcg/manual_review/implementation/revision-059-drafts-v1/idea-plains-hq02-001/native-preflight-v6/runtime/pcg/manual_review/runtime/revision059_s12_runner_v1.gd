extends "revision059_repair_runner_v1.gd"
func condition_met(state: String) -> bool:
 if state=='repair_s12_left_q':
  var q=carrier('Q');var t: float=context.module.clock
  return motor.is_on_floor() and q.position.x>=265 and q.position.x<=300 and q.definition.at_time(t+.05).y<q.position.y
 return super.condition_met(state)
