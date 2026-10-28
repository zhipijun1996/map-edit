extends "r2_pilot.gd"
## Consume only frozen Router inputs; observe actual physical arrivals afresh.
var inputs: Dictionary = {}

func configure(owner, data: Dictionary) -> String:
	var error: String = super.configure(owner, data)
	if not error.is_empty(): return error
	var values: Variant = data.get("recorded_frames", [])
	if not values is Array or values.is_empty(): return "recorded_router_inputs_required"
	var expected_frame := 0
	for value: Variant in values:
		if not value is Dictionary or int(value.get("frame", -1)) != expected_frame: return "noncontinuous_recorded_input_frames"
		if not value.has("axis") or not value.get("requested", []) is Array: return "invalid_recorded_router_input"
		inputs[expected_frame] = value.duplicate(true); expected_frame += 1
	if program.any(func(leg: Dictionary) -> bool: return leg.kind == "module"):
		if values.any(func(value: Dictionary) -> bool: return not value.has("plan_index")): return "module_replay_requires_plan_index_metadata"
	return ""

func tick(frame: int) -> Array:
	# Parent observations can queue an input. Native replay must never add it:
	# every submitted action is exactly the already bound source input row.
	queued_requests.clear()
	var requested: Array = []
	if failed:
		host.controller.router.set_move_axis(0.0); return requested
	if not completed and not started: _start(frame)
	if failed: return requested
	if not inputs.has(frame):
		stop("recorded_input_budget_exhausted", frame); return requested
	var row: Dictionary = inputs[frame]
	input_leg_id = str(active_leg().get("id", ""))
	host.controller.router.set_move_axis(float(row.axis))
	for action: Dictionary in row.get("requested", []):
		var direction_values: Array = action.get("direction", [0, 0])
		host.controller.router.request_action(StringName(action.type), Vector2(direction_values[0], direction_values[1]))
		requested.append(action.duplicate(true))
	if not completed and active_leg().kind == "module":
		# Progress of the frozen input program is metadata, never actor state.
		# Actual arrival, mechanism events and the resulting motion are rechecked.
		host.plan_index = int(row.get("plan_index", 0))
	return requested
