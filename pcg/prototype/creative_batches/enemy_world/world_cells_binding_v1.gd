extends RefCounted
## Shared manual/native-video binding for the exact authored Cells.
const OCC=preload("../occupancy/binding_v1.gd")
const RELAY=preload("attack_relay_v1.gd")
const GUARD=preload("guard_charger_v1.tres")
static func masked(case: Dictionary)->Dictionary:
	var result:=case.duplicate(true);result.latches=[]
	for spec: Dictionary in case.get("latches",[]):
		if not spec.has("occupancy") and not spec.has("attack_relay"):result.latches.append(spec)
	return result
static func install(owner,case: Dictionary)->void:
	OCC.install(owner,case)
	for i: int in owner.cells.enemies.size():
		var spec: Dictionary=case.get("enemies",[])[i]
		if spec.get("variant_definition","")!="enemy-world/guard-charger-v1":continue
		if FileAccess.get_sha256(GUARD.resource_path)!=str(spec.get("variant_tres_sha256","")):
			owner.setup_error="derived_enemy_definition_sha_mismatch";return
		var actor: EnemyActor=owner.cells.enemies[i]
		actor.definition=GUARD;actor.motor.configure(GUARD);actor.brain.configure(GUARD,actor.motor.global_position.x)
	for spec: Dictionary in case.get("latches",[]):
		if not spec.has("attack_relay"):continue
		var actor: EnemyActor
		for i: int in owner.cells.enemies.size():
			if str(case.enemies[i].id)==str(spec.attack_relay.enemy_id):actor=owner.cells.enemies[i]
		if actor==null or actor.attack_behavior==null:owner.setup_error="attack_relay_missing_native_enemy";return
		var latch:=RELAY.new();latch.link_id=str(spec.id);latch.open_seconds=float(spec.open_seconds);owner.world.add_child(latch)
		latch.setup(owner.controller,owner.context.lifetime,Vector2(spec.bell[0],spec.bell[1]),Rect2(spec.gate[0],spec.gate[1],spec.gate[2],spec.gate[3]))
		latch.bind_enemy(actor,str(spec.attack_relay.enemy_id),owner.cells)
		latch.opened.connect(owner.cells._bell_open.bind(latch,str(spec.id)));owner.cells.latches.append(latch)
