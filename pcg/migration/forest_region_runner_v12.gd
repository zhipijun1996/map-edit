extends "forest_feedback_runner_v9.gd"
const REGION_CHESTS=preload("runtime/original_region_chests_v5.gd")
var source_region_chests
var source_region_state
func validate_plan(raw: Variant) -> String:
	if not raw is Array:return super.validate_plan(raw)
	var translated: Array=raw.duplicate(true)
	for command: Dictionary in translated:
		if command.get("op","")=="native_region_interact":command.op="wait"
		elif command.get("op","")=="native_region_choose":
			if command.get("kind","")not in ["coin","note"]:return "unknown_original_region_resource_choice"
			command.op="wait"
	return super.validate_plan(translated)
func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	source_region_chests=REGION_CHESTS.new();world.add_child(source_region_chests);source_region_state=PlainsRegionState.new()
	var result: Dictionary=source_region_chests.setup(case.get("original_region_chests",[]),world,controller,context,extra.wallet,original_pickups.app.meta,source_region_state,str(case.id))
	if not result.ok:setup_error=str(result.reason)
func control_plan(frame: int) -> Array:
	var before:=plan_index
	for command: Dictionary in plan:
		if command.get("op","")=="native_region_interact":command.op="wait";command.source_region_interact=true
		elif command.get("op","")=="native_region_choose":command.op="wait";command.source_region_choose=str(command.kind)
	var requests:=super.control_plan(frame)
	for i: int in range(before,plan_index):
		if plan[i].get("source_region_interact",false):source_region_chests.request_interaction();requests.append({"type":"native_region_interact","direction":[0,0],"plan_index":i})
		if plan[i].has("source_region_choose"):source_region_chests.request_choice(str(plan[i].source_region_choose));requests.append({"type":"native_region_choose","kind":str(plan[i].source_region_choose),"direction":[0,0],"plan_index":i})
	return requests
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and source_region_chests!=null:
		source_region_chests.capture();captured[-1].original_region_chests=source_region_chests.snapshot();captured[-1].axis_after_native_interaction=controller.router.axis
func run_case(case: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(case)
	if not result.get("rejected",false)and source_region_chests!=null:result.original_region_chests=source_region_chests.snapshot()
	return result
