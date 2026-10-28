extends SceneTree
## GUI smoke through actual Input events, not Router/body/resource writes.
const TEARDOWN = preload("res://plains_lifecycle.gd")
var scene
var out := ""

func _initialize() -> void:
	run.call_deferred()

func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code; event.physical_keycode = code; event.pressed = pressed
	Input.parse_input_event(event)

func ticks(count: int) -> void:
	for _i: int in count:
		await physics_frame
		await process_frame

func run() -> void:
	var args := OS.get_cmdline_user_args()
	for i: int in args.size():
		if args[i] == "--out" and i + 1 < args.size(): out = args[i + 1]
	if out.is_empty(): push_error("--out required"); quit(2); return
	DirAccess.make_dir_recursive_absolute(out)
	var source := (get_script() as Script).resource_path.get_base_dir().path_join("r2_manual_scene.tscn")
	scene = (load(source) as PackedScene).instantiate(); root.add_child(scene)
	for _i: int in 120:
		await ticks(1)
		if scene.prepared and scene.manual_input_armed and scene.manual_extra != null and scene.motor.is_on_floor(): break
	if not scene.prepared or not scene.manual_input_armed or scene.manual_extra == null or not scene.motor.is_on_floor():
		push_error("manual scene did not become ready with grounded original actor"); quit(3); return
	var initial: Vector2 = scene.motor.position
	key(KEY_D, true); key(KEY_SPACE, true)
	await ticks(8)
	key(KEY_SPACE, false)
	await ticks(10)
	var point := Vector2(640, 610)
	var motion := InputEventMouseMotion.new(); motion.position = point; motion.global_position = point
	Input.parse_input_event(motion)
	var down := InputEventMouseButton.new(); down.button_index = MOUSE_BUTTON_LEFT
	down.position = point; down.global_position = point; down.pressed = true
	Input.parse_input_event(down)
	await ticks(1)
	var up := InputEventMouseButton.new(); up.button_index = MOUSE_BUTTON_LEFT
	up.position = point; up.global_position = point; up.pressed = false
	Input.parse_input_event(up)
	await ticks(12)
	key(KEY_D, false)
	var before_map := bool(scene.overview)
	key(KEY_M, true); await ticks(1); key(KEY_M, false)
	var map_toggled := bool(scene.overview) != before_map
	key(KEY_M, true); await ticks(1); key(KEY_M, false)
	await ticks(5)
	scene.export_attempt()
	await RenderingServer.frame_post_draw
	var png := out.path_join("manual-scene.png")
	var image_result := root.get_texture().get_image().save_png(png)
	var requests := 0
	for value: Dictionary in scene.recording: requests += value.requested_router_queue_before_controller.size()
	var result := {"schema": "pcg/r2-manual-gui-smoke/v1", "case_id": scene.case_data.id,
		"platforms": scene.case_data.platforms.size(), "nodes": scene.case_data.r2_semantics.nodes.size(),
		"gates": scene.case_data.get("gate_specs", []).size(), "initial_position": [initial.x, initial.y],
		"final_position": [scene.motor.position.x, scene.motor.position.y], "events": scene.event_counts,
		"map_toggle_worked": map_toggled, "recorded_frames": scene.recording.size(),
		"grounded_pre_input_entry": scene.manual_entry_snapshot.get("grounded", false),
		"initial_place_discovered": scene.manual_extra.report().get("visited_nodes", []).has("r5"),
		"observed_router_requests": requests, "screenshot_error": image_result,
		"human_playtest": false, "input_method": "Input.parse_input_event → original KeyboardMouseAdapter → original Router/Controller/Motor",
		"scope": "automated native GUI smoke only; no human fun or full-route manual approval"}
	result["ok"] = scene.event_counts.jump >= 1 and scene.event_counts.shot >= 1 and map_toggled and requests >= 2 and image_result == OK and scene.motor.position.distance_to(initial) > 10 and result.grounded_pre_input_entry and result.initial_place_discovered
	var file := FileAccess.open(out.path_join("result.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(result)); file.close()
	print("R2_MANUAL_SMOKE ", JSON.stringify(result))
	scene.prepared = false; scene.context.freeze()
	var cleanup: Dictionary = await TEARDOWN.dispose(self, scene.world, scene.controller)
	print("R2_MANUAL_SMOKE_CLEANUP ", JSON.stringify(cleanup))
	scene.world = null; scene.motor = null; scene.controller = null; scene.context = null; scene.cells = null
	quit(0 if result.ok and cleanup.released else 3)
