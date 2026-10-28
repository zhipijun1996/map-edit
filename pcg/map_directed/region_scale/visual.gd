extends "../valley_complete/visual.gd"
## Presentation only. Full-world exact Router replay is checked against the
## frozen candidate. This experimental world has no awarded chest/Boss claim.
func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	if not setup_error.is_empty():return
	(status_label.get_parent().get_child(0) as Label).text="平原整图接缝实验 · 39 地点 · 奖励 / Boss 尚未接入 · 程序回放"
