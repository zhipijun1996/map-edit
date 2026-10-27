extends "forest_region_drop_runner_v15.gd"
## Input intent only: original modal opens and independently accepts the choice.
func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	var translated: Array=raw.duplicate(true)
	for command: Dictionary in translated:
		if command.get("op","")=="native_region_select":
			if command.get("kind","")not in ["coin","note"]:return "explicit_original_region_choice_required"
			command.op="native_region_interact"
	return super.validate_plan(translated)
func control_plan(frame: int) -> Array:
	var before:=plan_index
	for command: Dictionary in plan:
		if command.get("op","")=="native_region_select":command.op="wait";command.source_region_select=str(command.kind)
	var requests:=super.control_plan(frame)
	for i: int in range(before,plan_index):
		if plan[i].has("source_region_select"):
			var selected: String=str(plan[i].source_region_select)
			source_region_chests.request_interaction();source_region_chests.request_choice(selected)
			requests.append({"type":"native_region_interact","direction":[0,0],"plan_index":i})
			requests.append({"type":"native_region_choose","kind":selected,"direction":[0,0],"plan_index":i})
	return requests
