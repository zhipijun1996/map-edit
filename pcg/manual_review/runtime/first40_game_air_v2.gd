extends "first40_game_air_v1.gd"

func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","")=="grounded_shot_ready":command.trigger.state="grounded"
	return super.validate_plan(translated)

func condition_met(state: String) -> bool:
	if state=="grounded_shot_ready":return motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
	return super.condition_met(state)
