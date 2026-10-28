extends RefCounted
const DEFINITION=preload("reverse_definition_v1.gd")
const CARRIER=preload("reverse_carrier_v1.gd")
const LATCH=preload("reverse_latch_v1.gd")
static func ordinary_case(source: Dictionary) -> Dictionary:
	var d:=source.duplicate(true);d.latches=[]
	for spec: Dictionary in source.get("latches",[]):
		if spec.get("control_mode","")!="reverse_on_hit":d.latches.append(spec)
	return d
static func install(owner,data: Dictionary) -> void:
	for raw: Dictionary in data.get("moving_platforms",[]):
		if raw.get("control_mode","")!="reverse_on_hit":continue
		var platforms: Array=owner.context.module.moving_platforms
		for i: int in platforms.size():
			var old: ModuleMovingPlatform=platforms[i]
			if str(old.definition.platform_id)!=str(raw.platform_id):continue
			var d=DEFINITION.new()
			for key: String in ["platform_id","start","finish","size","travel_duration","dwell_duration","initial_phase"]:d.set(key,old.definition.get(key))
			d.initial_clock_offset=float(raw.get("initial_clock_offset",0))
			var fresh=CARRIER.new();fresh.definition=d;fresh.module=owner.context.module;fresh.scope=owner.context
			fresh.signed_direction=int(raw.get("initial_direction",1));fresh.name=old.name
			old.get_parent().remove_child(old);old.free();owner.context.module.add_child(fresh);platforms[i]=fresh
			for spec: Dictionary in data.get("latches",[]):
				if spec.get("control_mode","")!="reverse_on_hit" or str(spec.ferry_id)!=str(raw.platform_id):continue
				var latch=LATCH.new();latch.link_id=str(spec.id);latch.formal_presentation=true;latch.prompt_text="SHOT / REVERSE"
				owner.world.add_child(latch)
				latch.setup(owner.controller,owner.context.lifetime,Vector2(spec.bell[0],spec.bell[1]),Rect2(spec.gate[0],spec.gate[1],spec.gate[2],spec.gate[3]))
				latch.bind_motion(fresh);latch.opened.connect(owner.cells._bell_open.bind(latch,str(spec.id)));owner.cells.latches.append(latch)
				if spec.get("carrier_mount","")==str(raw.platform_id):latch.reparent(fresh,true)
static func snapshot(owner) -> Array:
	var out: Array=[]
	for p: ModuleMovingPlatform in owner.context.module.moving_platforms:
		if p.has_method("snapshot_reverse"):out.append(p.snapshot_reverse())
	return out
