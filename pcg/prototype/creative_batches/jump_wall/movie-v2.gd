extends "/workspace/map-edit-task-a/pcg/prototype/workshop/main.gd"
# Presentation only; inherited original replay and exact trace capture unchanged.
const REVIEW_LABELS={
 "step-off-wall-return":{"title":"J1 · 踏空蹬回高岸","hint":"没有普通跳能力：先走出断崖贴壁，再蹬回左上方宝箱。"},
 "switchback-wall-ascent":{"title":"J2 · 换壁越过刺面","hint":"右壁上段带刺：先蹬向左壁，再从左壁越过右侧壁顶。"},
 "late-air-rise":{"title":"J3 · 临檐保留二跳","hint":"观察低檐出口，保留第二跳到临檐窗口，再抬升到高岸。"},
 "bell-wall-rebound":{"title":"J4 · 击铃离目标，借墙返回","hint":"朝左下击铃会反冲向右；空中枪已用尽，借墙蹬回左侧门后宝箱。"},
 "wall-slide-launch-window":{"title":"J5 · 下滑中择窗蹬出","hint":"贴壁持续下滑，等待会花掉高度；在锯离开狭口时蹬出。"}
}
func _refresh_labels() -> void:
	var info: Dictionary=REVIEW_LABELS.get(str(case_data.get("family","")),{})
	var rows:=ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text=str(info.get("title","动作候选"))+" · 原生60Hz程序回放 · 观感待评"
	var names:={"move":"移动","jump":"普通跳","double_jump":"二段跳","wall_climb":"贴墙/墙跳","shot_recoil":"射击反冲"}
	var labels: Array[String]=[]
	for cap: String in capabilities:labels.append(str(names.get(cap,cap)))
	ability_label.text="本局真实能力："+"、".join(labels)
	if not finished:status.text=str(info.get("hint","观察目标和落点。"))
func _ready() -> void:
	super._ready()
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	_refresh_labels()
	display.process_priority=-100
func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	if not is_instance_valid(motor):return
	_refresh_labels()
	metric.text="程序回放 %.1fs · HP%.0f · 稳定%d/6"%[frame/60.,controller.actor_resources.health.current,mini(stable_frames,6)]

func _process(_delta: float) -> void:
	if not prepared or not is_instance_valid(display) or not is_instance_valid(display.camera):return
	var positions:={"step-off-wall-return":Vector2(85,310),"switchback-wall-ascent":Vector2(165,250),"late-air-rise":Vector2(250,335),"bell-wall-rebound":Vector2(70,320),"wall-slide-launch-window":Vector2(60,145)}
	var zooms:={"step-off-wall-return":1.45,"switchback-wall-ascent":1.45,"late-air-rise":1.45,"bell-wall-rebound":1.4,"wall-slide-launch-window":1.2}
	var family: String=str(case_data.get("family",""))
	display.camera.position=positions.get(family,Vector2(150,300))
	var magnification: float=float(zooms.get(family,1.))
	display.camera.zoom=Vector2.ONE*magnification
	display.camera.force_update_scroll()
