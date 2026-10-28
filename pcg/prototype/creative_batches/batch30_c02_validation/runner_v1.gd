extends "../batch30_cell/runner_v3.gd"
## Read-only recovery strategy conditions. Parent input and world physics stay.
func validate_plan(raw: Variant) -> String:
	var error:=super.validate_plan(raw)
	if not error.is_empty():return error
	for item: Dictionary in raw:
		var trigger: Dictionary=item.get("trigger",{})
		if trigger.has("actual_support"):
			var q: Variant=trigger.actual_support
			if not q is Dictionary:return "support_observation_not_dictionary"
			if trigger.get("state","")!="grounded":return "support_observation_requires_grounded"
			var found:=false
			for i: int in current_case.get("platforms",[]).size():
				if str(q.get("id",""))=="Platform"+str(i):found=true
			if not found:return "support_observation_unknown_static_body"
			for key: String in ["x_range","y_range"]:
				if not q.get(key) is Array or q[key].size()!=2:return "support_observation_invalid_range"
				for value: Variant in q[key]:
					if not(value is float or value is int)or not is_finite(float(value)):return "support_observation_nonfinite_range"
				if q[key][0]>q[key][1]:return "support_observation_reversed_range"
		if trigger.has("actual_pair"):
			var q: Variant=trigger.actual_pair
			if not q is Dictionary or q.get("open","")not in ["A","B"]:return "pair_observation_invalid"
			var found:=false
			for spec: Dictionary in current_case.get("latches",[]):
				if str(spec.id)==str(q.get("id",""))and spec.has("paired_gate"):found=true
			if not found:return "pair_observation_unknown_original_pair"
	return ""
func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	if trigger.has("actual_support"):
		var q: Dictionary=trigger.actual_support
		var p:=motor.global_position
		if context.support_id()!=str(q.id)or p.x<float(q.x_range[0])or p.x>float(q.x_range[1])or p.y<float(q.y_range[0])or p.y>float(q.y_range[1])or motor.get_real_velocity().length()>1:return false
	if trigger.has("actual_pair"):
		var q: Dictionary=trigger.actual_pair
		var found:=false
		for pair: Dictionary in pair_runtime.snapshot():
			if str(pair.id)!=str(q.id):continue
			found=pair.open_a==(q.open=="A")and pair.open_b==(q.open=="B")
		if not found:return false
	return true
