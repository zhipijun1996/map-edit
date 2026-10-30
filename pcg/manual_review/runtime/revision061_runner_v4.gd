extends "revision061_runner_v3.gd"
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r061_low_cross':
  if motor.is_on_floor()or motor.position.x<112 or motor.position.y<135 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var up: float=clampf((motor.position.y-119)/154.,0,.7);c.direction=[-sqrt(1-up*up),up];return true
 if state=='r061_eave_ready':return not motor.is_on_floor()and motor.position.x>=428 and motor.position.x<=432 and motor.position.y<=70 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r061_ellipse_r_board':return motor.is_on_floor()and carrier('P').position.x>=460 and carrier('P').position.y>=190 and carrier('P').position.y<=225
 if state=='r061_ellipse_board'and current_case.route_spec.from_port=='B':return motor.is_on_floor()and carrier('P').position.x>=410 and carrier('P').position.y>=350
 if state=='r061_ellipse_exit'and current_case.route_spec.to_port=='R':return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='P'and carrier('P').position.x>=445 and carrier('P').position.y>=175 and carrier('P').position.y<=195
 if state=='r061_ring_ready'and str(context.snapshot().get('support_id',''))in ['P','Q']:
  if not motor.is_on_floor()or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var id: String=str(context.snapshot().get('support_id',''));var offset: float=-32 if id=='P'else -40
  if absf(motor.position.x-carrier(id).position.x-offset)>4:return false
  var target:=Vector2(144,384)if id=='P'else Vector2(192,64);var d:=corrected_aim(target);var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d);var query:=PhysicsRayQueryParameters2D.create(muzzle,target,1,[motor.get_rid()]);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(query)
  if hit.is_empty():c.direction=[d.x,d.y];return true
  return false
 if state=='r061_top_shot':
  if motor.is_on_floor()or motor.position.x>218 or motor.position.x<208 or motor.position.y>120 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var d: Vector2=(motor.position-Vector2(198,-40)).normalized();c.direction=[d.x,d.y];return true
 return super.condition_met(state)
