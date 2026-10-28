extends RefCounted
## Test-host teardown only. Audio runs unchanged during the simulated attempt.
## A fixed-FPS SceneTree can finish before Dummy audio's real-time mix thread.
## Stop players, drop streams, and wait on weak playback handles after world free.
static func dispose(tree: SceneTree, world: Node, controller: PlayerController) -> Dictionary:
	if not is_instance_valid(world):return {"playbacks":0,"wait_ms":0,"released":true}
	var handles: Array[WeakRef]=[]
	for node: Node in world.find_children("*", "", true, false):
		if node is AudioStreamPlayer or node is AudioStreamPlayer2D or node is AudioStreamPlayer3D:
			if node.has_stream_playback():handles.append(weakref(node.get_stream_playback()))
			node.stop();node.stream=null
	if is_instance_valid(controller):controller.shoot_ability.clear_projectiles()
	world.free()
	var started:=Time.get_ticks_msec()
	while Time.get_ticks_msec()-started<500:
		var alive:=false
		for handle: WeakRef in handles:
			if handle.get_ref()!=null:alive=true;break
		if not alive:return {"playbacks":handles.size(),"wait_ms":Time.get_ticks_msec()-started,"released":true}
		OS.delay_msec(2)
		await tree.process_frame
	push_error("Audio playback teardown deadline exceeded; batch is invalid")
	return {"playbacks":handles.size(),"wait_ms":Time.get_ticks_msec()-started,"released":false}
