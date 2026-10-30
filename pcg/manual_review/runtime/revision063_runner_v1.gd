extends "revision062_runner_v1.gd"
## Directionless pair waits observe only; omitted shot counters cannot fire.
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if c.get('trigger',{}).get('state','')=='r063_pair_observe':c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='r063_pair_observe':return super.condition_met('pair_desired')
 return super.condition_met(state)
