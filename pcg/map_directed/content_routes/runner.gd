extends "../woven_region/runner.gd"
const CONTENT_PILOT=preload("pilot.gd")
func prepare_dynamic_frame() -> void:
	if warmup_left==0 and not pilot is CONTENT_PILOT:
		var value=CONTENT_PILOT.new()
		var problem:String=value.configure(self,current_case)
		if not problem.is_empty():setup_error=problem
		pilot=value
	super.prepare_dynamic_frame()
