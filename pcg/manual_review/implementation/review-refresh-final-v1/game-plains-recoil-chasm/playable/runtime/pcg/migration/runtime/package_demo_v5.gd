extends Node2D
## Isolated playable host. Original Controller/Motor/Context own real physics.
const EXACT_PROFILE=preload("native_profile_v5.gd")
const PLAYER=preload("res://scenes/player/player.tscn")
const CONTEXT=preload("res://dynamic_context.gd")
const CAP=preload("res://capability_adapter.gd")
const LIFECYCLE=preload("res://plains_lifecycle.gd")
var world: Node2D
var package
var motor: PlayerMotor
var controller: PlayerController
var context
var case_data: Dictionary
var setup_error:=""
var frame:=0
var warmup_left:=4
var replay:=false
var verify:=false
var input_smoke:=false
var closed:=false
var prepared:=false
var stable:=0
var input_frames: Dictionary={}
var captured: Array=[]
var label: Label
var camera: Camera2D
var output_path:=""
var wallet:=RunWallet.new()
var native_meta:=MetaProgression.new()
var native_region_state:=PlainsRegionState.new()
var initial_fixture_profile: Variant=null
var initial_native_profile: Variant=null
var initial_tuning: Dictionary={}
var observed_jumps:=0
var observed_shots:=0

func _ready() -> void:
	var folder:=scene_file_path.get_base_dir();var selected:=0
	var args:=OS.get_cmdline_user_args()
	for i: int in args.size():
		if args[i]=="--case" and i+1<args.size():selected=int(args[i+1])
		if args[i]=="--replay":replay=true
		if args[i]=="--verify-package":verify=true;replay=true
		if args[i]=="--input-smoke":input_smoke=true
		if args[i]=="--receipt" and i+1<args.size():output_path=args[i+1]
	var manifest: Variant=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("godot-package.json")))
	if not manifest is Dictionary or FileAccess.get_sha256(folder.path_join("cases.json"))!=manifest.get("source",{}).get("cases_sha256",""):
		push_error("Changed canonical cases; recompile package");get_tree().quit(2);return
	var raw: Variant=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("cases.json")))
	var cases: Array=raw.cases if raw is Dictionary else raw
	if selected<0 or selected>=cases.size():push_error("Unknown canonical case");get_tree().quit(2);return
	case_data=cases[selected]
	world=Node2D.new();world.name="PackageWorld";world.process_mode=Node.PROCESS_MODE_DISABLED;add_child(world)
	var packed: PackedScene=load(folder.path_join("module.tscn"));package=packed.instantiate();world.add_child(package)
	if not package.setup_error.is_empty():push_error(package.setup_error);get_tree().quit(2);return
	motor=PLAYER.instantiate() as PlayerMotor;motor.get_node("PlayerFeedback").free();motor.position=Vector2(case_data.spawn[0],case_data.spawn[1]);world.add_child(motor)
	controller=motor.get_node("Controller") as PlayerController;controller.enable_shot_energy();CAP.apply(controller,case_data.capabilities)
	if case_data.get("original_tuning_profile") is Dictionary:
		var profile: Dictionary=case_data.original_tuning_profile
		if case_data.get("original_fixture_profile") is Dictionary:
			var initialized: Dictionary=EXACT_PROFILE.new().initialize_once(controller,profile,case_data.original_fixture_profile)
			if not initialized.ok:push_error(str(initialized));get_tree().quit(2);return
			initial_fixture_profile=case_data.original_fixture_profile.duplicate(true)
		elif not FoundryCatalog.apply_profile(controller,str(profile.id)):
			push_error("original_native_profile_rejected");get_tree().quit(2);return
		initial_native_profile=profile.duplicate(true)
		initial_tuning={"max_jumps":motor.tuning.max_jumps,"max_air_shots":motor.tuning.max_air_shots}
		initial_native_profile.effectiveTuning=initial_tuning.duplicate(true)
	motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(not replay)
	controller.jump_ability.jumped.connect(func():observed_jumps+=1)
	controller.shoot_ability.shot_fired.connect(func(_direction: Vector2,_id: int):observed_shots+=1)
	context=CONTEXT.new();context.runner=self;context.module=package.module;context.controller=controller;world.add_child(context);context.attach_damage()
	var bound: Dictionary=package.bind_player(controller,context.policy,context.lifetime,wallet,context,"native-demo-instance",native_meta,native_region_state)
	if not bound.ok:push_error(str(bound));get_tree().quit(2);return
	for value: Dictionary in case_data.recorded_frames:input_frames[int(value.frame)]=value
	camera=Camera2D.new();camera.position=motor.position;world.add_child(camera);camera.make_current()
	var ui:=CanvasLayer.new();add_child(ui);label=Label.new();label.position=Vector2(16,12);ui.add_child(label)
	warmup_left=int(case_data.get("warmup_frames",4));prepared=true;context.running=true;world.process_mode=Node.PROCESS_MODE_PAUSABLE

func prepare_dynamic_frame() -> void:
	context.frame=-warmup_left if warmup_left>0 else frame
	if warmup_left>0:controller.router.set_move_axis(0.)
	elif replay:
		var record: Dictionary=input_frames.get(frame,{})
		if record.has("axis"):controller.router.set_move_axis(float(record.axis))
		for request: Dictionary in record.get("requested",[]):
			if request.get("type","")=="native_region_interact":package.request_native_region_interaction()
			elif request.get("type","")=="native_region_choose":package.request_native_region_choice(str(request.get("kind","")))
			elif request.get("type","")=="native_pickup_interact":package.request_native_pickup_interaction()
			else:
				var direction: Array=request.get("direction",[0,0]);controller.router.request_action(StringName(request.type),Vector2(direction[0],direction[1]))
	elif input_smoke:
		if frame==5:_key(KEY_D,true)
		if frame==15:_key(KEY_SPACE,true)
		if frame==22:_key(KEY_SPACE,false)
		if frame==25:_mouse(true)
		if frame==30:_mouse(false)
		if frame==40:_key(KEY_D,false)

func capture_dynamic_frame() -> void:
	if warmup_left>0:warmup_left-=1;return
	var applied_axis: float=controller.router.axis
	package.capture()
	var goal: Array=case_data.goal
	var arrived:=Rect2(goal[0],goal[1],goal[2],goal[3]).has_point(motor.position) and motor.is_on_floor() and motor.get_real_velocity().length()<=1
	stable=stable+1 if arrived else 0
	captured.append({"frame":frame,"x":motor.position.x,"y":motor.position.y,"grounded":motor.is_on_floor(),"velocity":[motor.velocity.x,motor.velocity.y],"hp":controller.actor_resources.health.current,"shot_charges":controller.action_resources.shot_charges,"axis":applied_axis,"axis_after_native_interaction":controller.router.axis,"requested":input_frames.get(frame,{}).get("requested",[]),"support_id":context.support_id(),"package":package.snapshot()})
	camera.position=motor.position
	label.text="Module包 · "+str(case_data.id)+"\n"+("冻结输入回放"if replay else"A/D移动 · 空格跳跃 · 鼠标松开反冲")+" · E 拾取 · HP"+str(controller.actor_resources.health.current)+" · 币"+str(wallet.balance)
	frame+=1
	if (verify and frame>=input_frames.size()) or (input_smoke and frame>=90):_finish.call_deferred()

func _unhandled_key_input(event: InputEvent) -> void:
	if not replay and event is InputEventKey and event.pressed and not event.echo and event.physical_keycode==KEY_E:
		if not case_data.get("original_region_chests",[]).is_empty():package.request_native_region_interaction()
		else:package.request_native_pickup_interaction()

func _key(code: Key, pressed: bool) -> void:
	var event:=InputEventKey.new();event.physical_keycode=code;event.keycode=code;event.pressed=pressed;Input.parse_input_event(event)
func _mouse(pressed: bool) -> void:
	var event:=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_LEFT;event.pressed=pressed;event.position=Vector2(250,620);event.global_position=event.position;Input.parse_input_event(event)

func _finish() -> void:
	if closed:return
	closed=true
	var good: bool=stable>=6 and controller.actor_resources.health.current==5 and package.cells.player_damage.is_empty() and setup_error.is_empty()
	if input_smoke:good=observed_jumps>0 and observed_shots>0
	var receipt:={"schema":"pcg/godot-package-load/v1","case_id":case_data.id,"passed":good,"mode":"manual_input_smoke"if input_smoke else"canonical_replay","actual_frames":frame,"stable_frames":stable,"hp":controller.actor_resources.health.current,"coins":wallet.balance,"actual_jumps":observed_jumps,"actual_shots":observed_shots,"position":[motor.position.x,motor.position.y],"initial_native_profile":initial_native_profile,"initial_fixture_profile":initial_fixture_profile,"initial_tuning":initial_tuning,"damage":package.cells.player_damage,"returns":context.returns,"package":package.snapshot(),"human_playtest":false,"foundation_route_certification":false,"frames":captured}
	var folder:=scene_file_path.get_base_dir()
	receipt.binding={"manifest_sha256":FileAccess.get_sha256(folder.path_join("godot-package.json")),"module_sha256":FileAccess.get_sha256(folder.path_join("module.mapnote.json")),"cases_sha256":FileAccess.get_sha256(folder.path_join("cases.json")),"compiled_sha256":FileAccess.get_sha256(folder.path_join("compiled-content.json")),"scene_sha256":FileAccess.get_sha256(scene_file_path),"engine_sha256":FileAccess.get_sha256(OS.get_executable_path()),"engine_version":Engine.get_version_info(),"user_args":OS.get_cmdline_user_args()}
	if not output_path.is_empty():var file:=FileAccess.open(output_path,FileAccess.WRITE);file.store_string(JSON.stringify(receipt));file.close()
	print("GODOT_PACKAGE_LOAD ",JSON.stringify({"case_id":case_data.id,"passed":good,"actual_frames":frame,"hp":receipt.hp,"coins":receipt.coins,"shots":observed_shots,"jumps":observed_jumps}))
	context.freeze();prepared=false
	var cleanup: Dictionary=await LIFECYCLE.dispose(get_tree(),world,controller)
	get_tree().quit(0 if good and cleanup.released else 4)
