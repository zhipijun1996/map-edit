extends "clarified_three_runner_v3.gd"
## A player may fire as the trigger is entered. Use only the published spawn
## location before deferred creation; the real projectile must hit a real Actor.
func condition_met(state: String) -> bool:
	if state=="shot_ready" and current_case.approved_implementation.reviewId=="171":
		for event: Dictionary in fired_commands:
			if int(event.frame)==clarified_input_frame and plan[int(event.index)].op=="shoot":return false
		var r: Array=current_case.review029_wave.rect
		var overlaps:=Rect2(r[0],r[1],r[2],r[3]).intersects(Rect2(motor.position-Vector2(12,18),Vector2(24,36)))
		return (overlaps or cells.enemies.size()==2) and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=1./60.+.000001
	return super.condition_met(state)
func _cell_aim(query: Dictionary, fallback: Vector2) -> Vector2:
	if current_case.approved_implementation.reviewId=="171" and cells.enemies.is_empty() and query.get("kind","")=="enemy":
		for enemy: Dictionary in current_case.enemies:
			if str(enemy.id)!=str(query.id):continue
			var offset: Array=query.get("body_offset",[0,0]);var target:=Vector2(enemy.position[0]+offset[0],enemy.position[1]+offset[1])
			var aim:=(target-motor.position).normalized();var visual: CourierVisual=motor.get_node("CourierVisual")
			for _i: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
			return aim
	return super._cell_aim(query,fallback)
