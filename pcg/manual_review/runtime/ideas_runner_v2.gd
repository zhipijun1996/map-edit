extends "ideas_runner_v1.gd"
const IDEA_DEFINITION=preload("ideas_definition_v1.gd")
func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	var original:=super.definition_for(data)
	if data.get("route_spec",{}).get("from_port","")!=data.get("route_spec",{}).get("to_port",""):return original
	var result=IDEA_DEFINITION.new()
	for property: Dictionary in original.get_property_list():
		if int(property.usage)&PROPERTY_USAGE_STORAGE and property.name!="script":result.set(property.name,original.get(property.name))
	result.allow_same_port_return=true;return result
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="chain_final":command.trigger.state="shot_ready"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="chain_final":return not motor.is_on_floor() and motor.position.y<=float(plan[plan_index].height_threshold) and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
	return super.condition_met(state)
