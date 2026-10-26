extends "extra.gd"
## Reuse the existing discovery observer for the manual HUD. All graph rewards
## are zero; only Workshop's original chest services can grant coins.
const SEM=preload("../r2_full/state_extra.gd")
var discovery
func setup(value:Dictionary,world:Node2D,controller:PlayerController,context)->void:
	super.setup(value,world,controller,context)
	discovery=SEM.new();discovery.setup(value,world,controller,context)
func capture(frame:int,state:Dictionary)->void:
	super.capture(frame,state);discovery.capture(frame,state)
func report()->Dictionary:
	var result:Dictionary=super.report();var seen:Dictionary=discovery.report()
	for key:String in ["visited_nodes","opened_flags","visit_events","error"]:result[key]=seen[key]
	result.wallet_balance=result.workshop.coins
	return result
