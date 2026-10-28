extends "../batch30_d05/runner_v1.gd"
## Read-only recovery strategy observation; all original scheduling/physics stay.
func validate_plan(raw: Variant) -> String:
	var error:=super.validate_plan(raw)
	if not error.is_empty():return error
	for item: Dictionary in raw:
		var trigger: Dictionary=item.get("trigger",{})
		if not trigger.has("carrier_observation"):continue
		var q: Variant=trigger.carrier_observation
		if not q is Dictionary:return "carrier_observation_not_dictionary"
		if trigger.get("state","")!="grounded":return "carrier_observation_requires_original_grounded_condition"
		if not q.get("running") is bool:return "carrier_observation_running_not_bool"
		if not q.get("x_range") is Array or q.x_range.size()!=2:return "carrier_observation_invalid_range"
		for v: Variant in q.x_range:
			if not(v is float or v is int)or not is_finite(float(v)):return "carrier_observation_nonfinite_range"
		if q.x_range[0]>q.x_range[1]:return "carrier_observation_reversed_range"
		if q.has("vx_max")and(not(q.vx_max is float or q.vx_max is int)or not is_finite(float(q.vx_max))):return "carrier_observation_invalid_velocity"
		var found:=false
		for spec: Dictionary in current_case.get("moving_platforms",[]):
			if str(spec.platform_id)==str(q.get("id","")):found=true
		if not found:return "carrier_observation_unknown_original_body"
	return ""
func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	if not trigger.has("carrier_observation"):return true
	var q: Dictionary=trigger.carrier_observation
	for carrier: ModuleMovingPlatform in context.module.moving_platforms:
		if str(carrier.definition.platform_id)!=str(q.id):continue
		var x:=carrier.global_position.x
		var velocity: Array=context.platform_velocity(carrier)
		return carrier.motion_running==q.running and x>=float(q.x_range[0])and x<=float(q.x_range[1])and float(velocity[0])<=float(q.get("vx_max",1e20))
	return false
