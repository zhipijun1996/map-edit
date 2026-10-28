extends "/workspace/map-edit-task-a/pcg/prototype/workshop/runner.gd"
# Adapter only: instantiate original ShotLatch with its original sequence fields
# before setup. No movement, resource, projectile, or latch behavior is replaced.
func make_fixture(case: Dictionary) -> void:
	var routed:=case.duplicate(true)
	routed.latches=[]
	for spec: Dictionary in case.get("latches",[]):
		if not spec.has("sequence_offset"):routed.latches.append(spec)
	await super.make_fixture(routed)
	for spec: Dictionary in case.get("latches",[]):
		if not spec.has("sequence_offset"):continue
		var latch:=ShotLatch.new();latch.link_id=str(spec.id);latch.formal_presentation=true
		latch.open_seconds=float(spec.get("open_seconds",0))
		latch.sequence_offset=Vector2(spec.sequence_offset[0],spec.sequence_offset[1])
		var gate: Array=spec.sequence_gate
		latch.sequence_gate_rect=Rect2(gate[0],gate[1],gate[2],gate[3])
		world.add_child(latch)
		latch.setup(controller,context.lifetime,Vector2(spec.bell[0],spec.bell[1]),Rect2(spec.gate[0],spec.gate[1],spec.gate[2],spec.gate[3]))
		latch.opened.connect(cells._bell_open.bind(latch,str(spec.id)))
		cells.latches.append(latch)

func _cell_aim(query: Dictionary, fallback: Vector2) -> Vector2:
	if query.get("receiver","")!="second":return super._cell_aim(query,fallback)
	for latch: ShotLatch in cells.latches:
		if str(latch.link_id)!=str(query.id):continue
		var target:=latch.to_global(latch.bell_position+latch.sequence_offset)
		var aim:=(target-motor.global_position).normalized()
		var visual: CourierVisual=motor.get_node("CourierVisual")
		for _iteration: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
		return aim
	return fallback
