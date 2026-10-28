extends "state_extra.gd"
## Real optional Module objective; reward requires actual bell and supported visit.
var optional: Array = []
var optional_events: Array = []

func setup(data: Dictionary, world: Node2D, controller: PlayerController, dynamic_context) -> void:
	super.setup(data, world, controller, dynamic_context)
	optional = data.get("r2_optional_challenges", []).duplicate(true)
	for node: Dictionary in optional:
		var definition := SimpleRewardDefinition.new()
		definition.stable_id = StringName("r2-reward/" + str(node.id))
		definition.kind = SimpleRewardDefinition.Kind.COINS; definition.amount = float(node.reward)
		var service := SimpleRoomReward.new()
		if not service.configure(definition, context.lifetime, actor.actor_resources.health, wallet):
			error = "invalid_optional_reward/" + str(node.id); return
		services[str(node.id)] = service

func capture(frame: int, value: Dictionary) -> void:
	super.capture(frame, value)
	for node: Dictionary in optional:
		if node.get("required_enemy", "") != "" and value.get("plains_events_delta", []).any(func(event: Dictionary) -> bool: return event.get("type", "") == "enemy_hit" and event.get("id", "") == node.required_enemy and event.get("fired_airborne", false)):
			node.enemy_hit_observed = true
	if not actor.motor.is_on_floor(): return
	for node: Dictionary in optional:
		var service: SimpleRoomReward = services[str(node.id)]
		if service.claimed: continue
		var bells: Array = value.get("plains", {}).get("bells", [])
		var hit := bells.any(func(bell: Dictionary) -> bool: return str(bell.get("id", "")) == str(node.required_bell) and int(bell.get("open_count", 0)) > 0)
		if node.get("required_enemy", "") != "":
			hit = bool(node.get("enemy_hit_observed", false))
		var raw: Array = node.target.region
		if not hit or not Rect2(raw[0], raw[1], raw[2], raw[3]).has_point(actor.motor.position): continue
		var receipt := service.claim(context.lifetime.token(),StringName("r2_map:" + str(node.id)))
		var event := state(frame); event.challenge_id = node.id; event.accepted = receipt.accepted()
		event.amount_applied = receipt.amount_applied; event.balance = receipt.coins
		optional_events.append(event)

func report() -> Dictionary:
	var value := super.report()
	value.optional_challenge_events = optional_events.duplicate(true)
	return value
