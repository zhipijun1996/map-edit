extends "revision053_runner_v5.gd"
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")in ["aligned_refund","ledge_recoil","ledge_clear"]:command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="aligned_refund":
		var q: Dictionary=plan[plan_index].align_enemy;var enemy:=observed_enemy(str(q.id))
		return enemy!=null and not enemy.health.terminal and not motor.is_on_floor() and motor.velocity.y>=0 and motor.position.y>=float(q.height) and absf(enemy.motor.position.x-motor.position.x-float(q.distance))<=5 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
	if state=="ledge_recoil":return not motor.is_on_floor() and motor.velocity.y>=0 and motor.position.y>=280 and motor.position.y<=300 and motor.position.x>=367 and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
	if state=="ledge_clear":return motor.position.y+18<=208 and motor.position.x-12>=270
	return super.condition_met(state)
