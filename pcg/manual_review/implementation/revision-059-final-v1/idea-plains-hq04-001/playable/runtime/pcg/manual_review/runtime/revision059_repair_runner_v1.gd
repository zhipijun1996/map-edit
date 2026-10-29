extends "revision058_runner_v10.gd"
# Input-only repairs. Prediction calls original definitions and native swept contact.
var dodge_offset: float=-30
func make_fixture(data: Dictionary) -> void:
 var ordinary: Dictionary=data.duplicate(true)
 for spec: Dictionary in ordinary.get("latches",[]):spec.erase("additional_pair_access")
 await super.make_fixture(ordinary)
 current_case=data
 for spec: Dictionary in data.get("latches",[]):
  if not spec.has("additional_pair_access"):continue
  for latch in pair_runtime.pairs:
   if str(latch.link_id)==str(spec.id):latch.add_access_bell(Vector2(spec.additional_pair_access[0],spec.additional_pair_access[1]),false,false)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get("trigger",{}).get("state","")).begins_with("repair_"):c.trigger.state="grounded"
 return super.validate_plan(v)
func _cell_aim(q: Dictionary,fallback: Vector2) -> Vector2:
 if q.get("receiver","")=="additional":
  for latch in pair_runtime.pairs:
   if str(latch.link_id)==str(q.id) and latch.access_positions.size()>1:return corrected_aim(latch.to_global(latch.access_positions[1]))
 return super._cell_aim(q,fallback)
func condition_met(state: String) -> bool:
 if state=="repair_board_dodge":
  var p=carrier("P");var t: float=context.module.clock;var y: float=p.definition.at_time(t+.7).y
  if not motor.is_on_floor() or y<460 or p.definition.at_time(t+.8).y>y:return false
  var launch_t: float=-1
  for step: int in range(30,361):
   var u: float=t+float(step)/60
   if p.definition.at_time(u).y<=450 and p.definition.at_time(u+.02).y<p.definition.at_time(u).y:launch_t=u;break
  if launch_t<0:return false
  for offset: float in [-30.,30.]:
   var safe:=true
   for saw: ModuleSawDefinition in context.module.definition.saws:
    for step: int in range(0,19):
     var u: float=launch_t+float(step)/60
     if absf(saw.at_time(u).x-p.definition.at_time(u).x-offset)<60:safe=false;break
   if safe:dodge_offset=offset;return true
  return false
 if state=="repair_takeoff":
  var p=carrier("P")
  return motor.is_on_floor() and str(context.snapshot().get("support_id",""))=="P" and p.position.y<=450 and p.definition.at_time(context.module.clock+.05).y<p.position.y
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get("repair_follow_dodge",false):c.carrier_offset=dodge_offset
 return super.control_plan(frame)
