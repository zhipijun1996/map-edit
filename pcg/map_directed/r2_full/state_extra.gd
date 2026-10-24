extends RefCounted
## Actual discovered places and original reward service drive physical map gates.
const GATES = preload("gate_world.gd")
var semantics: Dictionary = {}
var actor: PlayerController
var context
var visited: Dictionary = {}
var opened_flags: Dictionary = {}
var services: Dictionary = {}
var reward_events: Array = []
var visit_events: Array = []
var wallet := RunWallet.new()
var gate_world
var error := ""

func setup(data: Dictionary, world: Node2D, controller: PlayerController, dynamic_context) -> void:
	semantics = data.get("r2_semantics", {}).duplicate(true)
	actor = controller; context = dynamic_context
	for node: Dictionary in semantics.get("nodes", []):
		if float(node.get("reward", 0)) <= 0: continue
		var definition := SimpleRewardDefinition.new()
		definition.stable_id = StringName("r2-reward/" + str(node.id))
		definition.kind = SimpleRewardDefinition.Kind.COINS; definition.amount = float(node.reward)
		var service := SimpleRoomReward.new()
		if not service.configure(definition, context.lifetime, actor.actor_resources.health, wallet):
			error = "invalid_original_reward/" + str(node.id); return
		services[str(node.id)] = service
	gate_world = GATES.new(); world.add_child(gate_world)
	gate_world.configure(data.get("gate_specs", []), actor, opened_flags)

func state(frame: int) -> Dictionary:
	return {"frame":frame,"position":[actor.motor.position.x,actor.motor.position.y],
		"grounded":actor.motor.is_on_floor(),"velocity":[actor.motor.velocity.x,actor.motor.velocity.y],
		"air_shots":actor.action_resources.shot_charges,"jumps_used":actor.jump_ability.used_jumps,
		"stamina":actor.actor_resources.stamina.current,"health":actor.actor_resources.health.current,
		"shot_cooldown":actor.shoot_ability.cooldown_remaining,"module_clock":context.module.clock,
		"actor_epoch":context.lifetime.actor_epoch}

func capture(frame: int, _value: Dictionary) -> void:
	gate_world.frame = frame
	if not actor.motor.is_on_floor(): return
	for node: Dictionary in semantics.get("nodes", []):
		var key := str(node.id)
		if visited.has(key): continue
		var raw: Array = node.target.region
		if not Rect2(raw[0],raw[1],raw[2],raw[3]).has_point(actor.motor.position): continue
		var accepted := true
		if services.has(key):
			var receipt := (services[key] as SimpleRoomReward).claim(context.lifetime.token(),StringName("r2_map:" + key))
			accepted = receipt.accepted()
			reward_events.append({"frame":frame,"node_id":key,"accepted":accepted,"amount_applied":receipt.amount_applied,
				"balance":receipt.coins,"event_id":str(receipt.event_id)})
		if not accepted: continue
		visited[key] = true
		var event := state(frame); event.node_id = key; event.opens = node.get("opens", []).duplicate()
		visit_events.append(event)
		for flag: Variant in node.get("opens", []): opened_flags[str(flag)] = true

func before_leg(_leg: Dictionary, _state: Dictionary) -> Dictionary:
	# The director plans stateful paths. Physics gates still own blocking; this
	# adapter does not short-circuit a closed-gate traversal into a success.
	return {"ok":error.is_empty(),"reason":error}

func report() -> Dictionary:
	var missing_nodes: Array = []; var missing_rewards: Array = []
	for key: Variant in semantics.get("required_nodes", []):
		if not visited.has(str(key)): missing_nodes.append(key)
	for key: Variant in semantics.get("required_rewards", []):
		if not services.has(str(key)) or not services[str(key)].claimed: missing_rewards.append(key)
	return {"ok":error.is_empty() and missing_nodes.is_empty() and missing_rewards.is_empty(),"error":error,
		"visited_nodes":visited.keys(),"opened_flags":opened_flags.keys(),"visit_events":visit_events,
		"reward_events":reward_events,"wallet_balance":wallet.balance,"missing_nodes":missing_nodes,
		"missing_rewards":missing_rewards,"gate_events":gate_world.events if gate_world != null else [],
		"scope":"full declared R2 world; actual visited policies, not universal physical reachability"}
