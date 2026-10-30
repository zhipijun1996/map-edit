extends "revision063_lift_runner_v4.gd"
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if c.get('trigger',{}).get('state','')=='r063_lift_above_g2':c.trigger.state='grounded'
 return super.validate_plan(v)
func lane_safe(id: String,after: float) -> bool:
 for extra: float in [.0,.05,.1,.15,.2,.25,.3]:
  var x:=gear_x('G2',after+extra)
  if (id=='L1' and x<110) or (id=='R1' and x>274):return false
 return true
func can_board(p,travel: float) -> bool:
 var y: float=p.definition.at_time(context.module.clock+travel+1).y
 if y<610 or y>650 or p.definition.at_time(context.module.clock+travel+1.1).y>=y:return false
 var id: String=str(p.definition.platform_id)
 for i: int in range(12,36):
  var dt:=travel+float(i)/10;var at: float=p.definition.at_time(context.module.clock+dt).y
  if at>=540 and at<=570 and p.definition.at_time(context.module.clock+dt+.05).y<at and lane_safe(id,dt) and not upper_choice(dt+.9).is_empty():return true
 return false
func condition_met(state: String) -> bool:
 if state=='revision_lift_transfer':
  var p=carrier(lower_id)
  if not supported(lower_id) or p.position.y<540 or p.position.y>570 or p.definition.at_time(context.module.clock+.05).y>=p.position.y or not lane_safe(lower_id,0):return false
  var next:=upper_choice(.9)
  if next.is_empty():return false
  upper_id=next;return true
 if state=='revision_lift_lower_launch':return supported(lower_id) and absf(motor.position.x-(66 if lower_id=='L1' else 318))<2
 if state=='r063_lift_above_g2':return not motor.is_on_floor() and motor.position.y+18<436
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get('revision_target','')=='lower_launch':c.revision_target='lower'
 for c: Dictionary in plan:
  if c.get('r063_transfer_shot',false):
   var up: float=clampf((motor.position.y-220)/(motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration),.5,.98)
   c.direction=[-sqrt(1-up*up) if upper_id=='R2' else sqrt(1-up*up),up]
 return super.control_plan(frame)
