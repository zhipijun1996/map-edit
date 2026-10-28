extends Node2D
## Presentation only: true boundary anchors, full rectangle, no collision Cells.
var data: Dictionary

static func show_module(host, overlay: Script) -> void:
	var node=overlay.new();node.data=host.case_data;node.z_index=85;host.world.add_child(node)
	host.display.set_process(false)
	var b: Dictionary=host.case_data.approved_implementation.rectangle
	var viewport: Vector2=host.get_viewport_rect().size
	var factor: float=minf((viewport.x-100)/float(b.w),(viewport.y-245)/float(b.h))
	host.display.camera.zoom=Vector2.ONE*factor
	host.display.camera.position=Vector2(b.x+b.w/2.,b.y+b.h/2.-95/factor)

func _draw() -> void:
	var b: Dictionary=data.approved_implementation.rectangle
	draw_rect(Rect2(b.x,b.y,b.w,b.h),Color(.43,.75,.7,.65),false,2)
	for cell: Array in data.block_grid.cells:
		draw_rect(Rect2(cell[0]*128,cell[1]*128,128,128),Color(.43,.75,.7,.14),false,1)
	for key: String in data.block_ports:
		var p: Dictionary=data.block_ports[key]
		var at:=Vector2(p.position[0],p.position[1])
		var dock:=Vector2(p.stagingPosition[0],p.stagingPosition[1])
		draw_circle(at,9,Color("b5f5df"),false,2)
		draw_line(at,dock,Color(.6,.95,.85,.8),1)
		draw_circle(dock,3,Color("e4c877"))
		draw_string(ThemeDB.fallback_font,at+Vector2(-10,-22),key+" "+str(p.surface)+" "+str(p.permission),HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("c7ffed"))
