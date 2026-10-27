extends "../../workshop/main.gd"
# Native consumer for the same original ShotLatch setup as runner-v2.gd.
# All replay inputs, Motor, resources, projectiles, rewards and trace logic are
# inherited unchanged. Configure original sequence fields before latch.setup.
func rebuild(new_mode: String) -> void:
	var index:=selection.selected
	var original: Dictionary=cases[index]
	var routed:=original.duplicate(true)
	routed.latches=[]
	for spec: Dictionary in original.get("latches",[]):
		if not spec.has("sequence_offset"):routed.latches.append(spec)
	cases[index]=routed
	await super.rebuild(new_mode)
	cases[index]=original;case_data=original
	if is_instance_valid(display):display.case_data=original
	for spec: Dictionary in original.get("latches",[]):
		if not spec.has("sequence_offset"):continue
		var latch:=ShotLatch.new();latch.link_id=str(spec.id);latch.formal_presentation=true
		latch.open_seconds=float(spec.get("open_seconds",0))
		latch.sequence_offset=Vector2(spec.sequence_offset[0],spec.sequence_offset[1])
		var gate: Array=spec.get("sequence_gate",[0,0,0,0])
		latch.sequence_gate_rect=Rect2(gate[0],gate[1],gate[2],gate[3])
		world.add_child(latch)
		latch.setup(controller,context.lifetime,Vector2(spec.bell[0],spec.bell[1]),Rect2(spec.gate[0],spec.gate[1],spec.gate[2],spec.gate[3]))
		latch.opened.connect(cells._bell_open.bind(latch,str(spec.id)))
		cells.latches.append(latch)
