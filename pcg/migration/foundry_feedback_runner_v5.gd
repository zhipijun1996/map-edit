extends "game_world_runner_v4.gd"
## Input-policy adapter only. The gain5.5 feedback is the original authored
## BranchModuleDriver.move_to; all motion/collision/resources stay native.
var feedback_axis_mode:="settle"
var feedback_axis_value:=0.0

func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	if raw.size()>384:return "original_feedback_plan_budget"
	for offset: int in range(0,raw.size(),128):
		var error:=super.validate_plan(raw.slice(offset,mini(offset+128,raw.size())))
		if not error.is_empty():return error
	for command: Dictionary in raw:
		var trigger: Dictionary=command.get("trigger",{})
		if trigger.has("migration_goal"):
			var goal: Variant=trigger.migration_goal
			if not goal is Array or goal.size()!=4:return "invalid_original_goal"
			for value: Variant in goal:
				if not(value is float or value is int)or not is_finite(float(value)):return "invalid_original_goal"
			if goal[2]<=0 or goal[3]<=0 or trigger.get("state","")!="grounded":return "invalid_original_goal_guard"
	return ""

func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	return not trigger.has("migration_goal")or rect(trigger.migration_goal).has_point(motor.position)

func make_fixture(case: Dictionary) -> void:
	feedback_axis_mode="settle";feedback_axis_value=0
	await super.make_fixture(case)

func control_plan(frame: int) -> Array:
	var before:=plan_index
	var requests:=super.control_plan(frame)
	for i: int in range(before,plan_index):
		if plan[i].op=="axis":feedback_axis_mode="axis";feedback_axis_value=float(plan[i].get("value",0))
		elif plan[i].op=="settle":feedback_axis_mode="settle"
	if feedback_axis_mode=="axis":
		settling=false;set_axis(feedback_axis_value)
	elif settling and settle_options.has("source_native_gain"):
		var target:=float(settle_options.get("target_x",settle_goal.get_center().x))
		if settle_options.has("source_carrier_id"):
			for moving: ModuleMovingPlatform in context.module.moving_platforms:
				if str(moving.definition.platform_id)==str(settle_options.source_carrier_id):target=moving.global_position.x
		var error:=target-motor.position.x
		set_axis(clampf(error/float(settle_options.source_native_gain),-1,1)if absf(error)>float(settle_options.get("deadband",.6))else 0.)
	return requests
