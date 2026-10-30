extends "revision059_repair_runner_v3.gd"
func condition_met(state: String) -> bool:
 if state=='repair_ledge_start':
  if not motor.is_on_floor() or carrier('P').position.y>250:return false
  var t: float=context.module.clock
  for s: ModuleSawDefinition in context.module.definition.saws:
   for k: int in range(24,67):
    if s.at_time(t+float(k)/60).x<240:return false
  return true
 return super.condition_met(state)
