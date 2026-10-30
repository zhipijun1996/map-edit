extends "revision060_runner_v3.gd"
var fight_jump_frame: int=-1000
var fight_jump_release:=true
var fight_ready: int=-1
var fight_actions:=0
var group_retry_ready: int=-1
var group_retry_serial:=0
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='carrier_supported'and current_case.get('approved_implementation',{}).get('reviewId','')=='idea-plains-hq01-001':
  var p=carrier(str(c.carrier));return motor.is_on_floor()and str(context.snapshot().get('support_id',''))==str(c.carrier)and absf(motor.position.x-p.position.x-float(settle_options.get('carrier_offset',0)))<4 and controller.shoot_ability.cooldown_remaining<=.000001
 if state=='r060_right_live_aim':
  if motor.is_on_floor()or motor.position.y>190 or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001:return false
  var up: float=clampf((motor.position.y-45.)/154.,0,.94);c.direction=[-sqrt(1-up*up),up];return true
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
 if plan_index<plan.size()and current_case.get('approved_implementation',{}).get('reviewId','')=='idea-plains-hq07-001':
  var battle: Dictionary=plan[plan_index]
  if battle.get('safety_first_arc',false):
   var e=observed_enemy(str(battle.enemy));var gx: float=798 if e!=null and e.health.current>=3 else 792;battle.guard_x=gx;settle_options.target_x=gx
 for command: Dictionary in plan:
  if command.get('adaptive_q_hold',false):command.trigger.after=8 if carrier('Q').position.y<200 else int(command.get('ordinary_hold',24))
 for c: Dictionary in plan:
  if c.get('group_transfer_out',false):c.target_x=carrier('Q').position.x+(-80 if carrier('P').position.x<carrier('Q').position.x else 80)
 var requests:=super.control_plan(frame)
 if not fight_jump_release and frame-fight_jump_frame>=8:
  controller.router.request_action(&'jump_release',Vector2.ZERO);requests.append({'type':'jump_release','direction':[0,0],'plan_index':plan_index});fight_jump_release=true
 if plan_index>=plan.size():return requests
 var c: Dictionary=plan[plan_index];var state: String=str(c.get('trigger',{}).get('state',''))
 if state=='r060_group_running':
  var matches:=false
  for l: ShotLatch in cells.latches:
   if str(l.link_id)=='group-bell':matches=l.is_open==bool(c.running)
  if not matches:
   var support: String=str(context.snapshot().get('support_id',''));c.group_carrier=support if support in ['P','Q']else null
   if condition_met('r060_ring_ready'):
    var key:=40000+group_retry_serial
    if group_retry_ready<0:group_retry_ready=frame+maxi(0,1+timing_error(key))
    if frame>=group_retry_ready:
     var d:=disturbed_direction(Vector2(c.direction[0],c.direction[1]),key);controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key});group_retry_serial+=1;group_retry_ready=-1
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

func corrected_aim(target: Vector2) -> Vector2:
 var direction:=super.corrected_aim(target)
 if plan_index<plan.size()and plan[plan_index].get('safety_first_arc',false):
  var e=observed_enemy(str(plan[plan_index].enemy))
  if e!=null and e.health.current>=3 and absf(e.motor.position.x-motor.position.x)<40:direction=Vector2(-sqrt(1-.35*.35),.35)
 return direction
