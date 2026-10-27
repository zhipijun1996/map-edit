extends "res://main_plains.gd"
## Full concrete R2 manual scene: original keyboard/mouse Router and physics.
const R2_CAMERA = preload("r2_camera.gd")
const R2_LABELS = preload("r2_annotations.gd")
var manual_extra
var camera_driver
var labels
var source_path := "res://r2_cases.json"
var source_sha256 := ""
var recording: Array = []
var input_queue_before_controller: Array = []
var recording_limit := 18000
var recording_truncated := false
var cell_cursor := 0
var cancellation_events: Array = []
var archived_attempts: Array = []
var evicted_attempts := 0
var attempt_serial := 0
var overview := false
var export_notice := ""
var export_button: Button
var manual_report: Dictionary = {}
var manual_entry_snapshot: Dictionary = {}
var manual_input_armed := false

func _ready() -> void:
	var selected := 0
	var args := OS.get_cmdline_user_args()
	for i: int in args.size():
		if args[i] == "--cases-json" and i + 1 < args.size(): source_path = args[i + 1]
		if args[i] == "--case" and i + 1 < args.size(): selected = int(args[i + 1])
	if not FileAccess.file_exists(source_path):
		push_error("Full R2 cases missing: " + source_path); get_tree().quit(2); return
	var frozen: Variant = JSON.parse_string(FileAccess.get_file_as_string(source_path))
	if not frozen is Dictionary or not frozen.get("cases") is Array or frozen.cases.is_empty():
		push_error("Invalid full R2 cases"); get_tree().quit(2); return
	source_sha256 = FileAccess.get_sha256(source_path)
	super._ready()
	cases = frozen.cases
	selection.clear()
	for value: Dictionary in cases: selection.add_item(str(value.get("title", value.id)))
	selection.select(clampi(selected, 0, cases.size() - 1))
	var rows := ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text = "完整 R2 风铃平原 · 手动探索候选 · 趣味与正式准入待评"
	var bar := rows.get_child(1)
	for button: Node in bar.get_children():
		if button is Button and "Replay" in button.text: button.hide()
	var map_button := Button.new(); map_button.text = "地图 M"; bar.add_child(map_button)
	map_button.pressed.connect(toggle_overview)
	export_button = Button.new(); export_button.text = "导出输入记录"; bar.add_child(export_button)
	export_button.pressed.connect(export_attempt)
	DisplayServer.window_set_title("Disordered Clock · Complete R2 Plains · Manual Candidate")

func rebuild(_new_mode: String) -> void:
	if not recording.is_empty():
		archived_attempts.append(attempt_payload())
		if archived_attempts.size() > 1:
			archived_attempts.pop_front(); evicted_attempts += 1
	await super.rebuild("manual")
	if not prepared: return
	attempt_serial += 1; recording = []; recording_truncated = false; cell_cursor = 0
	cancellation_events = []; input_queue_before_controller = []; overview = false; export_notice = ""
	manual_extra = null; manual_report = {}; manual_entry_snapshot = {}; manual_input_armed = false
	motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(false)
	recording_limit = clampi(int(case_data.get("manual_record_limit", 18000)), 1, 36000)
	controller.router.cancelled.connect(func(reason: String): cancellation_events.append({"frame": frame, "reason": reason}))
	var extra_path := str(case_data.get("extra_script", (get_script() as Script).resource_path.get_base_dir().get_base_dir().path_join("state_extra.gd")))
	if not FileAccess.file_exists(extra_path):
		reject_manual("r2_state_adapter_missing"); return
	var script: Script = load(extra_path)
	if script == null: reject_manual("invalid_r2_state_adapter"); return
	manual_extra = script.new(); manual_extra.setup(case_data, world, controller, context)
	var report: Dictionary = manual_extra.report()
	if not str(report.get("error", "")).is_empty(): reject_manual(str(report.error)); return
	manual_report = report
	# The original lab observer contributes no physics. Hide its diagnostic draw
	# and reuse its real Camera2D; control remains the original keyboard adapter.
	display.set_process(false); display.hide(); display.camera.position = motor.global_position
	camera_driver = R2_CAMERA.new(); camera_driver.camera = display.camera; camera_driver.actor = motor
	world.add_child(camera_driver)
	labels = R2_LABELS.new(); labels.semantics = case_data.get("r2_semantics", {}); labels.camera = display.camera
	labels.z_index = 80; world.add_child(labels)
	ability_label.text = "A/D 移动 · 空格普通单跳 · 鼠标松开射击反冲 · S 下穿单向台 · M 地图 · R 重试"
	telemetry_label.hide()

func announce_ready() -> void:
	print("R2_MANUAL_READY ", JSON.stringify({"case_id": case_data.id, "attempt": attempt_serial,
		"case_file_sha256": source_sha256, "platforms": case_data.platforms.size(),
		"one_way_platforms": case_data.get("one_way_platform_indices", []).size(),
		"nodes": case_data.get("r2_semantics", {}).get("nodes", []).size(),
		"state_gates": case_data.get("gate_specs", []).size(),
		"original_keyboard_mouse_adapter": true, "automatic_pilot": false,
		"physics_baseline": "12f6cb006d7119598e3235f4ca4f7323e4c9d092"}))

func reject_manual(reason: String) -> void:
	setup_error = reason; finished = true; status.text = "地图初始化失败：" + reason
	context.freeze(); controller.router.clear("r2_manual_setup_rejected")
	world.process_mode = Node.PROCESS_MODE_DISABLED
	push_error(reason)

func prepare_dynamic_frame() -> void:
	context.frame = -warmup_left if warmup_left > 0 else frame
	if warmup_left > 0: controller.router.set_move_axis(0.0)
	elif manual_entry_snapshot.is_empty() and manual_extra != null:
		manual_entry_snapshot = {"frame": -1, "position": [motor.position.x, motor.position.y],
			"grounded": motor.is_on_floor(), "velocity": [motor.velocity.x, motor.velocity.y],
			"air_shots": controller.action_resources.shot_charges,
			"jumps_used": controller.jump_ability.used_jumps,
			"stamina": controller.actor_resources.stamina.current, "health": controller.actor_resources.health.current,
			"shot_cooldown": controller.shoot_ability.cooldown_remaining,
			"plains": manual_cell_state(),
			"sampling_point": "before_first_original_router_consumption_after_warmup"}
		manual_extra.capture(-1, manual_entry_snapshot)
		manual_input_armed = true
		motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(true)
		announce_ready()
	input_queue_before_controller = []
	# Read-only observation before the original Controller consumes the queue.
	# These requests may still be rejected by the original epoch/age/resource rules.
	var queued: Variant = controller.router.get("_queue")
	if queued is Array:
		for action: Dictionary in queued:
			var direction: Vector2 = action.get("direction", Vector2.ZERO)
			input_queue_before_controller.append({"type": str(action.type),
				"direction": [direction.x, direction.y], "sequence": action.get("sequence"),
				"epoch": action.get("epoch"), "timestamp": action.get("timestamp")})
	before_grounded = motor.is_on_floor(); before_state = controller.traversal.state
	before_used = controller.jump_ability.used_jumps

func manual_cell_state() -> Dictionary:
	var bells: Array = []
	var enemies: Array = []
	for latch: ShotLatch in cells.latches:
		bells.append({"id": latch.link_id, "open": latch.is_open,
			"open_count": latch.open_count, "sequence_step": latch.sequence_step})
	for actor: EnemyActor in cells.enemies:
		enemies.append({"id": str(actor.definition.stable_id), "position": [actor.motor.position.x, actor.motor.position.y],
			"hp": actor.health.current, "dead": actor.health.terminal})
	return {"bells": bells, "enemies": enemies}

func capture_dynamic_frame() -> void:
	var contacts: Array = context.contacts_now()
	if not contacts.is_empty(): safe = false; context.contact_history.append({"frame": context.frame, "contacts": contacts})
	if cells != null and not cells.player_damage.is_empty(): safe = false
	if warmup_left > 0: warmup_left -= 1; return
	var position_now := motor.global_position
	var bounds := rect_v3(case_data.world_bounds)
	if not bounds.has_point(position_now):
		safe = false; finished = true; status.text = "离开地图边界 · R 重试"
	if context.fatal: finished = true; status.text = "本次探索死亡 · R 重试"
	last_snapshot = context.snapshot()
	var observed := {"frame": frame, "position": [position_now.x, position_now.y],
		"x": position_now.x, "y": position_now.y,
		"velocity": [motor.velocity.x, motor.velocity.y],
		"normal_velocity": [motor.normal_velocity.x, motor.normal_velocity.y],
		"real_velocity": [motor.get_real_velocity().x, motor.get_real_velocity().y],
		"grounded": motor.is_on_floor(), "axis": controller.router.axis,
		"requested_router_queue_before_controller": input_queue_before_controller.duplicate(true),
		"accepted_event_counts": event_counts.duplicate(true),
		"air_shots": controller.action_resources.shot_charges,
		"jumps_used": controller.jump_ability.used_jumps,
		"stamina": controller.actor_resources.stamina.current, "health": controller.actor_resources.health.current,
		"shot_cooldown": controller.shoot_ability.cooldown_remaining,
		"traversal_state": str(controller.traversal.state), "dynamic": last_snapshot,
		"plains": manual_cell_state(),
		"cell_events_delta": cells.events.slice(cell_cursor).duplicate(true)}
	cell_cursor = cells.events.size()
	if manual_extra != null: manual_extra.capture(frame, observed)
	if recording.size() < recording_limit: recording.append(observed)
	else: recording_truncated = true
	var goal := rect_v3(case_data.goal)
	var at_goal := goal.has_point(position_now) and motor.is_on_floor() and motor.get_real_velocity().length() <= 1.0
	stable_frames = stable_frames + 1 if at_goal else 0
	if frame % 15 == 0 and not finished:
		var report: Dictionary = manual_extra.report() if manual_extra != null else {}
		manual_report = report
		status.text = "已发现 %d/%d 场所 · 金币 %d · HP %.0f%s%s" % [
			report.get("visited_nodes", []).size(), case_data.get("r2_semantics", {}).get("nodes", []).size(),
			int(report.get("wallet_balance", 0)), controller.actor_resources.health.current,
			" · 已抵达目标，可继续探索" if stable_frames >= 6 else "",
			" · 记录已达上限" if recording_truncated else ""]
		if not export_notice.is_empty(): status.text += " · " + export_notice
	metric.text = "%.1fs · 空射%d · %s" % [frame / 60.0, controller.action_resources.shot_charges, "地图" if overview else "手动"]
	frame += 1
	if OS.has_feature("web"):
		var state := {"id": case_data.id, "frame": frame, "position": [position_now.x, position_now.y],
			"hp": controller.actor_resources.health.current, "safe": safe, "finished": finished,
			"mode": "manual", "platforms": case_data.platforms.size(), "recorded_frames": recording.size(),
			"recording_truncated": recording_truncated, "source_case_sha256": source_sha256,
			"nodes": case_data.get("r2_semantics", {}).get("nodes", []).size(),
			"state_gates": case_data.get("gate_specs", []).size(), "world_bounds": case_data.world_bounds,
			"capabilities": capabilities, "manual_original_input": true,
			"manual_input_armed": manual_input_armed,
			"visited_nodes": manual_report.get("visited_nodes", []),
			"wallet_balance": manual_report.get("wallet_balance", 0),
			"opened_flags": manual_report.get("opened_flags", [])}
		JavaScriptBridge.eval("window.__r2ManualState=" + JSON.stringify(state), true)
	if finished:
		context.freeze(); controller.router.clear("r2_manual_finished"); world.process_mode = Node.PROCESS_MODE_DISABLED

func toggle_overview() -> void:
	if not prepared or not is_instance_valid(display.camera): return
	overview = not overview
	camera_driver.follow = not overview; labels.overview = overview
	if overview:
		var bounds := rect_v3(case_data.world_bounds)
		var view := get_viewport_rect().size
		var factor := minf(view.x / (bounds.size.x + 120.0), view.y / (bounds.size.y + 120.0))
		display.camera.position = bounds.get_center(); display.camera.zoom = Vector2(factor, factor)
	else:
		display.camera.zoom = Vector2.ONE; display.camera.position = motor.global_position
	display.camera.force_update_scroll()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_M:
		toggle_overview(); get_viewport().set_input_as_handled(); return
	super._unhandled_input(event)

func attempt_payload() -> Dictionary:
	return {"schema": "pcg/r2-manual-attempt/v1", "attempt": attempt_serial,
		"case_id": case_data.get("id", "UNKNOWN"), "case_file_sha256": source_sha256,
		"physics_baseline": "12f6cb006d7119598e3235f4ca4f7323e4c9d092", "physics_hz": 60,
		"control_source": "actual original keyboard/mouse adapter; read-only Router queue before Controller",
		"frames": recording.duplicate(true), "recorded_frame_limit": recording_limit,
		"recording_truncated": recording_truncated, "total_elapsed_frames": frame,
		"cancellations": cancellation_events.duplicate(true), "safe": safe,
		"entry_snapshot": manual_entry_snapshot.duplicate(true),
		"setup_error": setup_error,
		"extra": manual_extra.report() if manual_extra != null else {},
		"scope": "observed manual input and physical states; automated browser input is not human fun or playtest approval"}

func export_attempt() -> void:
	if not prepared: return
	var payload := {"schema": "pcg/r2-manual-recording/v1", "current": attempt_payload(),
		"previous_retained_attempts": archived_attempts, "older_attempts_evicted": evicted_attempts}
	var text := JSON.stringify(payload)
	var name := "r2-attempt-%d-%d.json" % [Time.get_unix_time_from_system(), attempt_serial]
	if OS.has_feature("web"):
		JavaScriptBridge.download_buffer(text.to_utf8_buffer(), name, "application/json")
		export_notice = "输入记录已下载"
	else:
		DirAccess.make_dir_recursive_absolute("user://r2-manual-attempts")
		var path := "user://r2-manual-attempts/" + name
		var file := FileAccess.open(path, FileAccess.WRITE)
		file.store_string(text); file.close()
		export_notice = "输入记录已保存"
		print("R2_MANUAL_RECORD_SAVED ", JSON.stringify({"path": ProjectSettings.globalize_path(path),
			"case_id": case_data.id, "frames": recording.size(), "truncated": recording_truncated}))
