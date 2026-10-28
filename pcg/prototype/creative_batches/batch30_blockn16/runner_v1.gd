extends "../../workshop/runner.gd"
const OBSERVE=preload("observe_v1.gd")
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].n16=OBSERVE.snapshot(self)
