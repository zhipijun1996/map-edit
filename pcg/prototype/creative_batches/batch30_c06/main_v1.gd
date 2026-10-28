extends "../batch30_cell/main_v3.gd"
const NAMES=preload("../batch30_c04/stable_support_names_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	NAMES.install(self)
	if is_instance_valid(display):
		display.set_process(false)
		display.camera.zoom=Vector2.ONE*.66
		display.camera.position=Vector2(220,440)
func _process(_delta: float) -> void:
	if prepared and is_instance_valid(display) and is_instance_valid(motor):
		display.camera.position=Vector2(220,clampf(motor.position.y-350,440,850))
