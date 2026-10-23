extends "res://main_factory.gd"
## Record one frozen factory witness at native 60 Hz; no gameplay edits.
var clip_index:=0
var hold_frames:=0
var result_logged:=false

func _ready() -> void:
	var args:=OS.get_cmdline_user_args()
	var source_path:=""
	for i: int in args.size():
		if args[i]=="--cases-json" and i+1<args.size():source_path=args[i+1]
		if args[i]=="--case" and i+1<args.size():clip_index=int(args[i+1])
	if source_path.is_empty():push_error("Missing frozen --cases-json");get_tree().quit(2);return
	var frozen: Variant=JSON.parse_string(FileAccess.get_file_as_string(source_path))
	if not frozen is Dictionary or clip_index<0 or clip_index>=frozen.get("cases",[]).size():get_tree().quit(2);return
	super._ready()
	cases=frozen.cases
	selection.clear()
	for c: Dictionary in cases:selection.add_item(str(c.get("review_alias","Sample")))
	selection.select(clip_index);selection.disabled=true
	var rows:=ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text="样例 %02d · 原生60Hz / 正常速度 · 程序输入回放 · 观感待人工反馈"%[clip_index+1]
	for child: Node in rows.get_child(1).get_children():
		if child is BaseButton:child.disabled=true
	set_process_unhandled_input(false)
	print("FACTORY_MOVIE_START ",JSON.stringify({"index":clip_index,"module_sha256":cases[clip_index].module_sha256,"case_id":cases[clip_index].id,"physics_hz":60,"playtested_by_human":false}))

func rebuild(_mode: String) -> void:
	super.rebuild("replay")

func _physics_process(_delta: float) -> void:
	if not prepared or not finished:return
	if not result_logged:
		var result:={"index":clip_index,"case_id":case_data.id,"candidate_uid":case_data.factory_id,"module_sha256":case_data.module_sha256,"frame":frame,"safe":safe,"stable_frames":stable_frames,"hp":controller.actor_resources.health.current,"position":[motor.position.x,motor.position.y],"events":event_counts,"returns":context.returns.size(),"recorded_router_inputs":true,"human_reviews":0,"approved_offline":false}
		print("FACTORY_MOVIE_RESULT ",JSON.stringify(result));result_logged=true
		if not safe or stable_frames<6 or controller.actor_resources.health.current!=5:get_tree().quit(3);return
	hold_frames+=1
	if hold_frames>=60:get_tree().quit(0)
