extends Node2D
var data: Dictionary
func _draw() -> void:
	var b: Dictionary=data.get("approved_first30",data.get("approved_implementation",{})).rectangle
	draw_rect(Rect2(b.x,b.y,b.w,b.h),Color(.43,.75,.7,.65),false,2)
	var origin: Array=data.block_grid.get("origin",[0,0])
	for cell: Array in data.block_grid.cells:draw_rect(Rect2(cell[0]*128+origin[0],cell[1]*128+origin[1],128,128),Color(.43,.75,.7,.14),false,1)
	for key: String in data.block_ports:
		var p: Dictionary=data.block_ports[key];var at:=Vector2(p.position[0],p.position[1]);var dock:=Vector2(p.stagingPosition[0],p.stagingPosition[1])
		var air:=false;var permission: String=p.get("permission","INOUT")
		for contract: Dictionary in data.get("air_port_contracts",[]):
			if contract.id==key:air=true;permission=contract.permission
		draw_circle(at,9,Color("b5f5df"),false,2);draw_line(at,dock,Color(.6,.95,.85,.8),1);draw_circle(dock,3,Color("e4c877"))
		draw_string(ThemeDB.fallback_font,at+Vector2(-10,-22),key+" "+("AIR"if air else"ROCK")+" "+permission,HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("c7ffed"))
