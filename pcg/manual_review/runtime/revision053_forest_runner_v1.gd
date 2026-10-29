extends "review045_forest_runner_v2.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")in ["hook_done","hook_window"]:command.trigger.state="free"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="hook_done":return controller.traversal.state==&"free" and source_hook_contacts.size()>=int(plan[plan_index].hook_count)
	if state=="hook_window":
		if controller.traversal.state!=&"free":return false
		var target:=point(plan[plan_index].hook_target);var start:=motor.global_position+Vector2(0,-6)
		if start.distance_to(target)>controller.traversal.definition.hook_range-12:return false
		var query:=PhysicsRayQueryParameters2D.create(start,target,1,[motor.get_rid()])
		return motor.get_world_2d().direct_space_state.intersect_ray(query).is_empty()
	return super.condition_met(state)
