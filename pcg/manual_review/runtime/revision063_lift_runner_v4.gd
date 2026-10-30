extends "revision063_lift_runner_v2.gd"
## Observe all three saws before selecting a carrier handoff. Final launch
## phase is part of the choice; waiting above G3 is not a safe fallback.
func upper_choice(after: float) -> String:
 for id: String in ['L2','R2']:
  var p=carrier(id);var y: float=p.definition.at_time(context.module.clock+after).y
  if y<300 or p.definition.at_time(context.module.clock+after+.1).y>y:continue
  for step: int in range(0,25):
   var dt:=after+float(step)/20
   var at: float=p.definition.at_time(context.module.clock+dt).y
   if at<280 or at>375 or p.definition.at_time(context.module.clock+dt+.05).y>=at:continue
   var safe:=true
   for padding: float in [.15,.25,.35,.45,.55]:
    var x:=gear_x('G3',dt+padding)
    if (id=='L2' and x<260) or (id=='R2' and x>124):safe=false
   if safe:return id
 return ''
func condition_met(state: String) -> bool:
 if state=='revision_lift_finish':
  if not supported(upper_id):return false
  var p=carrier(upper_id)
  if p.position.y<280 or p.position.y>375:return false
  finish_x=140 if upper_id=='L2' else 244
  var travel:=absf(motor.position.x-finish_x)/motor.tuning.ground_speed
  for dt: float in [.05,.1,.15,.2,.25,.3]:
   var actor_x:=finish_x+signf(192-finish_x)*minf(absf(192-finish_x),motor.tuning.ground_speed*dt)
   if absf(actor_x-gear_x('G3',travel+dt))<60:return false
  return true
 return super.condition_met(state)
