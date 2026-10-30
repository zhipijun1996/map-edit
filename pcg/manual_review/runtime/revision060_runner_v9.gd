extends "revision060_runner_v8.gd"
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r060_top_aligned':return absf(motor.position.x-192)<=2.5 and not motor.is_on_floor()and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r060_group_entry_shot':
  if motor.is_on_floor()or motor.position.y>225 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var up: float=clampf((motor.position.y-60)/154.,0,.94);c.direction=[-sqrt(1-up*up),up];return true
 if state=='r060_group_left':return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='P'and carrier('P').position.x>=280 and carrier('P').position.x<=300 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r060_q_pose_check':return carrier('Q').position.y>=196 and carrier('Q').position.y<=230
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 if plan_index<plan.size()and plan[plan_index].get('trigger',{}).get('state','')=='r060_q_pose_check'and not condition_met('r060_q_pose_check'):
  for i: int in plan.size():
   if plan[i].get('q_pose_entry',false):plan_index=i;previous_plan_frame=frame;break
 for c: Dictionary in plan:
  if c.get('transfer_follow',false):c.carrier_offset=32 if carrier('P').position.x<216 else 0
 return super.control_plan(frame)
