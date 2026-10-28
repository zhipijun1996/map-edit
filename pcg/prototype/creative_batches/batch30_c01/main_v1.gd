extends "../batch30_cell/main_v3.gd"
## Identical stable support names and presentation-only whole-arch camera.
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	for latch in pair_runtime.pairs:
		latch.gate_body.name="PairGateA_"+str(latch.link_id)
		latch.paired_gate_body.name="PairGateB_"+str(latch.link_id)
	if not prepared or not is_instance_valid(display):return
	display.set_process(false)
	var width: float=1700.0 if int(case_data.get("interface",0))==0 else 1250.0
	var low:=Vector2(-135,80)
	var high:=Vector2(width-65,865)
	var viewport:=get_viewport_rect().size
	var factor: float=minf((viewport.x-70)/(high.x-low.x),(viewport.y-215)/(high.y-low.y))
	display.camera.zoom=Vector2.ONE*factor
	display.camera.position=(low+high)*0.5-Vector2(0,78/factor)
	display.queue_redraw()
	status.text="先在A桥起跳 · 同枪撤A/造B并反冲 · B桥真实落脚恢复后继续 · 程序回放，观感待评"
