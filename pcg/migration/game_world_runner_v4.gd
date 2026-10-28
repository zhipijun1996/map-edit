extends "game_search_runner.gd"
const NATIVE_PICKUPS=preload("runtime/original_pickups_v4.gd")
var original_pickups

func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	var translated: Array=raw.duplicate(true)
	for command: Dictionary in translated:
		if command.get("op","")=="native_pickup_interact":command.op="wait"
	return super.validate_plan(translated)

func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	original_pickups=NATIVE_PICKUPS.new();world.add_child(original_pickups)
	var result: Dictionary=original_pickups.setup(case.get("original_pickups",[]),world,controller,context,extra.wallet,MetaProgression.new(),str(case.id))
	if not result.ok:setup_error=str(result.reason)

func control_plan(frame: int) -> Array:
	var before:=plan_index
	for command: Dictionary in plan:
		if command.get("op","")=="native_pickup_interact":command.op="wait";command.native_pickup_interaction=true
	var requests:=super.control_plan(frame)
	for i: int in range(before,plan_index):
		if plan[i].get("native_pickup_interaction",false):
			original_pickups.request_interaction();requests.append({"type":"native_pickup_interact","direction":[0,0],"plan_index":i})
	return requests

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and original_pickups!=null:
		original_pickups.capture();captured[-1].original_pickups=original_pickups.snapshot()

func run_case(case: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(case)
	if not result.get("rejected",false)and original_pickups!=null:result.original_pickups=original_pickups.snapshot()
	return result
