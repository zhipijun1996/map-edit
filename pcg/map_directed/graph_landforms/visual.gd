extends "../catalog_feed/reentrant_visual.gd"
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not setup_error.is_empty(): return
	(status_label.get_parent().get_child(0) as Label).text = "风铃平原 · 同一探索图 · 高崖/溪谷两路 · 原生输入/正常速度"
