extends "/workspace/map-edit-task-a/pcg/prototype/creative_batches/batch30_d05/runner_v1.gd"
# Only choose a declared complete control program; inherit actual game physics.
func validate_plan(raw: Variant) -> String:
	var error:=super.validate_plan(raw)
	if not error.is_empty():return error
	for command: Dictionary in raw:
		var trigger: Dictionary=command.get("trigger",{})
		if trigger.has("migration_drop_ready") and (not trigger.migration_drop_ready is bool or trigger.get("state","")!="grounded"):return "invalid_migration_drop_guard"
		if not trigger.has("migration_goal"):continue
		var goal: Variant=trigger.migration_goal
		if not goal is Array or goal.size()!=4:return "invalid_migration_goal_rectangle"
		for value: Variant in goal:
			if not (value is float or value is int) or not is_finite(float(value)):return "invalid_migration_goal_rectangle"
		if float(goal[2])<=0. or float(goal[3])<=0. or trigger.get("state","")!="grounded":return "invalid_migration_goal_guard"
	return ""
func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	if trigger.get("migration_drop_ready",false) and is_instance_valid(motor.get("_drop_body")):return false
	return not trigger.has("migration_goal") or rect(trigger.migration_goal).has_point(motor.position)
func run_case(data: Dictionary) -> Dictionary:
	var routed:=data.duplicate(true)
	var probe: Dictionary=data.get("migration_probe",{})
	var kind: String=probe.get("kind","")
	var selected: Dictionary={}
	if kind in ["continuous_entry","continuous_exit","local_boundary"]:
		var port_id: String=probe.get("portId","")
		var direction: String=("local_"+str(probe.get("direction",""))) if kind=="local_boundary" else ("ingress" if kind=="continuous_entry" else "egress")
		var all_plans: Dictionary=data.get("migration_boundary_plans",{})
		var port_plans: Dictionary=all_plans.get(port_id,{})
		if port_plans.has(direction):
			routed.control_plan=port_plans[direction].duplicate(true)
			selected={"portId":port_id,"direction":direction,"completeControlPlan":true}
	var result: Dictionary=await super.run_case(routed)
	if not selected.is_empty():result.migration_boundary_control=selected
	return result
