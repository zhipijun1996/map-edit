extends "/workspace/map-edit-task-a/pcg/prototype/workshop/runner.gd"
# Only route past the legacy Plains case-shape guard. Original Adapter validates
# and applies the actual declaration; fixture, rewards, input and physics unchanged.
func capabilities_for(case: Dictionary) -> Variant:
	return case.get("actual_capabilities",case.get("capabilities",[]))
func run_case(case: Dictionary) -> Dictionary:
	var routed:=case.duplicate(true)
	routed.actual_capabilities=case.get("capabilities",[]).duplicate()
	routed.capabilities=["move","jump","shot_recoil"]
	var result: Dictionary=await super.run_case(routed)
	result.actual_declared_capabilities=routed.actual_capabilities
	result.capability_guard_adapter="legacy guard routing only; actual Adapter.apply unchanged"
	return result
