extends "../../workshop/runner.gd"
const OBSERVE=preload("observe_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	OBSERVE.install(self)
func capture_dynamic_frame() -> void:
	var active: bool=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].n04_seam=OBSERVE.snapshot(self)
