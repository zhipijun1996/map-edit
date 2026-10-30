extends "review040_movie_v1.gd"
const REGION=preload("../../migration/runtime/original_region_chests_v5.gd")
var region_consumer
func rebuild(new_mode: String) -> void:
	region_consumer=null
	await super.rebuild(new_mode)
	if not prepared or case_data.get("original_region_chests",[]).is_empty():return
	region_consumer=REGION.new();world.add_child(region_consumer)
	var result: Dictionary=region_consumer.setup(case_data.original_region_chests,world,controller,context,extra.wallet,MetaProgression.new(),PlainsRegionState.new(),str(case_data.id))
	if not result.ok:push_error(str(result));get_tree().quit(2)
func prepare_dynamic_frame() -> void:
	var requested: Array=actions.get(frame,[])
	if region_consumer!=null and warmup_left==0 and mode=="replay":
		for request: Dictionary in requested:
			if request.type=="native_region_interact":region_consumer.request_interaction()
			elif request.type=="native_region_choose":region_consumer.request_choice(str(request.kind))
		actions[frame]=requested.filter(func(r):return not str(r.type).begins_with("native_region_"))
	super.prepare_dynamic_frame()
	if region_consumer!=null:actions[frame]=requested
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and region_consumer!=null and not replay_trace.is_empty():
		region_consumer.capture();replay_trace[-1].original_region_chests=region_consumer.snapshot()
