extends "revision061_runner_v8.gd"
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r061_l_mode':route_mode='near'if carrier('P').position.x<=240 else'far';return motor.is_on_floor()
 if state=='r061_ring_ready'and str(context.snapshot().get('support_id',''))=='P':
  var p=carrier('P');var offset: float=60 if p.position.x<=240 else -50
  if not motor.is_on_floor()or absf(motor.position.x-p.position.x-offset)>4 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var target:=Vector2(448,432)if offset==60 else Vector2(144,384);var d:=corrected_aim(target);var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d);var query:=PhysicsRayQueryParameters2D.create(muzzle,target,1,[motor.get_rid()]);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(query)
  if hit.is_empty():c.direction=[d.x,d.y];return true
  return false
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get('r061_p_ring_follow',false):c.carrier_offset=60 if carrier('P').position.x<=240 else -50
 var requests:=super.control_plan(frame)
 if plan_index<plan.size()and plan_index>0:
  var c: Dictionary=plan[plan_index]
  if c.get('trigger',{}).get('state','')=='r061_running'and not condition_met('r061_running')and plan[plan_index-1].op=='shoot'and condition_met('r061_ring_ready'):
   var key: int=50000+group_retry_serial
   if group_retry_ready<0:group_retry_ready=frame+maxi(0,1+timing_error(key))
   if frame>=group_retry_ready:
    var d:=disturbed_direction(Vector2(c.direction[0],c.direction[1]),key);controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key});group_retry_serial+=1;group_retry_ready=-1
 return requests
