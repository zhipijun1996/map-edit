extends "../batch30_cell/main_v3.gd"
## Presentation-only overview, actual pair-state labels and failure-camera pan.
var station_labels: Array=[]
var station_base_y:=0.0
var station_x:=0.0
var lower_view:=750.0
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	station_labels=[]
	for latch in pair_runtime.pairs:
		latch.gate_body.name="PairGateA_"+str(latch.link_id)
		latch.paired_gate_body.name="PairGateB_"+str(latch.link_id)
		for member: String in ["A","B"]:
			var label:=Label.new();label.add_theme_font_size_override("font_size",22)
			label.add_theme_color_override("font_color",Color("ffe0a0"));label.add_theme_color_override("font_outline_color",Color("13212b"));label.add_theme_constant_override("outline_size",6)
			var rect: Rect2=latch.gate_rect if member=="A" else latch.paired_gate_rect
			label.position=Vector2(rect.position.x-26,minf(rect.end.y,400)-65);label.z_index=80;world.add_child(label)
			station_labels.append({"node":label,"latch":latch,"member":member})
	if not prepared or not is_instance_valid(display):return
	display.set_process(false)
	var tall: bool=int(case_data.get("interface",0))==1
	var low:=Vector2(-90,40) if tall else Vector2(-150,100)
	var high:=Vector2(1440,880) if tall else Vector2(1420,750)
	var viewport:=get_viewport_rect().size
	var factor: float=minf((viewport.x-70)/(high.x-low.x),(viewport.y-215)/(high.y-low.y))
	display.camera.zoom=Vector2.ONE*factor
	station_x=(low.x+high.x)*0.5;station_base_y=(low.y+high.y)*0.5-78/factor;lower_view=high.y
	display.camera.position=Vector2(station_x,station_base_y)
	display.queue_redraw()
func _process(_delta: float) -> void:
	if not prepared or not is_instance_valid(display) or not is_instance_valid(motor):return
	display.camera.position=Vector2(station_x,station_base_y+maxf(0,motor.global_position.y+80-lower_view))
	for item: Dictionary in station_labels:
		if not is_instance_valid(item.node) or not is_instance_valid(item.latch):continue
		var near_open: bool=item.latch.open_a
		item.node.text=("NEAR " if item.member=="A" else "FAR ")+("OPEN" if (near_open if item.member=="A" else not near_open) else "CLOSED")
	if not finished:status.text="真实载台继续运行 · 选择回折到上层入口，或击铃继续高侧出口 · 正常速度程序回放，观感待评"
