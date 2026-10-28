extends "../occupancy/runner_v1.gd"
const GUARD=preload("guard_charger_v1.tres")
func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	for i: int in cells.enemies.size():
		var spec: Dictionary=case.get("enemies",[])[i]
		if spec.get("variant_definition","")!="enemy-world/guard-charger-v1":continue
		var actor: EnemyActor=cells.enemies[i]
		# A real authored EnemyDefinition, preserving native health, motor,
		# attack state machine, cooldown, collision and accepted-hit knockback.
		actor.definition=GUARD
		actor.motor.configure(GUARD)
		actor.brain.configure(GUARD,actor.motor.global_position.x)

func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	if not trigger.has("enemy_state"):return true
	var query: Dictionary=trigger.enemy_state
	for i: int in cells.enemies.size():
		if str(current_case.get("enemies",[])[i].id)!=str(query.id):continue
		var actor: EnemyActor=cells.enemies[i]
		return actor.attack_behavior!=null and str(actor.attack_behavior.state)==str(query.state)
	return false
