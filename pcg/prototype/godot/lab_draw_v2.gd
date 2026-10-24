extends "res://lab_draw.gd"
func _process(delta: float) -> void:
	super._process(delta)
	if is_instance_valid(motor):
		camera.position.x=clampf(520.,motor.position.x-300.,motor.position.x+440.)
		camera.position.y=clampf(260.,motor.position.y-240.,motor.position.y+140.)

func _draw() -> void:
	super._draw()
	var platforms: Array=case_data.get("platforms",[])
	var walls: Array=case_data.get("wall_platform_indices",[])
	if "wall_climb" in case_data.get("capabilities",[]):
		for i: int in walls:
			if i<0 or i>=platforms.size():continue
			var p: Array=platforms[i]
			if p[3]>p[2]:
				draw_line(Vector2(p[0],p[1]),Vector2(p[0],p[1]+p[3]),Color("78b9e3"),3)
				draw_line(Vector2(p[0]+p[2],p[1]),Vector2(p[0]+p[2],p[1]+p[3]),Color("78b9e3"),3)
	for i: int in case_data.get("one_way_platform_indices",case_data.get("one_way_indices",[])):
		if i<0 or i>=platforms.size():continue
		var p: Array=platforms[i]
		draw_line(Vector2(p[0],p[1]),Vector2(p[0]+p[2],p[1]),Color("f4e297"),3)
