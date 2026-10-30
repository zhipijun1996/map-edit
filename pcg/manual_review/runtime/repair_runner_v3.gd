extends "/workspace/map-edit-task-a/pcg/prototype/creative_batches/batch30_c09/runner_v1.gd"
const REVIEW_AIR=preload("air_enemy_binding_v1.gd")

func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Variant in copy:
			if command is Dictionary and command.get("trigger",{}).get("state","") in ["shot_ready","grounded_shot_ready"]:command.trigger.state="grounded"
	return super.validate_plan(copy)

func condition_met(state: String) -> bool:
	if state=="shot_ready":return controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
	if state=="grounded_shot_ready":
		var ready:=motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
		var query: Dictionary=plan[plan_index].get("trigger",{}).get("dynamic",{})
		return ready and (query.is_empty() or context.phase_condition(query))
	return super.condition_met(state)

func enemy_alive(identifier: String) -> bool:
	for i: int in cells.enemies.size():
		var actor: EnemyActor=cells.enemies[i]
		if str(current_case.get("enemies",[])[i].id)==identifier:return is_instance_valid(actor) and not actor.health.terminal
	return false

func control_plan(frame: int) -> Array:
	# Conditional control belongs to the driver; only real world observations
	# may skip an unnecessary shot. No enemy or resource state is modified.
	while plan_index<plan.size() and plan[plan_index].has("skip_if_enemy_dead") and not enemy_alive(str(plan[plan_index].skip_if_enemy_dead)):
		plan_index+=1
	return super.control_plan(frame)

func _cell_aim(query: Dictionary, fallback: Vector2) -> Vector2:
	if query.get("kind","")!="enemy" or not query.has("target_offset"):return super._cell_aim(query,fallback)
	for i: int in cells.enemies.size():
		var actor: EnemyActor=cells.enemies[i]
		if str(current_case.get("enemies",[])[i].id)!=str(query.id) or not is_instance_valid(actor) or actor.health.terminal:continue
		var target:=actor.motor.global_position+Vector2(query.target_offset[0],query.target_offset[1])
		var aim:=(target-motor.global_position).normalized()
		var visual: CourierVisual=motor.get_node("CourierVisual")
		for _iteration: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
		return aim
	return fallback

func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(REVIEW_AIR.ordinary(data))
	REVIEW_AIR.install(data,world,controller,context,cells)
