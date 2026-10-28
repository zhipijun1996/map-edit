extends "../../workshop/runner.gd"
const REVERSE=preload("runtime_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(REVERSE.ordinary_case(data))
	REVERSE.install(self,data)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].workshop.reverse_carriers=REVERSE.snapshot(self)
func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if not result.get("rejected",false):result.workshop.reverse_carriers=REVERSE.snapshot(self)
	return result
