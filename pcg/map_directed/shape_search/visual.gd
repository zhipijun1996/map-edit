extends "../r2_full/godot/r2_movie_runner.gd"
func make_fixture(data:Dictionary)->void:
	await super.make_fixture(data)
	if not setup_error.is_empty():return
	if is_instance_valid(annotations):annotations.visible=false
	if not whole_map_path.is_empty() and is_instance_valid(minimap_layer):minimap_layer.visible=false
	camera.zoom=Vector2(.9,.9)
	(status_label.get_parent().get_child(0) as Label).text="风铃平原 · 岩谷空间搜索 / 实际形状与动作条件 · 程序输入回放"
