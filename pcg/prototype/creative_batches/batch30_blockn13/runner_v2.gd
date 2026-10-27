extends "runner_v1.gd"
const DOCK_OBS=preload("observe_v1.gd")
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0
 super.capture_dynamic_frame()
 if active:captured[-1].n13.docks=DOCK_OBS.docks(self)
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if not result.get("rejected",false):result.n13.docks=DOCK_OBS.docks(self)
 return result
