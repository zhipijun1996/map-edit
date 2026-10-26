extends "../r2_full/godot/r2_runner.gd"
const B=preload("binding.gd")
func make_fixture(data:Dictionary)->void:
	await super.make_fixture(B.masked(data));B.install(self,data)
func _cell_aim(q:Dictionary,fallback:Vector2)->Vector2:return B.aim(self,q,super._cell_aim(q,fallback))
func condition_met(state:String)->bool:return super.condition_met(state)and B.enemy_condition(self)
