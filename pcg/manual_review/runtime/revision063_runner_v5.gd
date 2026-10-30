extends "revision063_runner_v4.gd"
func control_plan(frame: int) -> Array:
 if plan_index<plan.size() and plan[plan_index].get('trigger',{}).get('state','')=='r063_air_clear':
  var enemy:=observed_enemy(str(plan[plan_index].enemy))
  if enemy!=null and not enemy.health.terminal:settle_options.target_x=clampf(enemy.motor.position.x+40,720,808)
 return super.control_plan(frame)
