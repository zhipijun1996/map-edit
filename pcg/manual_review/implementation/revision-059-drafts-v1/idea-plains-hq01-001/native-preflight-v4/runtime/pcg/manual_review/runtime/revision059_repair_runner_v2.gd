extends "revision059_repair_runner_v1.gd"
func condition_met(state: String) -> bool:
 if state=='repair_board_dodge':
  var p=carrier('P');var t: float=context.module.clock;var y: float=p.definition.at_time(t+.7).y
  if not motor.is_on_floor() or y<460 or p.definition.at_time(t+.8).y>y:return false
  for offset: float in [-28.,28.]:
   var safe:=true
   for step: int in range(30,361):
    var u: float=t+float(step)/60;var at: Vector2=p.definition.at_time(u)
    if at.y>405 or at.y<320:continue
    for saw: ModuleSawDefinition in context.module.definition.saws:
     if absf(saw.at_time(u).x-at.x-offset)<51:safe=false;break
   if safe:dodge_offset=offset;return true
  return false
 if state=='repair_takeoff':
  var p=carrier('P')
  return motor.is_on_floor() and str(context.snapshot().get('support_id',''))=='P' and p.position.y<=330 and p.definition.at_time(context.module.clock+.05).y<p.position.y
 return super.condition_met(state)
