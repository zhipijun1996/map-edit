extends "../../workshop/main.gd"
## Presentation-only HP readout; no combat/resource/actor state mutation.
var hp_labels: Dictionary={}

func rebuild(new_mode:String)->void:
	await super.rebuild(new_mode)
	hp_labels.clear()
	for enemy:EnemyActor in cells.enemies:
		var label:=Label.new()
		label.position=Vector2(-50,-72)
		label.add_theme_font_size_override("font_size",21)
		label.add_theme_color_override("font_color",Color("ffe0a0"))
		label.add_theme_color_override("font_outline_color",Color("13212b"))
		label.add_theme_constant_override("outline_size",6)
		label.z_index=80
		enemy.motor.add_child(label)
		hp_labels[enemy]=label

func capture_dynamic_frame()->void:
	super.capture_dynamic_frame()
	var values:Array[String]=[]
	for enemy:EnemyActor in cells.enemies:
		var actual:="HP %d / 3"%int(enemy.health.current)
		values.append(actual)
		if hp_labels.has(enemy):hp_labels[enemy].text=actual
	status.text="共享敌人 · "+" / ".join(values)+" · 命中会消耗未来借火机会；死后仍可走两侧落地路线"
