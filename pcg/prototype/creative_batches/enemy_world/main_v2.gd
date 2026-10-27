extends "main_v1.gd"
## Display-only end hold. EnemyActor and EnemyAttackProjectile explicitly use
## PAUSABLE, so disabling only the world parent does not freeze those nodes.
## Freeze after the final captured witness frame; no input/motion frame changes.
func capture_dynamic_frame()->void:
	super.capture_dynamic_frame()
	if finished and is_instance_valid(world):
		world.process_mode=Node.PROCESS_MODE_DISABLED
		for node: Node in world.find_children("*","",true,false):
			node.process_mode=Node.PROCESS_MODE_DISABLED
