extends "../r2_full/godot/r2_movie_runner.gd"
const OPEN_PAINT = preload("presentation.gd")
func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	if not setup_error.is_empty(): return
	OPEN_PAINT.install(world,context.module,case)
	if is_instance_valid(annotations): annotations.visible = false
	if not whole_map_path.is_empty() and is_instance_valid(minimap_layer): minimap_layer.visible = false
	camera.zoom = Vector2(.9,.9)
	if is_instance_valid(status_label):
		(status_label.get_parent().get_child(0) as Label).text = "风铃平原 · 回声风谷 · 开放地形样品"
func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	if is_instance_valid(status_label):
		status_label.text = "程序输入回放 · 正常速度 · %.1f 秒 · 单跳 / 射击反冲" % (current_frame/60.)
