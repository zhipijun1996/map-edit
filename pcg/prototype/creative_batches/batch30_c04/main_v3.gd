extends "../batch30_cell/main_v3.gd"
const OBSERVER=preload("attack_observer_v1.gd")
const NAMES=preload("stable_support_names_v1.gd")
var attack_observer
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	NAMES.install(self)
	attack_observer=OBSERVER.new();attack_observer.setup(self)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	var actual: Dictionary=attack_observer.snapshot() if active else {}
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():replay_trace[-1].workshop.cover=actual
