extends "res://main_plains.gd"
## Playable/manual consumer and native movie consumer share the original lab.
const EXTRA=preload("mechanics.gd")
var extra
var recording:=false
var clip_index:=0
var hold_frames:=0
var closing:=false
var trace_path:=""
var replay_trace: Array=[]

func _ready() -> void:
	var source:=""
	var args:=OS.get_cmdline_user_args()
	for i: int in args.size():
		if args[i]=="--cases-json" and i+1<args.size():source=args[i+1]
		if args[i]=="--case" and i+1<args.size():clip_index=int(args[i+1])
		if args[i]=="--trace-json" and i+1<args.size():trace_path=args[i+1];recording=true
	if source.is_empty():push_error("Workshop requires --cases-json");get_tree().quit(2);return
	var frozen: Variant=JSON.parse_string(FileAccess.get_file_as_string(source))
	if not frozen is Dictionary or frozen.get("cases",[]).is_empty():get_tree().quit(2);return
	super._ready()
	cases=frozen.cases;selection.clear()
	for c: Dictionary in cases:selection.add_item(str(c.get("review_alias",c.id)))
	selection.select(clip_index)
	var rows:=ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text="失序之钟 · 内容工坊候选 · 普通单跳 / 原反冲 · 观感待评"
	if recording:
		selection.disabled=true
		for child: Node in rows.get_child(1).get_children():
			if child is BaseButton:child.disabled=true
		set_process_unhandled_input(false)

func rebuild(new_mode: String) -> void:
	await super.rebuild("replay" if recording else new_mode)
	extra=EXTRA.new();extra.owner_runner=self;world.add_child(extra)
	extra.setup(case_data,world,controller,context,cells)
	replay_trace=[];hold_frames=0

func capture_dynamic_frame() -> void:
	if warmup_left>0:super.capture_dynamic_frame();return
	var f:={"frame":frame,"x":motor.position.x,"y":motor.position.y,"vx":motor.velocity.x,"vy":motor.velocity.y,"grounded":motor.is_on_floor(),"axis":controller.router.axis,"requested":actions.get(frame,[]).duplicate(true),"shot_charges":controller.action_resources.shot_charges,"shot_cooldown":controller.shoot_ability.cooldown_remaining,"jumps_used":controller.jump_ability.used_jumps,"jump_maximum":controller.jump_ability.maximum_jumps(),"energy":controller.actor_resources.stamina.current,"hp":controller.actor_resources.health.current,"traversal_state":str(controller.traversal.state),"real_velocity":[motor.get_real_velocity().x,motor.get_real_velocity().y],"normal_velocity":[motor.normal_velocity.x,motor.normal_velocity.y],"plains":cells.snapshot()}
	f.merge(context.snapshot())
	super.capture_dynamic_frame()
	extra.capture();f.workshop=extra.snapshot();f.goal_stable_frames=stable_frames
	replay_trace.append(f)
	if not finished:status.text=str(case_data.get("play_hint","跳入空中，观察落点，选择反冲方向"))+" · 金币 "+str(extra.wallet.balance)

func _physics_process(_delta: float) -> void:
	if not recording or closing or not prepared or not finished:return
	hold_frames+=1
	if hold_frames==1:print("WORKSHOP_MOVIE_RESULT ",JSON.stringify({"id":case_data.id,"safe":safe,"hp":controller.actor_resources.health.current,"stable_frames":stable_frames,"frame":frame,"position":[motor.position.x,motor.position.y],"workshop":extra.snapshot()}))
	if hold_frames>=60:
		closing=true;_finish_movie.call_deferred()

func _finish_movie() -> void:
	var file:=FileAccess.open(trace_path,FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"pcg/native-trace/v1","case_id":case_data.id,"module_sha256":case_data.module_sha256,"frames":replay_trace}));file.close()
	var good:=safe and stable_frames>=6 and controller.actor_resources.health.current==5
	var cleanup: Dictionary=await LIFECYCLE.dispose(get_tree(),world,controller)
	prepared=false;world=null;controller=null;motor=null;context=null;cells=null;extra=null
	print("WORKSHOP_MOVIE_CLEANUP ",JSON.stringify(cleanup))
	get_tree().quit(0 if good and cleanup.released else 4)
