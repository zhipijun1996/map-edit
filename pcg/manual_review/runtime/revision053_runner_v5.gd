extends "revision053_runner_v4.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="saw_exit_ready":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="saw_exit_ready":return motor.is_on_floor() and context.phase_condition({"kind":"saw_phase","id":"mouth-saw","window":[.28,.34]})
	return super.condition_met(state)
