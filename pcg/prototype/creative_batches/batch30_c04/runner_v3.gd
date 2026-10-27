extends "../batch30_cell/runner_v3.gd"
const OBSERVER=preload("attack_observer_v1.gd")
const NAMES=preload("stable_support_names_v1.gd")
var attack_observer
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	NAMES.install(self)
	attack_observer=OBSERVER.new();attack_observer.setup(self)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	var actual: Dictionary=attack_observer.snapshot() if active else {}
	super.capture_dynamic_frame()
	if active:captured[-1].workshop.cover=actual
func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if not result.get("rejected",false) and not result.frames.is_empty():
		result.workshop.cover=result.frames[-1].workshop.cover.duplicate(true)
		result.workshop.cover_sampling="last_active_physics_frame"
	return result
