extends "runner_v1.gd"
const RELAY=preload("attack_relay_v1.gd")
func make_fixture(case: Dictionary)->void:
	var masked:=case.duplicate(true);masked.latches=[]
	for spec: Dictionary in case.get("latches",[]):
		if not spec.has("attack_relay"):masked.latches.append(spec)
	await super.make_fixture(masked)
	for spec: Dictionary in case.get("latches",[]):
		if not spec.has("attack_relay"):continue
		var actor: EnemyActor
		for i: int in cells.enemies.size():
			if str(case.enemies[i].id)==str(spec.attack_relay.enemy_id):actor=cells.enemies[i]
		if actor==null or actor.attack_behavior==null:setup_error="attack_relay_missing_native_enemy";return
		var latch:=RELAY.new();latch.link_id=str(spec.id);latch.open_seconds=float(spec.open_seconds);world.add_child(latch)
		latch.setup(controller,context.lifetime,Vector2(spec.bell[0],spec.bell[1]),Rect2(spec.gate[0],spec.gate[1],spec.gate[2],spec.gate[3]))
		latch.bind_enemy(actor,str(spec.attack_relay.enemy_id),cells)
		latch.opened.connect(cells._bell_open.bind(latch,str(spec.id)));cells.latches.append(latch)
func condition_met(state: String)->bool:
	if not super.condition_met(state):return false
	var trigger: Dictionary=plan[plan_index].get("trigger",{})
	if not trigger.has("enemy_state"):return true
	var query: Dictionary=trigger.enemy_state
	for i: int in cells.enemies.size():
		if str(current_case.get("enemies",[])[i].id)!=str(query.id):continue
		var actor: EnemyActor=cells.enemies[i]
		return actor.attack_behavior!=null and str(actor.attack_behavior.state)==str(query.state)
	return false
