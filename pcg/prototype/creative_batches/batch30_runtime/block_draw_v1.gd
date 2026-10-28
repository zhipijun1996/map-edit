extends Node2D
## Presentation only: ownership cells and anchors never create collisions.
var data: Dictionary
func _draw() -> void:
	var g: Dictionary=data.block_grid
	var step: float=float(g.size)
	for cell: Array in g.cells:
		var at:=Vector2(g.origin[0]+cell[0]*step,g.origin[1]+cell[1]*step)
		draw_rect(Rect2(at,Vector2.ONE*step),Color(.43,.75,.7,.17),false,1)
	for key: String in data.block_ports:
		var p: Dictionary=data.block_ports[key]
		var at:=Vector2(p.position[0],p.position[1])
		var dock:=Vector2(p.grid.stagingPosition[0],p.grid.stagingPosition[1])
		draw_circle(at,9,Color("b5f5df"),false,2)
		draw_line(at,dock,Color(.6,.95,.85,.8),1)
		draw_circle(dock,3,Color("e4c877"))
		draw_string(ThemeDB.fallback_font,at+Vector2(-16,-22),"BLOCK PORT "+key,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("c7ffed"))
