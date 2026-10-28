extends "../../workshop/runner.gd"
const LOOP=preload("install_v1.gd")
var cell_audit: Dictionary={}
var pause_receipts: Array=[]
var pause_started:=false
func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	var d:=super.definition_for(data)
	LOOP.install(d,data)
	return d
func make_fixture(data: Dictionary) -> void:
	pause_receipts=[];pause_started=false;cell_audit={}
	await super.make_fixture(data)
	for d in context.module.definition.ferries:
		if d.get_script()==LOOP.DEFINITION:cell_audit=LOOP.definition_audit(d)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if not active:return
	captured[-1].n25=LOOP.snapshot(self)
	if current_case.get("cell_pause_probe",false) and current_frame==120 and not pause_started:
		pause_started=true;_exercise_pause.call_deferred()
func _exercise_pause() -> void:
	var before={"clock":context.module.clock,"actor":[motor.position.x,motor.position.y],"deck":LOOP.snapshot(self)}
	paused=true
	for _i: int in 3:await process_frame
	var after={"clock":context.module.clock,"actor":[motor.position.x,motor.position.y],"deck":LOOP.snapshot(self)}
	paused=false
	pause_receipts.append({"before":before,"after":after,"paused_process_frames":3,"unchanged":before==after})
func run_case(data: Dictionary) -> Dictionary:
	var r: Dictionary=await super.run_case(data)
	if not r.get("rejected",false):r.n25={"definition_audit":cell_audit,"pause_receipts":pause_receipts,"from_standard_document":data.has("trajectory_document")}
	return r
