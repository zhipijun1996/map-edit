extends "visual.gd"
## Presentation only; the exact whole-world inputs and runtime stay inherited.
func make_fixture(data:Dictionary)->void:
	await super.make_fixture(data)
	if not setup_error.is_empty():return
	var panel:Control=status_label.get_parent().get_parent()
	panel.size.x=minf(940,root.get_visible_rect().size.x-24)
	(status_label.get_parent().get_child(0)as Label).text="风铃平原 · 岩井回环样图 · 真实程序输入 / 正常速度"
	for label in status_label.get_parent().get_children():
		if label is Label:label.add_theme_font_size_override("font_size",14)

func capture_dynamic_frame()->void:
	super.capture_dynamic_frame()
	if is_instance_valid(status_label)and pilot!=null and is_instance_valid(controller):
		status_label.text="%s · %.1fs · HP %.0f · 路线 %d/%d"%[str(current_case.get("id","")),current_frame/60.0,controller.actor_resources.health.current,pilot.index,pilot.program.size()]
