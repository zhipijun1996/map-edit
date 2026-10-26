extends "../r2_full/godot/r2_movie_runner.gd"
const B=preload("binding.gd")
func make_fixture(data:Dictionary)->void:
	await super.make_fixture(B.masked(data));B.install(self,data)
	if not setup_error.is_empty():return
	if is_instance_valid(annotations):annotations.visible=false
	if not whole_map_path.is_empty()and is_instance_valid(minimap_layer):minimap_layer.visible=false
	camera.zoom=Vector2(.9,.9)
	(status_label.get_parent().get_child(0)as Label).text="风铃平原 · 最新内容库 / 完整双分流地图 · 程序输入"
func _cell_aim(q:Dictionary,fallback:Vector2)->Vector2:return B.aim(self,q,super._cell_aim(q,fallback))
func condition_met(state:String)->bool:return super.condition_met(state)and B.enemy_condition(self)
func prepare_dynamic_frame()->void:
	replay_mode=false
	super.prepare_dynamic_frame()
