extends "visual.gd"
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not setup_error.is_empty():return
	(status_label.get_parent().get_child(0) as Label).text="风铃平原 · 岩体反冲 / 限时宝库 / 双回环 · 程序输入回放"
