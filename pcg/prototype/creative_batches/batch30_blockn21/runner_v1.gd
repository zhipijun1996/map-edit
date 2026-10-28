extends "../plains50_new_relations/sequence_runner_v1.gd"
const OBSERVE=preload("observe_v1.gd")
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0
 super.capture_dynamic_frame()
 if active:captured[-1].n21=OBSERVE.snapshot(self)
