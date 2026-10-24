extends Node2D
## Research-only playable adapter. Original physics/input classes are unchanged.
const PLAYER := preload("res://scenes/player/player.tscn")
var cases: Array=[]
var case_data: Dictionary
var world: Node2D
var motor: PlayerMotor
var controller: PlayerController
var camera: Camera2D
var display: Node2D
var ui: CanvasLayer
var selection: OptionButton
var status: Label
var metric: Label
var mode:="manual"
var frame:=0
var prepared:=false
var finished:=false
var safe:=true
var reward_visited:=false
var previous:=Vector2.ZERO
var axes: Dictionary={}
var actions: Dictionary={}
var generation:=0
var witness_wait:=4
var traces: Array=[]
var event_counts:={"jump":0,"shot":0,"hook_cast":0,"hook_contact":0}

func _ready() -> void:
	var value: Variant=JSON.parse_string(FileAccess.get_file_as_string("res://modules.json" if FileAccess.file_exists("res://modules.json") else "res://smoke.json"))
	cases=value.get("cases",[]) if value is Dictionary else value
	if cases.is_empty():push_error("No modules supplied");return
	ui=CanvasLayer.new();add_child(ui)
	var panel:=PanelContainer.new();panel.position=Vector2(12,10);panel.size=Vector2(1256,108);ui.add_child(panel)
	var rows:=VBoxContainer.new();panel.add_child(rows)
	var title:=Label.new();title.text="失序之钟 · PCG 研究原型 / Research geometry · Fun and device approval pending";rows.add_child(title)
	var bar:=HBoxContainer.new();rows.add_child(bar)
	selection=OptionButton.new();selection.custom_minimum_size=Vector2(460,36)
	for c:Dictionary in cases:selection.add_item(str(c.get("id","Module")))
	bar.add_child(selection)
	selection.item_selected.connect(func(_i:int):rebuild.call_deferred("manual"))
	var retry:=Button.new();retry.text="手动重试 / Retry";bar.add_child(retry);retry.pressed.connect(func():rebuild.call_deferred("manual"))
	var replay:=Button.new();replay.text="见证回放 / Replay";bar.add_child(replay);replay.pressed.connect(func():rebuild.call_deferred("replay"))
	metric=Label.new();bar.add_child(metric)
	status=Label.new();status.text="A/D 或方向键移动 · 空格跳跃 · 左键松开射击反冲 · E / 右键松开钩索 · R 重试";rows.add_child(status)
	rebuild.call_deferred("manual")

func make_world() -> void:
	world=Node2D.new();add_child(world)
	for p:Array in case_data.get("platforms",[]):
		var body:=StaticBody2D.new();body.position=Vector2(p[0]+p[2]/2.0,p[1]+p[3]/2.0)
		var shape:=CollisionShape2D.new();var box:=RectangleShape2D.new();box.size=Vector2(p[2],p[3]);shape.shape=box
		body.add_child(shape);world.add_child(body)
	for h:Dictionary in case_data.get("hooks",[]):
		var anchor:=GrappleAnchor.new();anchor.position=Vector2(h.x,h.y);anchor.hang_enabled=h.get("kind","hang")=="hang";world.add_child(anchor)
	motor=PLAYER.instantiate() as PlayerMotor
	motor.get_node("CourierVisual").use_plains_v3=false
	motor.get_node("PlayerFeedback").free()
	var s:Array=case_data.get("spawn",[60,482]);motor.position=Vector2(s[0],s[1]);world.add_child(motor)
	controller=motor.get_node("Controller") as PlayerController
	controller.set_physics_process(false)
	event_counts={"jump":0,"shot":0,"hook_cast":0,"hook_contact":0}
	controller.jump_ability.jumped.connect(func():event_counts.jump+=1)
	controller.shoot_ability.shot_fired.connect(func(_d:Vector2,_id:int):event_counts.shot+=1)
	controller.traversal.action_changed.connect(func(state:StringName):
		if state==&"hook_cast":event_counts.hook_cast+=1)
	controller.traversal.hook_contact.connect(func(_p:Vector2):event_counts.hook_contact+=1)
	controller.enable_shot_energy()
	if case_data.get("profile","base") in ["grapple","all"]:controller.traversal.grant(&"grapple")
	if case_data.get("profile","base") in ["double_jump","all"]:controller.traversal.grant(&"double_jump")
	motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(mode=="manual")
	display=load("res://lab_draw.gd").new();display.show_text=false;display.case_data=case_data;display.motor=motor;display.controller=controller;world.add_child(display)
	axes.clear();actions.clear()
	for a:Dictionary in case_data.get("axes",[]):axes[int(a.frame)]=a.value
	for a:Dictionary in case_data.get("actions",[]):
		var i:=int(a.frame)
		if not actions.has(i):actions[i]=[]
		actions[i].append(a)
	previous=motor.position

func rebuild(new_mode:String) -> void:
	prepared=false;generation+=1
	mode=new_mode;frame=0;finished=false;safe=true;reward_visited=false;witness_wait=4;traces.clear()
	if is_instance_valid(world):
		controller.router.clear("lab_restart")
		controller.shoot_ability.clear_projectiles();world.free()
	case_data=cases[selection.selected]
	make_world()
	await get_tree().physics_frame
	await get_tree().process_frame
	prepared=true
	status.text="回放真实见证输入 / Replaying input witness" if mode=="replay" else "A/D 移动 · 空格跳 · 左键松开反冲 · E / 右键松开钩索 · R 重试"

func _unhandled_input(event:InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode==KEY_R:
		rebuild.call_deferred("manual");get_viewport().set_input_as_handled()

func _physics_process(delta:float) -> void:
	if not prepared or not is_instance_valid(controller) or finished:return
	if witness_wait>0:
		controller.physics_tick(1.0/60.0);witness_wait-=1;previous=motor.position;return
	if mode=="replay":
		if axes.has(frame):controller.router.set_move_axis(float(axes[frame]))
		for a:Dictionary in actions.get(frame,[]):
			var d:Array=a.get("direction",[0,0]);controller.router.request_action(StringName(a.type),Vector2(d[0],d[1]))
		controller.physics_tick(1.0/60.0)
	else:
		controller._physics_process(delta)
	var p:=motor.global_position
	var sweep:=Rect2(p-Vector2(12,18),Vector2(24,36)).merge(Rect2(previous-Vector2(12,18),Vector2(24,36)))
	for h:Array in case_data.get("hazards",[]):
		if sweep.intersects(Rect2(h[0],h[1],h[2],h[3]),true):safe=false
	previous=p
	if absf(p.y)>3000:safe=false
	var g:Array=case_data.get("goal",[100000,0,100,100])
	if case_data.has("reward_region"):
		var reward:Array=case_data.reward_region
		if Rect2(reward[0],reward[1],reward[2],reward[3]).has_point(p) and motor.is_on_floor():reward_visited=true
	if not safe:
		finished=true;status.text="危险接触 / Hazard contact — R 或手动重试";controller.router.clear("lab_hazard");controller.active=false
	elif (not case_data.has("reward_region") or reward_visited) and Rect2(g[0],g[1],g[2],g[3]).has_point(p) and (not case_data.get("goal_grounded",true) or motor.is_on_floor()):
		finished=true;status.text="到达出口 / Exit reached · 欢迎评价操作、公平性与重复感" if not case_data.has("reward_region") else "已访问奖励位置并汇流 / Reward position visited and exit reached; no reward transaction";controller.router.clear("lab_success");controller.active=false
	frame+=1
	metric.text="  %s  %.1fs  shots %d  H %s"%[mode,frame/60.0,controller.action_resources.shot_charges,"on" if controller.traversal.hook_enabled else "off"]
	if mode=="replay" and frame>=int(case_data.get("max_frames",360)) and not finished:
		finished=true;status.text="见证预算结束 / Witness ended; exit not reached";controller.router.clear("lab_budget");controller.active=false

	publish_state()

func publish_state() -> void:
	if not OS.has_feature("web") or not is_instance_valid(motor):return
	var state:={"id":str(case_data.get("id","")),"selected":selection.selected,"mode":mode,"frame":frame,"safe":safe,"finished":finished,"reward_visited":reward_visited,"position":[motor.position.x,motor.position.y],"status":status.text,"shot_charges":controller.action_resources.shot_charges,"traversal":str(controller.traversal.state),"case_count":cases.size(),"events":event_counts}
	JavaScriptBridge.eval("window.__pcgLabState="+JSON.stringify(state),true)
