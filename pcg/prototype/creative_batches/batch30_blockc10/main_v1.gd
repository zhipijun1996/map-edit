extends "../batch30_runtime/main_block_v1.gd"
const NAMES=preload("../batch30_c04/stable_support_names_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	NAMES.install(self)
	display.camera.zoom=Vector2.ONE*.75
	display.camera.position=Vector2(320,180)
