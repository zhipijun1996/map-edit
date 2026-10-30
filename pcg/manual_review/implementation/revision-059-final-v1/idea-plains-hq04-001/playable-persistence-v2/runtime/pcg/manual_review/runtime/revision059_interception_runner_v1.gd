extends "revision059_hq_runner_v3.gd"
const INTERCEPTION=preload('revision059_interception_observer_v1.gd')
var observer
func make_fixture(data: Dictionary) -> void:
 await super.make_fixture(data);observer=INTERCEPTION.new();world.add_child(observer);observer.setup(cells.enemies,context)
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0;super.capture_dynamic_frame()
 if active and not captured.is_empty():captured[-1].workshop.interceptions=observer.events.duplicate(true)
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if not result.get('rejected',false):result.workshop.interceptions=observer.events.duplicate(true)
 return result
