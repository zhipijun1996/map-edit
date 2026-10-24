extends "res://runner_v3.gd"
const CELLS=preload("res://plains_cells.gd")
var cells

func make_fixture(case: Dictionary) -> void:
	if is_instance_valid(world):
		controller.shoot_ability.clear_projectiles();world.free()
	await process_frame
	world=Node2D.new();world.process_mode=Node.PROCESS_MODE_DISABLED;root.add_child(world)
	var module:=PlatformingModule.new();module.definition=definition_for(case);module.authoring_debug=false
	world.add_child(module)
	for index: Variant in case.get("wall_platform_indices",[]):module.get_node("Platform"+str(int(index))).add_to_group(&"wall_climbable")
	for hook: Dictionary in case.get("hooks",[]):
		var anchor:=GrappleAnchor.new();anchor.position=Vector2(hook.x,hook.y);anchor.hang_enabled=hook.get("kind","hang")=="hang";world.add_child(anchor)
	motor=PLAYER.instantiate() as PlayerMotor;motor.get_node("PlayerFeedback").free()
	motor.position=point(case.get("spawn",[60,482]));world.add_child(motor)
	controller=motor.get_node("Controller") as PlayerController
	controller.process_physics_priority=0
	motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(false)
	controller.enable_shot_energy()
	current_caps=ADAPTER.validate(capabilities_for(case)).capabilities
	capability_snapshot=ADAPTER.apply(controller,current_caps).snapshot
	accepted=[];counters={"shots":0,"jumps":0,"grapples":0};wall_jumps=0;hook_contacts=0;air_jumps=0;anchor_jumps=0
	controller.shoot_ability.shot_fired.connect(func(direction: Vector2,id: int):counters.shots+=1;accepted.append({"type":"shot","direction":[direction.x,direction.y],"serial":id}))
	controller.jump_ability.jumped.connect(func():
		counters.jumps+=1
		var kind:="ground_jump"
		if before_state==&"hook_hang":kind="anchor_jump";anchor_jumps+=1
		elif not before_grounded and before_used_jumps>=1:kind="air_jump";air_jumps+=1
		accepted.append({"type":kind}))
	controller.traversal.action_changed.connect(func(state: StringName):
		accepted.append({"type":"traversal","state":str(state)})
		if state==&"wall_kick":wall_jumps+=1;counters.jumps+=1
		if state==&"hook_cast":counters.grapples+=1)
	controller.traversal.hook_contact.connect(func(_point: Vector2):hook_contacts+=1)
	context=DYNAMIC.new();context.runner=self;context.module=module;context.controller=controller
	context.driver_mode=case.get("schedule_mode","normal_controller")=="priority_driver"
	world.add_child(context);context.attach_damage()
	controller.set_physics_process(not context.driver_mode)
	var static_records:=module.world_static_hazard_records()
	for i: int in static_records.size():
		var record: Dictionary=static_records[i];var bounds: Rect2=record.rect
		var emitter:=DemoContactEmitter.new();emitter.controller=controller;emitter.policy=context.policy;emitter.kind=DamageRequest.Kind.ENVIRONMENT
		emitter.source_id=StringName(record.authored_id);emitter.position=bounds.get_center();emitter.half_size=bounds.size/2.
		for raw: Dictionary in case.get("thorns",[]):
			if raw.get("surface_id","")==record.authored_id:emitter.amount=float(raw.get("damage",emitter.amount));emitter.interval=float(raw.get("contact_interval",emitter.interval))
		module.add_child(emitter)
	initial_v3=motor.position;previous_v3=motor.position

	cells=CELLS.new();cells.owner_runner=self;world.add_child(cells);cells.setup(case,world,controller,context)

func capture_dynamic_frame() -> void:
	# Enemy damage is a successful player action, not player harm. Preserve all
	# original commits in context; only the player's outcomes determine no-harm.
	var contacts: Array=context.contacts_now()
	if not contacts.is_empty():safe_v3=false;context.contact_history.append({"frame":context.frame,"contacts":contacts})
	if cells!=null and not cells.player_damage.is_empty():safe_v3=false
	if warmup_left>0:warmup_left-=1;return
	if captured.is_empty():initial_clock_v3=context.module.clock
	var position:=motor.global_position
	if absf(position.x)>30000 or absf(position.y)>10000:safe_v3=false
	goal_min_v3=minf(goal_min_v3,position.distance_to(goal_v3.get_center()))
	var at_goal:=goal_v3.has_point(position) and motor.is_on_floor()
	reached_v3=reached_v3 or at_goal
	stable_v3=stable_v3+1 if at_goal and motor.get_real_velocity().length()<=1 else 0
	var value:=snapshot(current_frame,controller.router.axis,frame_actions);value.merge(context.snapshot());value.goal_stable_frames=stable_v3
	value.normal_velocity=[motor.normal_velocity.x,motor.normal_velocity.y];value.real_velocity=[motor.get_real_velocity().x,motor.get_real_velocity().y]
	value.plains=cells.snapshot() if cells!=null else {}
	captured.append(value);previous_v3=position;current_frame+=1

func run_case(case: Dictionary) -> Dictionary:
	if case.get("capabilities",[])!=["move","jump","shot_recoil"]:return reject(case,"plains_requires_exact_move_jump_recoil")
	var result: Dictionary=await super.run_case(case)
	if cells!=null:result.plains=cells.snapshot()
	return result

func _run() -> void:
	var input_path:="";var output_path:=""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--input="):input_path=arg.trim_prefix("--input=")
		if arg.begins_with("--output="):output_path=arg.trim_prefix("--output=")
	var data: Variant=JSON.parse_string(FileAccess.get_file_as_string(input_path))
	if not data is Dictionary or not data.get("cases") is Array or data.cases.is_empty():push_error("Invalid dynamic batch JSON");quit(2);return
	var results: Array=[]
	for case: Dictionary in data.cases:
		results.append(await run_case(case));print("CASE_V3 ",case.get("id","")," ",results[-1].reason)
		await process_frame
	if is_instance_valid(world):controller.shoot_ability.clear_projectiles();world.free()
	cells=null;context=null;controller=null;motor=null;world=null
	for _cleanup_frame: int in 4:await process_frame
	DirAccess.make_dir_recursive_absolute(output_path.get_base_dir())
	var file:=FileAccess.open(output_path,FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"disordered-clock/physics-batch/v3","engine":Engine.get_version_info().string,"source_commit":"12f6cb006d7119598e3235f4ca4f7323e4c9d092","physics_hz":60,"scheduling":"module -200, moving -100, input -10, original controller 0, hazard 900, policy 1000, observer 1100","results":results}));file.close()
	print("PCG_BATCH_V3_COMPLETE ",results.size());quit(0)
