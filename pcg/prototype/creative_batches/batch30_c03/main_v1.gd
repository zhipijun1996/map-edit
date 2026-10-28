extends "../batch30_cell/main_v3.gd"
## Original paired Cell consumer plus presentation-only camera/support names.
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	for latch in pair_runtime.pairs:
		latch.gate_body.name="PairGateA_"+str(latch.link_id)
		latch.paired_gate_body.name="PairGateB_"+str(latch.link_id)
	if not prepared or not is_instance_valid(display):return
	display.set_process(false)
	var low:=Vector2(-130,-205)
	var high:=Vector2(820,570)
	var viewport:=get_viewport_rect().size
	var factor: float=minf((viewport.x-70)/(high.x-low.x),(viewport.y-215)/(high.y-low.y))
	display.camera.zoom=Vector2.ONE*factor
	display.camera.position=(low+high)*0.5-Vector2(0,78/factor)
	display.queue_redraw()
	status.text="打开射窗借空中回充 · 下一枪封窗/开通口并反冲 · 敌死可走分段支撑 · 观感待评"
