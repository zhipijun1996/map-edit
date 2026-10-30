extends "revision063_s09_runner_v4.gd"
var r063_air_cycles:=0
func make_fixture(data: Dictionary) -> void:
 r063_air_cycles=0
 await super.make_fixture(data)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if c.get('trigger',{}).get('state','')=='r063_s09_dispatch':c.trigger.state='grounded'
 return super.validate_plan(v)
func condition_met(state: String) -> bool:
 if state=='r063_s09_dispatch':return false
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 if plan_index<plan.size() and plan[plan_index].get('trigger',{}).get('state','')=='r063_s09_dispatch' and motor.is_on_floor():
  var c: Dictionary=plan[plan_index];var enemy:=observed_enemy('middle-air-enemy')
  if motor.position.y>550:plan_index=int(c.bottom_index)
  elif enemy==null or enemy.health.terminal:plan_index=int(c.drop_index)
  else:
   var actual:=fired_commands.any(func(v: Dictionary):return int(v.index)==int(c.shot_index) and v.op=='shoot')
   if actual and r063_air_cycles<5:plan_index=int(c.repeat_index);r063_air_cycles+=1
   else:plan_index=int(c.drop_index)
  previous_plan_frame=frame
 for c: Dictionary in plan:
  if c.get('r063_air_repeat_shot',false):c.noise_key=68000+r063_air_cycles
 return super.control_plan(frame)
