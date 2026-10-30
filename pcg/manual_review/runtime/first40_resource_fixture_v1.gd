extends "../../migration/resource_fixture_runner_v10.gd"
## Driver observations only; original exact 1-jump/2-air-shot initialization stays.
func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","")=="shot_ready":command.trigger.state="grounded"
	return super.validate_plan(translated)

func condition_met(state: String) -> bool:
	if state=="shot_ready":return controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
	return super.condition_met(state)
