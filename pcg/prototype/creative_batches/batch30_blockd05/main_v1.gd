extends "../batch30_d05/main_v1.gd"
const BLOCK_DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	var overlay:=BLOCK_DRAW.new()
	overlay.data=case_data;overlay.z_index=20;world.add_child(overlay);overlay.queue_redraw()
	display.set_process(false)
	var g: Dictionary=case_data.block_grid
	var lo:=Vector2(INF,INF)
	var hi:=Vector2(-INF,-INF)
	for cell: Array in g.cells:
		var at:=Vector2(g.origin[0]+cell[0]*g.size,g.origin[1]+cell[1]*g.size)
		lo=lo.min(at);hi=hi.max(at+Vector2.ONE*g.size)
	var viewport:=get_viewport_rect().size
	var factor: float=minf((viewport.x-70)/(hi.x-lo.x),(viewport.y-215)/(hi.y-lo.y))
	display.camera.zoom=Vector2.ONE*factor
	display.camera.position=(lo+hi)*.5-Vector2(0,78/factor)
	display.queue_redraw()
func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	status.text="Block128 风铃台追接 · 原角色/原挂载铃/原移动台 · 首次射后落脚必须是移动台 · 程序回放，人工观感待评"
