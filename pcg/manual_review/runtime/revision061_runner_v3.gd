extends "revision061_runner_v2.gd"
func condition_met(state: String) -> bool:
 var c: Dictionary=plan[plan_index]
 if state=='r061_vertical_saw_window':
  var t: float=context.module.clock
  for saw: ModuleSawDefinition in context.module.definition.saws:
   for j: int in range(6,49,3):
    if absf(saw.at_time(t+float(j)/60).y-float(c.cross_y))<70:return false
  return motor.is_on_floor()
 if state=='r061_ring_air':
  if motor.is_on_floor()or controller.action_resources.shot_charges<=0 or controller.shoot_ability.cooldown_remaining>.000001 or motor.position.x<145:return false
  var d:=corrected_aim(Vector2(144,384));c.direction=[d.x,d.y];return true
 return super.condition_met(state)
