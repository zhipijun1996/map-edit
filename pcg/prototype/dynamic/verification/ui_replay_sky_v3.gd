extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var lab=load("res://main_v3.tscn").instantiate();root.add_child(lab)
	await process_frame
	var results: Array=[]
	var references: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/pcg-research/results/dynamic-worker-v1/ui-expected-sky-v3.json"))
	for index: int in lab.cases.size():
		if not lab.cases[index].has("region_profile"):continue
		await process_frame
		lab.selection.select(index);lab.rebuild("replay")
		var previous_frame:=0;var delta:=0.;var phase_delta:=0.;var compared:=0
		while not lab.finished:
			await lab.context.tick_finished
			if lab.frame<=previous_frame:continue
			previous_frame=lab.frame
			var expected: Dictionary=references[lab.case_data.id][lab.frame-1] if references.has(lab.case_data.id) and lab.frame<=references[lab.case_data.id].size() else {}
			if expected.is_empty():continue
			compared+=1
			delta=maxf(delta,absf(lab.motor.position.x-float(expected.x)));delta=maxf(delta,absf(lab.motor.position.y-float(expected.y)))
			phase_delta=maxf(phase_delta,absf(lab.module.clock-float(expected.module_clock)))
		var result:={"id":lab.case_data.id,"safe":lab.safe,"stable_frames":lab.stable_frames,"hp":lab.controller.actor_resources.health.current,"frames":lab.frame,"compared":compared,"maximum_position_delta":delta,"maximum_clock_delta":phase_delta,"contact_frames":lab.context.contact_history.size(),"commits":lab.context.damage.size(),"events":lab.event_counts.duplicate(true)}
		results.append(result);print("UI_V3_REPLAY ",JSON.stringify(result))
	await process_frame
	var file:=FileAccess.open("/workspace/pcg-research/delivery/dynamic-v3/ui-replay-sky-results.json",FileAccess.WRITE);file.store_string(JSON.stringify(results));file.close()
	lab.context.freeze();lab.queue_free();await process_frame
	quit(0)
