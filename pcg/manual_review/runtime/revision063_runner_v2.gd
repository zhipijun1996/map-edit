extends "revision063_runner_v1.gd"
var fight_serial:=0
var fight_ready:=-1
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if c.get('trigger',{}).get('state','')=='r063_air_clear':c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='r063_air_clear':return not enemy_alive(str(plan[plan_index].enemy))
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 var requests:=super.control_plan(frame)
 if plan_index>=plan.size() or plan[plan_index].get('trigger',{}).get('state','')!='r063_air_clear':return requests
 var c: Dictionary=plan[plan_index];var enemy:=observed_enemy(str(c.enemy))
 if enemy==null or enemy.health.terminal:return requests
 var jumping:=motor.is_on_floor()
 var target: Vector2=enemy.motor.position
 var can_shoot:=not jumping and motor.position.y>=245 and motor.position.y<=280 and absf(target.x-motor.position.x)<40 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if not jumping and not can_shoot:return requests
 var key:=63000+fight_serial
 if fight_ready<0:fight_ready=frame+maxi(0,1+timing_error(key))
 if frame<fight_ready:return requests
 if jumping:
  controller.router.request_action(&'jump');requests.append({'type':'jump','plan_index':plan_index,'noise_key':key})
  controller.router.request_action(&'jump_release');requests.append({'type':'jump_release','plan_index':plan_index,'noise_key':key})
 else:
  var d:=disturbed_direction(corrected_aim(target),key)
  controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key})
 fight_serial+=1;fight_ready=-1
 return requests
