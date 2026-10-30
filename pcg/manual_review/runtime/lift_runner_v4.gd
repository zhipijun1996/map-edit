extends "lift_runner_v3.gd"
var chosen_upper:="L2"
func condition_met(state: String) -> bool:
	if state in ["lift_supported","lift_finish"] and str(plan[plan_index].lift_window.id)=="selected_upper":
		var p=lift_named(chosen_upper)
		var on: bool=p!=null and motor.is_on_floor() and str(context.snapshot().get("support_id",""))==chosen_upper
		if state=="lift_supported":return on
		return on and p.position.y<=310 and absf(saw_x("G3",.3)-p.position.x)>90
	if state=="lift_transfer":
		var p=lift_named(str(plan[plan_index].lift_window.id))
		if p==null or not motor.is_on_floor() or str(context.snapshot().get("support_id",""))!=str(p.definition.platform_id) or p.position.y>630 or saw_x("G2",.25)<200:return false
		var best=null
		for id: String in ["L2","R2"]:
			var upper=lift_named(id)
			if upper.position.y>=380 and (best==null or upper.position.y>best.position.y):best=upper
		if best==null:return false
		chosen_upper=str(best.definition.platform_id)
		return true
	return super.condition_met(state)
func control_plan(frame: int) -> Array:
	for command: Dictionary in plan:
		if command.get("selected_upper",false):command.target_x=lift_named(chosen_upper).position.x
	return super.control_plan(frame)
