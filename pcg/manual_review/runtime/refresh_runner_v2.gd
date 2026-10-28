extends "refresh_runner_v1.gd"
## Closed-loop targeting and phase observation. Router still owns all inputs.
func observed_enemy(identifier: String) -> EnemyActor:
	for i: int in cells.enemies.size():
		if str(current_case.enemies[i].id)==identifier:return cells.enemies[i]
	return null
func validate_plan(raw: Variant) -> String:
	var translated: Variant=raw.duplicate(true) if raw is Array else raw
	if translated is Array:
		for command: Dictionary in translated:
			if command.get("trigger",{}).get("state","")in ["descending_height","latch_expiring"]:command.trigger.state="airborne"
	return super.validate_plan(translated)
func condition_met(state: String) -> bool:
	if state=="latch_expiring":
		var command: Dictionary=plan[plan_index]
		for latch: ShotLatch in cells.latches:
			if str(latch.link_id)==str(command.latch_id):return latch.is_open and latch.open_seconds-(latch._clock-latch._opened_at)<=float(command.seconds_left)
		return false
	if state=="descending_height":return not motor.is_on_floor() and motor.velocity.y>=0 and motor.position.y>=float(plan[plan_index].height_threshold)
	if not super.condition_met(state):return false
	var command: Dictionary=plan[plan_index]
	if command.has("requires_saw_phase") and not context.phase_condition(command.requires_saw_phase):return false
	if state=="grounded_shot_ready" and command.has("follow_enemy"):
		var q: Dictionary=command.follow_enemy;var actor:=observed_enemy(str(q.id))
		return actor!=null and absf((actor.motor.position.x-motor.position.x)*float(q.side)-float(q.distance))<=5
	return true
func _cell_aim(query: Dictionary, fallback: Vector2) -> Vector2:
	if query.get("kind","")!="enemy" or not query.has("body_offset"):return super._cell_aim(query,fallback)
	var actor:=observed_enemy(str(query.id))
	if actor==null or actor.health.terminal:return fallback
	var offset:=Vector2(query.body_offset[0],query.body_offset[1])
	if absf(offset.x)>actor.definition.collision_size.x/2 or absf(offset.y)>actor.definition.collision_size.y/2:return fallback
	var target:=actor.motor.global_position+offset;var aim:=(target-motor.global_position).normalized()
	var visual: CourierVisual=motor.get_node("CourierVisual")
	for _iteration: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
	return aim
func control_plan(frame: int) -> Array:
	for command: Dictionary in plan:
		if command.op!="settle" or not command.has("follow_enemy"):continue
		var q: Dictionary=command.follow_enemy;var actor:=observed_enemy(str(q.id))
		if actor!=null and not actor.health.terminal:command.target_x=actor.motor.position.x-float(q.side)*float(q.distance)
	return super.control_plan(frame)
