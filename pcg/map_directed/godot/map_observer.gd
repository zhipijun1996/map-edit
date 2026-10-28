extends RefCounted
## Map-level observation and original reward transactions. No motion or resource edits.
var semantics: Dictionary = {}
var required: Array = []
var checkpoints: Dictionary = {}
var checkpoint_events: Array = []
var seam_events: Array = []
var reward_events: Array = []
var bell_events: Array = []
var seen_bells: Dictionary = {}
var services: Dictionary = {}
var reward_specs: Dictionary = {}
var wallet := RunWallet.new()
var next_checkpoint := 0
var previous_state: Dictionary = {}
var error := ""

func configure(data: Dictionary, controller: PlayerController, context) -> void:
	semantics = data.get("map_semantics", {}).duplicate(true)
	required = semantics.get("required_checkpoints", []).duplicate()
	for raw: Dictionary in semantics.get("checkpoints", []):
		var key := str(raw.get("id", ""))
		if key.is_empty() or checkpoints.has(key):
			error = "invalid_checkpoint_id"; return
		checkpoints[key] = raw
	for key: Variant in required:
		if not checkpoints.has(str(key)):
			error = "unknown_required_checkpoint/" + str(key); return
	for raw: Dictionary in semantics.get("rewards", []):
		var key := str(raw.get("id", ""))
		if key.is_empty() or services.has(key):
			error = "invalid_reward_id"; return
		var definition := SimpleRewardDefinition.new()
		definition.stable_id = StringName(key)
		definition.kind = SimpleRewardDefinition.Kind.COINS
		definition.amount = float(raw.get("amount", 0))
		var service := SimpleRoomReward.new()
		if not service.configure(definition, context.lifetime, controller.actor_resources.health, wallet):
			error = "invalid_original_reward_service/" + key; return
		services[key] = service
		reward_specs[key] = raw

func region(raw: Dictionary) -> Rect2:
	var value: Array = raw.get("region", [0, 0, 0, 0])
	return Rect2(value[0], value[1], value[2], value[3])

func state(frame: int, controller: PlayerController, context) -> Dictionary:
	var motor := controller.motor
	return {"frame": frame, "position": [motor.position.x, motor.position.y],
		"grounded": motor.is_on_floor(), "velocity": [motor.velocity.x, motor.velocity.y],
		"normal_velocity": [motor.normal_velocity.x, motor.normal_velocity.y],
		"real_velocity": [motor.get_real_velocity().x, motor.get_real_velocity().y],
		"air_shots": controller.action_resources.shot_charges,
		"jumps_used": controller.jump_ability.used_jumps,
		"stamina": controller.actor_resources.stamina.current,
		"health": controller.actor_resources.health.current,
		"shot_cooldown": controller.shoot_ability.cooldown_remaining,
		"traversal_state": str(controller.traversal.state), "dynamic": context.snapshot()}

func observe(frame: int, controller: PlayerController, context, cell_events: Array = []) -> void:
	var motor := controller.motor
	var current := state(frame, controller, context)
	for event: Dictionary in cell_events:
		if event.get("type", "") == "bell_open" and not seen_bells.has(str(event.id)):
			seen_bells[str(event.id)] = true
			bell_events.append(event.duplicate(true))
	# Only the next declared route checkpoint is eligible. Returning to a region
	# later is not satisfied by standing there at initial spawn.
	if next_checkpoint < required.size():
		var key := str(required[next_checkpoint])
		var raw: Dictionary = checkpoints[key]
		if region(raw).has_point(motor.position) and (not raw.get("grounded", true) or motor.is_on_floor()):
			var event := current.duplicate(true)
			event.id = key; event.sequence = next_checkpoint
			checkpoint_events.append(event); next_checkpoint += 1
	for raw: Dictionary in semantics.get("seams", []):
		var key := str(raw.id)
		if previous_state.is_empty() or int(previous_state.frame) + 1 != frame: continue
		var area := region(raw)
		var before := Vector2(previous_state.position[0], previous_state.position[1])
		var crossing_x := float(raw.get("crossing_x", area.get_center().x))
		var direction := str(raw.get("crossing_direction", "right"))
		var crosses := before.x <= crossing_x and motor.position.x > crossing_x if direction == "right" else before.x >= crossing_x and motor.position.x < crossing_x
		var no_harm: bool = previous_state.grounded and current.grounded and current.health > 0 and current.health == previous_state.health and current.dynamic.damage_commits == previous_state.dynamic.damage_commits and current.dynamic.returns == previous_state.dynamic.returns and current.dynamic.hazard_contacts.is_empty() and previous_state.dynamic.hazard_contacts.is_empty()
		if crosses and area.has_point(before) and area.has_point(motor.position) and no_harm:
			seam_events.append({"id": key, "from": raw.get("from", "UNKNOWN"),
				"to": raw.get("to", "UNKNOWN"), "crossing_x": crossing_x,
				"crossing_direction": direction, "consecutive_frames": true,
				"grounded_both_sides": true, "health_stable": true,
				"before": previous_state.duplicate(true), "after": current.duplicate(true),
				"scope": "observed adjacent-frame concrete seam crossing; no universal transfer guarantee"})
	for key: String in services:
		var service: SimpleRoomReward = services[key]
		if service.claimed: continue
		if region(reward_specs[key]).has_point(motor.position) and motor.is_on_floor():
			# Original service owns accepted/stale/terminal/idempotent grant logic.
			var result := service.claim(context.lifetime.token(), StringName("map_claim:" + key))
			reward_events.append({"id": key, "frame": frame, "status": result.status,
				"accepted": result.accepted(), "amount_applied": result.amount_applied,
				"balance": result.coins, "event_id": str(result.event_id)})
	previous_state = current

func report() -> Dictionary:
	var missing_rewards: Array = []
	var missing_bells: Array = []
	var missing_seams: Array = []
	var crossed: Dictionary = {}
	for event: Dictionary in seam_events: crossed[str(event.id)] = true
	for key: Variant in semantics.get("required_seams", []):
		if not crossed.has(str(key)): missing_seams.append(key)
	for key: Variant in semantics.get("required_bells", []):
		if not seen_bells.has(str(key)): missing_bells.append(key)
	for key: Variant in semantics.get("required_rewards", []):
		if not services.has(str(key)) or not services[str(key)].claimed: missing_rewards.append(key)
	return {"ok": error.is_empty() and next_checkpoint == required.size() and missing_rewards.is_empty() and missing_bells.is_empty() and missing_seams.is_empty(),
		"error": error, "required_checkpoints": required.duplicate(), "checkpoint_events": checkpoint_events.duplicate(true),
		"missing_checkpoints": required.slice(next_checkpoint), "seam_events": seam_events.duplicate(true),
		"reward_events": reward_events.duplicate(true), "missing_rewards": missing_rewards,
		"bell_events": bell_events.duplicate(true), "missing_bells": missing_bells,
		"missing_seams": missing_seams,
		"wallet_balance": wallet.balance, "world_rebuilds_during_route": 0,
		"scope": "one concrete assembled world, observed route/entry policy; not universal transfer or full gameplay proof"}
