extends "revision060_runner_v1.gd"
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index];var t: float=context.module.clock
 if state=='revision_clear'and c.get('allow_partial',false):
  var e=observed_enemy(str(c.enemy))
  if e!=null and e.health.current<=1:return true
 if state=='r060_q_park_ready':
  var q=carrier('Q');return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='Q'and q.position.y>=205 and q.position.y<=214 and q.definition.at_time(q.motion_clock+.05).y>q.position.y and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r060_lure_window':
  var p=carrier('P');return motor.is_on_floor()and p.position.y>=420 and p.definition.at_time(t+.2).y<p.position.y
 if state=='r060_08_drop_clear':
  for saw: ModuleSawDefinition in context.module.definition.saws:
   for k: int in range(18,43):
    if saw.at_time(t+float(k)/60).x>250:return false
  return motor.is_on_floor()
 if state=='r060_barrier_clear':
  var p=carrier('P');return motor.is_on_floor()and p.position.y>=370 and p.definition.at_time(p.motion_clock+.4).y>=330
 return super.condition_met(state)
