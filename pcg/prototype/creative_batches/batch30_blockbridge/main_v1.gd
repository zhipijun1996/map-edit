extends "../batch30_c01/main_v1.gd"
const BLOCK_OVERLAY=preload("overlay_v1.gd")
func rebuild(new_mode: String) -> void:
 await super.rebuild(new_mode)
 if not prepared:return
 var overlay:=BLOCK_OVERLAY.new();overlay.data=case_data;overlay.z_index=85;world.add_child(overlay)
 var g: Dictionary=case_data.block_grid
 var lo:=Vector2(INF,INF);var hi:=Vector2(-INF,-INF)
 for cell: Array in g.cells:
  var p:=Vector2(g.origin[0]+cell[0]*g.size,g.origin[1]+cell[1]*g.size)
  lo=lo.min(p);hi=hi.max(p+Vector2(g.size,g.size))
 var viewport:=get_viewport_rect().size
 var factor: float=minf((viewport.x-60)/(hi.x-lo.x),(viewport.y-205)/(hi.y-lo.y))
 display.camera.zoom=Vector2.ONE*factor;display.camera.position=(lo+hi)*0.5-Vector2(0,76/factor)
 status.text="Block128换脚桥 · 黄点是真边界anchor，青框是实际dock · 同枪撤A造B，落B真实恢复后继续"
