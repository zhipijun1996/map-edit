extends "revision062_runner_v8.gd"
var r063_mount_attempts:=0
var r063_mount_restart:=-1
func make_fixture(data: Dictionary) -> void:
 r063_mount_attempts=0;r063_mount_restart=-1
 await super.make_fixture(data)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get('trigger',{}).get('state','')).begins_with('r063_mount_'):c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='r063_mount_started':
  for latch: ShotLatch in cells.latches:
   if str(latch.link_id)=='under-bell':return latch.is_open
  return false
 if state=='r063_mount_shot':
  if motor.position.y<carrier('P').position.y+3:return false
  if motor.is_on_floor() or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  for l: ShotLatch in cells.latches:
   if str(l.link_id)!='under-bell':continue
   var target: Vector2=l.bell_body.global_position+Vector2(-14,15)
   var ray:=PhysicsRayQueryParameters2D.create(motor.global_position,target,1,[motor.get_rid()])
   if motor.get_world_2d().direct_space_state.intersect_ray(ray).is_empty():
    var d:=corrected_aim(target);plan[plan_index].direction=[d.x,d.y];return true
  return false
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 if plan_index<plan.size() and plan[plan_index].get('trigger',{}).get('state','')=='r063_mount_started' and not condition_met('r063_mount_started') and motor.is_on_floor():
  var shot_index: int=int(plan[plan_index].r063_shot_index)
  var actual:=fired_commands.any(func(c: Dictionary):return int(c.index)==shot_index and c.op=='shoot')
  if actual and r063_mount_attempts<4 and frame-previous_plan_frame>=30:
   plan_index=int(plan[plan_index].r063_restart_index);previous_plan_frame=frame;r063_mount_attempts+=1
 return super.control_plan(frame)
