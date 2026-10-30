extends "ideas_runner_v2.gd"
## Only real Router inputs and native Cell observations. No actor/resource writes.
const PAIRS=preload("../../prototype/creative_batches/batch30_cell/runtime_v3.gd")
var pair_runtime
var last_pairs: Array=[]
var issued:=0
var ready_at:=-1
func make_fixture(data: Dictionary) -> void:
	issued=0;ready_at=-1;last_pairs=[]
	await super.make_fixture(PAIRS.ordinary_case(data))
	pair_runtime=PAIRS.new();world.add_child(pair_runtime);pair_runtime.setup(data,world,controller,context,cells)
	for spec: Dictionary in data.get("latches",[]):
		if not spec.has("additional_pair_access"):continue
		for latch in pair_runtime.pairs:
			if str(latch.link_id)==str(spec.id):latch.add_access_bell(Vector2(spec.additional_pair_access[0],spec.additional_pair_access[1]),false,false)
func carrier(id: String):
	for p: ModuleMovingPlatform in context.module.moving_platforms:
		if str(p.definition.platform_id)==id:return p
	return null
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for c: Dictionary in copy:
			if str(c.get("trigger",{}).get("state","")).begins_with("carrier_") or c.get("trigger",{}).get("state","")in ["pair_desired","route_carrier_ready","revision_shot_ready"]:c.trigger.state="grounded"
	return super.validate_plan(copy)
func pair_open(which: String) -> bool:
	for latch in pair_runtime.pairs:return latch.open_a if which=="A"else not latch.open_a
	return false
func condition_met(state: String) -> bool:
	var c: Dictionary=plan[plan_index]
	if state=="revision_shot_ready":return not motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001
	if state=="pair_desired":return pair_open(str(c.pair_desired))
	if state=="carrier_supported":return motor.is_on_floor() and str(context.snapshot().get("support_id",""))==str(c.carrier)
	if state=="carrier_board":
		var p=carrier(str(c.carrier));var y: float=p.definition.at_time(context.module.clock+.7).y
		return motor.is_on_floor() and y>=460 and p.definition.at_time(context.module.clock+.8).y<=y
	if state=="carrier_exit":
		var p=carrier(str(c.carrier));return motor.is_on_floor() and str(context.snapshot().get("support_id",""))==str(c.carrier) and p.position.y<=float(c.exit_y)
	return super.condition_met(state)
func control_plan(frame: int) -> Array:
	for c: Dictionary in plan:
		if c.has("aim_point") and c.op=="shoot":
			var d: Vector2=(Vector2(c.aim_point[0],c.aim_point[1])-motor.position).normalized();c.direction=[d.x,d.y]
		if c.has("follow_carrier"):
			var p=carrier(str(c.follow_carrier))
			if p!=null:c.target_x=p.position.x+float(c.get("carrier_offset",0))
	var requests:=super.control_plan(frame)
	if plan_index<plan.size() and plan[plan_index].get("trigger",{}).get("state","")=="pair_desired" and not pair_open(str(plan[plan_index].pair_desired)):
		if motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001:
			var key:=10000+issued
			if ready_at<0:ready_at=frame+maxi(0,1+timing_error(key))
			if frame>=ready_at:
				var d:=disturbed_direction(point(plan[plan_index].direction),key);controller.router.request_action(&"shoot_release",d);requests.append({"type":"shoot_release","direction":[d.x,d.y],"plan_index":plan_index,"noise_key":key});issued+=1;ready_at=-1
	return requests

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not captured.is_empty():last_pairs=pair_runtime.snapshot();captured[-1].workshop.paired_gates=last_pairs
func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if not result.get("rejected",false):result.workshop.paired_gates=last_pairs
	return result
