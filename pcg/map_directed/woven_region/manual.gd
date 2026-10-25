extends "../valley_complete/manual.gd"
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	(ui.get_child(0).get_child(0).get_child(0) as Label).text="风铃平原 · 岩谷织路 · 19地点 / 多路线 / 奖励回程 · 隔离候选"
	ability_label.text="A/D 移动 · 空格单跳 · 鼠标松开射击反冲 · S 下穿 · E 购买 · M 整图 · R 重试"
func toggle_overview() -> void:
	super.toggle_overview()
	if is_instance_valid(labels):labels.visible=overview
