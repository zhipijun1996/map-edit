extends "../../migration/foundry_feedback_runner_v5.gd"
const REVIEW_AIR=preload("air_enemy_binding_v1.gd")

func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(REVIEW_AIR.ordinary(data))
	current_case=data
	REVIEW_AIR.install(data,world,controller,context,cells)

func enemy_alive(identifier: String) -> bool:
	for i: int in cells.enemies.size():
		var actor: EnemyActor=cells.enemies[i]
		if str(current_case.enemies[i].id)==identifier:return is_instance_valid(actor) and not actor.health.terminal
	return false

func control_plan(frame: int) -> Array:
	while plan_index<plan.size() and plan[plan_index].has("skip_if_enemy_dead") and not enemy_alive(str(plan[plan_index].skip_if_enemy_dead)):plan_index+=1
	return super.control_plan(frame)
