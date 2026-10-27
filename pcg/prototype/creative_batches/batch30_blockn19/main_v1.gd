extends "../batch30_cell/main_v3.gd"
const BLOCK_DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
 await super.rebuild(new_mode)
 if not prepared:return
 var overlay:=BLOCK_DRAW.new();overlay.data=case_data;overlay.z_index=85;world.add_child(overlay)
 display.set_process(false)
 var viewport:=get_viewport_rect().size
 var factor: float=minf((viewport.x-60)/1024.0,(viewport.y-205)/1024.0)
 display.camera.zoom=Vector2.ONE*factor;display.camera.position=Vector2(512,512-76/factor)
