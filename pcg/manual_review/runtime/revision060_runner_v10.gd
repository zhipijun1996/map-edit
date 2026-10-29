extends "revision060_runner_v9.gd"
func condition_met(state: String) -> bool:
 if state=='r060_top_aligned':
  if motor.is_on_floor()or motor.position.x>226 or motor.position.x<210 or motor.position.y>120 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var d: Vector2=(motor.position-Vector2(192,-40)).normalized();plan[plan_index].direction=[d.x,d.y];return true
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 var requests:=super.control_plan(frame)
 if plan_index<plan.size()and plan[plan_index].get('trigger',{}).get('state','')=='r060_fight':settle_options.target_x=clampf(float(settle_options.target_x),224,300)
 return requests
