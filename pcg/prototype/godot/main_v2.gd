extends "res://main.gd"
## Pre-generated candidate review. Replays recorded real Router inputs, no online optimizer.
const CAPABILITIES_V2 = preload("res://capability_adapter.gd")
var caps_v2: Array=[]
var stable_frames_v2:=0
var before_grounded_v2:=false
var before_state_v2: StringName=&"free"
var before_used_v2:=0
var last_input_frame_v2:=0
var config_error_v2:=""
var ability_label_v2: Label

func _ready() -> void:
	if not FileAccess.file_exists("res://modules_v2.json"):
		push_error("V2 candidate file modules_v2.json is missing; old modules are not V2 evidence");return
	var raw: Variant=JSON.parse_string(FileAccess.get_file_as_string("res://modules_v2.json"))
	var candidates: Variant=raw.get("cases",[]) if raw is Dictionary else raw
	if not candidates is Array or candidates.is_empty():push_error("V2 candidate file is empty/invalid");return
	cases=candidates
	ui=CanvasLayer.new();add_child(ui)
	var panel:=PanelContainer.new();panel.position=Vector2(12,10);panel.size=Vector2(1256,140);ui.add_child(panel)
	var rows:=VBoxContainer.new();panel.add_child(rows)
	var title:=Label.new();title.text="失序之钟 · 能力组合候选（预生成 / 真实见证回放）· 趣味性尚待人工验证";rows.add_child(title)
	var bar:=HBoxContainer.new();rows.add_child(bar)
	selection=OptionButton.new();selection.custom_minimum_size=Vector2(520,36);selection.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	selection.fit_to_longest_item=false;selection.clip_text=true;selection.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS
	for item: Dictionary in cases:selection.add_item(str(item.get("title",item.get("id","Candidate"))))
	bar.add_child(selection);selection.item_selected.connect(func(_i:int):rebuild.call_deferred("manual"))
	var retry:=Button.new();retry.text="手动重试 / Retry";bar.add_child(retry);retry.pressed.connect(func():rebuild.call_deferred("manual"))
	var replay:=Button.new();replay.text="见证回放 / Replay";bar.add_child(replay);replay.pressed.connect(func():rebuild.call_deferred("replay"))
	metric=Label.new();bar.add_child(metric)
	ability_label_v2=Label.new();rows.add_child(ability_label_v2)
	status=Label.new();rows.add_child(status)
	rebuild.call_deferred("manual")

func make_world() -> void:
	super.make_world()
	stable_frames_v2=0;last_input_frame_v2=0;config_error_v2=""
	var values: Variant=case_data.get("capabilities",["move","jump","shot_recoil"])
	var validation: Dictionary=CAPABILITIES_V2.validate(values)
	if not validation.ok:config_error_v2=str(validation.reason);return
	caps_v2=validation.capabilities
	var names:={"move":"移动","jump":"跳跃","shot_recoil":"射击反冲","double_jump":"二段跳","grapple":"钩索","wall_climb":"贴墙/墙跳"}
	var enabled_names: Array[String]=[]
	for value: String in caps_v2:enabled_names.append(names[value])
	ability_label_v2.text="本候选能力："+"、".join(enabled_names)
	var review: Array=case_data.get("review_warnings",[])
	if not review.is_empty():ability_label_v2.text+=" · 研究提示："+"；".join(review)
	var result: Dictionary=CAPABILITIES_V2.apply(controller,caps_v2)
	if not result.ok:config_error_v2=str(result.reason);return
	var bodies: Array=[]
	for item: Node in world.get_children():
		if item is StaticBody2D:bodies.append(item)
	var wall_check: Dictionary=CAPABILITIES_V2.indices(case_data.get("wall_platform_indices",[]),bodies.size())
	var one_check: Dictionary=CAPABILITIES_V2.indices(case_data.get("one_way_platform_indices",case_data.get("one_way_indices",[])),bodies.size())
	if not wall_check.ok or not one_check.ok:config_error_v2="invalid_cell_indices";return
	var wall_indices: Dictionary=wall_check.indices
	var one_way: Dictionary=one_check.indices
	for i: int in bodies.size():
		var body: StaticBody2D=bodies[i]
		body.name="CellPlatform"+str(i)
		(body.get_child(0) as CollisionShape2D).name="CollisionShape2D"
		if wall_indices.has(i):body.add_to_group(&"wall_climbable")
		if one_way.has(i):
			body.add_to_group(&"one_way_platform")
			(body.get_child(0) as CollisionShape2D).one_way_collision=true
	# Actual accepted events; wall jump bypasses JumpAbility.jumped in production.
	event_counts.air_jump=0;event_counts.anchor_jump=0;event_counts.wall_jump=0
	controller.jump_ability.jumped.connect(func():
		if before_state_v2==&"hook_hang":event_counts.anchor_jump+=1
		elif not before_grounded_v2 and before_used_v2>=1:event_counts.air_jump+=1)
	controller.traversal.action_changed.connect(func(state: StringName):
		if state==&"wall_kick":event_counts.wall_jump+=1;event_counts.jump+=1)
	# Optional full real trace gives exact per-frame input witnesses.
	if case_data.has("recorded_frames"):
		axes.clear();actions.clear()
		for record: Dictionary in case_data.recorded_frames:
			var i:=int(record.frame)
			axes[i]=float(record.axis)
			for request: Dictionary in record.get("requested",[]):
				if not actions.has(i):actions[i]=[]
				actions[i].append(request)
	for i: Variant in axes:last_input_frame_v2=maxi(last_input_frame_v2,int(i))
	for i: Variant in actions:last_input_frame_v2=maxi(last_input_frame_v2,int(i))
	if is_instance_valid(display):display.free()
	display=load("res://lab_draw_v2.gd").new();display.show_text=false;display.case_data=case_data;display.motor=motor;display.controller=controller;world.add_child(display)

func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not config_error_v2.is_empty():
		finished=true;controller.active=false;status.text="能力配置拒绝 / Unsupported capability snapshot: "+config_error_v2
	publish_state()

func _physics_process(delta: float) -> void:
	if not prepared or not is_instance_valid(controller) or finished:return
	if witness_wait>0:
		controller.physics_tick(1./60.);witness_wait-=1;previous=motor.position;return
	before_grounded_v2=motor.is_on_floor();before_state_v2=controller.traversal.state;before_used_v2=controller.jump_ability.used_jumps
	if mode=="replay":
		if axes.has(frame):controller.router.set_move_axis(float(axes[frame]) if "move" in caps_v2 else 0.)
		for a: Dictionary in actions.get(frame,[]):
			var direction: Array=a.get("direction",[0,0]);controller.router.request_action(StringName(a.type),Vector2(direction[0],direction[1]))
		controller.physics_tick(1./60.)
	else:
		if "move" not in caps_v2:controller.router.set_move_axis(0.)
		controller._physics_process(delta)
	var pos:=motor.global_position
	var sweep:=Rect2(pos-Vector2(12,18),Vector2(24,36)).merge(Rect2(previous-Vector2(12,18),Vector2(24,36)))
	for hazard: Array in case_data.get("hazards",[]):
		if sweep.intersects(Rect2(hazard[0],hazard[1],hazard[2],hazard[3]),true):safe=false
	previous=pos
	if absf(pos.y)>10000 or absf(pos.x)>30000:safe=false
	if case_data.has("reward_region"):
		var reward: Array=case_data.reward_region
		if Rect2(reward[0],reward[1],reward[2],reward[3]).has_point(pos) and motor.is_on_floor():reward_visited=true
	var goal: Array=case_data.get("goal",[100000,0,100,100])
	var at_goal:=Rect2(goal[0],goal[1],goal[2],goal[3]).has_point(pos) and motor.is_on_floor() and absf(motor.velocity.x)<=1 and absf(motor.velocity.y)<=1
	stable_frames_v2=stable_frames_v2+1 if at_goal else 0
	if not safe:
		finished=true;status.text="危险接触 / Hazard contact — R 重试";controller.router.clear("lab_v2_hazard");controller.active=false
	elif stable_frames_v2>=maxi(6,int(case_data.get("settle_frames",6))) and (mode=="manual" or frame>=last_input_frame_v2) and (not case_data.has("reward_region") or reward_visited):
		finished=true;status.text="稳定抵达出口 / Exit reached and stable · 预生成候选" if not case_data.has("reward_region") else "奖励位置已访问并稳定汇流 / Reward position visited and exit reached; no reward transaction"
		controller.router.clear("lab_v2_success");controller.active=false
	frame+=1
	var labels: Array[String]=[]
	for value: String in caps_v2:
		if value=="double_jump":labels.append("DJ")
		elif value=="shot_recoil":labels.append("R")
		elif value=="grapple":labels.append("H")
		elif value=="wall_climb":labels.append("W")
	metric.text=" %s %.1fs | %s | stable %d/6"%[mode,frame/60.,"+".join(labels),mini(6,stable_frames_v2)]
	if mode=="replay" and frame>=int(case_data.get("max_frames",360)) and not finished:
		finished=true;status.text="见证预算结束 / Witness ended without stable exit";controller.router.clear("lab_v2_budget");controller.active=false
	publish_state()

func publish_state() -> void:
	if not OS.has_feature("web") or not is_instance_valid(motor):return
	var state:={"id":str(case_data.get("id","")),"selected":selection.selected,"mode":mode,"frame":frame,"safe":safe,"finished":finished,"reward_visited":reward_visited,"position":[motor.position.x,motor.position.y],"velocity":[motor.velocity.x,motor.velocity.y],"grounded":motor.is_on_floor(),"stable_frames":stable_frames_v2,"capabilities":caps_v2,"status":status.text,"shot_charges":controller.action_resources.shot_charges,"traversal":str(controller.traversal.state),"case_count":cases.size(),"events":event_counts,"candidate_generation":"offline/pre-generated","replay":"recorded real Router inputs"}
	JavaScriptBridge.eval("window.__pcgLabStateV2="+JSON.stringify(state),true)
