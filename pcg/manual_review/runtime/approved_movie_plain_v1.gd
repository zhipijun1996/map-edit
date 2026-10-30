extends "../../prototype/workshop/main.gd"
const APPROVED_DRAW=preload("approved_draw_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if prepared:APPROVED_DRAW.show_module(self,APPROVED_DRAW)

func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	# Presentation tail only. Explicit PAUSABLE enemy children otherwise keep
	# ticking after the old lab disables their parent collision space.
	if finished:
		for node: Node in world.find_children("*","",true,false):
			node.set_process(false);node.set_physics_process(false)
