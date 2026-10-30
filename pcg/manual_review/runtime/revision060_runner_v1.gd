extends "revision059_s12_runner_v1.gd"
const R060=preload('revision060_binding_v1.gd')
const INTERCEPT=preload('revision059_interception_observer_v1.gd')
var r060
var interception
var seed_serial:=0
var takeoff_y:=0.
func make_fixture(data: Dictionary) -> void:
 await super.make_fixture(R060.ordinary(data));current_case=data;r060=R060.new();world.add_child(r060);r060.setup(data,world,controller,context,cells,extra);interception=INTERCEPT.new();world.add_child(interception);interception.setup(cells.enemies,context)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get('trigger',{}).get('state','')).begins_with('r060_'):c.trigger.state='grounded'
 return super.validate_plan(v)
func has_interception() -> bool:
 return interception.events.any(func(e: Dictionary):return e.type=='original_enemy_projectile_intercepted'and e.get('disposed',false)and e.get('remaining_after',0)>0)
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index];var t: float=context.module.clock
 if state=='r060_seed':
  for actor: EnemyActor in cells.enemies:
   if actor.attack_behavior!=null and actor.attack_behavior._serial>seed_serial and not actor.attack_behavior._projectiles.is_empty():seed_serial=actor.attack_behavior._serial;return true
  return false
 if state=='r060_intercepted':return has_interception()
 if state=='r060_carrier_height':
  var p=carrier(str(c.get('carrier','P')));return motor.is_on_floor() and p.position.y>=float(c.get('ymin',-10000))and p.position.y<=float(c.get('ymax',10000))and(not c.get('supported',false)or str(context.snapshot().get('support_id',''))==str(c.get('carrier','P')))
 if state=='r060_top_aligned':return motor.position.x<=210 and motor.position.x>=174 and not motor.is_on_floor()and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r060_group_board':
  var p=carrier('P');return motor.is_on_floor()and p.position.x<=205 and p.definition.at_time(p.motion_clock+.5).x<=250 and p.definition.at_time(p.motion_clock+.05).x>=p.position.x
 if state=='r060_group_left':return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='P'and carrier('P').position.x>=240 and carrier('P').position.x<=270
 if state=='r060_ring_ready':
  if not motor.is_on_floor()or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var id: String=str(c.get('group_carrier',''))
  if id not in ['','<null>']:
   if str(context.snapshot().get('support_id',''))!=id:return false
   var offset: float=32 if id=='Q'or carrier(id).position.x<230 else 0
   if absf(motor.position.x-carrier(id).position.x-offset)>4:return false
  var targets: Array=[Vector2(136,368),Vector2(192,72),Vector2(584,48)]
  if id=='Q':targets=[Vector2(584,48)]
  elif id=='P'and carrier(id).position.x<230:targets=[Vector2(192,72)]
  elif str(current_case.route_spec.from_port)=='R'and id in ['','<null>']:targets=[Vector2(584,48)]
  for target: Vector2 in targets:
   var direction:=corrected_aim(target);var visual: CourierVisual=motor.get_node('CourierVisual');var muzzle: Vector2=visual.muzzle_position(direction)
   var query:=PhysicsRayQueryParameters2D.create(muzzle,target,1,[motor.get_rid()]);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(query)
   if hit.is_empty():c.direction=[direction.x,direction.y];return true
  return false
 if state=='r060_group_running':
  for l: ShotLatch in cells.latches:
   if str(l.link_id)=='group-bell':return l.is_open==bool(c.get('running',true))
  return false
 if state=='r060_08_exit':
  if not motor.is_on_floor()or str(context.snapshot().get('support_id',''))!='P' or carrier('P').position.y>300:return false
  for saw: ModuleSawDefinition in context.module.definition.saws:
   for k: int in range(18,40):
    if absf(saw.at_time(t+float(k)/60).x-320)<58:return false
  return true
 if state=='r060_s12_right':
  var q=carrier('Q')
  if motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='Q'and q.position.y>=245 and q.position.y<=290 and q.definition.at_time(t+.05).y<q.position.y:takeoff_y=motor.position.y;return true
  return false
 if state=='r060_bell_open':
  for l: ShotLatch in cells.latches:
   if str(l.link_id)==str(c.bell_id):return l.is_open
  return false
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 while plan_index<plan.size()and plan[plan_index].has('group_command'):
  var desired: bool=plan[plan_index].group_command;var actual:=false
  for l: ShotLatch in cells.latches:
   if str(l.link_id)=='group-bell':actual=l.is_open
  if desired!=actual:break
  plan_index+=1
 for c: Dictionary in plan:
  if c.get('ring_follow',false):c.carrier_offset=32 if c.revision_follow=='Q'or carrier(str(c.revision_follow)).position.x<230 else 0
 if plan_index<plan.size() and plan[plan_index].get('interception_loop_start',false)and has_interception():
  while plan_index<plan.size()and plan[plan_index].get('interception_loop',false):plan_index+=1
 for c: Dictionary in plan:
  if c.has('adaptive_right_shot'):
   var up: float=clampf((takeoff_y-193.)/154.,0,.7);c.direction=[-sqrt(1-up*up),up]
 return super.control_plan(frame)
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0;super.capture_dynamic_frame()
 if active and not captured.is_empty():captured[-1].workshop.approved_hq=r060.snapshot();captured[-1].workshop.interceptions=interception.events.duplicate(true)
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if not result.get('rejected',false):result.workshop.approved_hq=r060.snapshot();result.workshop.interceptions=interception.events.duplicate(true)
 return result
