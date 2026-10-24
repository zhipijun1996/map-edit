extends SceneTree
## JSON batch worker. Original production Player scene, Motor/Controller/Router unchanged.
const PLAYER = preload("res://scenes/player/player.tscn")
const DT := 1.0/60.0
var world: Node2D
var motor: PlayerMotor
var controller: PlayerController
var accepted: Array = []
var counters := {"shots":0,"jumps":0,"grapples":0}
var dangers: Array[Rect2] = []
var setup_error := ""
var draw_node: Node2D
var demo := false
var manual := false
var fps := 0

func _initialize() -> void:
	_run.call_deferred()

func point(raw: Array) -> Vector2:
	return Vector2(float(raw[0]),float(raw[1]))
func rect(raw: Array) -> Rect2:
	return Rect2(float(raw[0]),float(raw[1]),float(raw[2]),float(raw[3]))

func make_fixture(case: Dictionary) -> void:
	if is_instance_valid(world):
		controller.shoot_ability.clear_projectiles()
		world.free()
	await process_frame
	world = Node2D.new()
	root.add_child(world)
	dangers.clear()
	for value: Array in case.get("platforms",[]):
		var body := StaticBody2D.new()
		body.position = Vector2(value[0]+value[2]/2.0,value[1]+value[3]/2.0)
		body.collision_layer = 1
		var shape := CollisionShape2D.new()
		var box := RectangleShape2D.new()
		box.size = Vector2(value[2],value[3]);shape.shape=box
		body.add_child(shape);world.add_child(body)
	for value: Array in case.get("hazards",[]): dangers.append(rect(value))
	for hook: Dictionary in case.get("hooks",[]):
		var anchor := GrappleAnchor.new()
		anchor.position=Vector2(hook.x,hook.y)
		anchor.hang_enabled=hook.get("kind","hang")=="hang"
		world.add_child(anchor)
	motor=PLAYER.instantiate() as PlayerMotor
	motor.get_node("CourierVisual").use_plains_v3=false
	# Cosmetic feedback is removed before _ready: no audio objects in this diagnostic lab.
	motor.get_node("PlayerFeedback").free()
	motor.position=point(case.get("spawn",[60,482]))
	world.add_child(motor)
	controller=motor.get_node("Controller") as PlayerController
	controller.set_physics_process(false)
	motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(false)
	if not controller.enable_shot_energy(): setup_error="shot_energy_configuration_failed"
	if case.get("profile","base") in ["grapple","all"]: controller.traversal.grant(&"grapple")
	if case.get("profile","base") in ["double_jump","all"]: controller.traversal.grant(&"double_jump")
	accepted=[];counters={"shots":0,"jumps":0,"grapples":0}
	controller.shoot_ability.shot_fired.connect(func(d: Vector2,id: int):
		counters.shots+=1
		accepted.append({"type":"shot","direction":[d.x,d.y],"serial":id}))
	controller.shoot_ability.shot_rejected.connect(func(reason: StringName):accepted.append({"type":"shot_rejected","reason":str(reason)}))
	controller.router.action_rejected.connect(func(reason: String):accepted.append({"type":"router_rejected","reason":reason}))
	controller.jump_ability.jumped.connect(func():
		counters.jumps+=1
		accepted.append({"type":"jump"}))
	controller.traversal.action_changed.connect(func(state: StringName):
		if state==&"hook_cast": counters.grapples+=1
		accepted.append({"type":"traversal","state":str(state)}))
	controller.traversal.hook_contact.connect(func(p:Vector2):accepted.append({"type":"hook_contact","position":[p.x,p.y]}))
	await physics_frame
	await process_frame
	for i: int in 4:
		await physics_frame
		controller.physics_tick(DT)
	accepted.clear()
	if demo:
		draw_node=load("res://lab_draw.gd").new()
		draw_node.case_data=case
		draw_node.motor=motor
		draw_node.controller=controller
		world.add_child(draw_node)

func snapshot(index: int, axis: float, actions: Array) -> Dictionary:
	return {"frame":index,"x":motor.position.x,"y":motor.position.y,"vx":motor.velocity.x,"vy":motor.velocity.y,"grounded":motor.is_on_floor(),"traversal_state":str(controller.traversal.state),"shot_charges":controller.action_resources.shot_charges,"jumps_used":controller.jump_ability.used_jumps,"energy":controller.actor_resources.stamina.current,"hp":controller.actor_resources.health.current,"axis":axis,"requested":actions,"accepted":accepted.duplicate(true)}

func run_case(case: Dictionary) -> Dictionary:
	var started := Time.get_ticks_usec()
	await make_fixture(case)
	var frames: Array=[]
	var actions_by_frame: Dictionary={}
	var axes_by_frame: Dictionary={}
	for a: Dictionary in case.get("actions",[]):
		var frame:=int(a.frame)
		if not actions_by_frame.has(frame): actions_by_frame[frame]=[]
		actions_by_frame[frame].append(a)
	for a: Dictionary in case.get("axes",[]):axes_by_frame[int(a.frame)]=float(a.value)
	var goal:=rect(case.get("goal",[100000,0,100,100]))
	var safe:=true
	var reached:=false
	var reason:="frame_budget"
	var minimum_goal_distance:=INF
	var initial:=motor.position
	var previous:=initial
	var failure_frame:=-1
	for frame: int in int(case.get("max_frames",360)):
		await physics_frame
		accepted.clear()
		if axes_by_frame.has(frame):controller.router.set_move_axis(axes_by_frame[frame])
		var actions: Array=actions_by_frame.get(frame,[])
		if not manual:
			for action: Dictionary in actions:
				var direction:=point(action.get("direction",[0,0]))
				controller.router.request_action(StringName(action.type),direction)
		controller.physics_tick(DT)
		var p:=motor.global_position
		var body:=Rect2(p-Vector2(12,18),Vector2(24,36))
		var swept:=body.merge(Rect2(previous-Vector2(12,18),Vector2(24,36)))
		for danger: Rect2 in dangers:
			if swept.intersects(danger,true):
				if safe:failure_frame=frame;reason="hazard_contact"
				safe=false
		if absf(p.x)>30000 or absf(p.y)>10000:
			safe=false;reason="out_of_bounds";failure_frame=frame
		minimum_goal_distance=minf(minimum_goal_distance,p.distance_to(goal.get_center()))
		frames.append(snapshot(frame,controller.router.axis,actions))
		previous=p
		if goal.has_point(p) and (not case.get("goal_grounded",true) or motor.is_on_floor()):
			reached=true
			if safe:reason="goal_reached"
			if not case.get("trace_all",false):break
		if not safe and not case.get("trace_all",false):break
		if demo:
			draw_node.queue_redraw()
			await process_frame
	var result={"id":case.get("id","unnamed"),"ok":safe and reached and setup_error.is_empty(),"safe":safe,"goal_reached":reached,"reason":reason,"failure_frame":failure_frame,"shots":counters.shots,"jumps":counters.jumps,"grapples":counters.grapples,"ticks":frames.size(),"elapsed_ms":(Time.get_ticks_usec()-started)/1000.0,"minimum_goal_distance":minimum_goal_distance,"initial_position":[initial.x,initial.y],"frames":frames}
	if not setup_error.is_empty():result.error=setup_error
	return result

func _run() -> void:
	var input_path:=""
	var output_path:=""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--input="): input_path=arg.trim_prefix("--input=")
		if arg.begins_with("--output="): output_path=arg.trim_prefix("--output=")
		if arg=="--demo":demo=true
		if arg=="--manual":manual=true;demo=true
	if input_path.is_empty() or output_path.is_empty():
		push_error("Usage: --script runner.gd -- --input=/absolute/batch.json --output=/absolute/result.json [--demo]")
		quit(2);return
	var data: Variant=JSON.parse_string(FileAccess.get_file_as_string(input_path))
	if not data is Dictionary or not data.get("cases") is Array:
		push_error("Invalid cases JSON");quit(2);return
	var results: Array=[]
	var started:=Time.get_ticks_usec()
	for case: Dictionary in data.cases:
		results.append(await run_case(case))
		print("CASE ",case.get("id","")," ",results[-1].reason)
	if is_instance_valid(world):
		controller.shoot_ability.clear_projectiles()
		world.free()
	await process_frame
	DirAccess.make_dir_recursive_absolute(output_path.get_base_dir())
	var file:=FileAccess.open(output_path,FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"disordered-clock/physics-batch/v1","engine":Engine.get_version_info().string,"source_commit":"12f6cb006d7119598e3235f4ca4f7323e4c9d092","physics_hz":60,"elapsed_ms":(Time.get_ticks_usec()-started)/1000.0,"results":results}))
	file.close()
	print("PCG_BATCH_COMPLETE ",results.size())
	quit(0)
