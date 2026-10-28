extends Node2D
## Source ownership overlay only: no collision shapes or player writes.
var frames: Array = []
func _ready() -> void:
	z_index = -20
	queue_redraw()
func _draw() -> void:
	var colors := [Color("438d95"), Color("8273aa"), Color("b88b55"), Color("698e69")]
	for i: int in frames.size():
		var f: Dictionary = frames[i]
		var r: Array = f.bounds; var p: Array = f.placement
		var area := Rect2(p[0]+r[0],p[1]+r[1],r[2],r[3])
		var color: Color = colors[i % colors.size()]
		draw_rect(area,Color(color,.075))
		draw_rect(area,color,false,2.)
		draw_string(ThemeDB.fallback_font,area.position+Vector2(26,40),str(f.id),HORIZONTAL_ALIGNMENT_LEFT,-1,24,color.lightened(.3))
