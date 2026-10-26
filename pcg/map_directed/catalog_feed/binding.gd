extends RefCounted
## Reuse A's actual native world Cells; no replacement player/mechanism physics.
const EW=preload("../../prototype/creative_batches/enemy_world/world_cells_binding_v1.gd")
const DOCK=preload("../../prototype/creative_batches/machinery/dock_binding_v11.gd")
static func masked(data:Dictionary)->Dictionary:
	var v:Dictionary=DOCK.masked(EW.masked(data));v.latches=v.latches.filter(func(s:Dictionary)->bool:return not s.has("sequence_offset"));return v
static func install(owner,data:Dictionary)->void:
	EW.install(owner,data);DOCK.install(owner,data)
	for spec:Dictionary in data.get("latches",[]):
		if not spec.has("sequence_offset"):continue
		var latch:=ShotLatch.new();latch.link_id=str(spec.id);latch.formal_presentation=true;latch.open_seconds=float(spec.get("open_seconds",0))
		latch.sequence_offset=Vector2(spec.sequence_offset[0],spec.sequence_offset[1])
		var g:Array=spec.get("sequence_gate",[0,0,0,0]);latch.sequence_gate_rect=Rect2(g[0],g[1],g[2],g[3]);owner.world.add_child(latch)
		latch.setup(owner.controller,owner.context.lifetime,Vector2(spec.bell[0],spec.bell[1]),Rect2(spec.gate[0],spec.gate[1],spec.gate[2],spec.gate[3]));latch.opened.connect(owner.cells._bell_open.bind(latch,str(spec.id)));owner.cells.latches.append(latch)
static func aim(owner,q:Dictionary,fallback:Vector2)->Vector2:
	if q.get("receiver","")not in ["access","second"]:return fallback
	for latch:ShotLatch in owner.cells.latches:
		if str(latch.link_id)!=str(q.id):continue
		var target:Vector2
		if q.receiver=="access":
			if latch.access_positions.is_empty():return fallback
			target=latch.to_global(latch.access_positions[0])
		else:target=latch.to_global(latch.bell_position+latch.sequence_offset)
		var a:Vector2=(target-owner.motor.global_position).normalized();var visual:CourierVisual=owner.motor.get_node("CourierVisual")
		for _i:int in 4:a=(target-visual.muzzle_position(a)).normalized()
		return a
	return fallback
static func enemy_condition(owner)->bool:
	var q:Dictionary=owner.plan[owner.plan_index].get("trigger",{}).get("enemy_state",{})
	if q.is_empty():return true
	for i:int in owner.cells.enemies.size():
		if str(owner.current_case.enemies[i].id)==str(q.id):
			var actor:EnemyActor=owner.cells.enemies[i];return actor.attack_behavior!=null and str(actor.attack_behavior.state)==str(q.state)
	return false
