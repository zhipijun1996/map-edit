extends "review031_runner_v2.gd"
## Reward release and physical carrying are installed as actual native Cells.
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="reward_released":command.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="reward_released":return false
	return super.condition_met(state)
