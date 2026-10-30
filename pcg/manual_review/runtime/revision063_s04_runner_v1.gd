extends "revision062_runner_v8.gd"
var r063_clear_serial:=0
var r063_clear_ready:=-1
func make_fixture(data: Dictionary) -> void:
 r063_clear_serial=0;r063_clear_ready=-1
 await super.make_fixture(data)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if c.get('trigger',{}).get('state','')=='r063_safe_clear':c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='r063_safe_clear':return not enemy_alive(str(plan[plan_index].enemy))
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 var requests:=super.control_plan(frame)
 if plan_index>=plan.size() or plan[plan_index].get('trigger',{}).get('state','')!='r063_safe_clear':return requests
 var c: Dictionary=plan[plan_index];var enemy:=observed_enemy(str(c.enemy))
 if enemy==null or enemy.health.terminal or not motor.is_on_floor() or absf(motor.position.x-float(c.guard_x))>3 or enemy.motor.position.x>=196 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return requests
 var lead: float=motor.position.distance_to(enemy.motor.position)/motor.tuning.projectile_speed
 var target: Vector2=enemy.motor.position+enemy.motor.velocity*minf(lead,.18)
 var d:=corrected_aim(target)
 if d.x>=0:return requests
 var key:=64000+r063_clear_serial
 if r063_clear_ready<0:r063_clear_ready=frame+maxi(0,1+timing_error(key))
 if frame>=r063_clear_ready:
  d=disturbed_direction(d,key);controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key});r063_clear_serial+=1;r063_clear_ready=-1
 return requests
