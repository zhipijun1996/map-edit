extends "../r2_full/godot/r2_manual_scene.gd"
const B=preload("binding.gd")
func rebuild(new_mode:String)->void:
	var original:Dictionary=cases[selection.selected]
	cases[selection.selected]=B.masked(original)
	await super.rebuild(new_mode)
	cases[selection.selected]=original;case_data=original
	if not prepared:return
	B.install(self,original)
	if is_instance_valid(display):display.case_data=original
	if is_instance_valid(labels):labels.visible=false
	display.camera.zoom=Vector2(.9,.9)
	ability_label.text="A/D 移动 · 空格单跳 · 鼠标松开反冲 · S 下穿 · M 整图 · R 重试"
	(ui.get_child(0).get_child(0).get_child(0)as Label).text="最新内容库双分流整图 · 隔离实验 / 尚未通过所有路线"
