extends "revision065_lift_runner_v1.gd"
## Aim from the real takeoff arc, preserving the original aim perturbation.
func control_plan(frame: int) -> Array:
 for c: Dictionary in plan:
  if c.get('relay065_height_shot',false):
   var length: float=motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration
   var up: float=clampf((motor.position.y-32)/length,.5,.92)
   c.direction=[-sqrt(1-up*up),up]
 return super.control_plan(frame)
