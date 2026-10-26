extends "../catalog_feed/reentrant_visual.gd"
## Presentation only: original Motor, geometry, input and clock are inherited.
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not setup_error.is_empty(): return
	(status_label.get_parent().get_child(0) as Label).text = "风铃平原 · Block128 · Module零间隙拼接 · 真实输入 / 正常速度"
