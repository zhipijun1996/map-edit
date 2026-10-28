extends Node
## Presentation-only camera. No actor transforms or simulation state are edited.
var camera: Camera2D
var actor: PlayerMotor
var follow := true

func _process(_delta: float) -> void:
	if follow and is_instance_valid(actor) and is_instance_valid(camera):
		camera.position = actor.global_position
		camera.force_update_scroll()
