extends "../valley_complete/manual.gd"
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	(ui.get_child(0).get_child(0).get_child(0) as Label).text="平原大图接缝实验 · 39 地点 · 宝箱 / Boss 尚未接入"
	ability_label.text="A/D 移动 · 空格跳跃 · 鼠标松开射击反冲 · S 下穿 · M 整图 · R 重试"
