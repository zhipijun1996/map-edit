extends RefCounted
## Input-only long-map pilot. The original Controller/Motor own every motion.
var host
var program: Array = []
var index := 0
var leg_start_frame := -1
var stable := 0
var started := false
var airborne_seen := false
var jump_released := false
var initial_position := Vector2.ZERO
var failed := false
var completed := false
var failure: Dictionary = {}
var legs: Array = []
var current_log: Dictionary = {}
var module_command_cursor := 0
var input_leg_id := ""
var queued_requests: Array = []
var drop_attempts := 0
var last_drop_frame := -100000

func configure(owner, data: Dictionary) -> String:
	host = owner
	var raw: Variant = data.get("pilot_program", [])
	if not raw is Array or raw.is_empty() or raw.size() > 2048: return "invalid_pilot_program"
	program = raw.duplicate(true)
	var ids: Dictionary = {}
	for value: Variant in program:
		if not value is Dictionary: return "pilot_leg_must_be_dictionary"
		var leg: Dictionary = value
		var id := str(leg.get("id", ""))
		if id.is_empty() or ids.has(id): return "invalid_or_duplicate_leg_id"
		ids[id] = true
		if str(leg.get("kind", "")) not in ["walk", "jump", "drop", "module"]: return "unsupported_pilot_leg_kind"
		var budget: Variant = leg.get("budget_ticks", 360)
		if not integer_range(budget, 1, 3600 if leg.kind == "module" else 360): return "invalid_leg_budget"
		if not leg.get("target") is Dictionary: return "missing_leg_target"
		var target: Dictionary = leg.target
		if not vector(target.get("position")) or not rectangle(target.get("region")): return "invalid_target_geometry"
		if target.get("grounded", true) != true: return "this_pilot_requires_grounded_arrival"
		if not integer_range(target.get("stable_ticks", 3), 1, 120): return "invalid_arrival_stability"
		var supports: Variant = target.get("support_indices", [])
		if not supports is Array or supports.is_empty(): return "target_support_indices_required"
		if not host.valid_support_indices(supports): return "invalid_target_support_indices"
		if leg.has("hold_ticks") and not integer_range(leg.hold_ticks, 1, 120): return "invalid_jump_hold_ticks"
		if leg.has("maximum_drop_attempts") and not integer_range(leg.maximum_drop_attempts, 1, 16): return "invalid_drop_attempt_budget"
		if leg.get("kind") == "module":
			var error: String = host.validate_plan(leg.get("control_plan", []))
			if not error.is_empty(): return "module_" + error
			for command: Dictionary in leg.get("control_plan", []):
				if command.has("aim_cell"):
					var query: Dictionary = command.aim_cell
					var candidates: Array = data.get("latches", []) if query.get("kind") == "bell" else data.get("enemies", []) if query.get("kind") == "enemy" else []
					if not candidates.any(func(candidate: Dictionary) -> bool: return str(candidate.get("id", "")) == str(query.get("id", ""))): return "unknown_module_aim_cell"
				var dynamic: Dictionary = command.get("trigger", {}).get("dynamic", {})
				if dynamic.get("kind") in ["saw_phase", "platform_phase", "on_platform"]:
					var candidates: Array = data.get("saws", []) if dynamic.kind == "saw_phase" else data.get("moving_platforms", [])
					var field := "source_id" if dynamic.kind == "saw_phase" else "platform_id"
					if not candidates.any(func(candidate: Dictionary) -> bool: return str(candidate.get(field, "")) == str(dynamic.get("id", ""))): return "unknown_module_dynamic_cell"
	return ""

func integer_range(value: Variant, low: int, high: int) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floorf(float(value)) and value >= low and value <= high

func vector(value: Variant) -> bool:
	return value is Array and value.size() == 2 and (value[0] is int or value[0] is float) and (value[1] is int or value[1] is float) and is_finite(float(value[0])) and is_finite(float(value[1]))

func rectangle(value: Variant) -> bool:
	return value is Array and value.size() == 4 and vector(value.slice(0, 2)) and vector(value.slice(2, 4)) and value[2] > 0 and value[3] > 0

func active_leg() -> Dictionary:
	return program[index] if index < program.size() else {}

func _request(type: StringName, requested: Array) -> void:
	host.controller.router.request_action(type)
	requested.append({"type": str(type), "direction": [0, 0], "pilot_leg": str(active_leg().get("id", ""))})

func _axis_to(target_x: float) -> void:
	var distance: float = target_x - host.motor.global_position.x
	var frame_travel: float = host.motor.tuning.ground_speed / float(Engine.physics_ticks_per_second)
	# Existing formal drivers steer proportionally near the target. Derive the
	# transition band from the real tuning rather than duplicating movement speed.
	var axis := 0.0 if absf(distance) <= 1.0 else clampf(distance / maxf(1.0, frame_travel * 1.25), -1.0, 1.0)
	host.controller.router.set_move_axis(axis)

func _start(frame: int) -> void:
	var leg := active_leg()
	leg_start_frame = frame; stable = 0; started = true; airborne_seen = false; jump_released = false
	initial_position = host.motor.global_position
	drop_attempts = 0; last_drop_frame = -100000
	current_log = {"id": leg.id, "edge_id": leg.get("edge_id", "UNKNOWN"), "kind": leg.kind,
		"start": host.state_for_pilot(frame), "input_program": leg.get("control_plan", []).duplicate(true),
		"target": leg.target.duplicate(true), "commands": []}
	host.plan = []; host.plan_index = 0; host.previous_plan_frame = frame
	host.plan_error = ""; host.fired_commands = []; host.settling = false; host.settle_options = {}
	module_command_cursor = 0
	if leg.has("entry"):
		var entry: Dictionary = leg.entry
		if entry.get("grounded", false) and not host.motor.is_on_floor():
			stop("entry_not_grounded", frame); return
		if entry.has("region") and not host.rect(entry.region).has_point(host.motor.global_position):
			stop("entry_region_mismatch", frame); return
		if entry.has("support_indices") and not host.feet_on_supports(entry.support_indices).ok:
			stop("entry_support_mismatch", frame); return
		if host.controller.action_resources.shot_charges < int(entry.get("required_air_shots", 0)):
			stop("entry_air_shots_unavailable", frame); return
		if entry.has("maximum_shot_cooldown") and host.controller.shoot_ability.cooldown_remaining > float(entry.maximum_shot_cooldown):
			stop("entry_shot_cooldown_unsatisfied", frame); return
	var admission: Dictionary = host.extra_before_leg(leg, host.state_for_pilot(frame))
	if not admission.get("ok", false): stop("state_gate/" + str(admission.get("reason", "unsatisfied")), frame); return
	if leg.kind in ["jump", "drop"] and not host.motor.is_on_floor():
		stop("cell_takeoff_not_grounded", frame); return
	if leg.kind == "drop" and float(leg.target.position[1]) <= host.motor.global_position.y + 1:
		stop("drop_target_not_lower", frame); return
	if leg.kind == "module":
		host.plan = leg.control_plan.duplicate(true)
		for command: Dictionary in host.plan:
			var trigger: Dictionary = command.get("trigger", {})
			if trigger.has("dynamic") and not trigger.has("state"): trigger.state = "__dynamic__"
		host.settle_goal = host.rect(leg.target.region)

func tick(frame: int) -> Array:
	var requested: Array = []
	for action: Dictionary in queued_requests:
		host.controller.router.request_action(StringName(action.type))
		requested.append(action)
	queued_requests.clear()
	if failed or completed:
		host.controller.router.set_move_axis(0.0); return requested
	if not started: _start(frame)
	if failed: return requested
	var leg := active_leg()
	input_leg_id = str(leg.id)
	var age := frame - leg_start_frame
	if age >= int(leg.get("budget_ticks", 360)):
		stop("leg_frame_budget", frame); return requested
	if leg.kind == "module":
		requested.append_array(host.control_plan(frame))
		while module_command_cursor < host.fired_commands.size():
			current_log.commands.append(host.fired_commands[module_command_cursor].duplicate(true))
			module_command_cursor += 1
		if not host.plan_error.is_empty(): stop("module_program/" + host.plan_error, frame)
		return requested
	_axis_to(float(leg.target.position[0]))
	if leg.kind == "jump":
		if age == 0: _request(&"jump", requested)
		var default_hold := maxi(1, ceili(host.motor.tuning.jump_hold_duration * Engine.physics_ticks_per_second))
		if age >= int(leg.get("hold_ticks", default_hold)) and not jump_released:
			_request(&"jump_release", requested); jump_released = true
	elif leg.kind == "drop" and age == 0:
		_request(&"drop_through", requested); drop_attempts += 1; last_drop_frame = frame
	elif leg.kind == "drop" and airborne_seen and host.motor.is_on_floor():
		var below_intermediate: bool = host.motor.global_position.y < float(leg.target.position[1]) - 1.0
		var interval := ceili(host.motor.tuning.drop_through_duration * Engine.physics_ticks_per_second) + 2
		if below_intermediate and host.on_one_way_support() and frame - last_drop_frame >= interval:
			if drop_attempts >= int(leg.get("maximum_drop_attempts", 8)):
				stop("drop_attempt_budget", frame); return requested
			_request(&"drop_through", requested); drop_attempts += 1; last_drop_frame = frame
	return requested

func observe(frame: int) -> void:
	if failed or completed or not started: return
	var leg := active_leg()
	if not host.motor.is_on_floor(): airborne_seen = true
	var at_target: bool = host.rect(leg.target.region).has_point(host.motor.global_position)
	at_target = at_target and host.motor.is_on_floor() and host.motor.get_real_velocity().length() <= float(leg.target.get("maximum_speed", 1.0))
	if at_target: at_target = host.feet_on_supports(leg.target.support_indices).ok
	if leg.kind == "module": at_target = at_target and host.plan_index == host.plan.size()
	stable = stable + 1 if at_target else 0
	if stable >= int(leg.target.get("stable_ticks", 3)):
		if leg.kind == "jump" and not jump_released:
			queued_requests.append({"type": "jump_release", "direction": [0, 0], "pilot_leg": str(leg.id)})
			jump_released = true
		current_log["end"] = host.state_for_pilot(frame)
		current_log["ok"] = true; current_log["ticks"] = frame - leg_start_frame + 1
		legs.append(current_log.duplicate(true)); index += 1; started = false
		if index >= program.size():
			completed = true; host.controller.router.set_move_axis(0.0)
	elif leg.kind in ["jump", "drop"] and airborne_seen and host.motor.is_on_floor() and frame - leg_start_frame > 3:
		var intermediate_drop: bool = leg.kind == "drop" and host.motor.global_position.y < float(leg.target.position[1]) - 1.0 and host.on_one_way_support()
		if not intermediate_drop and not host.touches_supports(leg.target.support_indices):
			stop("landed_on_unexpected_support", frame)

func stop(reason: String, frame: int) -> void:
	if failed: return
	failed = true
	var leg := active_leg()
	failure = {"reason": reason, "frame": frame, "leg_index": index,
		"leg_id": leg.get("id", "UNKNOWN"), "edge_id": leg.get("edge_id", "UNKNOWN"),
		"expected_target": leg.get("target", {}).duplicate(true), "actual": host.state_for_pilot(frame)}
	host.controller.router.set_move_axis(0.0)
	current_log["ok"] = false; current_log["failure"] = failure.duplicate(true)
	legs.append(current_log.duplicate(true))

func compact() -> Dictionary:
	return {"index": index, "total": program.size(), "input_leg_id": input_leg_id,
		"current_leg_id": str(active_leg().get("id", "")), "edge_id": str(active_leg().get("edge_id", "")),
		"kind": str(active_leg().get("kind", "")), "stable_ticks": stable,
		"completed": completed, "failed": failed}

func report() -> Dictionary:
	return {"ok": completed and not failed, "completed": completed, "failed": failed,
		"legs_completed": index, "legs_total": program.size(), "legs": legs.duplicate(true),
		"failure": failure.duplicate(true), "scope": "actual input-only finite policy in one concrete world"}
