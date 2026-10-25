extends "../woven_region/visual.gd"
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not setup_error.is_empty():return
	(status_label.get_parent().get_child(0) as Label).text="风铃平原 · 风隙回响 / 击铃反冲 · 敌人回充 · 尖刺岩拱 · 程序回放"
