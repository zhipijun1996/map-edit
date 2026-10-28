extends "/workspace/map-edit-task-a/pcg/prototype/workshop/main.gd"
# Presentation only. Original replay, resource components, capture and cleanup remain inherited.
func _ready() -> void:
	super._ready()
	var titles: Dictionary={"grapple-anchor-gap":"挂停，再主动跃出", "grapple-bounce-brake":"自动弹出，再用反冲改轨", "grapple-jump-refill":"耗尽二跳，触环恢复，再跃向高岸", "grapple-hazard-window":"观察周期锯，选择离挂窗口"}
	var rows: VBoxContainer=ui.get_child(0).get_child(0)
	var family: String=str(cases[clip_index].get("family",""))
	(rows.get_child(0) as Label).text=str(titles.get(family,family))+" · 程序回放 60Hz / 正常速度 · 观感待评"
	# A compact caption keeps high anchors visible; this changes no world node or input.
	rows.get_child(1).hide()
	ability_label.hide();telemetry_label.hide();status.hide()
	(ui.get_child(0) as PanelContainer).size=Vector2(1256,48)
