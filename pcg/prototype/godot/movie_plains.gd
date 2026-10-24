extends "res://main_plains.gd"
## Record one frozen factory witness at native 60 Hz; no gameplay edits.
var clip_index:=0
var hold_frames:=0
var result_logged:=false
var closing:=false
var trace_path:=""
var replay_trace: Array=[]

func _ready() -> void:
	var args:=OS.get_cmdline_user_args()
	var source_path:=""
	for i: int in args.size():
		if args[i]=="--cases-json" and i+1<args.size():source_path=args[i+1]
		if args[i]=="--case" and i+1<args.size():clip_index=int(args[i+1])
		if args[i]=="--trace-json" and i+1<args.size():trace_path=args[i+1]
	if source_path.is_empty():push_error("Missing frozen --cases-json");get_tree().quit(2);return
	var frozen: Variant=JSON.parse_string(FileAccess.get_file_as_string(source_path))
	if not frozen is Dictionary or clip_index<0 or clip_index>=frozen.get("cases",[]).size():get_tree().quit(2);return
	super._ready()
	cases=frozen.cases
	selection.clear()
	for c: Dictionary in cases:selection.add_item(str(c.get("review_alias","Sample")))
	selection.select(clip_index);selection.disabled=true
	var rows:=ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text=str(cases[clip_index].get("review_alias","R%02d"%[clip_index+1]))+" · 单跳+反冲 · 真实60Hz / 正常速度 · 待观感反馈"
	for child: Node in rows.get_child(1).get_children():
		if child is BaseButton:child.disabled=true
	set_process_unhandled_input(false)
	print("PLAINS_MOVIE_START ",JSON.stringify({"index":clip_index,"module_sha256":cases[clip_index].module_sha256,"case_id":cases[clip_index].id,"physics_hz":60,"playtested_by_human":false}))

func rebuild(_mode: String) -> void:
	super.rebuild("replay")

func _physics_process(_delta: float) -> void:
	if closing or not prepared or not finished:return
	if not result_logged:
		var result:={"plains":cells.snapshot(),"index":clip_index,"case_id":case_data.id,"candidate_uid":case_data.factory_id,"module_sha256":case_data.module_sha256,"frame":frame,"safe":safe,"stable_frames":stable_frames,"hp":controller.actor_resources.health.current,"position":[motor.position.x,motor.position.y],"events":event_counts,"returns":context.returns.size(),"recorded_router_inputs":true,"human_reviews":0,"approved_offline":false}
		print("PLAINS_MOVIE_RESULT ",JSON.stringify(result));result_logged=true
		if not safe or stable_frames<6 or controller.actor_resources.health.current!=5:get_tree().quit(3);return
	hold_frames+=1
	if hold_frames>=60:
		closing=true;_finish_movie.call_deferred()

func capture_dynamic_frame() -> void:
	if warmup_left>0:super.capture_dynamic_frame();return
	var observed_frame:={"frame":frame,"x":motor.position.x,"y":motor.position.y,"vx":motor.velocity.x,"vy":motor.velocity.y,"grounded":motor.is_on_floor(),"axis":controller.router.axis,"requested":actions.get(frame,[]).duplicate(true),"shot_charges":controller.action_resources.shot_charges,"shot_cooldown":controller.shoot_ability.cooldown_remaining,"jumps_used":controller.jump_ability.used_jumps,"jump_maximum":controller.jump_ability.maximum_jumps(),"energy":controller.actor_resources.stamina.current,"hp":controller.actor_resources.health.current,"traversal_state":str(controller.traversal.state),"real_velocity":[motor.get_real_velocity().x,motor.get_real_velocity().y],"normal_velocity":[motor.normal_velocity.x,motor.normal_velocity.y],"plains":cells.snapshot(),"events":event_counts.duplicate(true)}
	observed_frame.merge(context.snapshot())
	super.capture_dynamic_frame()
	observed_frame.goal_stable_frames=stable_frames
	replay_trace.append(observed_frame)

func _finish_movie() -> void:
	if not trace_path.is_empty():
		DirAccess.make_dir_recursive_absolute(trace_path.get_base_dir())
		var file:=FileAccess.open(trace_path,FileAccess.WRITE)
		file.store_string(JSON.stringify({"schema":"pcg/native-trace/v1","module_sha256":case_data.module_sha256,"case_id":case_data.id,"physics_hz":60,"frames":replay_trace}));file.close()
	var cleanup: Dictionary=await LIFECYCLE.dispose(get_tree(),world,controller)
	prepared=false;world=null;controller=null;motor=null;context=null;cells=null
	print("PLAINS_MOVIE_CLEANUP ",JSON.stringify(cleanup))
	get_tree().quit(0 if cleanup.released else 4)
