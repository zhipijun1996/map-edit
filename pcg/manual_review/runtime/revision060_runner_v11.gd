extends "revision060_runner_v10.gd"
func condition_met(state: String) -> bool:
 if state=='r060_top_aligned':
  if motor.is_on_floor()or motor.position.x>218 or motor.position.x<208 or motor.position.y>120 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var d: Vector2=(motor.position-Vector2(198,-40)).normalized();plan[plan_index].direction=[d.x,d.y];return true
 if state=='r060_group_left':
  var p=carrier('P');return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='P'and p.position.x>=300 and p.position.x<=320 and p.definition.at_time(p.motion_clock+.05).x<p.position.x and controller.shoot_ability.cooldown_remaining<=.000001
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 var requests:=super.control_plan(frame)
 for c: Dictionary in plan:
  if c.get('group_transfer_out',false):c.target_x=carrier('Q').position.x+(-62 if carrier('P').position.x<carrier('Q').position.x else 62)
 return requests
