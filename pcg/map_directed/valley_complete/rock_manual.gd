extends "manual.gd"
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if prepared:(ui.get_child(0).get_child(0).get_child(0) as Label).text="风铃平原 · 岩体反冲 / 限时宝库 / 双回环 · 隔离候选"
