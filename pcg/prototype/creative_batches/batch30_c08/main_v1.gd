extends "../batch30_cell/main_v3.gd"
const NAMES=preload("../batch30_c04/stable_support_names_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	NAMES.install(self)
	if is_instance_valid(display):
		display.set_process(false)
		display.camera.zoom=Vector2.ONE*.80
		display.camera.position=Vector2(350,260)
