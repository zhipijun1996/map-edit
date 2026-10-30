extends "revision058_runner_v11.gd"
const HQ=preload('revision059_hq_binding_v1.gd')
var hq
func make_fixture(data: Dictionary) -> void:
 await super.make_fixture(HQ.ordinary(data));current_case=data;hq=HQ.new();world.add_child(hq);hq.setup(data,world,controller,context,cells,extra)
func validate_plan(raw: Variant) -> String:
 var v: Variant=raw.duplicate(true) if raw is Array else raw
 if v is Array:
  for c: Dictionary in v:
   if str(c.get('trigger',{}).get('state','')).begins_with('hq_'):c.trigger.state='grounded'
 return super.validate_plan(v)
func corrected_aim(target: Vector2) -> Vector2:
 var d: Vector2=(target-motor.position).normalized();var visual: CourierVisual=motor.get_node('CourierVisual')
 for i: int in 4:d=(target-visual.muzzle_position(d)).normalized()
 return d
func condition_met(state: String) -> bool:
 var t: float=context.module.clock
 if state=='hq_board':
  var p=carrier('P');var y: float=p.definition.at_time(t+.6).y
  return motor.is_on_floor() and y>=385 and p.definition.at_time(t+.7).y<=y
 if state=='hq_upper':return motor.is_on_floor() and str(context.snapshot().get('support_id',''))=='P' and carrier('P').position.y<=165
 if state=='hq_group_park_window':return motor.is_on_floor() and carrier('P').position.x>=240 and carrier('P').position.x<=300 and carrier('Q').position.y<=204
 if state=='hq_saw_low' or state=='hq_saw_high':
  var safe:=true
  for s: ModuleSawHazard in context.module.saws:
   for k: int in range(18,43):
    var y: float=s.definition.at_time(t+float(k)/60).y
    if state=='hq_saw_low' and y<240 or state=='hq_saw_high' and y>270:safe=false
  return motor.is_on_floor() and safe
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.has('native_aim_point'):
   var d:=corrected_aim(Vector2(c.native_aim_point[0],c.native_aim_point[1]));c.direction=[d.x,d.y]
  if c.has('revision_follow'):
   var p=carrier(str(c.revision_follow));c.target_x=p.position.x+float(c.get('carrier_offset',0))
 return super.control_plan(frame)
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0;super.capture_dynamic_frame()
 if active and not captured.is_empty():captured[-1].workshop.approved_hq=hq.snapshot()
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if not result.get('rejected',false):result.workshop.approved_hq=hq.snapshot()
 return result