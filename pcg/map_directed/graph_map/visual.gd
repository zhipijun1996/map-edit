extends "../catalog_feed/visual.gd"
## Same input-only combat adapter as the real headless worker.
func control_plan(frame:int)->Array:
	if pilot==null or extra==null or not extra.has_method("duel_input"):return super.control_plan(frame)
	var leg:Dictionary=pilot.active_leg()
	if not leg.has("boss_duel"):return super.control_plan(frame)
	var value:Dictionary=extra.duel_input(str(leg.boss_duel),frame,leg.target.position)
	if value.get("done",false):return super.control_plan(frame)
	return value.get("requested",[])
func make_fixture(data:Dictionary)->void:
	await super.make_fixture(data)
	if not setup_error.is_empty():return
	(status_label.get_parent().get_child(0)as Label).text="风铃平原 · 多路线联合空间原型 · 程序输入回放"

func prepare_dynamic_frame()->void:
	# Install the existing frozen-input consumer before Catalog's legacy
	# prepare override. That override does not replace an installed replay pilot.
	if movie_mode and warmup_left==0 and not pilot is REPLAY_PILOT:
		for row:Dictionary in current_case.get("recorded_frames",[]):
			if row.has("axis_bits"):row.axis=bytes_to_var(str(row.axis_bits).hex_decode())
		var observer=REPLAY_PILOT.new()
		var error:String=observer.configure(self,current_case)
		if not error.is_empty():setup_error=error
		pilot=observer
	super.prepare_dynamic_frame()

func capture_dynamic_frame()->void:
	var before:int=captured.size()
	super.capture_dynamic_frame()
	if captured.size()>before:captured[-1]["axis_bits"]=var_to_bytes(controller.router.axis).hex_encode()
