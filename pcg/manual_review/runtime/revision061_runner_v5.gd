extends "revision061_runner_v4.gd"
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='carrier_supported':
  var p=carrier(str(c.carrier));return motor.is_on_floor()and str(context.snapshot().get('support_id',''))==str(c.carrier)and absf(motor.position.x-p.position.x-float(settle_options.get('carrier_offset',0)))<3 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r061_ellipse_board'and current_case.route_spec.from_port=='B':
  var p=carrier('P');return motor.is_on_floor()and p.position.x>=455 and p.position.y>=300 and p.position.y<=335
 if state=='r061_above_ellipse':return not motor.is_on_floor()and motor.position.y+18<=carrier('P').position.y-8
 if state=='r061_p_bottom':
  var p=carrier('P');return motor.is_on_floor()and p.position.x>=440 and p.definition.at_time(p.motion_clock+.05).x>=p.position.x
 if state=='r061_ring_ready'and str(context.snapshot().get('support_id',''))=='P':
  if not motor.is_on_floor()or absf(motor.position.x-carrier('P').position.x+50)>4 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var d:=corrected_aim(Vector2(144,384));var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d);var query:=PhysicsRayQueryParameters2D.create(muzzle,Vector2(144,384),1,[motor.get_rid()]);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(query)
  if hit.is_empty():c.direction=[d.x,d.y];return true
  return false
 return super.condition_met(state)
