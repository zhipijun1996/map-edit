extends "../valley_complete/rock_mechanics.gd"
const SHAPE_PAINT=preload("presentation.gd")
var scenery_receipt:Dictionary={}
func before_leg(leg:Dictionary,state:Dictionary)->Dictionary:
	var admitted:Dictionary=super.before_leg(leg,state)
	if not admitted.get("ok",false):return admitted
	if leg.kind=="module":
		var v:Array=state.get("real_velocity",[INF,INF])
		if Vector2(v[0],v[1]).length()>1.0:return {"ok":false,"reason":"shape_entry_speed_unsatisfied"}
	return admitted
func setup(data:Dictionary,world:Node2D,controller:PlayerController,dynamic_context)->void:
	super.setup(data,world,controller,dynamic_context)
	scenery_receipt=SHAPE_PAINT.install(world,dynamic_context.module,data,controller.motor)
func report()->Dictionary:
	var result:=super.report();result.scenery=scenery_receipt.duplicate(true);return result
