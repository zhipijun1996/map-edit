extends "main.gd"
## Automated UI smoke, explicitly not a human playtest or physics quality gate.
var smoke_tick:=0
var smoke_closing:=false

func key_event(code: Key, pressed: bool) -> void:
	var event:=InputEventKey.new();event.physical_keycode=code;event.keycode=code;event.pressed=pressed
	Input.parse_input_event(event)

func mouse_event(pressed: bool) -> void:
	var event:=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_LEFT;event.pressed=pressed;event.position=Vector2(250,620);event.global_position=event.position
	Input.parse_input_event(event)

func _physics_process(_delta: float) -> void:
	if not prepared or smoke_closing:return
	smoke_tick+=1
	if smoke_tick==6:key_event(KEY_D,true)
	if smoke_tick==20:key_event(KEY_SPACE,true)
	if smoke_tick==27:key_event(KEY_SPACE,false)
	if smoke_tick==30:mouse_event(true)
	if smoke_tick==35:mouse_event(false)
	if smoke_tick==45:key_event(KEY_D,false)
	if smoke_tick==90:
		smoke_closing=true;_finish_smoke.call_deferred()

func _finish_smoke() -> void:
	var ok: bool=mode=="manual" and event_counts.jump>0 and event_counts.shot>0
	var result:={"schema":"pcg/workshop-native-ui-smoke/v1","automated":true,"human_playtest":false,"mode":mode,"actual_events":event_counts,"position":[motor.position.x,motor.position.y],"hp":controller.actor_resources.health.current,"ok":ok}
	var target:=""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--smoke-out="):target=arg.trim_prefix("--smoke-out=")
	if not target.is_empty():
		get_viewport().get_texture().get_image().save_png(target+".png")
		var file:=FileAccess.open(target+".json",FileAccess.WRITE);file.store_string(JSON.stringify(result));file.close()
	print("WORKSHOP_MANUAL_UI_SMOKE ",JSON.stringify(result))
	var cleanup: Dictionary=await LIFECYCLE.dispose(get_tree(),world,controller)
	prepared=false;world=null;controller=null;motor=null;context=null;cells=null;extra=null
	get_tree().quit(0 if ok and cleanup.released else 4)
