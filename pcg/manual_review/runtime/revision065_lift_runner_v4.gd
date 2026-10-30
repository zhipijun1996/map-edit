extends "revision065_lift_runner_v3.gd"
func condition_met(state: String) -> bool:
 if state=='relay065_choose_lower':
  if not super.condition_met(state):return false
  for dt: float in [.85,.95,1.05,1.15,1.25,1.35,1.45,1.55]:
   if gear_x('G1',dt)<130:return false
  return true
 if state=='relay065_edge':return motor.is_on_floor() and absf(motor.position.x-32)<2
 return super.condition_met(state)
