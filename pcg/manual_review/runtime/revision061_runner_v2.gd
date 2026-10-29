extends "revision061_runner_v1.gd"
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r061_ring_ready':
  if not motor.is_on_floor()or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  for spec: Dictionary in current_case.get('approved_hq_cells',[]):
   if spec.kind!='group_motion'or spec.id!=c.group_id:continue
   var targets: Array=[spec.bell]+spec.access;targets.sort_custom(func(a,b):return motor.position.distance_squared_to(Vector2(a[0],a[1]))<motor.position.distance_squared_to(Vector2(b[0],b[1])))
   for p: Array in targets:
    var target:=Vector2(p[0],p[1]);var d:=corrected_aim(target);var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d);var query:=PhysicsRayQueryParameters2D.create(muzzle,target,1,[motor.get_rid()]);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(query)
    if hit.is_empty()and motor.position.x-d.x*80>=20 and motor.position.x-d.x*80<=620:c.direction=[d.x,d.y];return true
  return false
 if state=='r061_eave_ready':return not motor.is_on_floor()and absf(motor.position.x-428)<4 and motor.position.y<=70 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r061_ellipse_r_board':
  var p=carrier('P');var at: Vector2=p.definition.at_time(context.module.clock+.65);return motor.is_on_floor()and at.x>=450 and at.y>=175 and at.y<=255
 if state=='r061_ellipse_board'and current_case.route_spec.from_port=='B':
  var p=carrier('P');var at: Vector2=p.definition.at_time(context.module.clock+.6);return motor.is_on_floor()and at.x>=410 and at.y>=340
 if state=='r061_ellipse_exit':
  if not motor.is_on_floor()or str(context.snapshot().get('support_id',''))!='P':return false
  var p=carrier('P');var to: String=str(current_case.route_spec.to_port)
  if to=='R':return p.position.x>=440 and p.position.y>=145 and p.position.y<=175 and p.definition.at_time(context.module.clock+.05).x>p.position.x
  if to=='L':return p.position.x<=200 and p.position.y>=260 and p.position.y<=330
  return p.position.x>=400 and p.position.y>=345
 return super.condition_met(state)
func capture_dynamic_frame() -> void:
 super.capture_dynamic_frame()
 if warmup_left==0 and not captured.is_empty():
  var es: Array=[]
  for p: ModuleMovingPlatform in context.module.moving_platforms:
   if p.definition.get_script()==ELLIPSE.DEFINITION:
    var sampled: float=context.module.clock-1./60.;var expected: Vector2=p.definition.at_time(sampled);es.append({'id':str(p.definition.platform_id),'sampled_clock':sampled,'sampling':'original platform priority -100 before module clock increment','expected_error':p.position.distance_to(expected),'rotation':p.rotation,'period':p.definition.period()})
  captured[-1].ellipse=es
