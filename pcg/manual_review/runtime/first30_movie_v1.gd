extends "../../prototype/creative_batches/batch30_cell/main_v3.gd"
## Presentation consumer: original Router replay, actors and Cell implementations.
const REVIEW_AIR=preload("air_enemy_binding_v1.gd")
const GEARS=preload("retractable_gears_v1.gd")
const AIR_DEFINITION=preload("air_port_definition_v1.gd")
const OVERLAY=preload("first30_overlay_v1.gd")
var gear_groups: Array=[]
var air_streak:=0

func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	var original:=super.definition_for(data)
	if data.get("air_port_contracts",[]).is_empty():return original
	var result=AIR_DEFINITION.new()
	for property: Dictionary in original.get_property_list():
		if int(property.usage)&PROPERTY_USAGE_STORAGE and property.name!="script":result.set(property.name,original.get(property.name))
	for port: Dictionary in data.air_port_contracts:result.air_points.append(Vector2(port.stagingPosition[0],port.stagingPosition[1]))
	return result

func rebuild(new_mode: String) -> void:
	gear_groups=[];air_streak=0
	var index:=selection.selected;var source: Dictionary=cases[index]
	var ordinary:=REVIEW_AIR.ordinary(source)
	ordinary.latches=ordinary.get("latches",[]).filter(func(l):return l.get("kind","")!="retractable_gears/v1")
	for latch: Dictionary in ordinary.latches:
		if latch.get("return_access_side_policy","")=="any":latch.erase("return_access")
	cases[index]=ordinary
	await super.rebuild(new_mode)
	cases[index]=source;case_data=source
	if not prepared:return
	REVIEW_AIR.install(source,world,controller,context,cells)
	for pair in pair_runtime.pairs:
		pair.gate_body.name="PairGateA_"+str(pair.link_id);pair.paired_gate_body.name="PairGateB_"+str(pair.link_id)
	for spec: Dictionary in source.get("latches",[]):
		if spec.get("return_access_side_policy","")!="any":continue
		for latch: ShotLatch in cells.latches:
			if str(latch.link_id)==str(spec.id):latch.add_access_bell(Vector2(spec.return_access[0],spec.return_access[1]),false,false)
	for spec: Dictionary in source.get("retractable_groups",[]):
		var group=GEARS.new();group.configure(spec,world,controller,context);group.opened.connect(cells._bell_open.bind(group,str(spec.id)))
		cells.latches.append(group);gear_groups.append(group)
	for port: Dictionary in source.get("air_port_contracts",[]):
		if port.id==source.route_spec.from_port and port.permission=="INPUT":context.anchor_ready=true
	display.case_data=source;display.set_process(false)
	var overlay=OVERLAY.new();overlay.data=source;overlay.z_index=85;world.add_child(overlay)
	var b: Dictionary=source.get("approved_first30",source.get("approved_implementation",{})).rectangle
	var viewport:=get_viewport_rect().size
	var factor:=minf((viewport.x-100)/float(b.w),(viewport.y-245)/float(b.h))
	display.camera.zoom=Vector2.ONE*factor;display.camera.position=Vector2(b.x+b.w/2.,b.y+b.h/2.-95/factor)

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():
		replay_trace[-1].workshop.retractable_groups=gear_groups.map(func(g):return g.snapshot_gears())
		for port: Dictionary in case_data.get("air_port_contracts",[]):
			if port.id!=case_data.route_spec.to_port or port.permission!="OUTPUT":continue
			var crossed:=motor.position.y-18>=float(port.position[1]) and motor.position.y<=float(port.position[1])+128 and absf(motor.position.x-float(port.position[0]))+12<=32 and motor.velocity.y>0
			air_streak=air_streak+1 if crossed else 0
			if air_streak>=6:
				stable_frames=air_streak;finished=true;context.freeze();controller.router.clear("downward_air_exit");world.process_mode=Node.PROCESS_MODE_DISABLED
				status.text="完整身体向下穿过 AIR 出口 · 无地面支撑"
	if finished:
		for node: Node in world.find_children("*","",true,false):node.set_process(false);node.set_physics_process(false)
