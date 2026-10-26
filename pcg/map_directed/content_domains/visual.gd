extends "../catalog_feed/reentrant_visual.gd"
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not setup_error.is_empty(): return
	(status_label.get_parent().get_child(0) as Label).text = "风铃平原 · 库内容驱动 / Block128直拼 · 程序输入 / 正常速度"
