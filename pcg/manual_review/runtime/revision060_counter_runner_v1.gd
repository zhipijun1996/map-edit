extends "revision060_runner_v11.gd"
## A directionless pair wait is observation, including omission counter cases.
## Do not invent an omitted shot or let the legacy retry read a missing key.
func run_case(data: Dictionary) -> Dictionary:
 var c:=data.duplicate(true)
 for command: Dictionary in c.get('control_plan',[]):
  if command.get('trigger',{}).get('state','')=='pair_desired'and not command.has('direction'):command.trigger.state='r060_pair_observe'
 return await super.run_case(c)
func condition_met(state: String) -> bool:
 if state=='r060_pair_observe':return pair_open(str(plan[plan_index].pair_desired))
 return super.condition_met(state)
