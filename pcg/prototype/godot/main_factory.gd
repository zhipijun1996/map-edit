extends "res://main_v3.gd"
## Adds observation/export only. The frozen V3 components still own gameplay.
var attempt_serial:=0
var manual_input_events:=0
var manual_axis_frames:=0
var ended_sent:=false

func _ready() -> void:
	super._ready()
	if is_instance_valid(ui):
		(ui.get_child(0).get_child(0).get_child(0) as Label).text="失序之钟 · 离线模块盲评 · 技术候选，尚未获得人工批准"
		telemetry_label.visible=false
		ui.get_child(0).size.y=140

func rebuild(new_mode: String) -> void:
	if prepared and frame>0:send_review_state("attempt_end")
	super.rebuild(new_mode)
	attempt_serial+=1;manual_input_events=0;manual_axis_frames=0;ended_sent=false

func _input(event: InputEvent) -> void:
	if mode!="manual" or not prepared or finished:return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode in [KEY_A,KEY_D,KEY_SPACE,KEY_E]:manual_input_events+=1
	elif event is InputEventMouseButton and event.pressed and event.button_index in [MOUSE_BUTTON_LEFT,MOUSE_BUTTON_RIGHT] and event.position.y>190:
		manual_input_events+=1

func prepare_dynamic_frame() -> void:
	super.prepare_dynamic_frame()
	if mode=="manual" and warmup_left<=0 and absf(controller.router.axis)>.01:manual_axis_frames+=1

func publish_state() -> void:
	super.publish_state()
	if frame%15==0 or finished:
		send_review_state("attempt_end" if finished and not ended_sent else "telemetry")
		if finished:ended_sent=true

func send_review_state(kind: String) -> void:
	if not OS.has_feature("web") or not is_instance_valid(motor):return
	var accepted_inputs:=manual_axis_frames+int(event_counts.get("jump",0))+int(event_counts.get("shot",0))+int(event_counts.get("hook_cast",0))
	var payload:={"kind":kind,"attempt_id":attempt_serial,"candidate_uid":case_data.get("factory_id",""),"module_sha256":case_data.get("module_sha256",""),"alias":case_data.get("review_alias",""),"mode":mode,"frames":frame,"input_events":accepted_inputs,"raw_input_presses":manual_input_events,"axis_frames":manual_axis_frames,"finished":finished,"safe":safe,"stable_frames":stable_frames,"hp":controller.actor_resources.health.current,"returns":context.returns.size(),"events":event_counts,"module_clock":module.clock}
	JavaScriptBridge.eval("window.__pcgFactoryState="+JSON.stringify(payload)+";window.parent.postMessage({type:'pcg-factory-state',payload:window.__pcgFactoryState},window.location.origin)",true)
