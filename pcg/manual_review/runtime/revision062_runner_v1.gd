extends "revision061_runner_v11.gd"
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true)if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get('trigger',{}).get('state','')).begins_with('r062_'):c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='r060_below_q':return motor.position.y>=carrier('Q').position.y+28
 if state=='r062_top_vertical':return not motor.is_on_floor()and absf(motor.position.x-192)<=2.5 and motor.position.y<=140 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r062_left_window':
  var p=carrier('P');return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='P'and p.position.x>=280 and p.position.x<=300 and p.definition.at_time(p.motion_clock+.05).x<p.position.x and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r062_left_pose_ok':return carrier('P').position.x<=280
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 if plan_index<plan.size()and plan[plan_index].get('trigger',{}).get('state','')=='r062_left_pose_ok'and not condition_met('r062_left_pose_ok'):
  for i: int in plan.size():
   if plan[i].get('r062_left_pose_entry',false):plan_index=i;previous_plan_frame=frame;break
 for c: Dictionary in plan:
  if c.get('r062_group_transfer_out',false):c.target_x=carrier('Q').position.x+(-62 if carrier('P').position.x<carrier('Q').position.x else 62)
 var requests:=super.control_plan(frame)
 if plan_index<plan.size()and current_case.get('approved_implementation',{}).get('reviewId','')=='idea-plains-hq03-001'and current_case.route_spec.from_port=='R'and plan[plan_index].get('trigger',{}).get('state','')=='r060_fight':settle_options.target_x=368
 return requests
