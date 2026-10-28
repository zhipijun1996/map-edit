extends "../r2_full/godot/r2_pilot.gd"
## Original Router inputs only; carrier boarding/ride/exit are physically observed.
var carrier_stage := "waiting"
var carrier_leg := ""
var release_at := -1
var board_seen := false

func tick(frame: int) -> Array:
	if failed or completed or not active_leg().has("carrier_transfer"):
		return super.tick(frame)
	var requested: Array = []
	queued_requests.clear()
	if not started: _start(frame)
	if failed: return requested
	var leg := active_leg()
	input_leg_id = str(leg.id)
	if carrier_leg != str(leg.id):
		carrier_leg = str(leg.id); carrier_stage = "waiting"; release_at = -1; board_seen = false
	if frame - leg_start_frame >= int(leg.get("budget_ticks", 1000)):
		stop("carrier_transfer_budget/" + carrier_stage, frame); return requested
	var transfer: Dictionary = leg.carrier_transfer
	var ferry: ModuleMovingPlatform
	for item: ModuleMovingPlatform in host.context.module.moving_platforms:
		if str(item.definition.platform_id) == str(transfer.id): ferry = item; break
	if ferry == null: stop("missing_actual_carrier", frame); return requested
	var on_carrier: bool = host.context.support_id() == str(transfer.id)
	if on_carrier: board_seen = true
	var phase := fposmod((ferry.motion_clock if ferry.bell_controlled else host.context.module.clock) / ferry.definition.period() + ferry.definition.initial_phase, 1.0)
	var base_level: float = ferry.definition.start.y - ferry.definition.size.y / 2.0 - 18.0
	var boarding_phase := 0.0 if absf(float(transfer.source_level) - base_level) < 4.0 else .5
	if carrier_stage == "waiting":
		host.controller.router.set_move_axis(0.0)
		if phase >= boarding_phase and phase <= boarding_phase + .015:
			carrier_stage = "crossing" if transfer.mode == "cross" else "boarding"
	if carrier_stage == "crossing":
		_axis_to(float(leg.target.position[0])); host.plan_index = host.plan.size()
		if on_carrier and float(host.motor.global_position.y) > float(transfer.source_level) + 6.0 and absf(host.motor.global_position.x - ferry.global_position.x) < 24.0 and release_at < 0:
			_request(&"jump", requested); release_at = frame + 7
		if release_at >= 0 and frame >= release_at and not jump_released:
			_request(&"jump_release", requested); jump_released = true
	elif carrier_stage == "boarding":
		_axis_to(ferry.global_position.x)
		if on_carrier and absf(host.motor.global_position.x - ferry.global_position.x) < 3.0:
			carrier_stage = "riding"
	elif carrier_stage == "riding":
		_axis_to(ferry.global_position.x)
		var top := ferry.global_position.y - ferry.definition.size.y / 2.0
		var target_surface := float(leg.target.position[1]) + 18.0
		var velocity: Variant = host.context.platform_velocity(ferry)
		if absf(top - (target_surface + 16.0)) < 2.0 and absf(float(velocity[1])) < 1.0 and on_carrier:
			_request(&"jump", requested); release_at = frame + 7; carrier_stage = "exiting"
	elif carrier_stage == "exiting":
		_axis_to(float(leg.target.position[0]))
		if frame >= release_at and not jump_released:
			_request(&"jump_release", requested); jump_released = true
		host.plan_index = host.plan.size()
	return requested
