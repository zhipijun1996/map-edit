extends "revision058_runner_v2.gd"
# Input-only driver: forecast from the original platform definition, not a new simulation.
func validate_plan(raw: Variant) -> String:
 var copy: Variant=raw.duplicate(true) if raw is Array else raw
 if copy is Array:
  for c: Dictionary in copy:
   if str(c.get("trigger",{}).get("state","")).begins_with("revision_"):c.trigger.state="grounded"
 return super.validate_plan(copy)
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=="revision_window":
  for q: Dictionary in c.windows:
   var p=carrier(str(q.id));var v: Vector2=p.definition.at_time(context.module.clock+float(q.get("ahead",0)))
   if v.x<float(q.get("xmin",-10000)) or v.x>float(q.get("xmax",10000)) or v.y<float(q.get("ymin",-10000)) or v.y>float(q.get("ymax",10000)):return false
   if q.has("up") and (p.definition.at_time(context.module.clock+float(q.get("ahead",0))+.05).y<=v.y)!=bool(q.up):return false
  return not c.get("grounded",true) or motor.is_on_floor()
 if state=="revision_actor":return motor.position.y<=float(c.get("ymax",10000)) and motor.position.y>=float(c.get("ymin",-10000)) and motor.position.x>=float(c.get("xmin",-10000)) and motor.position.x<=float(c.get("xmax",10000)) and (not c.get("descending",false) or motor.velocity.y>=0)
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.has("revision_follow"):
   var p=carrier(str(c.revision_follow))
   if p!=null:c.target_x=p.position.x+float(c.get("carrier_offset",0))
 return super.control_plan(frame)
