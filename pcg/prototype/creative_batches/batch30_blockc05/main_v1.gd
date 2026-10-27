extends "../batch30_c05/main_v1.gd"
const BLOCK_DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
 await super.rebuild(new_mode)
 if not prepared:return
 var overlay:=BLOCK_DRAW.new();overlay.data=case_data;overlay.z_index=85;world.add_child(overlay)
 var g: Dictionary=case_data.block_grid
 var lo:=Vector2(INF,INF);var hi:=Vector2(-INF,-INF)
 for cell: Array in g.cells:
  var p:=Vector2(g.origin[0]+cell[0]*g.size,g.origin[1]+cell[1]*g.size)
  lo=lo.min(p);hi=hi.max(p+Vector2(g.size,g.size))
 var viewport:=get_viewport_rect().size
 var factor: float=minf((viewport.x-60)/(hi.x-lo.x),(viewport.y-205)/(hi.y-lo.y))
 display.camera.zoom=Vector2.ONE*factor;station_x=(lo.x+hi.x)*0.5;station_base_y=(lo.y+hi.y)*0.5-76/factor;lower_view=hi.y
 display.camera.position=Vector2(station_x,station_base_y)
