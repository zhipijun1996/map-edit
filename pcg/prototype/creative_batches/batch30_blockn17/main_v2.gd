extends "main_v1.gd"
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	var width: float=1152.0 if int(case_data.get("interface",0))==1 else 1024.0
	var viewport:=get_viewport_rect().size
	var factor: float=minf((viewport.x-60)/width,(viewport.y-205)/1024.0)
	display.camera.zoom=Vector2.ONE*factor;display.camera.position=Vector2(width*.5,512-76/factor)
