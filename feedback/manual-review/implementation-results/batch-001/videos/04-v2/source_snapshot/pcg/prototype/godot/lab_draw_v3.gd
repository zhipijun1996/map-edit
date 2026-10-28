extends Node2D
## Draw actual Module actors; this observer adds only goal and collision guides.
var case_data: Dictionary
var motor: PlayerMotor
var controller: PlayerController
var module: PlatformingModule
var camera: Camera2D
func _ready() -> void:
	z_index=20
	camera=Camera2D.new();camera.position=Vector2(520,260);get_parent().add_child(camera);camera.make_current()
func _process(_delta: float) -> void:
	if is_instance_valid(motor):
		camera.position.x=clampf(520.,motor.position.x-300.,motor.position.x+440.)
		camera.position.y=clampf(260.,motor.position.y-240.,motor.position.y+140.)
	queue_redraw()
func _draw() -> void:
	var goal: Array=case_data.get("goal",[100000,0,100,100]);var area:=Rect2(goal[0],goal[1],goal[2],goal[3])
	draw_rect(area,Color(.2,.8,.6,.2));draw_rect(area,Color("69daa0"),false,2)
	draw_string(ThemeDB.fallback_font,area.position+Vector2(0,-9),"EXIT / STABLE",HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("69daa0"))
	for port: Dictionary in case_data.get("ports",[]):
		var at:=Vector2(port.position[0],port.position[1]);var normal:=Vector2(port.normal[0],port.normal[1])
		draw_circle(at,9,Color("e8c76a"));draw_line(at,at+normal*30,Color("e8c76a"),2)
		draw_string(ThemeDB.fallback_font,at+Vector2(-29,-55),"PORT "+str(port.id),HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("ffe9a3"))
	if is_instance_valid(motor):
		draw_rect(Rect2(motor.position-Vector2(12,18),Vector2(24,36)),Color("f3d88e"),false,1)
		if controller.traversal.state in [&"hook_cast",&"hook_pull",&"hook_hang"]:draw_line(motor.position,controller.traversal.hook_tip,Color("f8d788"),2)
