extends "revision059_repair_runner_v4.gd"
func condition_met(state: String) -> bool:
 if state=='repair_ledge_board':
  var p=carrier('P');var t: float=context.module.clock
  if not motor.is_on_floor() or p.position.y<360 or p.position.y>430 or p.definition.at_time(t+.05).y>=p.position.y:return false
  for s: ModuleSawDefinition in context.module.definition.saws:
   for k: int in range(24,61):
    if s.at_time(t+float(k)/60).x<210:return false
  return true
 return super.condition_met(state)
