extends "revision060_runner_v10.gd"
const ELLIPSE=preload('revision061_ellipse_install_v1.gd')
func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
 var d:=super.definition_for(data);ELLIPSE.install(d,data);return d
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true)if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get('trigger',{}).get('state','')).begins_with('r061_'):c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r061_running':
  for l: ShotLatch in cells.latches:
   if str(l.link_id)==str(c.group_id):return l.is_open==bool(c.running)
  return false
 if state=='r061_ring_ready':
  if not motor.is_on_floor()or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  for spec: Dictionary in current_case.get('approved_hq_cells',[]):
   if spec.kind!='group_motion'or spec.id!=c.group_id:continue
   var targets: Array=[spec.bell]+spec.access
   for p: Array in targets:
    var target:=Vector2(p[0],p[1]);var d:=corrected_aim(target);var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d);var query:=PhysicsRayQueryParameters2D.create(muzzle,target,1,[motor.get_rid()]);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(query)
    if hit.is_empty():c.direction=[d.x,d.y];return true
  return false
 if state=='r061_p_board':
  var p=carrier('P');return motor.is_on_floor()and p.position.x<=210 and p.definition.at_time(p.motion_clock+.5).x<250
 if state=='r061_p_bottom':return motor.is_on_floor()and carrier('P').position.x>=420
 if state=='r061_p_transfer':return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='P'and carrier('P').position.x>=270 and carrier('P').position.x<=300
 if state=='r061_q_exit':return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='Q'and carrier('Q').position.y>=200 and carrier('Q').position.y<=220
 if state=='r061_p_left':return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='P'and carrier('P').position.x>=230 and carrier('P').position.x<=250
 if state=='r061_top_shot':
  if motor.is_on_floor()or motor.position.x>226 or motor.position.y>120 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var d: Vector2=(motor.position-Vector2(192,-40)).normalized();c.direction=[d.x,d.y];return true
 if state=='r061_ellipse_board':
  var p=carrier('P');var t: float=context.module.clock;var at: Vector2=p.definition.at_time(t+.6);return motor.is_on_floor()and absf(at.x-float(c.x))<150 and at.y<float(c.y)-12 and at.y>float(c.y)-130
 if state=='r061_ellipse_exit':
  if not motor.is_on_floor()or str(context.snapshot().get('support_id',''))!='P':return false
  var p=carrier('P');var goal:=Vector2(c.target[0],c.target[1]);return absf(p.position.x-goal.x)<170 and p.position.y-26<=goal.y+120 and p.position.y-26>=goal.y-50
 if state=='r061_saw_window':
  var t: float=context.module.clock
  for saw: ModuleSawDefinition in context.module.definition.saws:
   if saw.at_time(t+.35).x>175 or saw.at_time(t+.7).x>175:return false
  return motor.is_on_floor()
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 while plan_index<plan.size()and plan[plan_index].has('group_id')and plan[plan_index].op=='shoot'and plan[plan_index].has('running'):
  var matches:=false
  for l: ShotLatch in cells.latches:
   if str(l.link_id)==str(plan[plan_index].group_id):matches=l.is_open==bool(plan[plan_index].running)
  if not matches:break
  plan_index+=1
 return super.control_plan(frame)
func capture_dynamic_frame() -> void:
 super.capture_dynamic_frame()
 if warmup_left==0 and not captured.is_empty():
  var es: Array=[]
  for p: ModuleMovingPlatform in context.module.moving_platforms:
   if p.definition.get_script()==ELLIPSE.DEFINITION:
    var expected: Vector2=p.definition.at_time(context.module.clock);es.append({'id':str(p.definition.platform_id),'expected_error':p.position.distance_to(expected),'rotation':p.rotation,'period':p.definition.period()})
  captured[-1].ellipse=es
