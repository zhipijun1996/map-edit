extends "revision061_runner_v9.gd"
func condition_met(state: String) -> bool:
 if state=='r061_transfer_mode':route_mode='nearP'if absf(carrier('P').position.x-carrier('Q').position.x)<65 else'farP';return motor.is_on_floor()and str(context.snapshot().get('support_id',''))=='Q'
 if state=='r061_below_q':return motor.position.y>=carrier('Q').position.y+28
 return super.condition_met(state)
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get('r061_walkoff_q',false):c.target_x=carrier('Q').position.x+(-62 if carrier('P').position.x<=carrier('Q').position.x else 62)
 return super.control_plan(frame)
