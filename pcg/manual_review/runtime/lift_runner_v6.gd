extends "lift_runner_v5.gd"
func condition_met(state: String) -> bool:
	if state=="lift_board":
		var p=lift_named("L1")
		if not motor.is_on_floor() or p.position.y<710 or p.definition.at_time(context.module.clock+.15).y>p.position.y:return false
		for dt: float in [.18,.3,.45]:
			if saw_x("G1",dt)<205:return false
		for i: int in range(5,19):
			var dt:=float(i)/10
			if p.definition.at_time(context.module.clock+dt).y>670 and saw_x("G1",dt)<110:return false
		return true
	if state=="lift_edge":return motor.is_on_floor() and str(context.snapshot().get("support_id",""))=="L1" and absf(motor.position.x-132)<2
	if state=="lift_transfer":
		var p=lift_named("L1")
		if not motor.is_on_floor() or str(context.snapshot().get("support_id",""))!="L1" or p.position.y>650 or absf(saw_x("G2",.5)-192)<85:return false
		var best=null
		for id: String in ["L2","R2"]:
			var upper=lift_named(id)
			var future: float=upper.definition.at_time(context.module.clock+1.1).y
			if future>=350 and (best==null or future>best.definition.at_time(context.module.clock+1.1).y):best=upper
		if best==null:return false
		chosen_upper=str(best.definition.platform_id);return true
	if state=="lift_finish" and str(plan[plan_index].lift_window.id)=="selected_upper":
		var p=lift_named(chosen_upper)
		return motor.is_on_floor() and str(context.snapshot().get("support_id",""))==chosen_upper and p.position.y<=340 and absf(saw_x("G3",.2)-p.position.x)>90
	return super.condition_met(state)
