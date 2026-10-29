extends "revision062_runner_v1.gd"
## Counter omission waits observe state; they must not synthesize omitted shots.
func run_case(data: Dictionary) -> Dictionary:
 var c:=data.duplicate(true)
 for command: Dictionary in c.get('control_plan',[]):
  if command.get('trigger',{}).get('state','')=='pair_desired'and not command.has('direction'):command.trigger.state='r062_pair_observe'
 return await super.run_case(c)
func condition_met(state: String) -> bool:
 if state=='r062_pair_observe':return pair_open(str(plan[plan_index].pair_desired))
 return super.condition_met(state)
