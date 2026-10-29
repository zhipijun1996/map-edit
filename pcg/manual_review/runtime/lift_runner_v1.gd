extends "ideas_runner_v2.gd"
func lift_named(id: String):
	for p: ModuleMovingPlatform in context.module.moving_platforms:
		if str(p.definition.platform_id)==id:return p
	return null
func saw_x(id: String,after: float) -> float:
	for p in context.module.definition.saws:
		if str(p.source_id)==id:return p.at_time(context.module.clock+after).x
	return -1000
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if str(command.get("trigger",{}).get("state","")).begins_with("lift_"):command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state.begins_with("lift_"):
		var q: Dictionary=plan[plan_index].lift_window;var p=lift_named(str(q.id))
		if p==null:return false
		var on: bool=motor.is_on_floor() and str(context.snapshot().get("support_id",""))==str(q.id)
		if state=="lift_supported":return on
		if state=="lift_board":return motor.is_on_floor() and p.position.y>=775 and p.definition.at_time(context.module.clock+.15).y<=p.position.y and saw_x("G1",.9)>190
		if state=="lift_transfer":
			var next=lift_named(str(q.next_id))
			return on and p.position.y<=600 and next!=null and next.position.y>=300 and saw_x("G2",.5)>185
		if state=="lift_finish":return on and p.position.y<=310 and saw_x("G3",.3)>185
	return super.condition_met(state)
