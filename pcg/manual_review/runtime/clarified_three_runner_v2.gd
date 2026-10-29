extends "review029_runner_v4.gd"
const CLARIFIED_WAVE=preload("review029_ambush_v2.gd")
var clarified_wave
var clarified_input_frame:=-1
func make_fixture(data: Dictionary) -> void:
	var ordinary:=data.duplicate(true)
	if data.has("review029_wave"):
		ordinary.enemies=[];ordinary.erase("review029_wave")
	await super.make_fixture(ordinary)
	current_case=data
	if data.has("review029_wave"):
		clarified_wave=CLARIFIED_WAVE.new();world.add_child(clarified_wave);clarified_wave.setup(data,world,controller,context,cells,self)
func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","")=="boarding_window":command.trigger.state="grounded"
	return super.validate_plan(translated)
func condition_met(state: String) -> bool:
	if state=="shot_ready" or state=="grounded_shot_ready":
		for event: Dictionary in fired_commands:
			if int(event.frame)==clarified_input_frame and plan[int(event.index)].op=="shoot":return false
	if state=="boarding_window":
		if not motor.is_on_floor():return false
		for ferry: ModuleMovingPlatform in context.module.moving_platforms:
			if str(ferry.definition.platform_id)!=str(plan[plan_index].carrier_id):continue
			var front: float=ferry.global_position.x+ferry.definition.size.x/2
			return front>=motor.global_position.x-float(plan[plan_index].lead_distance) and front<=motor.global_position.x+12
		return false
	return super.condition_met(state)
func control_plan(frame: int) -> Array:
	clarified_input_frame=frame
	while plan_index<plan.size() and plan[plan_index].has("skip_if_carrier_running"):
		var running:=false
		for ferry: ModuleMovingPlatform in context.module.moving_platforms:
			if str(ferry.definition.platform_id)==str(plan[plan_index].skip_if_carrier_running):running=ferry.motion_running
		if not running:break
		plan_index+=1
	return super.control_plan(frame)
func snapshot(index: int, axis: float, actions: Array) -> Dictionary:
	var value:=super.snapshot(index,axis,actions)
	if is_instance_valid(clarified_wave):value.review029_wave=clarified_wave.snapshot()
	return value
