extends "main_v1.gd"
## Overview and failure-pan only; actual PlayerMotor/Cell remain untouched.
var view_x:=0.0
var view_y:=0.0
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared or not is_instance_valid(display):return
	display.set_process(false)
	var viewport:=get_viewport_rect().size
	var low:=Vector2(-180,100)
	var high:=Vector2(980,730)
	var factor: float=minf((viewport.x-70)/(high.x-low.x),(viewport.y-215)/(high.y-low.y))
	display.camera.zoom=Vector2.ONE*factor
	view_x=(low.x+high.x)*0.5;view_y=(low.y+high.y)*0.5-78/factor
	display.camera.position=Vector2(view_x,view_y)
func _process(_delta: float) -> void:
	if not prepared or not is_instance_valid(display) or not is_instance_valid(motor):return
	display.camera.position=Vector2(view_x,view_y+maxf(0,motor.global_position.y-700))
	if not finished:status.text="同枪开前路、关后墙，真实碰墙接住反冲 · 可多跳一次提前开路 · 正常速度程序回放，观感待评"
