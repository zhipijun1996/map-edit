extends "revision063_lift_runner_v2.gd"
## Input-only relay policy: decouple lower ferry arrival from upper ferry timing.
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get('trigger',{}).get('state','')).begins_with('relay065_'):c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='relay065_choose_lower':
  lower_id='L1';upper_id='L2'
  var y: float=carrier('L1').definition.at_time(context.module.clock+1.7).y
  return motor.is_on_floor() and y>=610 and y<=650 and carrier('L1').definition.at_time(context.module.clock+1.8).y<y
 if state=='relay065_edge':return motor.is_on_floor() and absf(motor.position.x-20)<2
 if state=='relay065_deboard':return supported('L1') and carrier('L1').position.y<=550 and carrier('L1').position.y>=530
 if state=='relay065_choose_upper':
  var p=carrier('L2')
  if not motor.is_on_floor() or absf(motor.position.y-526)>.1:return false
  if p.definition.at_time(context.module.clock+.35).y<440 or p.definition.at_time(context.module.clock+.85).y<410:return false
  for step: int in range(16,100):
   var dt:=float(step)/20;var y: float=p.definition.at_time(context.module.clock+dt).y
   if y<310 or y>325 or p.definition.at_time(context.module.clock+dt+.05).y>=y:continue
   for extra: float in [0.0,.1,.2,.3]:
    if gear_x('G3',dt+extra)<180:return false
   return true
  return false
 if state=='relay065_above_upper':return not motor.is_on_floor() and motor.position.y+18<432 and motor.position.y+18<carrier('L2').position.y-12
 if state=='relay065_finish':return supported('L2') and carrier('L2').position.y<=325
 if state=='relay065_final_shot':return not motor.is_on_floor() and motor.position.y+18<208 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
 return super.condition_met(state)
