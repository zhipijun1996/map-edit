extends "review045_runner_v3.gd"
const LOOP=preload("../../prototype/creative_batches/batch30_blockn25/install_v1.gd")
func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	var d:=super.definition_for(data);LOOP.install(d,data);return d
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")in ["chain_shot","on_carrier","carrier_ready"]:command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state in ["on_carrier","carrier_ready"]:
		var q: Dictionary=plan[plan_index].carrier_window
		for p: ModuleMovingPlatform in context.module.moving_platforms:
			if str(p.definition.platform_id)!=str(q.id):continue
			if not motor.is_on_floor() or str(context.snapshot().get("support_id",""))!=str(q.id):return false
			if state=="on_carrier":return true
			var phase:=fposmod(p.motion_clock/p.definition.period()+p.definition.initial_phase,1)
			return p.motion_running and phase>=float(q.low) and phase<=float(q.high) and controller.shoot_ability.cooldown_remaining<=0.000001
		return false
	if state=="chain_shot":
		var q: Dictionary=plan[plan_index].chain_window;var enemy:=observed_enemy(str(q.id))
		return enemy!=null and not enemy.health.terminal and not motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001 and motor.position.y<=float(q.maximum_actor_y) and enemy.motor.position.y-motor.position.y>=float(q.minimum_drop) and (enemy.motor.position.x-motor.position.x)*float(q.side)>=10
	return super.condition_met(state)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not captured.is_empty():
		var loops: Array=[]
		for p: ModuleMovingPlatform in context.module.moving_platforms:
			if p.definition.get_script()==LOOP.DEFINITION:
				var expected: Vector2=p.definition.at_time(p.motion_clock if p.bell_controlled else context.module.clock)
				loops.append({"id":str(p.definition.platform_id),"position":[p.position.x,p.position.y],"clock":p.motion_clock,"running":p.motion_running,"controlled":p.bell_controlled,"expected_error":p.position.distance_to(expected),"rotation":p.rotation})
		captured[-1].idea_loops=loops

func control_plan(frame: int) -> Array:
	for command: Dictionary in plan:
		if command.op=="settle" and command.has("follow_carrier"):
			for p: ModuleMovingPlatform in context.module.moving_platforms:
				if str(p.definition.platform_id)==str(command.follow_carrier):command.target_x=p.position.x
	return super.control_plan(frame)
