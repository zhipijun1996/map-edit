extends "../woven_region/manual.gd"
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	(ui.get_child(0).get_child(0).get_child(0) as Label).text="风铃平原 · 风隙回响 / 内容驱动整图 · 趣味待评"
