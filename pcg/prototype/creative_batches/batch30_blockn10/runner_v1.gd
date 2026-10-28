extends "../../workshop/runner.gd"
const OBS=preload("observe_v1.gd")
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0
 super.capture_dynamic_frame()
 if active:captured[-1].n10=OBS.read(cells)
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if not result.get("rejected",false):result.n10=OBS.read(cells)
 return result
