extends "res://main_plains.gd"
## Interactive map / native movie adapter. Only original Router inputs move player.
const MAP_OBSERVER = preload("map_observer.gd")
const MAP_OVERLAY = preload("map_overlay.gd")
var map_observer
var map_overlay
var force_replay := false
var movie_mode := false
var recording_trace: Array = []
var trace_path := ""
var map_png := ""
var quit_after_capture := false
var hold_frames := 0
var movie_logged := false
var closing := false
var show_index := 0

func _ready() -> void:
	var source := ""
	var args := OS.get_cmdline_user_args()
	for i: int in args.size():
		if args[i] == "--cases-json" and i + 1 < args.size(): source = args[i + 1]
		if args[i] == "--case" and i + 1 < args.size(): show_index = int(args[i + 1])
		if args[i] == "--trace-json" and i + 1 < args.size(): trace_path = args[i + 1]
		if args[i] == "--whole-map" and i + 1 < args.size(): map_png = args[i + 1]
		if args[i] == "--replay": force_replay = true
		if args[i] == "--movie": movie_mode = true; force_replay = true
		if args[i] == "--quit-after-capture": quit_after_capture = true
	if source.is_empty(): push_error("Missing --cases-json"); get_tree().quit(2); return
	var frozen: Variant = JSON.parse_string(FileAccess.get_file_as_string(source))
	if not frozen is Dictionary or show_index < 0 or show_index >= frozen.get("cases", []).size():
		push_error("Invalid map cases JSON / index"); get_tree().quit(2); return
	super._ready()
	cases = frozen.cases
	selection.clear()
	for value: Dictionary in cases: selection.add_item(str(value.get("title", value.id)))
	selection.select(show_index)
	if movie_mode: selection.disabled = true
	var rows := ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text = "MAP DIRECTOR · 风铃平原闭环候选 · 真实连续物理 / 趣味待评"
	if movie_mode:
		for child: Node in rows.get_child(1).get_children():
			if child is BaseButton: child.disabled = true
		set_process_unhandled_input(false)
	DisplayServer.window_set_title("Disordered Clock · Map-driven module library · isolated playable")

func rebuild(new_mode: String) -> void:
	await super.rebuild("replay" if force_replay else new_mode)
	if not prepared: return
	map_observer = MAP_OBSERVER.new()
	map_observer.configure(case_data, controller, context)
	map_overlay = MAP_OVERLAY.new()
	map_overlay.semantics = case_data.get("map_semantics", {})
	map_overlay.observer = map_observer
	map_overlay.z_index = 30
	world.add_child(map_overlay)
	recording_trace.clear(); hold_frames = 0; movie_logged = false; closing = false
	ability_label.text = "移动 · 普通单跳 · 射击反冲 · A/D 移动 / 空格跳 / 鼠标松开射击 · R 重试"
	if not map_png.is_empty(): capture_whole_map.call_deferred()
	print("MAP_NATIVE_START ", JSON.stringify({"case_id": case_data.id,
		"mode": mode, "physics_hz": 60, "source_commit": "12f6cb006d7119598e3235f4ca4f7323e4c9d092",
		"module_sha256": case_data.get("module_sha256", "UNKNOWN"), "human_playtest": false}))

func capture_dynamic_frame() -> void:
	if warmup_left > 0: super.capture_dynamic_frame(); return
	if map_observer != null: map_observer.observe(frame, controller, context, cells.events)
	var value := {"frame": frame, "x": motor.position.x, "y": motor.position.y,
		"vx": motor.velocity.x, "vy": motor.velocity.y, "grounded": motor.is_on_floor(),
		"axis": controller.router.axis, "requested": actions.get(frame, []).duplicate(true),
		"shot_charges": controller.action_resources.shot_charges,
		"shot_cooldown": controller.shoot_ability.cooldown_remaining,
		"jumps_used": controller.jump_ability.used_jumps, "jump_maximum": controller.jump_ability.maximum_jumps(),
		"energy": controller.actor_resources.stamina.current, "hp": controller.actor_resources.health.current,
		"traversal_state": str(controller.traversal.state),
		"real_velocity": [motor.get_real_velocity().x, motor.get_real_velocity().y],
		"normal_velocity": [motor.normal_velocity.x, motor.normal_velocity.y],
		"plains": cells.snapshot(), "events": event_counts.duplicate(true)}
	value.merge(context.snapshot())
	super.capture_dynamic_frame()
	value.goal_stable_frames = stable_frames
	value.map = map_observer.report()
	recording_trace.append(value)
	if finished and not value.map.ok:
		status.text = "已结束，但本条地图策略的检查点 / 奖励 / 风铃条件未完整满足；不计通过"
	if not finished:
		status.text = "连续世界 · 已到检查点 %d/%d · 奖励金币 %d · HP %.0f" % [
			map_observer.next_checkpoint, map_observer.required.size(), map_observer.wallet.balance,
			controller.actor_resources.health.current]

func prepare_dynamic_frame() -> void:
	if warmup_left == 0 and frame == 0 and map_observer != null:
		map_observer.observe(-1, controller, context, cells.events)
	super.prepare_dynamic_frame()

func _physics_process(_delta: float) -> void:
	if not movie_mode or closing or not prepared or not finished: return
	if not movie_logged:
		var result := {"case_id": case_data.id, "module_sha256": case_data.get("module_sha256", "UNKNOWN"),
			"frame": frame, "safe": safe, "stable_frames": stable_frames,
			"hp": controller.actor_resources.health.current, "position": [motor.position.x, motor.position.y],
			"events": event_counts, "plains": cells.snapshot(), "map_validation": map_observer.report(),
			"returns": context.returns.size(), "human_playtest": false}
		print("MAP_NATIVE_RESULT ", JSON.stringify(result)); movie_logged = true
		if not safe or stable_frames < 6 or not result.map_validation.ok:
			closing = true; finish_native.call_deferred(3); return
	hold_frames += 1
	if hold_frames >= 60: closing = true; finish_native.call_deferred(0)

func capture_whole_map() -> void:
	for _i: int in 8: await get_tree().process_frame
	if not prepared or not is_instance_valid(world): return
	context.freeze(); controller.router.clear("map_overview_capture")
	world.process_mode = Node.PROCESS_MODE_DISABLED
	display.set_process(false)
	ui.visible = false
	var bounds := rect_v3(case_data.world_bounds)
	var camera: Camera2D = display.camera
	camera.position = bounds.get_center()
	var view := get_viewport_rect().size
	var factor := minf(view.x / (bounds.size.x + 120), view.y / (bounds.size.y + 120))
	camera.zoom = Vector2(factor, factor)
	camera.force_update_scroll()
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(map_png.get_base_dir())
	var result := get_viewport().get_texture().get_image().save_png(map_png)
	print("MAP_WHOLE_CAPTURE ", JSON.stringify({"path": map_png, "error": result,
		"case_id": case_data.id, "bounds": case_data.world_bounds,
		"player_position_unchanged_for_camera": true, "actual_godot_world": true}))
	if quit_after_capture: closing = true; await finish_native(0 if result == OK else 5)

func finish_native(code: int) -> void:
	if not trace_path.is_empty():
		DirAccess.make_dir_recursive_absolute(trace_path.get_base_dir())
		var file := FileAccess.open(trace_path, FileAccess.WRITE)
		file.store_string(JSON.stringify({"schema": "pcg/map-native-trace/v1", "case_id": case_data.id,
			"module_sha256": case_data.get("module_sha256", "UNKNOWN"), "physics_hz": 60,
			"frames": recording_trace, "map_validation": map_observer.report()})); file.close()
	var cleanup: Dictionary = await LIFECYCLE.dispose(get_tree(), world, controller)
	prepared = false; world = null; controller = null; motor = null; context = null; cells = null
	print("MAP_NATIVE_CLEANUP ", JSON.stringify(cleanup))
	get_tree().quit(code if cleanup.released else 4)
