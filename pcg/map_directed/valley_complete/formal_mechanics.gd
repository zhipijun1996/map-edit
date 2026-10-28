extends "mechanics.gd"
const FORMAL=preload("formal_style.gd")
var style_receipt: Dictionary={}
func setup(data:Dictionary,world:Node2D,controller:PlayerController,dynamic_context)->void:
	super.setup(data,world,controller,dynamic_context)
	style_receipt=FORMAL.actors(world,controller,context.module)
	if not style_receipt.ok:error="formal_presentation_not_completely_installed"
func report()->Dictionary:
	var result:=super.report()
	result.formal_style=style_receipt.duplicate(true)
	return result
