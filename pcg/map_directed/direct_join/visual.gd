extends "../r2_full/godot/r2_movie_runner.gd"
const MODULE_BOUNDS = preload("module_bounds.gd")
func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	if not setup_error.is_empty(): return
	if not whole_map_path.is_empty() and is_instance_valid(minimap_layer): minimap_layer.visible = false
	var outlines = MODULE_BOUNDS.new()
	outlines.frames = case.get("module_frames", [])
	world.add_child(outlines)
	if is_instance_valid(status_label):
		(status_label.get_parent().get_child(0) as Label).text = "风铃平原 · Module直接拼接 · 27模块 / 39接缝 · 无Map补路平台"
