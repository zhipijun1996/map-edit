extends "revision060_runner_v3.gd"
var fight_jump_frame: int=-1000
var fight_jump_release:=true
var fight_ready: int=-1
var fight_actions:=0
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r060_hq02_board':
  var p=carrier('P');var t: float=context.module.clock;return motor.is_on_floor()and p.position.y>=385 and p.definition.at_time(t+.05).y<p.position.y
 if state=='r060_group_transfer':route_mode='close' if absf(carrier('P').position.x-carrier('Q').position.x)<95 else 'far';return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='Q'
 if state=='r060_below_q':return motor.position.y>=carrier('Q').position.y+32
 if state=='r060_fight':return not enemy_alive(str(c.enemy))
 if state=='r060_perch':return motor.is_on_floor()and absf(motor.position.y-238)<1 and absf(motor.position.x-272)<4
 if state=='r060_air_shot':return not motor.is_on_floor()and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r060_08_exit':
  if not motor.is_on_floor()or str(context.snapshot().get('support_id',''))!='P'or carrier('P').position.y>330:return false
  var t: float=context.module.clock
  for saw: ModuleSawDefinition in context.module.definition.saws:
   for k: int in range(10,43):
    if absf(saw.at_time(t+float(k)/60).x-320)<58:return false
  return true
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get('group_transfer_out',false):c.target_x=carrier('Q').position.x+(-80 if carrier('P').position.x<carrier('Q').position.x else 80)
 var requests:=super.control_plan(frame)
 if not fight_jump_release and frame-fight_jump_frame>=8:
  controller.router.request_action(&'jump_release',Vector2.ZERO);requests.append({'type':'jump_release','direction':[0,0],'plan_index':plan_index});fight_jump_release=true
 if plan_index>=plan.size():return requests
 var c: Dictionary=plan[plan_index];var state: String=str(c.get('trigger',{}).get('state',''))
 var needs_jump:=state in ['r060_fight','r060_perch']or state=='r060_air_shot'and str(context.snapshot().get('support_id',''))in ['P','Q']
 if needs_jump and motor.is_on_floor()and frame-fight_jump_frame>20:
  controller.router.request_action(&'jump',Vector2.ZERO);requests.append({'type':'jump','direction':[0,0],'plan_index':plan_index});fight_jump_frame=frame;fight_jump_release=false
 if state=='r060_fight':
  var actor=observed_enemy(str(c.enemy))
  if actor!=null and not actor.health.terminal:
   settle_options.target_x=clampf(actor.motor.position.x,210,334)
   if not motor.is_on_floor()and motor.position.y>=180 and motor.velocity.y>=0 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001:
    var key:=30000+fight_actions
    if fight_ready<0:fight_ready=frame+maxi(0,1+timing_error(key))
    if frame>=fight_ready:
     var d:=disturbed_direction(corrected_aim(actor.motor.position),key);controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key});fight_actions+=1;fight_ready=-1
 return requests
