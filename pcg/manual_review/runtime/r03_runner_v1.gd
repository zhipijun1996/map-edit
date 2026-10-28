extends "/workspace/map-edit-task-a/pcg/prototype/workshop/runner.gd"
const REVIEW_AIR=preload("air_enemy_binding_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(REVIEW_AIR.ordinary(data))
	REVIEW_AIR.install(data,world,controller,context,cells)
