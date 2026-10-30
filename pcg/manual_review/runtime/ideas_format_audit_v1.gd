extends SceneTree
const D=preload("ideas_definition_v1.gd")
const LOOP=preload("../../prototype/creative_batches/batch30_blockn25/install_v1.gd")
func sample():
	var d=D.new();d.module_id=&"format-audit";d.world_bounds=Rect2(0,0,128,128)
	d.platforms.append(Rect2(0,32,128,16));d.anchors.append(Vector2(32,14))
	d.entry_port=PlatformingModulePort.new();d.entry_port.port_id=&"entry";d.entry_port.position=Vector2(32,14)
	d.exit_port=PlatformingModulePort.new();d.exit_port.port_id=&"exit";d.exit_port.position=Vector2(32,14)
	return d
func _initialize() -> void:
	var checks: Dictionary={}
	var d=sample();checks.legacy_coincident_rejected=not d.is_valid()
	d.allow_same_port_return=true;checks.explicit_same_port_accepted=d.is_valid()
	d=sample();d.allow_same_port_return=true;d.exit_port.port_id=&"entry";checks.duplicate_role_rejected=not d.is_valid()
	d=sample();d.allow_same_port_return=true;d.platforms.clear();checks.missing_support_rejected=not d.is_valid()
	d=sample();d.allow_same_port_return=true;d.timing_pressure=4;checks.invalid_pressure_rejected=not d.is_valid()
	d=sample();d.allow_same_port_return=true;d.one_way_platform_indices.append(9);checks.bad_platform_index_rejected=not d.is_valid()
	var cases: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/map-edit-approved-implementation/pcg/manual_review/implementation/new-ideas-final-v1/idea-orbit-choice-001/physics-input-cases.json"))
	var loop=LOOP.definition_audit(LOOP.from_raw(cases.cases[0].moving_platforms[0]))
	var passed: bool=checks.values().all(func(value):return value) and loop.valid and loop.points==17 and loop.period==4 and loop.malformed.all(func(value):return value.rejected)
	var out=FileAccess.open("/workspace/map-edit-approved-implementation/feedback/manual-review/implementation-results/new-ideas-v1/format-audit.json",FileAccess.WRITE)
	out.store_string(JSON.stringify({"passed":passed,"samePortGuards":checks,"loopCell":loop,"simulationTrials":0},"  "));out.close()
	quit(0 if passed else 2)
