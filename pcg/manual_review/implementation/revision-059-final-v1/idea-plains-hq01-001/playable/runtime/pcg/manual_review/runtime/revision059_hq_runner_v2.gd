extends "revision059_hq_runner_v1.gd"
func condition_met(state: String) -> bool:
 if state=='hq_top_aligned':return motor.position.x<=210 and motor.position.x>=174 and not motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='hq_saw_low' or state=='hq_saw_high':
  var t: float=context.module.clock;var safe:=true
  for s: ModuleSawDefinition in context.module.definition.saws:
   for k: int in range(18,43):
    var y: float=s.at_time(t+float(k)/60).y
    if state=='hq_saw_low' and y<240 or state=='hq_saw_high' and y>270:safe=false
  return motor.is_on_floor() and safe
 return super.condition_met(state)
