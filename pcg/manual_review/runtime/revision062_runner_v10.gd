extends "revision062_runner_v9.gd"
func condition_met(state: String) -> bool:
 if state=='r062_saw_low':
  for saw: ModuleSawDefinition in context.module.definition.saws:
   var delay: float=float(plan[plan_index].get('lookahead',.4))
   for i: int in range(0,7,2):
    if saw.at_time(context.module.clock+delay+float(i)/60).y>197:return false
  return motor.is_on_floor()
 return super.condition_met(state)
