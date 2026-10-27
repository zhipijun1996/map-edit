extends "../batch30_cell/main_v3.gd"
## Presentation-only overview and failure pan on original actors/world.
var view_x:=0.0
var view_y:=0.0
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared or not is_instance_valid(display):return
	display.set_process(false)
	var viewport:=get_viewport_rect().size
	var low:=Vector2(-130,20)
	var high:=Vector2(1300,730)
	var factor: float=minf((viewport.x-70)/(high.x-low.x),(viewport.y-215)/(high.y-low.y))
	display.camera.zoom=Vector2.ONE*factor
	view_x=(low.x+high.x)*0.5;view_y=(low.y+high.y)*0.5-78/factor
	display.camera.position=Vector2(view_x,view_y)
func _process(_delta: float) -> void:
	if not prepared or not is_instance_valid(display) or not is_instance_valid(motor):return
	display.camera.position=Vector2(view_x,view_y+maxf(0,motor.global_position.y-710))
	if not finished:status.text="原枪反冲退到载台后侧 · 随真实下降读出岩底净空，再抢前缘离台 · 后侧登台也是合法解 · 正常速度回放，观感待评"
