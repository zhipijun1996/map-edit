extends "res://runner_v2.gd"
## Original Node scheduling: module -200, carrier -100, input -10, player 0,
## original hazards 900, original policy 1000, observer 1100.
const DYNAMIC = preload("res://dynamic_context.gd")
var context
var current_case: Dictionary
var current_frame:=0
var warmup_left:=0
var frame_actions: Array=[]
var axes_v3: Dictionary={}
var actions_v3: Dictionary={}
var captured: Array=[]
var stable_v3:=0
var reached_v3:=false
var safe_v3:=true
var goal_v3:=Rect2()
var previous_v3:=Vector2.ZERO
var initial_clock_v3:=0.0
var goal_min_v3:=INF
var initial_v3:=Vector2.ZERO
var last_input_v3:=0

func definition_for(case: Dictionary) -> PlatformingModuleDefinition:
	var def:=PlatformingModuleDefinition.new();def.module_id=StringName(case.get("id","dynamic"))
	def.world_bounds=rect(case.get("world_bounds",[-5000,-5000,15000,15000]))
	for value: Array in case.get("platforms",[]):def.platforms.append(rect(value))
	for value: Array in case.get("hazards",[]):def.danger_bounds.append(rect(value))
	for index: Variant in case.get("one_way_platform_indices",case.get("one_way_indices",[])):def.one_way_platform_indices.append(int(index))
	for raw: Dictionary in case.get("moving_platforms",[]):
		var value:=ModuleMovingPlatformDefinition.new()
		for key: String in ["platform_id","travel_duration","dwell_duration","initial_phase"]:
			if raw.has(key):value.set(key,raw[key])
		for key: String in ["start","finish","size"]:
			if raw.has(key):value.set(key,point(raw[key]))
		def.ferries.append(value)
	for raw: Dictionary in case.get("saws",[]):
		var value:=ModuleSawDefinition.new()
		for key: String in ["source_id","radius","period","initial_phase","damage","contact_interval"]:
			if raw.has(key):value.set(key,raw[key])
		for key: String in ["origin","travel"]:
			if raw.has(key):value.set(key,point(raw[key]))
		def.saws.append(value)
	for raw: Dictionary in case.get("thorns",[]):
		var value:=PlatformThornDefinition.new()
		for key: String in ["surface_id","platform_index","start_offset","length","depth"]:
			if raw.has(key):value.set(key,raw[key])
		var face: Variant=raw.get("face","top")
		value.face=["top","left","right","bottom"].find(face) if face is String else int(face)
		def.surface_thorns.append(value)
	def.entry_port=PlatformingModulePort.new();def.entry_port.port_id=&"entry";def.entry_port.position=point(case.get("entry_port",case.get("spawn",[60,482])))
	def.exit_port=PlatformingModulePort.new();def.exit_port.port_id=&"exit";def.exit_port.position=point(case.get("exit_port",[goal_v3.get_center().x,goal_v3.get_center().y]))
	def.anchors.append(def.entry_port.position);def.anchors.append(def.exit_port.position)
	return def

func validate_plan(raw: Variant) -> String:
	if not raw is Array:return "control_plan_must_be_array"
	var copy: Array=raw.duplicate(true)
	for item: Variant in copy:
		if not item is Dictionary:continue
		var trigger: Variant=item.get("trigger",{})
		if not trigger is Dictionary or not trigger.has("dynamic"):continue
		var query: Variant=trigger.dynamic
		if not query is Dictionary:return "dynamic_must_be_dictionary"
		if query.get("kind","") not in ["platform_phase","saw_phase","on_platform","actor_x"]:return "unsupported_dynamic_condition"
		if query.kind in ["platform_phase","saw_phase"]:
			if not query.get("window") is Array or query.window.size()!=2:return "invalid_phase_window"
			for value: Variant in query.window:
				if not (value is float or value is int) or not is_finite(float(value)) or value<0 or value>1:return "invalid_phase_window"
		if query.kind=="actor_x" and (not query.get("value") is float and not query.get("value") is int):return "invalid_crossing_value"
		trigger.erase("dynamic")
	return super.validate_plan(copy)

func condition_met(state: String) -> bool:
	var base:=true if state=="__dynamic__" else super.condition_met(state)
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	return base and (not trigger.has("dynamic") or context.phase_condition(trigger.dynamic))

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
	motor=PLAYER.instantiate() as PlayerMotor;motor.get_node("CourierVisual").use_plains_v3=false;motor.get_node("PlayerFeedback").free()
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

func prepare_dynamic_frame() -> void:
	context.frame=-warmup_left if warmup_left>0 else current_frame
	accepted.clear();frame_actions=[]
	if warmup_left>0:set_axis(0.)
	else:
		if axes_v3.has(current_frame):set_axis(axes_v3[current_frame])
		if not plan.is_empty():frame_actions=control_plan(current_frame)
		else:
			for action: Dictionary in actions_v3.get(current_frame,[]):
				controller.router.request_action(StringName(action.type),point(action.get("direction",[0,0])));frame_actions.append(action)
	before_grounded=motor.is_on_floor();before_state=controller.traversal.state;before_used_jumps=controller.jump_ability.used_jumps

func capture_dynamic_frame() -> void:
	var contacts: Array=context.contacts_now()
	if not contacts.is_empty():
		safe_v3=false;context.contact_history.append({"frame":context.frame,"contacts":contacts})
	if not context.damage.is_empty():safe_v3=false
	if warmup_left>0:warmup_left-=1;return
	if captured.is_empty():initial_clock_v3=context.module.clock
	var position:=motor.global_position
	if absf(position.x)>30000 or absf(position.y)>10000:safe_v3=false
	goal_min_v3=minf(goal_min_v3,position.distance_to(goal_v3.get_center()))
	var at_goal:=goal_v3.has_point(position) and motor.is_on_floor()
	reached_v3=reached_v3 or at_goal
	stable_v3=stable_v3+1 if at_goal and motor.get_real_velocity().length()<=1 else 0
	var value:=snapshot(current_frame,controller.router.axis,frame_actions)
	value.merge(context.snapshot());value.goal_stable_frames=stable_v3
	value.normal_velocity=[motor.normal_velocity.x,motor.normal_velocity.y]
	value.real_velocity=[motor.get_real_velocity().x,motor.get_real_velocity().y]
	captured.append(value);previous_v3=position;current_frame+=1

func run_case(case: Dictionary) -> Dictionary:
	var started:=Time.get_ticks_usec();current_case=case;setup_error=""
	goal_v3=rect(case.get("goal",[100000,0,100,100]))
	var validation: Dictionary=ADAPTER.validate(capabilities_for(case))
	if not validation.ok:return reject(case,"rejected_capabilities/"+str(validation.reason))
	var error:=validate_plan(case.get("control_plan",[]))
	if not error.is_empty():return reject(case,"rejected_control_plan/"+error)
	if int(case.get("max_frames",360))<1 or int(case.get("max_frames",360))>3600:return reject(case,"rejected_frame_budget")
	var budget: Variant=case.get("max_frames",360)
	if not (budget is int or budget is float) or not is_finite(float(budget)) or float(budget)!=floorf(float(budget)):return reject(case,"rejected_frame_budget")
	var warmup: Variant=case.get("warmup_frames",4)
	if not (warmup is int or warmup is float) or not is_finite(float(warmup)) or float(warmup)!=floorf(float(warmup)) or warmup<0 or warmup>120:return reject(case,"rejected_warmup_budget")
	if case.get("schedule_mode","normal_controller") not in ["normal_controller","priority_driver"]:return reject(case,"rejected_schedule_mode")
	for key: String in ["wall_platform_indices","one_way_platform_indices","one_way_indices"]:
		if case.has(key) and not ADAPTER.indices(case[key],case.get("platforms",[]).size()).ok:return reject(case,"rejected_"+key)
	var raw_noise: Variant=case.get("noise",{})
	if not raw_noise is Dictionary:return reject(case,"rejected_noise/not_dictionary")
	for key: String in ["seed","timing_frames","aim_degrees"]:
		if raw_noise.has(key) and (not (raw_noise[key] is int or raw_noise[key] is float) or not is_finite(float(raw_noise[key]))):return reject(case,"rejected_noise/nonfinite_number")
	if float(raw_noise.get("timing_frames",0))<0 or float(raw_noise.get("timing_frames",0))>30 or float(raw_noise.get("aim_degrees",0))<0 or float(raw_noise.get("aim_degrees",0))>45:return reject(case,"rejected_noise/out_of_range")
	for raw: Dictionary in case.get("thorns",[]):
		if float(raw.get("damage",1))<=0 or float(raw.get("contact_interval",.7))<=0:return reject(case,"rejected_thorn_damage")
	var def:=definition_for(case)
	if not def.is_valid():return reject(case,"rejected_module_definition")
	for trigger_command: Dictionary in case.get("control_plan",[]):
		var query: Dictionary=trigger_command.get("trigger",{}).get("dynamic",{})
		if query.is_empty():continue
		var found: bool=query.get("kind")=="actor_x"
		for platform: ModuleMovingPlatformDefinition in def.ferries:
			if query.get("kind") in ["platform_phase","on_platform"] and str(platform.platform_id)==str(query.get("id")):found=true
		for saw: ModuleSawDefinition in def.saws:
			if query.get("kind")=="saw_phase" and str(saw.source_id)==str(query.get("id")):found=true
		if not found:return reject(case,"rejected_dynamic_unknown_id")
	await make_fixture(case)
	noise=case.get("noise",{});plan=case.get("control_plan",[]).duplicate(true)
	for command: Dictionary in plan:
		var trigger: Dictionary=command.get("trigger",{})
		if trigger.has("dynamic") and not trigger.has("state"):trigger.state="__dynamic__"
	plan_index=0;previous_plan_frame=0;plan_error="";fired_commands=[];settling=false;settle_options={};settle_goal=goal_v3
	axes_v3.clear();actions_v3.clear();last_input_v3=0
	var axis_serial:=0
	for axis: Dictionary in case.get("axes",[]):
		var index:=maxi(0,int(axis.frame)+timing_error(axis.get("noise_key","axis/"+str(axis_serial))))
		axes_v3[index]=float(axis.value);last_input_v3=maxi(last_input_v3,index);axis_serial+=1
	var action_serial:=0
	for action: Dictionary in case.get("actions",[]):
		var key: Variant=action.get("noise_key",action_serial);action_serial+=1
		var index:=maxi(0,int(action.frame)+timing_error(key))
		action=action.duplicate(true);action.frame=index
		if action.type in ["shoot_release","grapple"]:
			var direction:=disturbed_direction(point(action.get("direction",[0,0])),key);action.direction=[direction.x,direction.y]
		if not actions_v3.has(index):actions_v3[index]=[]
		actions_v3[index].append(action);last_input_v3=maxi(last_input_v3,index)
	current_frame=0;warmup_left=int(case.get("warmup_frames",4));captured=[];stable_v3=0;reached_v3=false;safe_v3=true;goal_min_v3=INF
	context.running=true;world.process_mode=Node.PROCESS_MODE_PAUSABLE
	while current_frame<int(case.get("max_frames",360)):
		await context.tick_finished
		if not setup_error.is_empty() or not plan_error.is_empty() or not safe_v3 or context.fatal:break
		var complete:=(not plan.is_empty() and plan_index==plan.size()) or (plan.is_empty() and current_frame>last_input_v3)
		if stable_v3>=maxi(6,int(case.get("settle_frames",6))) and complete and not case.get("trace_all",false):break
	context.freeze();world.process_mode=Node.PROCESS_MODE_DISABLED
	var complete:=(not plan.is_empty() and plan_index==plan.size()) or (plan.is_empty() and current_frame>last_input_v3)
	var settled:=stable_v3>=maxi(6,int(case.get("settle_frames",6)))
	var ok: bool=safe_v3 and settled and complete and plan_error.is_empty() and setup_error.is_empty() and not context.fatal
	var reason:="settled_goal" if ok else "frame_budget"
	if not safe_v3:reason="real_damage" if not context.damage.is_empty() else ("hazard_contact" if not context.contact_history.is_empty() else "out_of_bounds")
	if context.fatal:reason="player_fatal"
	if not plan_error.is_empty():reason=plan_error
	if not setup_error.is_empty():reason=setup_error
	return {"id":case.get("id",""),"ok":ok,"safe":safe_v3,"reason":reason,"settled_goal":settled,"goal_reached":reached_v3,"goal_stable_frames":stable_v3,"ticks":current_frame,"elapsed_ms":(Time.get_ticks_usec()-started)/1000.,"minimum_goal_distance":goal_min_v3,"initial_position":[initial_v3.x,initial_v3.y],"plan_completed":complete,"plan_error":plan_error,"fired_commands":fired_commands,"capability_snapshot":capability_snapshot,"shots":counters.shots,"jumps":counters.jumps,"grapples":counters.grapples,"wall_jumps":wall_jumps,"air_jumps":air_jumps,"anchor_jumps":anchor_jumps,"hook_contacts":hook_contacts,"hazard_contacts":context.contact_history,"contact_frames":context.contact_history.size(),"damage_submissions":context.policy.records,"damage_commits":context.damage,"returns":context.returns,"dead":context.fatal,"hp":controller.actor_resources.health.current,"frames":captured,"module_definition_valid":true,"entry_port":[def.entry_port.position.x,def.entry_port.position.y],"exit_port":[def.exit_port.position.x,def.exit_port.position.y],"frame0_module_clock":initial_clock_v3,"schedule_mode":case.get("schedule_mode","normal_controller"),"warmup_frames":int(case.get("warmup_frames",4))}

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
	await process_frame
	DirAccess.make_dir_recursive_absolute(output_path.get_base_dir())
	var file:=FileAccess.open(output_path,FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"disordered-clock/physics-batch/v3","engine":Engine.get_version_info().string,"source_commit":"12f6cb006d7119598e3235f4ca4f7323e4c9d092","physics_hz":60,"scheduling":"module -200, moving -100, input -10, original controller 0, hazard 900, policy 1000, observer 1100","results":results}));file.close()
	print("PCG_BATCH_V3_COMPLETE ",results.size());quit(0)
