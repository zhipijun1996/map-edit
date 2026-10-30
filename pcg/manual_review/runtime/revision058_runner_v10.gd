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
var route_mode: String=""
func condition_met(state: String) -> bool:
 var command: Dictionary=plan[plan_index]
 if command.has("route_mode") and str(command.route_mode)!=route_mode:return false
 if state=="revision_transfer_shot":return motor.position.x<=128 and motor.position.y>=190 and motor.velocity.y>=0 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=="revision_always":return true
 if state=="revision_select_top":
  var p=carrier("P");var q=carrier("Q");var t: float=context.module.clock
  if not motor.is_on_floor() or str(context.snapshot().get("support_id",""))!="P" or p.position.y<280 or p.position.y>320 or p.definition.at_time(t+.05).y>p.position.y:return false
  route_mode="via" if q.definition.at_time(t+.5).x<=240 else "direct"
  return true
 if state=="revision_board_saw":
  var p=carrier("P");var t: float=context.module.clock
  var y: float=p.definition.at_time(t+.7).y
  if not motor.is_on_floor() or y<460 or p.definition.at_time(t+.8).y>y:return false
  for saw: ModuleSawHazard in context.module.saws:
   if str(saw.definition.source_id)=="G":return saw.definition.at_time(t+3.3).x>=225 and saw.definition.at_time(t+3.65).x>=170
  return false
 if state=="revision_clear":return not enemy_alive(str(plan[plan_index].enemy))
 return super.condition_met(state)
func corrected_aim(target: Vector2) -> Vector2:
 var d: Vector2=(target-motor.position).normalized();var visual: CourierVisual=motor.get_node("CourierVisual")
 for i: int in 4:d=(target-visual.muzzle_position(d)).normalized()
 return d
func control_plan(frame: int) -> Array:
 while plan_index<plan.size() and plan[plan_index].has("route_mode") and str(plan[plan_index].route_mode)!=route_mode:plan_index+=1
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
 if c.get("high_shore",false) and d.y>.64:return requests
 var key:=20000+issued
 if ready_at<0:ready_at=frame+maxi(0,1+timing_error(key))
 if frame>=ready_at:
  d=disturbed_direction(d,key);controller.router.request_action(&"shoot_release",d);requests.append({"type":"shoot_release","direction":[d.x,d.y],"plan_index":plan_index,"noise_key":key});issued+=1;ready_at=-1
 return requests
