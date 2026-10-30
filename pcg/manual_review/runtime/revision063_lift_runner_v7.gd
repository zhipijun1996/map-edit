extends "revision063_lift_runner_v4.gd"
var r063_transfer_takeoff:=100000.0
func make_fixture(data: Dictionary) -> void:
 r063_transfer_takeoff=100000.0
 await super.make_fixture(data)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get('trigger',{}).get('state','')).begins_with('r063_lift_'):c.trigger.state='grounded'
 return super.validate_plan(v)
func lane_safe(id: String,after: float) -> bool:
 for extra: float in [.0,.05,.1,.15,.2,.25,.3]:
  var x:=gear_x('G2',after+extra)
  if (id=='L1' and x<250) or (id=='R1' and x>134):return false
 return true
func can_board(p,travel: float) -> bool:
 var y: float=p.definition.at_time(context.module.clock+travel+1).y
 if y<610 or y>650 or p.definition.at_time(context.module.clock+travel+1.1).y>=y:return false
 var id: String=str(p.definition.platform_id)
 for i: int in range(12,36):
  var dt:=travel+float(i)/10;var at: float=p.definition.at_time(context.module.clock+dt).y
  if at>=580 and at<=610 and p.definition.at_time(context.module.clock+dt+.05).y<at and lane_safe(id,dt+.4) and not upper_choice(dt+1.3).is_empty():return true
 return false
func condition_met(state: String) -> bool:
 if state=='revision_lift_transfer':
  var p=carrier(lower_id)
  if not supported(lower_id) or p.position.y<580 or p.position.y>610 or p.definition.at_time(context.module.clock+.05).y>=p.position.y or not lane_safe(lower_id,.4):return false
  var next:=upper_choice(1.3)
  if next.is_empty():return false
  upper_id=next;return true
 if state=='revision_lift_lower_launch':return supported(lower_id) and absf(motor.position.x-(164 if lower_id=='L1' else 220))<2
 if state=='r063_lift_transfer_shot':return r063_transfer_takeoff<10000 and not motor.is_on_floor() and motor.position.y<=r063_transfer_takeoff-130 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r063_lift_above_g2':return not motor.is_on_floor() and motor.position.y+18<436
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get('revision_target','') in ['lower_launch','lower','r063_lower_launch'] and c.get('r063_launch_pose',false):c.revision_target='r063_lower_launch';c.target_x=164 if lower_id=='L1' else 220
 for c: Dictionary in plan:
  if c.get('r063_transfer_shot',false):
   var up: float=clampf((motor.position.y-220)/(motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration),.5,.98)
   c.direction=[-sqrt(1-up*up) if upper_id=='R2' else sqrt(1-up*up),up]
 var requests:=super.control_plan(frame)
 if not fired_commands.is_empty():
  var last: Dictionary=fired_commands[-1]
  if int(last.index)==16 and last.op=='jump' and int(last.frame)==frame:r063_transfer_takeoff=float(last.position[1])
 return requests
