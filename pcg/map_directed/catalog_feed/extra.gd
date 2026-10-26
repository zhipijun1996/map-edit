extends RefCounted
const REWARDS=preload("../../prototype/workshop/mechanics.gd")
const PAINT=preload("../shape_search/presentation.gd")
const STYLE=preload("../valley_complete/formal_style.gd")
var rewards
var data:Dictionary
var scenery:Dictionary
func setup(value:Dictionary,world:Node2D,controller:PlayerController,context)->void:
	data=value;rewards=REWARDS.new();rewards.owner_runner=context.runner;world.add_child(rewards);rewards.setup(value,world,controller,context,context.runner.cells)
	STYLE.actors(world,controller,context.module);scenery=PAINT.install(world,context.module,value,controller.motor)
func before_leg(_leg:Dictionary,_state:Dictionary)->Dictionary:return {"ok":true}
func capture(_frame:int,_state:Dictionary)->void:rewards.capture()
func report()->Dictionary:
	var v:Dictionary=rewards.snapshot();var claimed:Array=[]
	for e:Dictionary in v.events:
		if e.type=="chest_claim"and e.accepted:claimed.append(str(e.id))
	var missing:Array=[]
	for id:String in data.get("required_reward_ids",[]):
		if id not in claimed:missing.append(id)
	return {"ok":missing.is_empty(),"missing_rewards":missing,"workshop":v,"scenery":scenery,"scope":"One real actor, wallet and mechanism world; finite route only"}
