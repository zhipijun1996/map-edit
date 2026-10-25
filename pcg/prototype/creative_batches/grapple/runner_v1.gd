extends "res://runner_v3.gd"
const CELLS=preload("res://plains_cells.gd")
var cells
const LIFECYCLE=preload("res://plains_lifecycle.gd")
var cleanup_records: Array=[]
var entry_capture: Dictionary={}
const EXTRA=preload("../../../workshop/mechanics.gd")
var extra

func make_fixture(case: Dictionary) -> void:
	if is_instance_valid(world):
		cleanup_records.append(await LIFECYCLE.dispose(self,world,controller))
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
	extra=EXTRA.new();extra.owner_runner=self;world.add_child(extra)
	extra.setup(case,world,controller,context,cells)

func control_plan(frame: int) -> Array:
	var requested: Array=[]
	var command_budget:=16
	while plan_index<plan.size() and plan_error.is_empty() and command_budget>0:
		command_budget-=1
		var command: Dictionary=plan[plan_index]
		var trigger: Dictionary=command.get("trigger",{})
		var age:=frame-previous_plan_frame
		var key: Variant=command.get("noise_key",plan_index)
		var jitter:=timing_error(key) if command.get("timing_noise",true) else 0
		var earliest:=maxi(0,int(trigger.get("after",trigger.get("min_after",0)))+jitter)
		var timeout:=int(trigger.get("timeout",3600))
		if age>timeout:
			plan_error="trigger_timeout/"+str(plan_index)+"/"+str(trigger.get("state","after"));break
		if age<earliest:break
		if trigger.has("state") and not condition_met(str(trigger.state)):break
		var op: String=command.op
		var direction:=point(command.get("direction",[0,0]))
		if command.has("aim_target"):
			var origin:=motor.global_position+Vector2(0,-6) if op=="grapple" else motor.global_position
			direction=(point(command.aim_target)-origin).normalized()
		if command.has("aim_cell"):direction=_cell_aim(command.aim_cell,direction)
		var applied_aim:=aim_error(key) if op in ["shoot","grapple"] else 0.
		if op in ["shoot","grapple"]:direction=disturbed_direction(direction,key)
		var submitted_type:=""
		if op=="axis":set_axis(float(command.get("value",0.)))
		elif op=="settle":settling=true;settle_options=command
		elif op!="wait":
			submitted_type="shoot_release" if op=="shoot" else op
			controller.router.request_action(StringName(submitted_type),direction)
			requested.append({"type":submitted_type,"direction":[direction.x,direction.y],"plan_index":plan_index})
		fired_commands.append({"index":plan_index,"frame":frame,"op":op,"state":str(controller.traversal.state),"grounded":motor.is_on_floor(),"position":[motor.position.x,motor.position.y],"direction":[direction.x,direction.y],"noise_key":key,"timing_error":jitter,"threshold":earliest,"aim_error_degrees":applied_aim})
		previous_plan_frame=frame;plan_index+=1
	if settling:
		var center:=float(settle_options.get("target_x",settle_goal.get_center().x))
		var deadband:=float(settle_options.get("deadband",minf(12,settle_goal.size.x*.15)))
		set_axis(signf(center-motor.position.x) if absf(center-motor.position.x)>deadband else 0.)
	return requested

func _cell_aim(query: Dictionary, fallback: Vector2) -> Vector2:
	var found:=false;var target:=Vector2.ZERO
	if query.kind=="bell":
		for latch: ShotLatch in cells.latches:
			if str(latch.link_id)==str(query.id):target=latch.to_global(latch.bell_position);found=true;break
	elif query.kind=="enemy":
		for i: int in cells.enemies.size():
			var actor: EnemyActor=cells.enemies[i]
			if str(current_case.get("enemies",[])[i].id)==str(query.id) and not actor.health.terminal:
				target=actor.motor.global_position;found=true;break
	if not found:return fallback
	# The original muzzle is offset from the body. Solve its bearing as a
	# forward-model query; do not move the body or grant resources. The original
	# Router/weapon still executes the shot and the original aim noise is applied.
	var aim:=(target-motor.global_position).normalized()
	var visual: CourierVisual=motor.get_node("CourierVisual")
	for _iteration: int in 4:
		aim=(target-visual.muzzle_position(aim)).normalized()
	return aim

func prepare_dynamic_frame() -> void:
	# Observe the actual boundary BEFORE Router receives the first action.
	# Module/dynamic nodes have already stepped at priorities -200/-100.
	if warmup_left==0 and entry_capture.is_empty():
		entry_capture=snapshot(-1,controller.router.axis,[])
		entry_capture.merge(context.snapshot())
		entry_capture.real_velocity=[motor.get_real_velocity().x,motor.get_real_velocity().y]
		entry_capture.normal_velocity=[motor.normal_velocity.x,motor.normal_velocity.y]
		entry_capture.plains=cells.snapshot()
		entry_capture.sampling_point="before_first_router_input_after_dynamic_update"
	super.prepare_dynamic_frame()

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
	extra.capture();value.workshop=extra.snapshot()
	captured.append(value);previous_v3=position;current_frame+=1

func run_case(case: Dictionary) -> Dictionary:
	for command: Dictionary in case.get("control_plan",[]):
		if not command.has("aim_cell"):continue
		var query: Dictionary=command.aim_cell
		var known:=false
		for spec: Dictionary in case.get("latches",[]) if query.get("kind")=="bell" else case.get("enemies",[]) if query.get("kind")=="enemy" else []:
			if str(spec.id)==str(query.get("id","")):known=true
		if not known:return reject(case,"unregistered_aim_target_cell")
	entry_capture={}
	var result: Dictionary=await super.run_case(case)
	if cells!=null and not result.get("rejected",false):result.plains=cells.snapshot();result.entry_snapshot=entry_capture;result.workshop=extra.snapshot()
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
	if is_instance_valid(world):cleanup_records.append(await LIFECYCLE.dispose(self,world,controller))
	cells=null;context=null;controller=null;motor=null;world=null
	for _cleanup_frame: int in 4:await process_frame
	DirAccess.make_dir_recursive_absolute(output_path.get_base_dir())
	var file:=FileAccess.open(output_path,FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"disordered-clock/physics-batch/v3","engine":Engine.get_version_info().string,"source_commit":"12f6cb006d7119598e3235f4ca4f7323e4c9d092","physics_hz":60,"scheduling":"module -200, moving -100, input -10, original controller 0, hazard 900, policy 1000, observer 1100","results":results,"cleanup":cleanup_records}));file.close()
	print("PCG_BATCH_V3_COMPLETE ",results.size());quit(0)
