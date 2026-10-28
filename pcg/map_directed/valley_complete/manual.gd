extends "../r2_full/godot/r2_manual_scene.gd"
const PAINT=preload("presentation.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	PAINT.install(world,module,case_data)
	if is_instance_valid(labels):labels.visible=false
	display.camera.zoom=Vector2(.9,.9)
	ability_label.text="A/D 移动 · 空格跳跃 · 鼠标松开射击反冲 · S 下穿 · E 商店购买(8金币) · M 整图 · R 重试"
	(ui.get_child(0).get_child(0).get_child(0) as Label).text="风铃平原 · 回声风谷 · 宝箱、商人和停靠风铃"
func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode==KEY_E and manual_extra!=null:manual_extra.request_purchase()
