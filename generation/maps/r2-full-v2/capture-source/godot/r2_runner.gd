extends "res://runner_plains.gd"
## Long-map consumer. Original short-module runner and its limits stay unchanged.
const R2_PILOT = preload("r2_pilot.gd")
var pilot
var extra
var cell_event_cursor := 0
var player_damage_cursor := 0
var map_bounds := Rect2()
var body_size := Vector2.ZERO

func make_extra(case: Dictionary):
	if case.has("extra_script"):
		var path := str(case.extra_script)
		if not FileAccess.file_exists(path):
			setup_error = "missing_map_extra_script"; return null
		var script: Script = load(path)
		if script == null:
			setup_error = "invalid_map_extra_script"; return null
		return script.new()
	return null

func valid_support_indices(value: Variant) -> bool:
	return ADAPTER.indices(value, current_case.get("platforms", []).size()).ok

func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	var collision := motor.get_node("CollisionShape2D") as CollisionShape2D
	if not collision.shape is RectangleShape2D:
		setup_error = "unsupported_actor_shape"; return
	body_size = (collision.shape as RectangleShape2D).size
	extra = make_extra(case)
	if extra != null:
		var status: Variant = extra.setup(case, world, controller, context)
		if status is Dictionary and not status.get("ok", true): setup_error = str(status.get("reason", "extra_setup_failed"))
	elif case.get("extra_required", false): setup_error = "map_extra_required_but_missing"

func touches_supports(indices: Array) -> bool:
	for contact_index: int in motor.get_slide_collision_count():
		var contact := motor.get_slide_collision(contact_index)
		if contact.get_normal().dot(Vector2.UP) < .7: continue
		for index: Variant in indices:
			if contact.get_collider() == context.module.get_node_or_null("Platform" + str(int(index))): return true
	return false

func on_one_way_support() -> bool:
	for contact_index: int in motor.get_slide_collision_count():
		var contact := motor.get_slide_collision(contact_index)
		var collider: Object = contact.get_collider()
		if contact.get_normal().dot(Vector2.UP) >= .7 and collider is Node and collider.is_in_group(&"one_way_platform"): return true
	return false

func feet_on_supports(indices: Array) -> Dictionary:
	var feet := motor.global_position + Vector2(0.0, body_size.y * .5)
	var witnesses: Array = []
	var module: PlatformingModule = context.module
	for offset: float in [-body_size.x * .5 + 1.0, 0.0, body_size.x * .5 - 1.0]:
		var ray := PhysicsRayQueryParameters2D.create(feet + Vector2(offset, -.5), feet + Vector2(offset, 8.0), motor.collision_mask, [motor.get_rid()])
		var hit := motor.get_world_2d().direct_space_state.intersect_ray(ray)
		if hit.is_empty(): return {"ok": false, "reason": "missing_floor_under_body", "rays": witnesses}
		var normal: Vector2 = hit.normal
		var accepted_support := false
		var found_index := -1
		for index: Variant in indices:
			if hit.collider == module.get_node_or_null("Platform" + str(int(index))):
				accepted_support = true; found_index = int(index); break
		witnesses.append({"offset": offset, "point": [hit.position.x, hit.position.y],
			"normal": [normal.x, normal.y], "support_index": found_index})
		if not accepted_support or normal.dot(Vector2.UP) < .7:
			return {"ok": false, "reason": "unexpected_floor_under_body", "rays": witnesses}
	return {"ok": true, "rays": witnesses}

func state_for_pilot(frame: int) -> Dictionary:
	return {"frame": frame, "position": [motor.global_position.x, motor.global_position.y],
		"grounded": motor.is_on_floor(), "velocity": [motor.velocity.x, motor.velocity.y],
		"normal_velocity": [motor.normal_velocity.x, motor.normal_velocity.y],
		"real_velocity": [motor.get_real_velocity().x, motor.get_real_velocity().y],
		"air_shots": controller.action_resources.shot_charges,
		"jumps_used": controller.jump_ability.used_jumps,
		"stamina": controller.actor_resources.stamina.current,
		"health": controller.actor_resources.health.current,
		"shot_cooldown": controller.shoot_ability.cooldown_remaining,
		"traversal_state": str(controller.traversal.state), "dynamic": context.snapshot()}

func extra_before_leg(leg: Dictionary, state: Dictionary) -> Dictionary:
	if extra != null and extra.has_method("before_leg"):
		var result: Variant = extra.before_leg(leg, state)
		return result if result is Dictionary else {"ok": false, "reason": "invalid_extra_leg_admission"}
	return {"ok": true}

func prepare_dynamic_frame() -> void:
	context.frame = -warmup_left if warmup_left > 0 else current_frame
	accepted.clear(); frame_actions = []
	if warmup_left > 0:
		controller.router.set_move_axis(0.0)
	else:
		if entry_capture.is_empty():
			entry_capture = state_for_pilot(-1)
			entry_capture["sampling_point"] = "before_first_router_input_after_dynamic_update"
		frame_actions = pilot.tick(current_frame)
	before_grounded = motor.is_on_floor(); before_state = controller.traversal.state; before_used_jumps = controller.jump_ability.used_jumps

func cell_state() -> Dictionary:
	var bells: Array = []
	var actors: Array = []
	for latch: ShotLatch in cells.latches:
		bells.append({"id": latch.link_id, "open": latch.is_open, "open_count": latch.open_count, "sequence_step": latch.sequence_step})
	for actor: EnemyActor in cells.enemies:
		actors.append({"id": str(actor.definition.stable_id), "x": actor.motor.position.x,
			"y": actor.motor.position.y, "hp": actor.health.current, "dead": actor.health.terminal,
			"state": str(actor.attack_behavior.state) if actor.attack_behavior != null else "patrol"})
	return {"bells": bells, "enemies": actors}

func capture_dynamic_frame() -> void:
	var contacts: Array = context.contacts_now()
	if not contacts.is_empty():
		safe_v3 = false; context.contact_history.append({"frame": context.frame, "contacts": contacts})
	if cells != null and not cells.player_damage.is_empty(): safe_v3 = false
	if warmup_left > 0: warmup_left -= 1; return
	if captured.is_empty(): initial_clock_v3 = context.module.clock
	var position := motor.global_position
	if not map_bounds.has_point(position): safe_v3 = false; setup_error = "outside_declared_map_bounds"
	goal_min_v3 = minf(goal_min_v3, position.distance_to(goal_v3.get_center()))
	var at_goal := goal_v3.has_point(position) and motor.is_on_floor()
	reached_v3 = reached_v3 or at_goal
	stable_v3 = stable_v3 + 1 if at_goal and motor.get_real_velocity().length() <= 1.0 else 0
	var value := snapshot(current_frame, controller.router.axis, frame_actions)
	value.merge(context.snapshot())
	value["goal_stable_frames"] = stable_v3
	value["normal_velocity"] = [motor.normal_velocity.x, motor.normal_velocity.y]
	value["real_velocity"] = [motor.get_real_velocity().x, motor.get_real_velocity().y]
	value["plains"] = cell_state()
	value["plains_events_delta"] = cells.events.slice(cell_event_cursor).duplicate(true)
	value["player_damage_delta"] = cells.player_damage.slice(player_damage_cursor).duplicate(true)
	value["pilot"] = pilot.compact()
	cell_event_cursor = cells.events.size(); player_damage_cursor = cells.player_damage.size()
	if extra != null and extra.has_method("capture"):
		var result: Variant = extra.capture(current_frame, value)
		if result is Dictionary: value["extra_delta"] = result
	pilot.observe(current_frame)
	value["pilot"] = pilot.compact()
	captured.append(value); previous_v3 = position; current_frame += 1

func run_case(case: Dictionary) -> Dictionary:
	var started_at := Time.get_ticks_usec()
	current_case = case; setup_error = ""; entry_capture = {}; extra = null; pilot = null
	if case.get("capabilities", []) != ["move", "jump", "shot_recoil"]: return reject(case, "r2_requires_exact_basic_plains_capabilities")
	var raw_budget: Variant = case.get("map_budget_ticks", 18000)
	if not R2_PILOT.new().integer_range(raw_budget, 1, 36000): return reject(case, "invalid_long_map_budget")
	if not R2_PILOT.new().rectangle(case.get("world_bounds")): return reject(case, "explicit_finite_map_bounds_required")
	map_bounds = rect(case.world_bounds)
	if not case.get("goal") is Array or not R2_PILOT.new().rectangle(case.goal): return reject(case, "explicit_goal_required")
	goal_v3 = rect(case.goal)
	if case.get("platforms", []).size() > 4096: return reject(case, "map_platform_budget")
	for key: String in ["wall_platform_indices", "one_way_platform_indices", "one_way_indices"]:
		if case.has(key) and not ADAPTER.indices(case[key], case.get("platforms", []).size()).ok: return reject(case, "invalid_" + key)
	var warmup: Variant = case.get("warmup_frames", 4)
	if not R2_PILOT.new().integer_range(warmup, 0, 120): return reject(case, "invalid_warmup_budget")
	var raw_noise: Variant = case.get("noise", {})
	if not raw_noise is Dictionary: return reject(case, "invalid_noise")
	for key: String in ["seed", "timing_frames", "aim_degrees"]:
		if raw_noise.has(key) and (not (raw_noise[key] is int or raw_noise[key] is float) or not is_finite(float(raw_noise[key]))): return reject(case, "invalid_noise_number")
	if float(raw_noise.get("timing_frames", 0)) < 0 or float(raw_noise.get("timing_frames", 0)) > 30 or float(raw_noise.get("aim_degrees", 0)) < 0 or float(raw_noise.get("aim_degrees", 0)) > 45: return reject(case, "noise_out_of_range")
	var definition := definition_for(case)
	if not definition.is_valid(): return reject(case, "invalid_map_definition")
	await make_fixture(case)
	if not setup_error.is_empty(): return reject(case, setup_error)
	noise = raw_noise; noise_records = []
	plan = []; plan_index = 0; previous_plan_frame = 0; plan_error = ""; fired_commands = []
	settling = false; settle_options = {}; axes_v3.clear(); actions_v3.clear()
	current_frame = 0; warmup_left = int(warmup); captured = []; stable_v3 = 0; reached_v3 = false
	safe_v3 = true; goal_min_v3 = INF; cell_event_cursor = 0; player_damage_cursor = 0
	pilot = R2_PILOT.new()
	var configuration_error: String = pilot.configure(self, case)
	if not configuration_error.is_empty(): return reject(case, configuration_error)
	context.running = true; world.process_mode = Node.PROCESS_MODE_PAUSABLE
	while current_frame < int(raw_budget):
		await context.tick_finished
		if not setup_error.is_empty() or pilot.failed or not safe_v3 or context.fatal: break
		if pilot.completed and stable_v3 >= 6: break
	context.freeze(); world.process_mode = Node.PROCESS_MODE_DISABLED
	var extra_report: Dictionary = {"ok": true, "scope": "no extra mechanics requested"}
	if extra != null and extra.has_method("report"):
		var reported: Variant = extra.report()
		extra_report = reported if reported is Dictionary else {"ok": false, "reason": "invalid_extra_report"}
	var ok: bool = safe_v3 and pilot.completed and not pilot.failed and stable_v3 >= 6 and setup_error.is_empty() and not context.fatal and extra_report.get("ok", false)
	var reason := "r2_policy_complete" if ok else "map_frame_budget"
	if pilot.failed: reason = str(pilot.failure.reason)
	if not safe_v3: reason = "real_damage_or_hazard" if not context.contact_history.is_empty() or not cells.player_damage.is_empty() else "unsafe_map_state"
	if context.fatal: reason = "player_fatal"
	if not setup_error.is_empty(): reason = setup_error
	if not extra_report.get("ok", false) and ok == false and pilot.completed: reason = "map_mechanics_incomplete"
	return {"id": case.get("id", ""), "schema": "map-notes/r2-concrete-policy/v1", "ok": ok,
		"safe": safe_v3, "reason": reason, "ticks": current_frame,
		"elapsed_ms": (Time.get_ticks_usec() - started_at) / 1000.0,
		"hp": controller.actor_resources.health.current, "shots": counters.shots, "jumps": counters.jumps,
		"grapples": counters.grapples, "air_jumps": air_jumps, "wall_jumps": wall_jumps,
		"goal_reached": reached_v3, "goal_stable_frames": stable_v3, "settled_goal": stable_v3 >= 6,
		"pilot": pilot.report(), "extra": extra_report, "frames": captured,
		"entry_snapshot": entry_capture, "capability_snapshot": capability_snapshot,
		"plains": cells.snapshot(), "hazard_contacts": context.contact_history,
		"damage_submissions": context.policy.records, "damage_commits": context.damage,
		"returns": context.returns, "dead": context.fatal, "map_budget_ticks": int(raw_budget),
		"scope": "one full concrete world / actual finite input policy; unvisited paths and arbitrary states unverified"}
