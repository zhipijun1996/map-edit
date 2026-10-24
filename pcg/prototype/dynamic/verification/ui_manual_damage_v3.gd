extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var lab=load("res://main_v3.tscn").instantiate();root.add_child(lab)
	await process_frame
	var fixture: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/pcg-research/results/dynamic-worker-v1/thorn-real-return.json")).cases[0]
	lab.cases=[fixture];lab.selection.clear();lab.selection.add_item("Manual actual thorn-return probe");lab.selection.select(0);lab.rebuild("manual")
	for i: int in 5:await lab.context.tick_finished
	var press:=InputEventKey.new();press.physical_keycode=KEY_D;press.pressed=true
	lab.motor.get_node("KeyboardMouseAdapter")._unhandled_input(press)
	for i: int in 200:
		await lab.context.tick_finished
		if not lab.context.damage.is_empty():break
	var returned: Dictionary=lab.context.returns[0] if not lab.context.returns.is_empty() else {}
	var before_clock: float=lab.module.clock
	for i: int in 10:await lab.context.tick_finished
	var result:={"hp":lab.controller.actor_resources.health.current,"safe":lab.safe,"finished":lab.finished,"commits":lab.context.damage,"returns":lab.context.returns,"clock_before_continuation":before_clock,"clock_after_10frames":lab.module.clock,"actor_epoch":lab.context.lifetime.actor_epoch,"source":"actual KeyboardMouseAdapter D input / original static-thorn emitter"}
	print("UI_V3_MANUAL_DAMAGE ",JSON.stringify(result))
	var file:=FileAccess.open("/workspace/pcg-research/delivery/dynamic-v3/ui-manual-damage-results.json",FileAccess.WRITE);file.store_string(JSON.stringify(result));file.close()
	await process_frame;lab.context.freeze();lab.queue_free();await process_frame;quit(0)
