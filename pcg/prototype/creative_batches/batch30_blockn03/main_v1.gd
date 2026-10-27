extends "../../workshop/main.gd"
const REVERSE=preload("runtime_v1.gd")
const BLOCK_DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
	var index:=selection.selected
	var source: Dictionary=cases[index]
	cases[index]=REVERSE.ordinary_case(source)
	await super.rebuild(new_mode)
	cases[index]=source;case_data=source
	REVERSE.install(self,source);display.case_data=source
	var overlay:=BLOCK_DRAW.new();overlay.data=source;overlay.z_index=20;world.add_child(overlay);overlay.queue_redraw()
	display.set_process(false)
	var viewport:=get_viewport_rect().size
	var factor: float=minf((viewport.x-70)/1536.0,(viewport.y-215)/1024.0)
	display.camera.zoom=Vector2.ONE*factor;display.camera.position=Vector2(768,512)-Vector2(0,78/factor);display.queue_redraw()
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():replay_trace[-1].workshop.reverse_carriers=REVERSE.snapshot(self)
	status.text="N03 开发原型 · 实弹让载台真正反向/端点保持 · 自动双路策略未通过，尚非候选 · 仅手动探索"
