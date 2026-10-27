extends "../batch30_cell/runner_v3.gd"
const OBSERVER=preload("attack_observer_v1.gd")
var attack_observer
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	attack_observer=OBSERVER.new();attack_observer.setup(self)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].workshop.cover=attack_observer.snapshot()
func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if not result.get("rejected",false):result.workshop.cover=attack_observer.snapshot()
	return result
