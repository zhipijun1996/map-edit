extends "../../workshop/main.gd"
## Presentation only: keep all junction openings in view. Physics is unchanged.

func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared or not is_instance_valid(display):return
	display.set_process(false)
	var low:=Vector2(INF,INF)
	var high:=Vector2(-INF,-INF)
	for rect: Array in case_data.platforms:
		low=low.min(Vector2(rect[0],rect[1]-85))
		high=high.max(Vector2(rect[0]+rect[2],rect[1]+rect[3]))
	var viewport:=get_viewport_rect().size
	var extent:=high-low+Vector2(100,90)
	var zoom_value: float=minf((viewport.x-70)/extent.x,(viewport.y-245)/extent.y)
	display.camera.zoom=Vector2.ONE*zoom_value
	display.camera.position=(low+high)*.5-Vector2(0,95/zoom_value)
	display.queue_redraw()
	status.text="地图路口候选 · A/B/C/D为外接方向 · 正常速度输入回放，观感待评"
