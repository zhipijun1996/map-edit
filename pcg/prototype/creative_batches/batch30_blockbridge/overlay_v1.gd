extends Node2D
## Visual ownership/anchor/dock distinctions only; no collision or state writes.
var data: Dictionary
func _draw() -> void:
 var g: Dictionary=data.block_grid
 for cell: Array in g.cells:
  var at:=Vector2(g.origin[0]+cell[0]*g.size,g.origin[1]+cell[1]*g.size)
  draw_rect(Rect2(at,Vector2(g.size,g.size)),Color(0.3,0.55,0.8,0.19),false,1.0)
 for key: String in data.block_ports:
  var p: Dictionary=data.block_ports[key]
  var a:=Vector2(p.position[0],p.position[1])
  var d:=Vector2(p.grid.stagingPosition[0],p.grid.stagingPosition[1])
  draw_circle(a,7,Color("ffd36e"));draw_line(a,d,Color("80e9ec"),2)
  draw_rect(Rect2(d-Vector2(12,18),Vector2(24,36)),Color("80e9ec"),false,2)
  draw_string(ThemeDB.fallback_font,a+Vector2(-20,-14),key+" anchor",HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("ffd36e"))
  draw_string(ThemeDB.fallback_font,d+Vector2(-18,35),"dock",HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("80e9ec"))
