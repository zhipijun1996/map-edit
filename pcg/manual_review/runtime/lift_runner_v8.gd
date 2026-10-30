extends "lift_runner_v7.gd"
func future_transfer_window(p) -> bool:
	for i: int in range(11,27):
		var dt:=float(i)/10
		var y: float=p.definition.at_time(context.module.clock+dt).y
		if y<580 or y>650 or absf(saw_x("G2",dt+.5)-192)<90:continue
		for id: String in ["L2","R2"]:
			var upper=lift_named(id)
			if upper.definition.at_time(context.module.clock+dt+1.1).y>=350:return true
	return false
func condition_met(state: String) -> bool:
	if state=="lift_board":return super.condition_met(state) and future_transfer_window(lift_named("L1"))
	if state=="lift_transfer" and lift_named("L1").position.y<580:return false
	return super.condition_met(state)
