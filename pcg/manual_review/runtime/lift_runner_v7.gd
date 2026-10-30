extends "lift_runner_v6.gd"
func condition_met(state: String) -> bool:
	if state=="lift_board":
		var p=lift_named("L1")
		if not motor.is_on_floor() or p.position.y<710 or p.definition.at_time(context.module.clock+.15).y>p.position.y:return false
		for dt: float in [.2,.35,.5]:
			if saw_x("G1",dt)<250:return false
		for i: int in range(7,19):
			var dt:=float(i)/10
			if p.definition.at_time(context.module.clock+dt).y>670 and saw_x("G1",dt)<110:return false
		return true
	return super.condition_met(state)
