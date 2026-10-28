extends "/workspace/map-edit-task-a/pcg/prototype/creative_batches/batch30_cell/runner_v3.gd"
const REVIEW_AIR=preload("air_enemy_binding_v1.gd")
const GEARS=preload("retractable_gears_v1.gd")
const AIR_DEFINITION=preload("air_port_definition_v1.gd")
var gear_groups: Array=[]
var air_exit_streak:=0

func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	var original:=super.definition_for(data)
	if data.get("air_port_contracts",[]).is_empty():return original
	var result=AIR_DEFINITION.new()
	for property: Dictionary in original.get_property_list():
		if int(property.usage)&PROPERTY_USAGE_STORAGE and property.name!="script":result.set(property.name,original.get(property.name))
	for port: Dictionary in data.air_port_contracts:
		if port.surface!="AIR" or not ((port.face=="TOP" and port.permission=="INPUT") or (port.face=="BOTTOM" and port.permission=="OUTPUT")):
			setup_error="invalid_air_port_contract";continue
		result.air_points.append(Vector2(port.stagingPosition[0],port.stagingPosition[1]))
	if data.has("migration_probe") and data.has("air_goal_probe"):
		for raw: Array in data.get("air_probe_points",[]):
			var boundary: Array=data.air_goal_probe.boundary
			if absf(float(raw[0])-float(boundary[0]))<=2 and absf(float(raw[1])-float(boundary[1]))<=48:result.air_points.append(Vector2(raw[0],raw[1]))
	return result

func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Variant in copy:
			if command is Dictionary and command.get("trigger",{}).get("state","") in ["shot_ready","grounded_shot_ready","observed_height","carrier_x_gte"]:command.trigger.state="grounded"
			if command is Dictionary and command.get("trigger",{}).get("dynamic",{}).get("kind","")=="actor_y":command.trigger.dynamic.kind="actor_x"
	return super.validate_plan(copy)

func condition_met(state: String) -> bool:
	if state=="carrier_x_gte":
		var command: Dictionary=plan[plan_index]
		for platform: ModuleMovingPlatform in context.module.moving_platforms:
			if str(platform.definition.platform_id)==str(command.carrier_id):return platform.position.x>=float(command.carrier_value)
		return false
	if state=="observed_height":
		var query: Dictionary=plan[plan_index].observed_y
		return motor.position.y<=float(query.value) if query.get("direction")=="lte" else motor.position.y>=float(query.value)
	var dynamic: Dictionary=plan[plan_index].get("trigger",{}).get("dynamic",{})
	if state=="__dynamic__" and dynamic.get("kind","")=="actor_y":return motor.position.y<=float(dynamic.value) if dynamic.get("direction")=="lte" else motor.position.y>=float(dynamic.value)
	if state=="shot_ready":return controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
	if state=="grounded_shot_ready":
		var ready:=motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=0.000001
		var query: Dictionary=plan[plan_index].get("trigger",{}).get("dynamic",{})
		return ready and (query.is_empty() or context.phase_condition(query))
	return super.condition_met(state)

func enemy_alive(identifier: String) -> bool:
	for i: int in cells.enemies.size():
		var actor: EnemyActor=cells.enemies[i]
		if str(current_case.get("enemies",[])[i].id)==identifier:return is_instance_valid(actor) and not actor.health.terminal
	return false

func carrier_running(identifier: String) -> bool:
	for platform: ModuleMovingPlatform in context.module.moving_platforms:
		if str(platform.definition.platform_id)==identifier:return platform.motion_running
	return false

func control_plan(frame: int) -> Array:
	# Conditional control belongs to the driver; only real world observations
	# may skip an unnecessary shot. No enemy or resource state is modified.
	while plan_index<plan.size() and plan[plan_index].has("skip_if_enemy_dead") and not enemy_alive(str(plan[plan_index].skip_if_enemy_dead)):
		plan_index+=1
	while plan_index<plan.size() and plan[plan_index].has("skip_if_carrier_running") and carrier_running(str(plan[plan_index].skip_if_carrier_running)):
		plan_index+=1
	var before:=fired_commands.size()
	var requested: Array=super.control_plan(frame)
	var cancel_auto:=false;var manual_axis:=0.0
	for event: Dictionary in fired_commands.slice(before):
		var command: Dictionary=plan[int(event.index)]
		if command.op=="settle":cancel_auto=false
		elif command.op=="axis" and (cancel_auto or command.get("cancel_settle",false)):
			cancel_auto=true;manual_axis=float(command.value)
	if cancel_auto:settling=false;controller.router.set_move_axis(manual_axis)
	return requested

func _cell_aim(query: Dictionary, fallback: Vector2) -> Vector2:
	if query.get("kind","")=="bell" and query.has("target_offset"):
		for latch: ShotLatch in cells.latches:
			if str(latch.link_id)!=str(query.id):continue
			var target:=latch.to_global(latch.bell_position)+Vector2(query.target_offset[0],query.target_offset[1])
			var aim:=(target-motor.global_position).normalized()
			var visual: CourierVisual=motor.get_node("CourierVisual")
			for _iteration: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
			return aim
	if query.get("kind","")!="enemy" or not query.has("target_offset"):return super._cell_aim(query,fallback)
	for i: int in cells.enemies.size():
		var actor: EnemyActor=cells.enemies[i]
		if str(current_case.get("enemies",[])[i].id)!=str(query.id) or not is_instance_valid(actor) or actor.health.terminal:continue
		var target:=actor.motor.global_position+Vector2(query.target_offset[0],query.target_offset[1])
		var aim:=(target-motor.global_position).normalized()
		var visual: CourierVisual=motor.get_node("CourierVisual")
		for _iteration: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
		return aim
	return fallback

func make_fixture(data: Dictionary) -> void:
	gear_groups=[];air_exit_streak=0
	var ordinary:=REVIEW_AIR.ordinary(data)
	ordinary.latches=ordinary.get("latches",[]).filter(func(l):return l.get("kind","")!="retractable_gears/v1")
	for latch: Dictionary in ordinary.latches:
		if latch.get("return_access_side_policy","")=="any":latch.erase("return_access")
	await super.make_fixture(ordinary)
	if data.has("air_goal_probe"):context.anchor_ready=true
	# Preserve the existing C09 stable support names used by N08's observer.
	for latch in pair_runtime.pairs:
		latch.gate_body.name="PairGateA_"+str(latch.link_id)
		latch.paired_gate_body.name="PairGateB_"+str(latch.link_id)
	REVIEW_AIR.install(data,world,controller,context,cells)
	for spec: Dictionary in data.get("latches",[]):
		if spec.get("return_access_side_policy","")!="any":continue
		for latch: ShotLatch in cells.latches:
			if str(latch.link_id)==str(spec.id):latch.add_access_bell(Vector2(spec.return_access[0],spec.return_access[1]),false,false)
	for port: Dictionary in data.get("air_port_contracts",[]):
		if port.id==data.get("route_spec",{}).get("from_port","") and port.permission=="INPUT":
			# AIR ingress is not a grounded recovery anchor. The original
			# damage policy remains active; no unsafe anchor is activated.
			context.anchor_ready=true
	for spec: Dictionary in data.get("retractable_groups",[]):
		var group=GEARS.new();group.configure(spec,world,controller,context)
		group.opened.connect(cells._bell_open.bind(group,str(spec.id)))
		cells.latches.append(group);gear_groups.append(group)

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].workshop.retractable_groups=gear_groups.map(func(g):return g.snapshot_gears())
	if active:
		if current_case.has("air_goal_probe"):
			var probe: Dictionary=current_case.air_goal_probe
			var x:=float(probe.boundary[0]);var y:=float(probe.boundary[1])
			var crossed:=motor.position.y-18>=y and motor.position.y<=y+128 and absf(motor.position.x-x)+12<=32 and motor.velocity.y>0
			air_exit_streak=air_exit_streak+1 if crossed else 0
			stable_v3=air_exit_streak;reached_v3=reached_v3 or crossed
			captured[-1].air_exit_complete_frames=air_exit_streak
			return
		for port: Dictionary in current_case.get("air_port_contracts",[]):
			if port.id!=current_case.get("route_spec",{}).get("to_port","") or port.permission!="OUTPUT":continue
			var x:=float(port.position[0]);var y:=float(port.position[1])
			var crossed:=motor.position.y-18>=y and motor.position.y<=y+128 and absf(motor.position.x-x)+12<=32 and motor.velocity.y>0
			air_exit_streak=air_exit_streak+1 if crossed else 0
			stable_v3=air_exit_streak;reached_v3=reached_v3 or crossed
			captured[-1].air_exit_complete_frames=air_exit_streak

func run_case(data: Dictionary) -> Dictionary:
	var executable:=data.duplicate(true)
	for command: Dictionary in executable.get("control_plan",[]):
		if command.get("trigger",{}).get("dynamic",{}).get("kind","")=="actor_y":
			command.observed_y=command.trigger.dynamic.duplicate(true);command.trigger.erase("dynamic");command.trigger.state="observed_height"
	var result: Dictionary=await super.run_case(executable)
	if not result.get("rejected",false):result.workshop.retractable_groups=gear_groups.map(func(g):return g.snapshot_gears())
	if air_exit_streak>0:
		result.air_exit_complete_frames=air_exit_streak;result.goal_stable_frames=0
		result.exit_contract="downward_air_full_body_crossing; not grounded stability"
	return result
