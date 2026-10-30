extends "revision062_runner_v6.gd"
func condition_met(state: String) -> bool:
 if state=='r062_mount_corner_shot':
  if motor.is_on_floor()or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  for l: ShotLatch in cells.latches:
   if str(l.link_id)!='under-bell':continue
   var target: Vector2=l.bell_body.global_position+Vector2(-14,15);var d:=corrected_aim(target);var visual: CourierVisual=motor.get_node('CourierVisual');var muzzle: Vector2=visual.muzzle_position(d)
   var hit:=motor.get_world_2d().direct_space_state.intersect_ray(PhysicsRayQueryParameters2D.create(motor.global_position,target,1,[motor.get_rid()]))
   if hit.is_empty():plan[plan_index].direction=[d.x,d.y];return true
  return false
 return super.condition_met(state)
