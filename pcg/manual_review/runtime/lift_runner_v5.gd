extends "lift_runner_v4.gd"
func control_plan(frame: int) -> Array:
	for command: Dictionary in plan:
		if command.get("lift_transfer_shot",false):command.direction=[-.6,.8] if chosen_upper=="R2" else [.4,.916515139]
	return super.control_plan(frame)
