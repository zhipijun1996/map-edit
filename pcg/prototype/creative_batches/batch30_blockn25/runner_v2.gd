extends "runner_v1.gd"
const MEASURE=preload("measure_v2.gd")
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].n25_calibration=MEASURE.snapshot(self)
