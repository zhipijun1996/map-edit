extends "ideas_runner_v10.gd"
## Read-only aiming geometry for the original burst; only Router inputs change.
func third_endpoint(x: float, target: Vector2) -> float:
	var aim: Vector2=(target-Vector2(x,motor.position.y)).normalized()
	var visual: CourierVisual=motor.get_node("CourierVisual")
	for iteration: int in 4:
		aim=(target-(visual.muzzle_position(aim)+Vector2(x-motor.position.x,0))).normalized()
	return x-aim.x*motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration
func third_target_x() -> float:
	var enemy:=observed_enemy("enemy-3")
	if enemy==null:return 245
	var target: Vector2=enemy.motor.global_position+Vector2(-8,-6)
	var low:=target.x+12;var high:=320.0
	for iteration: int in 12:
		var mid: float=(low+high)*.5
		if third_endpoint(mid,target)<320:low=mid
		else:high=mid
	return (low+high)*.5
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")in ["chain_third","top_finish"]:command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="chain_third":
		var enemy:=observed_enemy("enemy-3")
		return enemy!=null and super.condition_met("chain_shot") and absf(third_endpoint(motor.position.x,enemy.motor.global_position+Vector2(-8,-6))-320)<=20
	if state=="top_finish":
		var aligned: bool=absf(motor.position.x-320)<=3
		var ready: bool=controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
		return aligned and ready and ((motor.is_on_floor() and absf(motor.position.y-46)<2) or super.condition_met("chain_final"))
	return super.condition_met(state)
func control_plan(frame: int) -> Array:
	for command: Dictionary in plan:
		if command.get("third_target",false):command.target_x=third_target_x()
	return super.control_plan(frame)
