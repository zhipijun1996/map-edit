extends "../../workshop/main.gd"
## Presentation only: expose actual configured capabilities without touching case.
func _ready()->void:
	super._ready()
	if ui!=null:
		var rows:=ui.get_child(0).get_child(0)
		(rows.get_child(0) as Label).text="失序之钟 · 内容工坊候选 · 按本局配置提供能力 · 观感待评"
func rebuild(new_mode:String)->void:
	await super.rebuild(new_mode)
	var names:={"move":"移动","jump":"普通跳跃","shot_recoil":"射击反冲","double_jump":"二段跳","grapple":"钩索","wall_climb":"贴墙 / 墙跳"}
	var labels:Array[String]=[]
	for value:String in capabilities:labels.append(str(names.get(value,value)))
	ability_label.text="本局能力："+"、".join(labels)
