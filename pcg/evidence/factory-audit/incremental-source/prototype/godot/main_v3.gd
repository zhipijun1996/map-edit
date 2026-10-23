extends Node2D
## Research candidates only. Original Module, Controller and damage policy own gameplay.
const PLAYER_V3 = preload("res://scenes/player/player.tscn")
const CAP_V3 = preload("res://capability_adapter.gd")
const CONTEXT_V3 = preload("res://dynamic_context.gd")
const DRAW_V3 = preload("res://lab_draw_v3.gd")
var cases: Array=[]
var case_data: Dictionary={}
var world: Node2D
var module: PlatformingModule
var motor: PlayerMotor
var controller: PlayerController
var context
var display
var selection: OptionButton
var status: Label
var metric: Label
var ability_label: Label
var telemetry_label: Label
var ui: CanvasLayer
var mode:="manual"
var frame:=0
var warmup_left:=4
var prepared:=false
var finished:=false
var safe:=true
var setup_error:=""
var stable_frames:=0
var last_input_frame:=0
var capabilities: Array=[]
var axes: Dictionary={}
var actions: Dictionary={}
var event_counts: Dictionary={}
var before_grounded:=false
var before_state: StringName=&"free"
var before_used:=0
var reward_visited:=false
var last_snapshot: Dictionary={}

func _ready() -> void:
	if not FileAccess.file_exists("res://modules_v3.json"):push_error("V3 candidates modules_v3.json missing");return
	var raw: Variant=JSON.parse_string(FileAccess.get_file_as_string("res://modules_v3.json"))
	var values: Variant=raw.get("cases",[]) if raw is Dictionary else raw
	if not values is Array or values.is_empty():push_error("V3 candidate list empty or invalid");return
	cases=values
	ui=CanvasLayer.new();add_child(ui)
	var panel:=PanelContainer.new();panel.position=Vector2(12,10);panel.size=Vector2(1256,180);ui.add_child(panel)
	var rows:=VBoxContainer.new();panel.add_child(rows)
	var title:=Label.new();title.text="失序之钟 · 真实动态模块研究候选（预生成 / 输入见证）· 趣味性待人工验证";rows.add_child(title)
	var bar:=HBoxContainer.new();rows.add_child(bar)
	selection=OptionButton.new();selection.custom_minimum_size=Vector2(510,36);selection.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	selection.fit_to_longest_item=false;selection.clip_text=true;selection.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS
	for item: Dictionary in cases:selection.add_item(str(item.get("title",item.get("id","Dynamic candidate"))))
	bar.add_child(selection);selection.item_selected.connect(func(_index: int):rebuild.call_deferred("manual"))
	var retry:=Button.new();retry.text="重建实验 / Retry";bar.add_child(retry);retry.pressed.connect(func():rebuild.call_deferred("manual"))
	var replay:=Button.new();replay.text="见证回放 / Replay";bar.add_child(replay);replay.pressed.connect(func():rebuild.call_deferred("replay"))
	metric=Label.new();metric.custom_minimum_size=Vector2(230,0);metric.clip_text=true;metric.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS;bar.add_child(metric)
	ability_label=Label.new();ability_label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;rows.add_child(ability_label)
	telemetry_label=Label.new();telemetry_label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;rows.add_child(telemetry_label)
	status=Label.new();status.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;rows.add_child(status)
	rebuild.call_deferred("manual")

func point_v3(value: Array) -> Vector2:return Vector2(value[0],value[1])
func rect_v3(value: Array) -> Rect2:return Rect2(value[0],value[1],value[2],value[3])

func definition_for(case: Dictionary) -> PlatformingModuleDefinition:
	var def:=PlatformingModuleDefinition.new();def.module_id=StringName(case.get("id","dynamic"))
	def.world_bounds=rect_v3(case.get("world_bounds",[-5000,-5000,15000,15000]))
	for value: Array in case.get("platforms",[]):def.platforms.append(rect_v3(value))
	for value: Array in case.get("hazards",[]):def.danger_bounds.append(rect_v3(value))
	for index: Variant in case.get("one_way_platform_indices",case.get("one_way_indices",[])):def.one_way_platform_indices.append(int(index))
	for raw: Dictionary in case.get("moving_platforms",[]):
		var value:=ModuleMovingPlatformDefinition.new()
		for key: String in ["platform_id","travel_duration","dwell_duration","initial_phase"]:
			if raw.has(key):value.set(key,raw[key])
		for key: String in ["start","finish","size"]:
			if raw.has(key):value.set(key,point_v3(raw[key]))
		def.ferries.append(value)
	for raw: Dictionary in case.get("saws",[]):
		var value:=ModuleSawDefinition.new()
		for key: String in ["source_id","radius","period","initial_phase","damage","contact_interval"]:
			if raw.has(key):value.set(key,raw[key])
		for key: String in ["origin","travel"]:
			if raw.has(key):value.set(key,point_v3(raw[key]))
		def.saws.append(value)
	for raw: Dictionary in case.get("thorns",[]):
		var value:=PlatformThornDefinition.new()
		for key: String in ["surface_id","platform_index","start_offset","length","depth"]:
			if raw.has(key):value.set(key,raw[key])
		var face: Variant=raw.get("face","top")
		value.face=["top","left","right","bottom"].find(face) if face is String else int(face)
		def.surface_thorns.append(value)
	var goal:=rect_v3(case.get("goal",[100000,0,100,100]))
	def.entry_port=PlatformingModulePort.new();def.entry_port.port_id=&"entry";def.entry_port.position=point_v3(case.get("entry_port",case.get("spawn",[60,482])))
	def.exit_port=PlatformingModulePort.new();def.exit_port.port_id=&"exit";def.exit_port.position=point_v3(case.get("exit_port",[goal.get_center().x,goal.get_center().y]))
	def.anchors.append(def.entry_port.position);def.anchors.append(def.exit_port.position)
	return def

func rebuild(new_mode: String) -> void:
	prepared=false
	if is_instance_valid(world):
		context.freeze();controller.router.clear("dynamic_lab_rebuild");controller.shoot_ability.clear_projectiles();world.free()
	mode=new_mode;frame=0;safe=true;finished=false;stable_frames=0;setup_error="";reward_visited=false;last_snapshot={};last_input_frame=0
	case_data=cases[selection.selected]
	var validation: Dictionary=CAP_V3.validate(case_data.get("capabilities",[]))
	var def:=definition_for(case_data)
	if not validation.ok or not def.is_valid():
		finished=true;status.text="候选配置拒绝：能力或原Definition不合法";return
	capabilities=validation.capabilities
	world=Node2D.new();world.process_mode=Node.PROCESS_MODE_DISABLED;add_child(world)
	module=PlatformingModule.new();module.definition=def;module.authoring_debug=false;world.add_child(module)
	for index: Variant in case_data.get("wall_platform_indices",[]):module.get_node("Platform"+str(int(index))).add_to_group(&"wall_climbable")
	for raw: Dictionary in case_data.get("hooks",[]):
		var anchor:=GrappleAnchor.new();anchor.position=Vector2(raw.x,raw.y);anchor.hang_enabled=raw.get("kind","hang")=="hang";world.add_child(anchor)
	motor=PLAYER_V3.instantiate() as PlayerMotor;motor.get_node("CourierVisual").use_plains_v3=false;motor.get_node("PlayerFeedback").free()
	motor.position=point_v3(case_data.get("spawn",[60,482]));world.add_child(motor)
	controller=motor.get_node("Controller") as PlayerController;controller.process_physics_priority=0
	controller.enable_shot_energy();CAP_V3.apply(controller,capabilities)
	motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(mode=="manual")
	event_counts={"jump":0,"air_jump":0,"anchor_jump":0,"wall_jump":0,"shot":0,"hook_cast":0,"hook_contact":0}
	controller.jump_ability.jumped.connect(func():
		event_counts.jump+=1
		if before_state==&"hook_hang":event_counts.anchor_jump+=1
		elif not before_grounded and before_used>=1:event_counts.air_jump+=1)
	controller.shoot_ability.shot_fired.connect(func(_direction: Vector2,_id: int):event_counts.shot+=1)
	controller.traversal.action_changed.connect(func(state: StringName):
		if state==&"wall_kick":event_counts.wall_jump+=1;event_counts.jump+=1
		if state==&"hook_cast":event_counts.hook_cast+=1)
	controller.traversal.hook_contact.connect(func(_position: Vector2):event_counts.hook_contact+=1)
	context=CONTEXT_V3.new();context.runner=self;context.module=module;context.controller=controller;world.add_child(context);context.attach_damage()
	var records:=module.world_static_hazard_records()
	for record: Dictionary in records:
		var bounds: Rect2=record.rect
		var emitter:=DemoContactEmitter.new();emitter.controller=controller;emitter.policy=context.policy;emitter.kind=DamageRequest.Kind.ENVIRONMENT
		emitter.source_id=StringName(record.authored_id);emitter.position=bounds.get_center();emitter.half_size=bounds.size/2.
		for raw: Dictionary in case_data.get("thorns",[]):
			if raw.get("surface_id","")==record.authored_id:emitter.amount=float(raw.get("damage",emitter.amount));emitter.interval=float(raw.get("contact_interval",emitter.interval))
		module.add_child(emitter)
	axes.clear();actions.clear()
	for record: Dictionary in case_data.get("recorded_frames",[]):
		var index:=int(record.frame);axes[index]=float(record.axis);last_input_frame=maxi(last_input_frame,index)
		for request: Dictionary in record.get("requested",[]):
			if not actions.has(index):actions[index]=[]
			actions[index].append(request)
	if not case_data.has("recorded_frames"):
		for axis: Dictionary in case_data.get("axes",[]):axes[int(axis.frame)]=float(axis.value);last_input_frame=maxi(last_input_frame,int(axis.frame))
		for action: Dictionary in case_data.get("actions",[]):
			var index:=int(action.frame);last_input_frame=maxi(last_input_frame,index)
			if not actions.has(index):actions[index]=[]
			actions[index].append(action)
	var names:={"move":"移动","jump":"跳跃","shot_recoil":"射击反冲","double_jump":"二段跳","grapple":"钩索","wall_climb":"贴墙/墙跳"}
	var labels: Array[String]=[]
	for value: String in capabilities:labels.append(names[value])
	var hazard_scopes: Array[String]=[]
	if not case_data.get("saws",[]).is_empty():hazard_scopes.append("真实锯轮")
	if not case_data.get("thorns",[]).is_empty():hazard_scopes.append("宿主荆棘")
	if not case_data.get("hazards",[]).is_empty():hazard_scopes.append("静态接触源")
	ability_label.text="本局能力："+"、".join(labels)+(" · 无伤范围："+"/".join(hazard_scopes)+"；完整身体扫掠" if not hazard_scopes.is_empty() else " · 本候选无伤害源；仅验证地形/能力轨迹")
	var warnings: Array=case_data.get("review_warnings",[])
	if not warnings.is_empty():ability_label.text+=" · "+"；".join(warnings)
	status.text="真实见证输入回放；无在线搜索" if mode=="replay" else "A/D移动 · 空格跳 · 左键松开反冲 · E/右键钩索 · R重建实验；受伤自动回退且相位保留"
	display=DRAW_V3.new();display.case_data=case_data;display.motor=motor;display.controller=controller;display.module=module;world.add_child(display)
	warmup_left=int(case_data.get("warmup_frames",4));prepared=true
	context.running=true;world.process_mode=Node.PROCESS_MODE_PAUSABLE

func prepare_dynamic_frame() -> void:
	context.frame=-warmup_left if warmup_left>0 else frame
	if warmup_left>0:controller.router.set_move_axis(0.)
	elif mode=="replay":
		if axes.has(frame):controller.router.set_move_axis(float(axes[frame]) if "move" in capabilities else 0.)
		for request: Dictionary in actions.get(frame,[]):controller.router.request_action(StringName(request.type),point_v3(request.get("direction",[0,0])))
	if "move" not in capabilities:controller.router.set_move_axis(0.)
	before_grounded=motor.is_on_floor();before_state=controller.traversal.state;before_used=controller.jump_ability.used_jumps

func capture_dynamic_frame() -> void:
	var contacts: Array=context.contacts_now()
	if not contacts.is_empty():safe=false;context.contact_history.append({"frame":context.frame,"contacts":contacts})
	if not context.damage.is_empty():safe=false
	if warmup_left>0:warmup_left-=1;return
	last_snapshot=context.snapshot()
	var position:=motor.global_position
	if absf(position.x)>30000 or absf(position.y)>10000:safe=false;finished=true
	var goal:=rect_v3(case_data.get("goal",[100000,0,100,100]))
	var stable:=goal.has_point(position) and motor.is_on_floor() and motor.get_real_velocity().length()<=1
	stable_frames=stable_frames+1 if stable else 0
	if case_data.has("reward_region") and rect_v3(case_data.reward_region).has_point(position) and motor.is_on_floor():reward_visited=true
	if context.fatal:finished=true;status.text="本次实验死亡 · HP0 · R重建"
	elif not setup_error.is_empty():finished=true;status.text="实验配置拒绝："+setup_error
	elif stable_frames>=maxi(6,int(case_data.get("settle_frames",6))) and (mode=="manual" or frame>=last_input_frame) and (not case_data.has("reward_region") or reward_visited):
		finished=true;status.text="无伤稳定出口：通过本次真实物理见证；趣味性待人工验证" if safe else "已抵达出口，但发生过危险接触；无伤条件未满足"
	elif mode=="replay" and frame+1>=int(case_data.get("max_frames",360)):finished=true;status.text="见证预算结束，未获得无伤稳定出口"
	elif not safe:status.text="危险接触：无伤未满足 · HP %.0f / 提交%d / 实际伤害%d / 回退%d · R重建（回退保留相位）"%[controller.actor_resources.health.current,context.policy.records.size(),context.damage.size(),context.returns.size()]
	var phases: Array[String]=[]
	for platform: Dictionary in last_snapshot.get("moving_platforms",[]):phases.append(str(platform.id)+" %.2f"%float(platform.phase))
	for saw: Dictionary in last_snapshot.get("saws",[]):phases.append(str(saw.id)+" %.2f"%float(saw.phase))
	metric.text="%s %.1fs HP%.0f | %s | 稳定%d/6"%[mode,frame/60.,controller.actor_resources.health.current," / ".join(phases),mini(stable_frames,6)]
	telemetry_label.text="实际相位：%s · 时钟%.2fs · HP%.0f · 伤害提交%d / 扣血%d / 回退%d · 无伤%s"%[" / ".join(phases) if not phases.is_empty() else "无动态机关",module.clock,controller.actor_resources.health.current,context.policy.records.size(),context.damage.size(),context.returns.size(),"保持" if safe else "未满足"]
	frame+=1
	publish_state()
	if finished:context.freeze();controller.router.clear("dynamic_lab_finished")

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode==KEY_R:
		rebuild.call_deferred("manual");get_viewport().set_input_as_handled()

func publish_state() -> void:
	if not OS.has_feature("web") or not is_instance_valid(motor):return
	var state:={"id":case_data.get("id",""),"selected":selection.selected,"case_count":cases.size(),"mode":mode,"frame":frame,"safe":safe,"finished":finished,"stable_frames":stable_frames,"capabilities":capabilities,"hp":controller.actor_resources.health.current,"position":[motor.position.x,motor.position.y],"velocity":[motor.velocity.x,motor.velocity.y],"status":status.text,"events":event_counts,"dynamic":last_snapshot,"damage_submissions":context.policy.records,"damage_commits":context.damage,"returns":context.returns,"contact_frames":context.contact_history.size(),"generation":"pre-generated research candidates","replay":"recorded real Router inputs","fun_approval":"unverified"}
	JavaScriptBridge.eval("window.__pcgLabStateV3="+JSON.stringify(state),true)
