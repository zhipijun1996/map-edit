extends "../r2_full/godot/r2_manual_scene.gd"
func rebuild(new_mode:String)->void:
	await super.rebuild(new_mode)
	if not prepared:return
	if is_instance_valid(labels):labels.visible=false
	display.camera.zoom=Vector2(.9,.9)
	ability_label.text="A/D 移动 · 空格单跳 · 鼠标松开反冲 · S 下穿 · E 购买 · M 整图 · R 重试"
	(ui.get_child(0).get_child(0).get_child(0) as Label).text="岩谷空间搜索 · 原型候选 / 多路线 / 奖励回程"
func _unhandled_key_input(event:InputEvent)->void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode==KEY_E and manual_extra!=null:manual_extra.request_purchase()
