extends "first40_game_air_v4.gd"
var refresh_consumers: Array=[]
const REFRESH=preload("refresh_cells_v1.gd")

func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(REFRESH.ordinary(data))
	current_case=data
	refresh_consumers=REFRESH.install(data,world,controller,context,cells)

func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","")=="shot_ready":command.trigger.state="airborne"
	return super.validate_plan(translated)

func condition_met(state: String) -> bool:
	if state=="shot_ready":return controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
	var dynamic: Dictionary=plan[plan_index].get("trigger",{}).get("dynamic",{})
	if dynamic.get("kind","")=="platform_phase":
		for moving: ModuleMovingPlatform in context.module.moving_platforms:
			if str(moving.definition.platform_id)!=str(dynamic.id) or not moving.bell_controlled:continue
			var phase:=fposmod(moving.motion_clock/moving.definition.period()+moving.definition.initial_phase,1.)
			var window: Array=dynamic.window
			return phase>=float(window[0]) and phase<=float(window[1]) and (state=="__dynamic__" or state=="grounded" and motor.is_on_floor())
	return super.condition_met(state)

func snapshot(index: int, axis: float, actions: Array) -> Dictionary:
	var value:=super.snapshot(index,axis,actions)
	value.refresh_consumers=refresh_consumers.map(func(c):return c.snapshot())
	return value
