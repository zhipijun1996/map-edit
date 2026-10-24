extends Node2D
var case_data: Dictionary
var motor: PlayerMotor
var controller: PlayerController
var camera: Camera2D
var font := ThemeDB.fallback_font
var show_text := true
func _ready() -> void:
	z_index=-10
	camera=Camera2D.new()
	camera.position=Vector2(520,260)
	get_parent().add_child(camera)
	camera.make_current()
func _process(_delta:float) -> void:
	if is_instance_valid(motor):camera.position=Vector2(maxf(520,motor.position.x),260)
	queue_redraw()
func _draw() -> void:
	for p:Array in case_data.get("platforms",[]):
		var r:=Rect2(p[0],p[1],p[2],p[3])
		draw_rect(r,Color("556a76"));draw_line(r.position,r.position+Vector2(r.size.x,0),Color("a4d3b2"),3)
	for p:Array in case_data.get("hazards",[]):
		var r:=Rect2(p[0],p[1],p[2],p[3]);draw_rect(r,Color("ba5264"))
		for x:int in range(int(r.position.x),int(r.end.x),16):
			draw_colored_polygon(PackedVector2Array([Vector2(x,minf(r.end.y,r.position.y+10)),Vector2(x+8,r.position.y),Vector2(minf(x+16,r.end.x),minf(r.end.y,r.position.y+10))]),Color("ed9b9b"))
	if case_data.has("reward_region"):
		var reward:Array=case_data.reward_region
		var rr:=Rect2(reward[0],reward[1],reward[2],reward[3])
		draw_rect(rr,Color(1,.8,.2,.2));draw_rect(rr,Color("f6cf59"),false,3)
		draw_string(font,rr.position+Vector2(0,-8),"REWARD POSITION",HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("f6cf59"))
	var g:Array=case_data.get("goal",[1000,420,100,80])
	draw_rect(Rect2(g[0],g[1],g[2],g[3]),Color(.3,.8,.6,.25))
	draw_rect(Rect2(g[0],g[1],g[2],g[3]),Color("69daa0"),false,2)
	if is_instance_valid(motor):
		var body:=Rect2(motor.position-Vector2(12,18),Vector2(24,36))
		draw_rect(body,Color("f3d88e"),false,1)
		var top:=camera.position-Vector2(610,320)
		if show_text: draw_string(font,top,str(case_data.get("id","PCG Lab"))+" | Research geometry / original Godot player",HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color.WHITE)
		if show_text: draw_string(font,top+Vector2(0,27),"Shots %d | energy %.0f | %s"%[controller.action_resources.shot_charges,controller.actor_resources.stamina.current,controller.traversal.state],HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("b3c5cf"))
		if controller.traversal.state!=&"free":draw_line(motor.position,controller.traversal.hook_tip,Color("f8d788"),2)
