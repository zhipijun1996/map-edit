extends "../../workshop/main.gd"
# Presentation only: preserve all original bodies, cells, resources, input and
# trace logic. Keep the actual low receiver, entry and pocket visible together.
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not is_instance_valid(world):return
	if is_instance_valid(display) and is_instance_valid(display.camera):
		display.camera.enabled=false
	var overview:=Camera2D.new()
	overview.position=Vector2(260,480)
	overview.zoom=Vector2(.65,.65)
	world.add_child(overview)
	overview.make_current()
