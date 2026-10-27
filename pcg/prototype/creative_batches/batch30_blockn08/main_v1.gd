extends "../batch30_c09/main_v1.gd"
const BLOCK_DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	var overlay:=BLOCK_DRAW.new();overlay.data=case_data;overlay.z_index=85;world.add_child(overlay)
	display.set_process(false)
	var viewport:=get_viewport_rect().size
	var factor: float=minf((viewport.x-60)/1536.0,(viewport.y-205)/1408.0)
	display.camera.zoom=Vector2.ONE*factor;display.camera.position=Vector2(768,704-76/factor)
func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	status.text="折页回廊 · 真实上桥取奖/同世界换下桥回来 · 普通旧路为合法对照，不预称捷径 · 人工观感待评"
