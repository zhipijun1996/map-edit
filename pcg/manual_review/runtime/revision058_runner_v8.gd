extends "revision058_runner_v7.gd"
var selected_offset: float=-30
func condition_met(state: String) -> bool:
 if state!="revision_board_saw":return super.condition_met(state)
 var p=carrier("P");var t: float=context.module.clock;var y: float=p.definition.at_time(t+.7).y
 if not motor.is_on_floor() or y<460 or p.definition.at_time(t+.8).y>y:return false
 for offset: float in [-30.,30.]:
  var safe:=true
  for saw: ModuleSawDefinition in context.module.definition.saws:
   if str(saw.source_id)!="G":continue
   var prev_p: Vector2=p.definition.at_time(t)+Vector2(offset,-26);var prev_g: Vector2=saw.at_time(t)
   for step: int in range(1,361):
    var future_t: float=t+float(step)/60
    var pp: Vector2=p.definition.at_time(future_t)+Vector2(offset,-26);var gg: Vector2=saw.at_time(future_t)
    if pp.y<400 and pp.y>275 and pp.y<prev_p.y and SawHazard.swept_contact(prev_p-prev_g,pp-gg,Vector2(12,18),saw.radius+8):safe=false;break
    prev_p=pp;prev_g=gg
  if safe:selected_offset=offset;return true
 return false
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get("revision_follow","")=="P":c.carrier_offset=selected_offset
 return super.control_plan(frame)
