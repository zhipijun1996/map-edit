extends "revision063_s04_runner_v2.gd"
func condition_met(state: String) -> bool:
 if state=='r062_ring' and current_case.route_spec.from_port=='T':
  var c: Dictionary=plan[plan_index]
  if not motor.is_on_floor() or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  for spec: Dictionary in current_case.get('approved_hq_cells',[]):
   if spec.kind!='group_motion' or spec.id!=c.group_id:continue
   for point: Array in [spec.bell]+spec.access:
    var target:=Vector2(point[0],point[1]);var ray:=PhysicsRayQueryParameters2D.create(motor.global_position,target,1,[motor.get_rid()])
    if motor.get_world_2d().direct_space_state.intersect_ray(ray).is_empty():
     var d:=corrected_aim(target);c.direction=[d.x,d.y];return true
  return false
 return super.condition_met(state)
