extends "revision063_s04_runner_v1.gd"
func make_fixture(data: Dictionary) -> void:
 r062_retry_serial=0;r062_retry_ready=-1
 await super.make_fixture(data)
func condition_met(state: String) -> bool:
 if state=='r062_ring':
  if not motor.is_on_floor() or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var c: Dictionary=plan[plan_index]
  for spec: Dictionary in current_case.get('approved_hq_cells',[]):
   if spec.kind!='group_motion' or str(spec.id)!=str(c.group_id):continue
   var points: Array=[spec.bell]+spec.access
   points.sort_custom(func(a: Array,b: Array):return motor.position.distance_squared_to(Vector2(a[0],a[1]))<motor.position.distance_squared_to(Vector2(b[0],b[1])))
   for point: Array in points:
    var target:=Vector2(point[0],point[1]);var d:=corrected_aim(target);var muzzle: Vector2=motor.get_node('CourierVisual').muzzle_position(d)
    var end:=target-d*24
    var ray:=PhysicsRayQueryParameters2D.create(muzzle,end,1,[motor.get_rid()])
    if motor.get_world_2d().direct_space_state.intersect_ray(ray).is_empty():c.direction=[d.x,d.y];return true
  return false
 return super.condition_met(state)
