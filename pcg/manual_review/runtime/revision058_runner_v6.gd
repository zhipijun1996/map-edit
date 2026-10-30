extends "revision058_runner_v3.gd"
func make_fixture(data: Dictionary) -> void:
 var ordinary: Dictionary=data.duplicate(true)
 for spec: Dictionary in ordinary.get("latches",[]):
  if spec.get("return_access_side_policy","")=="any":spec.erase("return_access")
 await super.make_fixture(ordinary)
 current_case=data
 for spec: Dictionary in data.get("latches",[]):
  if spec.get("return_access_side_policy","")!="any":continue
  for latch: ShotLatch in cells.latches:
   if str(latch.link_id)==str(spec.id):latch.add_access_bell(Vector2(spec.return_access[0],spec.return_access[1]),false,false)
func condition_met(state: String) -> bool:
 if state=="revision_board_saw":
  var p=carrier("P");var t: float=context.module.clock
  var y: float=p.definition.at_time(t+.7).y
  if not motor.is_on_floor() or y<460 or p.definition.at_time(t+.8).y>y:return false
  for saw: ModuleSawDefinition in context.module.definition.saws:
   if str(saw.source_id)=="G":return saw.at_time(t+3.3).x>=225 and saw.at_time(t+3.65).x>=170
  return false
 if state=="revision_clear":return not enemy_alive(str(plan[plan_index].enemy))
 return super.condition_met(state)
func corrected_aim(target: Vector2) -> Vector2:
 var d: Vector2=(target-motor.position).normalized();var visual: CourierVisual=motor.get_node("CourierVisual")
 for i: int in 4:d=(target-visual.muzzle_position(d)).normalized()
 return d
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.has("native_aim_point"):
   var d:=corrected_aim(Vector2(c.native_aim_point[0],c.native_aim_point[1]));c.direction=[d.x,d.y]
 var requests:=super.control_plan(frame)
 if plan_index>=plan.size() or plan[plan_index].get("trigger",{}).get("state","")!="revision_clear":return requests
 var c: Dictionary=plan[plan_index];var actor:=observed_enemy(str(c.enemy))
 if actor==null or actor.health.terminal:return requests
 if not motor.is_on_floor() or controller.shoot_ability.cooldown_remaining>0.000001 or absf(motor.position.x-float(c.guard_x))>3:return requests
 var lead: float=motor.position.distance_to(actor.motor.position)/controller.shoot_ability.tuning.projectile_speed
 var d:=corrected_aim(actor.motor.position+actor.motor.velocity*minf(lead,.18))
 if c.get("high_shore",false) and d.y>.55:return requests
 var key:=20000+issued
 if ready_at<0:ready_at=frame+maxi(0,1+timing_error(key))
 if frame>=ready_at:
  d=disturbed_direction(d,key);controller.router.request_action(&"shoot_release",d);requests.append({"type":"shoot_release","direction":[d.x,d.y],"plan_index":plan_index,"noise_key":key});issued+=1;ready_at=-1
 return requests
