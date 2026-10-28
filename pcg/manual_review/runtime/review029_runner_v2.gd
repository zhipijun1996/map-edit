extends "review029_runner_v1.gd"
## Read-only carrier/height conditions, fed by actual runtime state.
func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","") in ["carrier_x_gte","observed_height"]:command.trigger.state="grounded"
	return super.validate_plan(translated)
func condition_met(state: String) -> bool:
	var command: Dictionary=plan[plan_index]
	if state=="carrier_x_gte":
		for carrier: ModuleMovingPlatform in context.module.moving_platforms:
			if str(carrier.definition.platform_id)==str(command.carrier_id):return carrier.position.x>=float(command.carrier_value)
		return false
	if state=="observed_height":
		var q: Dictionary=command.observed_y
		return motor.position.y>=float(q.value) if q.direction=="gte" else motor.position.y<=float(q.value)
	return super.condition_met(state)
