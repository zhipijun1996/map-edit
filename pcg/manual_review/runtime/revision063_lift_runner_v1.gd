extends "revision053_lift_runner_v2.gd"
func can_board(p,travel: float) -> bool:
 var y: float=p.definition.at_time(context.module.clock+travel+1).y
 return y>=610 and y<=650 and p.definition.at_time(context.module.clock+travel+1.1).y<y
func condition_met(state: String) -> bool:
 if state=='revision_lift_finish':
  if not supported(upper_id):return false
  var p=carrier(upper_id)
  if p.position.y<330 or p.position.y>375:return false
  finish_x=140 if upper_id=='L2' else 244
  return true
 if state=='revision_lift_finish_edge':
  if not supported(upper_id) or absf(motor.position.x-finish_x)>=2:return false
  for i: int in range(0,29,2):
   var x:=gear_x('G3',float(i)/60)
   if (upper_id=='L2' and x<260) or (upper_id=='R2' and x>124):return false
  return true
 return super.condition_met(state)
