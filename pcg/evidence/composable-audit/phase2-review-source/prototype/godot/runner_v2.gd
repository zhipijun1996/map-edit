extends "res://runner.gd"
## Composable capability snapshots + state-triggered Router plans. Production core is unchanged.
const ADAPTER = preload("res://capability_adapter.gd")
const OPS := ["axis","jump","jump_release","shoot","grapple","wait","settle","drop_through"]
const STATES := ["airborne","grounded","hook_hang","wall_attach","free","descending","apex"]
var current_caps: Array=[]
var capability_snapshot: Dictionary={}
var plan: Array=[]
var plan_index:=0
var previous_plan_frame:=0
var plan_error:=""
var fired_commands: Array=[]
var settling:=false
var settle_goal:=Rect2()
var settle_options: Dictionary={}
var before_grounded:=false
var before_state: StringName=&"free"
var before_used_jumps:=0
var wall_jumps:=0
var hook_contacts:=0
var air_jumps:=0
var anchor_jumps:=0
var noise: Dictionary={}
var noise_records: Array=[]

func capabilities_for(case: Dictionary) -> Variant:
	if case.has("capabilities"):return case.capabilities
	var caps: Array=["move","jump","shot_recoil"]
	var profile: String=case.get("profile","base")
	if profile in ["grapple","all"]:caps.append("grapple")
	if profile in ["double_jump","all"]:caps.append("double_jump")
	if profile=="all":caps.append("wall_climb")
	if profile not in ["base","grapple","double_jump","all"]:return null
	return caps

func validate_plan(raw: Variant) -> String:
	if not raw is Array:return "control_plan_must_be_array"
	if raw.size()>128:return "control_plan_budget"
	for item: Variant in raw:
		if not item is Dictionary or item.get("op","") not in OPS:return "unsupported_control_op"
		if item.has("timing_noise") and (not item.timing_noise is bool or item.op!="axis"):return "invalid_axis_timing_noise_flag"
		var trigger: Variant=item.get("trigger",{})
		if not trigger is Dictionary:return "invalid_trigger"
		if trigger.has("state") and trigger.state not in STATES:return "unsupported_trigger_state"
		for key: String in ["after","min_after","timeout"]:
			if trigger.has(key) and (not (trigger[key] is float or trigger[key] is int) or trigger[key]<0 or trigger[key]>3600):return "invalid_trigger_time"
		for key: String in ["direction","aim_target"]:
			if item.has(key) and (not item[key] is Array or item[key].size()!=2 or not is_finite(float(item[key][0])) or not is_finite(float(item[key][1]))):return "invalid_control_vector"
	return ""

func make_fixture(case: Dictionary) -> void:
	setup_error=""
	var creation:=case.duplicate(true)
	creation.profile="base"
	await super.make_fixture(creation)
	current_caps=ADAPTER.validate(capabilities_for(case)).capabilities
	var applied: Dictionary=ADAPTER.apply(controller,current_caps)
	capability_snapshot=applied.get("snapshot",{})
	if not applied.ok:setup_error=str(applied.reason)
	var bodies: Array=[]
	for child: Node in world.get_children():
		if child is StaticBody2D:bodies.append(child)
	var wall_indices: Dictionary=ADAPTER.indices(case.get("wall_platform_indices",[]),bodies.size()).indices
	var one_way: Dictionary=ADAPTER.indices(case.get("one_way_platform_indices",case.get("one_way_indices",[])),bodies.size()).indices
	for i: int in bodies.size():
		var body: StaticBody2D=bodies[i]
		body.name="CellPlatform"+str(i)
		(body.get_child(0) as CollisionShape2D).name="CollisionShape2D"
		if wall_indices.has(i):body.add_to_group(&"wall_climbable")
		if one_way.has(i):
			body.add_to_group(&"one_way_platform")
			(body.get_child(0) as CollisionShape2D).one_way_collision=true
	wall_jumps=0;hook_contacts=0;air_jumps=0;anchor_jumps=0
	controller.jump_ability.jumped.connect(func():
		var kind:="ground_jump"
		if before_state==&"hook_hang":kind="anchor_jump";anchor_jumps+=1
		elif not before_grounded and before_used_jumps>=1:kind="air_jump";air_jumps+=1
		accepted.append({"type":kind,"used_jumps":controller.jump_ability.used_jumps}))
	controller.traversal.action_changed.connect(func(state: StringName):
		if state==&"wall_kick":
			wall_jumps+=1;counters.jumps+=1
			accepted.append({"type":"wall_jump","wall_ready":controller.traversal.wall_ready}))
	controller.traversal.hook_contact.connect(func(_p: Vector2):hook_contacts+=1)

func condition_met(state: String) -> bool:
	if state=="airborne":return not motor.is_on_floor()
	if state=="grounded":return motor.is_on_floor()
	if state=="descending":return not motor.is_on_floor() and motor.velocity.y>=0
	if state=="apex":return not motor.is_on_floor() and absf(motor.velocity.y)<=100
	return str(controller.traversal.state)==state

func noise_rng(key: Variant, channel: String) -> RandomNumberGenerator:
	var rng:=RandomNumberGenerator.new()
	rng.seed=int(noise.get("seed",0))+int((str(key)+"/"+channel).hash())
	return rng

func timing_error(key: Variant) -> int:
	var width:=maxi(0,int(noise.get("timing_frames",0)))
	return noise_rng(key,"timing").randi_range(-width,width) if width else 0

func aim_error(key: Variant) -> float:
	var width:=maxf(0,float(noise.get("aim_degrees",0)))
	return noise_rng(key,"aim").randf_range(-width,width) if width else 0.

func disturbed_direction(value: Vector2, key: Variant) -> Vector2:
	return value.rotated(deg_to_rad(aim_error(key)))

func set_axis(value: float) -> void:
	controller.router.set_move_axis(clampf(value,-1,1) if "move" in current_caps else 0.)

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

func snapshot(index: int, axis: float, actions: Array) -> Dictionary:
	var value:=super.snapshot(index,axis,actions)
	value.hook_used=controller.traversal.hook_used
	value.wall_ready=controller.traversal.wall_ready
	value.jump_maximum=controller.jump_ability.maximum_jumps()
	value.can_air_jump=controller.jump_ability.can_air_jump()
	value.shot_cooldown=controller.shoot_ability.cooldown_remaining
	value.plan_index=plan_index
	return value

func reject(case: Dictionary, reason: String) -> Dictionary:
	return {"id":case.get("id","unnamed"),"ok":false,"safe":false,"settled_goal":false,"goal_reached":false,"reason":reason,"frames":[],"ticks":0,"capabilities":capabilities_for(case),"rejected":true}

func run_case(case: Dictionary) -> Dictionary:
	var started:=Time.get_ticks_usec()
	var frame_budget: Variant=case.get("max_frames",360)
	if not (frame_budget is float or frame_budget is int) or not is_finite(float(frame_budget)) or float(frame_budget)!=floorf(float(frame_budget)) or frame_budget<1 or frame_budget>3600:return reject(case,"rejected_frame_budget")
	var platform_count: int=case.get("platforms",[]).size()
	for key: String in ["wall_platform_indices","one_way_platform_indices","one_way_indices"]:
		if case.has(key):
			var index_check: Dictionary=ADAPTER.indices(case[key],platform_count)
			if not index_check.ok:return reject(case,"rejected_"+key+"/"+str(index_check.reason))
	var validation: Dictionary=ADAPTER.validate(capabilities_for(case))
	if not validation.ok:return reject(case,"rejected_capabilities/"+str(validation.reason))
	var raw_noise: Variant=case.get("noise",{})
	if not raw_noise is Dictionary:return reject(case,"rejected_noise/not_dictionary")
	for key: String in ["seed","timing_frames","aim_degrees"]:
		if raw_noise.has(key) and (not (raw_noise[key] is int or raw_noise[key] is float) or not is_finite(float(raw_noise[key]))):return reject(case,"rejected_noise/nonfinite_number")
	if float(raw_noise.get("timing_frames",0))<0 or float(raw_noise.get("timing_frames",0))>30 or float(raw_noise.get("aim_degrees",0))<0 or float(raw_noise.get("aim_degrees",0))>45:return reject(case,"rejected_noise/out_of_range")
	var validation_error:=validate_plan(case.get("control_plan",[]))
	if not validation_error.is_empty():return reject(case,"rejected_control_plan/"+validation_error)
	await make_fixture(case)
	noise=case.get("noise",{});noise_records=[]
	plan=case.get("control_plan",[]);plan_index=0;previous_plan_frame=0;plan_error="";fired_commands=[];settling=false;settle_options={}
	var actions_by_frame: Dictionary={};var axes_by_frame: Dictionary={}
	var action_i:=0;var axis_i:=0;var last_input_frame:=0
	for raw: Dictionary in case.get("actions",[]):
		var a:=raw.duplicate(true)
		var key: Variant=a.get("noise_key",action_i);action_i+=1
		var frame:=maxi(0,int(a.frame)+timing_error(key));a.frame=frame
		if a.type in ["shoot_release","grapple"]:
			var direction:=disturbed_direction(point(a.get("direction",[0,0])),key)
			a.direction=[direction.x,direction.y]
		noise_records.append({"kind":"action","noise_key":key,"frame":frame,"timing_error":timing_error(key),"aim_error_degrees":aim_error(key) if a.type in ["shoot_release","grapple"] else 0.})
		if not actions_by_frame.has(frame):actions_by_frame[frame]=[]
		actions_by_frame[frame].append(a);last_input_frame=maxi(last_input_frame,frame)
	for a: Dictionary in case.get("axes",[]):
		var key: Variant=a.get("noise_key","axis/"+str(axis_i));axis_i+=1
		var frame:=maxi(0,int(a.frame)+timing_error(key))
		axes_by_frame[frame]=float(a.value);last_input_frame=maxi(last_input_frame,frame)
	var goal:=rect(case.get("goal",[100000,0,100,100]));settle_goal=goal
	var safe:=true;var reached:=false;var settled:=false;var stable_frames:=0;var max_stable_frames:=0
	var reason:="frame_budget";var failure_frame:=-1;var min_distance:=INF
	var initial:=motor.position;var previous:=initial;var frames: Array=[]
	for frame: int in int(case.get("max_frames",360)):
		await physics_frame
		accepted.clear()
		if axes_by_frame.has(frame):set_axis(float(axes_by_frame[frame]))
		var actions: Array=[]
		if not plan.is_empty():actions=control_plan(frame)
		else:
			for a: Dictionary in actions_by_frame.get(frame,[]):
				controller.router.request_action(StringName(a.type),point(a.get("direction",[0,0])))
				actions.append(a)
		before_grounded=motor.is_on_floor();before_state=controller.traversal.state;before_used_jumps=controller.jump_ability.used_jumps
		controller.physics_tick(DT)
		var pos:=motor.global_position
		var sweep:=Rect2(pos-Vector2(12,18),Vector2(24,36)).merge(Rect2(previous-Vector2(12,18),Vector2(24,36)))
		for danger: Rect2 in dangers:
			if sweep.intersects(danger,true):
				if safe:failure_frame=frame;reason="hazard_contact"
				safe=false
		if absf(pos.x)>30000 or absf(pos.y)>10000:
			safe=false;reason="out_of_bounds";failure_frame=frame
		min_distance=minf(min_distance,pos.distance_to(goal.get_center()))
		var at_goal:=goal.has_point(pos) and motor.is_on_floor()
		reached=reached or at_goal
		var still:=at_goal and absf(motor.velocity.x)<=1 and absf(motor.velocity.y)<=1
		stable_frames=stable_frames+1 if still else 0
		max_stable_frames=maxi(max_stable_frames,stable_frames)
		settled=stable_frames>=maxi(6,int(case.get("settle_frames",6)))
		var snap:=snapshot(frame,controller.router.axis,actions);snap.goal_stable_frames=stable_frames
		frames.append(snap);previous=pos
		if not plan_error.is_empty():reason=plan_error
		elif settled and safe:reason="settled_goal"
		if demo:
			draw_node.queue_redraw();await process_frame
		if not case.get("trace_all",false) and (not safe or not plan_error.is_empty() or (settled and ((plan.is_empty() and frame>=last_input_frame) or (not plan.is_empty() and plan_index==plan.size())))):break
	var complete:=(not plan.is_empty() and plan_index==plan.size()) or (plan.is_empty() and frames.size()>last_input_frame)
	if safe and plan_error.is_empty() and not complete:reason="incomplete_plan_or_inputs"
	var result:={"id":case.get("id","unnamed"),"ok":safe and settled and complete and plan_error.is_empty() and setup_error.is_empty(),"safe":safe,"goal_reached":reached,"settled_goal":settled,"goal_stable_frames":stable_frames,"maximum_goal_stable_frames":max_stable_frames,"reason":reason,"failure_frame":failure_frame,"minimum_goal_distance":min_distance,"ticks":frames.size(),"elapsed_ms":(Time.get_ticks_usec()-started)/1000.,"initial_position":[initial.x,initial.y],"capability_snapshot":capability_snapshot,"plan_completed":complete,"plan_error":plan_error,"fired_commands":fired_commands,"noise":noise,"noise_model":"sequential_trigger_threshold" if not plan.is_empty() else "absolute_action_time","noise_records":noise_records,"shots":counters.shots,"jumps":counters.jumps,"grapples":counters.grapples,"wall_jumps":wall_jumps,"hook_contacts":hook_contacts,"air_jumps":air_jumps,"anchor_jumps":anchor_jumps,"frames":frames}
	if not setup_error.is_empty():result.error=setup_error
	return result

func _run() -> void:
	var input_path:="";var output_path:=""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--input="):input_path=arg.trim_prefix("--input=")
		if arg.begins_with("--output="):output_path=arg.trim_prefix("--output=")
		if arg=="--demo":demo=true
	if input_path.is_empty() or output_path.is_empty():push_error("Require --input= and --output=");quit(2);return
	var data: Variant=JSON.parse_string(FileAccess.get_file_as_string(input_path))
	if not data is Dictionary or not data.get("cases") is Array or data.cases.is_empty():push_error("Invalid batch JSON");quit(2);return
	var results: Array=[];var started:=Time.get_ticks_usec()
	for case: Dictionary in data.cases:
		results.append(await run_case(case));print("CASE_V2 ",case.get("id","")," ",results[-1].reason)
	if is_instance_valid(world):controller.shoot_ability.clear_projectiles();world.free()
	await process_frame
	DirAccess.make_dir_recursive_absolute(output_path.get_base_dir())
	var file:=FileAccess.open(output_path,FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"disordered-clock/physics-batch/v2","engine":Engine.get_version_info().string,"source_commit":"12f6cb006d7119598e3235f4ca4f7323e4c9d092","physics_hz":60,"elapsed_ms":(Time.get_ticks_usec()-started)/1000.,"results":results}));file.close()
	print("PCG_BATCH_V2_COMPLETE ",results.size());quit(0)
