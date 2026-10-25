extends "../r2_full/godot/r2_manual_scene.gd"
const OPEN_PAINT = preload("presentation.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared: return
	OPEN_PAINT.install(world,module,case_data)
	if is_instance_valid(labels): labels.visible = false
	display.camera.zoom = Vector2(.9,.9)
	var rows := ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text = "风铃平原 · 回声风谷 · 手动探索样品"
