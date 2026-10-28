extends "../../workshop/main.gd"
const WORLD_CELLS=preload("world_cells_binding_v1.gd")
var ew_events: Array=[]
var ew_seen: Dictionary={}
var ew_gates: Dictionary={}
func rebuild(new_mode: String)->void:
	var original: Dictionary=cases[selection.selected];cases[selection.selected]=WORLD_CELLS.masked(original)
	await super.rebuild(new_mode)
	cases[selection.selected]=original;case_data=original;WORLD_CELLS.install(self,original)
	ew_events=[];ew_seen={};ew_gates={}
func capture_dynamic_frame()->void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if not active:return
	var seeds: Array=[]
	for node: Node in world.get_children():
		if not node is EnemyAttackProjectile:continue
		var seed:=node as EnemyAttackProjectile
		var row:={"id":str(seed.event_id),"position":[seed.global_position.x,seed.global_position.y],"direction":[seed.direction.x,seed.direction.y],"spent":seed.spent,"remaining":seed.remaining};seeds.append(row)
		if not ew_seen.has(str(seed.event_id)):ew_events.append({"frame":context.frame,"type":"native_seed_spawn","seed":row.duplicate(true)})
		if seed.spent and not ew_seen.get(str(seed.event_id),false):ew_events.append({"frame":context.frame,"type":"native_seed_spent","seed":row.duplicate(true)})
		ew_seen[str(seed.event_id)]=seed.spent
	for latch: ShotLatch in cells.latches:
		var id:=str(latch.link_id)
		if ew_gates.has(id) and ew_gates[id] and not latch.is_open:ew_events.append({"frame":context.frame,"type":"native_gate_closed","id":id})
		ew_gates[id]=latch.is_open
	replay_trace[-1].enemy_world={"seeds":seeds,"events":ew_events.duplicate(true)}
