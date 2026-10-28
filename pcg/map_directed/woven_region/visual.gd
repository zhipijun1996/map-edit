extends "../valley_complete/visual.gd"
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not setup_error.is_empty():return
	(status_label.get_parent().get_child(0) as Label).text="风铃平原 · 岩谷织路 / 19地点 / R2实际拼装 · 程序输入回放"
