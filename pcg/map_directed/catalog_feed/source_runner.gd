extends "../../prototype/workshop/runner.gd"
const B=preload("binding.gd")
const STYLE=preload("../valley_complete/formal_style.gd")
func make_fixture(data:Dictionary)->void:
	await super.make_fixture(B.masked(data));B.install(self,data);STYLE.actors(world,controller,context.module)
func _cell_aim(q:Dictionary,fallback:Vector2)->Vector2:return B.aim(self,q,super._cell_aim(q,fallback))
func condition_met(state:String)->bool:return super.condition_met(state)and B.enemy_condition(self)
## Same scoped legacy-guard adapter as task A's runner-capabilities-v1.
## Actual Adapter.apply still receives each source declaration; Map stays basic.
func capabilities_for(data:Dictionary)->Variant:return data.get("actual_capabilities",data.get("capabilities",[]))
func run_case(data:Dictionary)->Dictionary:
	var routed:Dictionary=data.duplicate(true);routed.actual_capabilities=data.capabilities.duplicate();routed.capabilities=["move","jump","shot_recoil"]
	var result:Dictionary=await super.run_case(routed);result.actual_declared_capabilities=routed.actual_capabilities;return result
