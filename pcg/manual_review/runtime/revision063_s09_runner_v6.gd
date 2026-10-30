extends "revision063_s09_runner_v5.gd"
func condition_met(state: String) -> bool:
 if state=='r062_saw_low' and current_case.route_spec.from_port=='B':
  if not motor.is_on_floor():return false
  for saw: ModuleSawDefinition in context.module.definition.saws:
   for ticks: int in range(21,34,2):
    if saw.at_time(context.module.clock+float(ticks)/60).y>200:return false
  return true
 return super.condition_met(state)
