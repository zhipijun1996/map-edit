extends "../catalog_feed/manual.gd"
func rebuild(new_mode:String)->void:
	await super.rebuild(new_mode)
	if not prepared:return
	(ui.get_child(0).get_child(0).get_child(0)as Label).text=str(case_data.get("preview_title","风铃平原 · 多路线隔离原型"))
	ability_label.text="A/D 移动 · 空格单跳 · 鼠标松开射击反冲 · E 购买 · M 整图 · R 重试"
func _unhandled_key_input(event:InputEvent)->void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode==KEY_E and manual_extra!=null:manual_extra.request_purchase()
