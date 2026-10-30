extends "revision062_runner_v1.gd"
const MOUNT062=preload('revision062_mount_v1.gd')
func make_fixture(data: Dictionary) -> void:
 await super.make_fixture(data);MOUNT062.install(data,context,cells)
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r062_ring':
  if not motor.is_on_floor()or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  for spec: Dictionary in current_case.get('approved_hq_cells',[]):
   if spec.kind!='group_motion'or spec.id!=c.group_id:continue
   for p: Array in [spec.bell]+spec.access:
    var target:=Vector2(p[0],p[1]);var d:=corrected_aim(target);var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(PhysicsRayQueryParameters2D.create(muzzle,target,1,[motor.get_rid()]))
    if hit.is_empty():c.direction=[d.x,d.y];return true
  return false
 if state=='r062_running':
  for l: ShotLatch in cells.latches:
   if str(l.link_id)==str(c.group_id):return l.is_open==bool(c.running)
  return false
 if state=='r062_height':
  var p=carrier(str(c.get('carrier','P')));return motor.is_on_floor()and p.position.y>=float(c.get('ymin',-10000))and p.position.y<=float(c.get('ymax',10000))and(not c.get('supported',false)or str(context.snapshot().get('support_id',''))==str(c.carrier))and(not c.has('up')or(p.definition.at_time(p.motion_clock+.05).y<p.position.y)==bool(c.up))
 if state=='r062_mount_shot':
  if controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  if bool(c.get('air_only',false))and motor.is_on_floor():return false
  for l: ShotLatch in cells.latches:
   if str(l.link_id)!='under-bell':continue
   var target: Vector2=l.bell_body.global_position;var d:=corrected_aim(target);var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d);var hit:=motor.get_world_2d().direct_space_state.intersect_ray(PhysicsRayQueryParameters2D.create(muzzle,target,1,[motor.get_rid()]))
   if hit.is_empty():c.direction=[d.x,d.y];return true
  return false
 if state=='r062_saw_low':
  for saw: ModuleSawDefinition in context.module.definition.saws:
   if saw.at_time(context.module.clock+.4).y>205 or saw.at_time(context.module.clock+.6).y>210:return false
  return motor.is_on_floor()
 return super.condition_met(state)
