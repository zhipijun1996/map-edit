extends "revision063_s04_runner_v3.gd"
var r063_dynamic_serial:=0
var r063_dynamic_ready:=-1
func make_fixture(data: Dictionary) -> void:
 r063_dynamic_serial=0;r063_dynamic_ready=-1
 await super.make_fixture(data)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if c.get('trigger',{}).get('state','')=='r063_dynamic_clear':c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='r063_dynamic_clear':return not enemy_alive(str(plan[plan_index].enemy))
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 if plan_index<plan.size() and plan[plan_index].get('trigger',{}).get('state','')=='r063_dynamic_clear':
  var c: Dictionary=plan[plan_index];var actor:=observed_enemy(str(c.enemy))
  if actor!=null and not actor.health.terminal:
   var gx:=clampf(actor.motor.position.x-16,float(c.guard_min),float(c.guard_max))
   c.guard_x=gx;settle_options.target_x=gx
 var requests:=super.control_plan(frame)
 if plan_index>=plan.size():return requests
 var c: Dictionary=plan[plan_index];var state: String=str(c.get('trigger',{}).get('state',''))
 if state=='r062_height':
  var group: String=str(c.carrier)+'-bell';var issued_index:=-1
  for i: int in plan_index:
   if plan[i].op=='shoot' and str(plan[i].get('group_id',''))==group:issued_index=i
  if issued_index<0 or not plan[issued_index].get('running',false):return requests
  if not fired_commands.any(func(v: Dictionary):return int(v.index)==issued_index and v.op=='shoot'):return requests
  var is_running:=true
  for latch: ShotLatch in cells.latches:
   if str(latch.link_id)==group:is_running=latch.is_open
  if is_running:return requests
  c.group_id=group
  if condition_met('r062_ring'):
   var key:=66000+r063_dynamic_serial
   if r063_dynamic_ready<0:r063_dynamic_ready=frame+maxi(0,1+timing_error(key))
   if frame>=r063_dynamic_ready:
    var d:=disturbed_direction(Vector2(c.direction[0],c.direction[1]),key)
    controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key});r063_dynamic_serial+=1;r063_dynamic_ready=-1
  return requests
 if state!='r063_dynamic_clear':return requests
 var actor:=observed_enemy(str(c.enemy))
 if actor==null or actor.health.terminal or not motor.is_on_floor() or absf(motor.position.x-float(c.guard_x))>3 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return requests
 var lead: float=motor.position.distance_to(actor.motor.position)/motor.tuning.projectile_speed
 var target: Vector2=actor.motor.position+actor.motor.velocity*minf(lead,.18)
 var d:=corrected_aim(target);var key:=67000+r063_dynamic_serial
 if r063_dynamic_ready<0:r063_dynamic_ready=frame+maxi(0,1+timing_error(key))
 if frame>=r063_dynamic_ready:
  d=disturbed_direction(d,key);controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key});r063_dynamic_serial+=1;r063_dynamic_ready=-1
 return requests
