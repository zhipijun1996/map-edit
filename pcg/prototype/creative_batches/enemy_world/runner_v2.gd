extends "runner_v1.gd"
## Observation-conditioned input strategy only; native EnemyActor owns all motion.
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
