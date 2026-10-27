extends Node2D
## Presentation only. Exact receiver rectangles; no collision or input changes.
var data: Dictionary

func _draw() -> void:
	for index: int in range(data.get("latches", []).size()):
		var spec: Dictionary=data.latches[index]
		var bell:=Vector2(spec.bell[0],spec.bell[1])
		var gate:=Rect2(spec.gate[0],spec.gate[1],spec.gate[2],spec.gate[3])
		var tint:=Color("ffd280") if index==0 else Color("80e5ff")
		var name: String="左门" if index==0 else "右门"
		var link:=Color(tint,0.50)
		draw_dashed_line(bell+Vector2(0,-21),gate.get_center(),link,2,9)
		draw_rect(Rect2(bell-Vector2(14,17),Vector2(28,34)),Color(tint,0.13),true)
		draw_rect(Rect2(bell-Vector2(14,17),Vector2(28,34)),tint,false,3)
		draw_line(bell+Vector2(-9,27),bell+Vector2(0,20),tint,3)
		draw_line(bell+Vector2(9,27),bell+Vector2(0,20),tint,3)
		draw_string(ThemeDB.fallback_font,bell+Vector2(-36,58),name+"铃",HORIZONTAL_ALIGNMENT_LEFT,-1,24,tint)
		draw_string(ThemeDB.fallback_font,Vector2(gate.position.x-34,gate.position.y-63),name+"标识",HORIZONTAL_ALIGNMENT_LEFT,-1,20,tint)
