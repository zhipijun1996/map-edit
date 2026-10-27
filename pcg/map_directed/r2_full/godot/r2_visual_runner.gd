extends "r2_runner.gd"
## Same concrete world and Node schedule, with read-only GUI/camera observation.
const REPLAY_PILOT = preload("r2_replay_pilot.gd")
const CAMERA_DRIVER = preload("r2_camera.gd")
const ANNOTATIONS = preload("r2_annotations.gd")
var camera: Camera2D
var camera_driver
var annotations
var ui: CanvasLayer
var status_label: Label
var selected_case: Dictionary = {}
var recording_trace_path := ""
var movie_mode := false
var replay_mode := false
var whole_map_path := ""
var visual_result: Dictionary = {}

func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	if not setup_error.is_empty(): return
	camera = Camera2D.new(); camera.position = motor.global_position
	world.add_child(camera); camera.make_current()
	camera_driver = CAMERA_DRIVER.new(); camera_driver.camera = camera; camera_driver.actor = motor
	root.add_child(camera_driver)
	annotations = ANNOTATIONS.new(); annotations.semantics = case.get("r2_semantics", {})
	annotations.camera = camera; annotations.z_index = 80; world.add_child(annotations)
	ui = CanvasLayer.new(); root.add_child(ui)
	var panel := PanelContainer.new(); panel.position = Vector2(12, 10); panel.size = Vector2(1000, 72); ui.add_child(panel)
	var rows := VBoxContainer.new(); panel.add_child(rows)
	var title := Label.new(); title.text = "完整 R2 风铃平原 · 真实 Godot 隔离地图 · 输入回放 / 趣味待评"; rows.add_child(title)
	status_label = Label.new(); status_label.text = str(case.get("title", case.get("id", "R2"))); rows.add_child(status_label)

func prepare_dynamic_frame() -> void:
	if replay_mode and warmup_left == 0 and not pilot is REPLAY_PILOT:
		var observer = REPLAY_PILOT.new()
		var error: String = observer.configure(self, current_case)
		if not error.is_empty(): setup_error = error
		pilot = observer
	super.prepare_dynamic_frame()

func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	if is_instance_valid(status_label) and pilot != null and is_instance_valid(controller):
		status_label.text = "%s · %.1fs · leg %d/%d · HP %.0f · 单跳 / 反冲 · 无中途重建" % [
			str(current_case.get("title", current_case.get("id", "R2"))), current_frame / 60.0,
			pilot.index, pilot.program.size(), controller.actor_resources.health.current]

func _run() -> void:
	var input_path := ""
	var output_path := ""
	var index := 0
	var args := OS.get_cmdline_user_args()
	for i: int in args.size():
		if args[i].begins_with("--input="): input_path = args[i].trim_prefix("--input=")
		if args[i].begins_with("--output="): output_path = args[i].trim_prefix("--output=")
		if args[i] == "--cases-json" and i + 1 < args.size(): input_path = args[i + 1]
		if args[i] == "--case" and i + 1 < args.size(): index = int(args[i + 1])
		if args[i] == "--whole-map" and i + 1 < args.size(): whole_map_path = args[i + 1]
		if args[i] == "--trace-json" and i + 1 < args.size(): recording_trace_path = args[i + 1]
		if args[i] == "--movie": movie_mode = true; replay_mode = true
		if args[i] == "--replay": replay_mode = true
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(input_path))
	if not data is Dictionary or not data.get("cases") is Array or index < 0 or index >= data.cases.size():
		push_error("Invalid R2 visual case input"); quit(2); return
	selected_case = data.cases[index]
	if not whole_map_path.is_empty():
		await capture_whole_map(selected_case)
		return
	print("R2_NATIVE_START ", JSON.stringify({"case_id": selected_case.id, "replay": replay_mode,
		"physics_hz": 60, "human_playtest": false}))
	visual_result = await run_case(selected_case)
	if not recording_trace_path.is_empty():
		DirAccess.make_dir_recursive_absolute(recording_trace_path.get_base_dir())
		var trace_file := FileAccess.open(recording_trace_path, FileAccess.WRITE)
		trace_file.store_string(JSON.stringify({"schema": "pcg/r2-native-trace/v1", "case_id": selected_case.id,
			"physics_hz": 60, "replay": replay_mode, "result": visual_result})); trace_file.close()
	if not output_path.is_empty():
		var output := FileAccess.open(output_path, FileAccess.WRITE)
		output.store_string(JSON.stringify({"results": [visual_result]})); output.close()
	var summary := visual_result.duplicate()
	summary.erase("frames"); summary.erase("plains"); summary.erase("pilot")
	summary["legs_completed"] = visual_result.get("pilot", {}).get("legs_completed", 0)
	print("R2_NATIVE_RESULT ", JSON.stringify(summary))
	if movie_mode:
		for _frame: int in 60: await physics_frame
	var code := 0 if visual_result.get("ok", false) else 3
	await dispose_visual(code)

func capture_whole_map(case: Dictionary) -> void:
	current_case = case; setup_error = ""; goal_v3 = rect(case.goal)
	await make_fixture(case)
	if not setup_error.is_empty(): push_error(setup_error); await dispose_visual(3); return
	world.process_mode = Node.PROCESS_MODE_DISABLED
	camera_driver.follow = false
	ui.visible = false
	annotations.overview = true
	var bounds := rect(case.get("overview_bounds",case.world_bounds))
	camera.position = bounds.get_center()
	var view := root.get_visible_rect().size
	var factor := minf(view.x / (bounds.size.x + 120.0), view.y / (bounds.size.y + 120.0))
	camera.zoom = Vector2(factor, factor); camera.force_update_scroll()
	annotations.queue_redraw()
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(whole_map_path.get_base_dir())
	var error := root.get_texture().get_image().save_png(whole_map_path)
	print("R2_WHOLE_MAP_CAPTURE ", JSON.stringify({"case_id": case.id, "file": whole_map_path,
		"error": error, "world_bounds": case.world_bounds, "camera_bounds":case.get("overview_bounds",case.world_bounds), "viewport": [view.x, view.y],
		"actual_platforms": case.platforms.size(), "one_way_platforms": case.get("one_way_platform_indices", []).size(),
		"state_gates": case.get("gate_specs", []).size(), "player_position": [motor.position.x, motor.position.y],
		"player_position_not_changed_for_capture": true, "scope": "actual complete instantiated world at initial state, camera-only overview"}))
	await dispose_visual(0 if error == OK else 5)

func dispose_visual(code: int) -> void:
	if is_instance_valid(world):
		var cleanup: Dictionary = await LIFECYCLE.dispose(self, world, controller)
		print("R2_NATIVE_CLEANUP ", JSON.stringify(cleanup))
		if not cleanup.released: code = 4
	world = null; motor = null; controller = null; context = null; cells = null
	if is_instance_valid(camera_driver): camera_driver.queue_free()
	if is_instance_valid(ui): ui.queue_free()
	await process_frame
	quit(code)
