extends "../r2_full/godot/r2_runner.gd"
const VALLEY_PILOT = preload("pilot.gd")
func prepare_dynamic_frame() -> void:
	if warmup_left == 0 and not pilot is VALLEY_PILOT:
		var value = VALLEY_PILOT.new()
		var problem: String = value.configure(self,current_case)
		if not problem.is_empty(): setup_error = problem
		pilot = value
	super.prepare_dynamic_frame()
