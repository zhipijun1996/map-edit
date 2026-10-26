extends "../catalog_feed/runner.gd"
## Reuse source_runner's scoped legacy guard adapter. The actual capability
## adapter receives the source declaration, including grapple/wall/double jump.
func capabilities_for(data: Dictionary) -> Variant:
	return data.get("actual_capabilities", data.get("capabilities", []))

func run_case(data: Dictionary) -> Dictionary:
	var routed: Dictionary = data.duplicate(true)
	routed.actual_capabilities = data.capabilities.duplicate()
	routed.capabilities = ["move", "jump", "shot_recoil"]
	var result: Dictionary = await super.run_case(routed)
	result.actual_declared_capabilities = routed.actual_capabilities
	return result
