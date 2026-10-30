extends "ideas_runner_v2.gd"
## Input-only policy: real projectile clearing, original Cell phase forecasts,
## side corridors and actual support contacts. No actor/resource/state writes.
var lower_id:="L1"
var upper_id:="L2"
var finish_x:=66.0
var clear_issued:=0
var clear_ready_frame:=-1
func make_fixture(data: Dictionary) -> void:
	lower_id="L1";upper_id="L2";finish_x=66;clear_issued=0;clear_ready_frame=-1
	await super.make_fixture(data)
func carrier(id: String):
	for p: ModuleMovingPlatform in context.module.moving_platforms:
		if str(p.definition.platform_id)==id:return p
	return null
func gear_x(id: String, after: float) -> float:
	for d in context.module.definition.saws:
		if str(d.source_id)==id:return d.at_time(context.module.clock+after).x
	return -10000
func g2_clear(after: float) -> bool:
	var left:=true;var right:=true
	for dt: float in [.35,.45,.55,.65,.75,.85]:
		var x:=gear_x("G2",after+dt);left=left and x<110;right=right and x>274
	return left or right
func supported(id: String) -> bool:return motor.is_on_floor() and str(context.snapshot().get("support_id",""))==id
func upper_choice(after: float) -> String:
	var result:="";var best:=350.0
	for id: String in ["L2","R2"]:
		var p=carrier(id);var y: float=p.definition.at_time(context.module.clock+after).y
		if y>=best and p.definition.at_time(context.module.clock+after+.1).y<=y:result=id;best=y
	return result
func can_board(p,travel: float) -> bool:
	var y: float=p.definition.at_time(context.module.clock+travel+1).y
	if y<610 or y>650 or p.definition.at_time(context.module.clock+travel+1.1).y>=y:return false
	for i: int in range(11,17):
		var dt:=travel+float(i)/10;var at: float=p.definition.at_time(context.module.clock+dt).y
		if at>=580 and at<=615 and g2_clear(dt) and not upper_choice(dt+1.1).is_empty():return true
	return false
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for c: Dictionary in copy:
			if str(c.get("trigger",{}).get("state","")).begins_with("revision_lift_"):c.trigger.state="grounded"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="revision_lift_clear":
		var enemy:=observed_enemy("air-enemy");return enemy==null or enemy.health.terminal
	if state=="revision_lift_choose_lower":
		if not motor.is_on_floor():return false
		for id: String in ["L1","R1"]:
			var edge:=20.0 if id=="L1" else 364.0
			if can_board(carrier(id),absf(motor.position.x-edge)/motor.tuning.ground_speed):lower_id=id;return true
		return false
	if state=="revision_lift_edge":return motor.is_on_floor() and absf(motor.position.x-(20 if lower_id=="L1" else 364))<2
	if state=="revision_lift_above_g1":return motor.position.y+18<656
	if state=="revision_lift_lower_support":return supported(lower_id)
	if state=="revision_lift_transfer":
		var p=carrier(lower_id)
		if not supported(lower_id) or p.position.y>615 or p.position.y<580 or not g2_clear(0):return false
		var next:=upper_choice(1.1)
		if next.is_empty():return false
		upper_id=next;return true
	if state=="revision_lift_lower_launch":return supported(lower_id) and absf(motor.position.x-(132 if lower_id=="L1" else 252))<2
	if state=="revision_lift_upper_support":return supported(upper_id)
	if state=="revision_lift_finish":
		if not supported(upper_id):return false
		var p=carrier(upper_id)
		if p.position.y<310:return false
		var choices: Array=[140.0,66.0] if upper_id=="L2" else [244.0,318.0]
		for x: float in choices:
			var travel:=absf(motor.position.x-x)/motor.tuning.ground_speed;var y: float=p.definition.at_time(context.module.clock+travel).y
			if y<315 or y>350:continue
			var safe:=true
			for dt: float in [.05,.1,.15,.2,.25,.3]:
				var actor_x:=x+signf(192-x)*minf(absf(192-x),motor.tuning.ground_speed*dt)
				if absf(actor_x-gear_x("G3",travel+dt))<50:safe=false
			if safe:finish_x=x;return true
		return false
	if state=="revision_lift_finish_edge":return supported(upper_id) and absf(motor.position.x-finish_x)<2
	return super.condition_met(state)
func clear_aim(enemy) -> Vector2:
	var target: Vector2=enemy.motor.global_position
	var visual: CourierVisual=motor.get_node("CourierVisual")
	var flight: float=target.distance_to(motor.global_position)/motor.tuning.projectile_speed
	target+=enemy.motor.velocity*flight
	var aim: Vector2=(target-motor.global_position).normalized()
	for iteration: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
	return aim
func control_plan(frame: int) -> Array:
	for c: Dictionary in plan:
		match str(c.get("revision_target","")):
			"edge":c.target_x=20 if lower_id=="L1" else 364
			"lower":c.target_x=66 if lower_id=="L1" else 318
			"lower_launch":c.target_x=132 if lower_id=="L1" else 252
			"upper":c.target_x=66 if upper_id=="L2" else 318
			"finish":c.target_x=finish_x
		if c.get("revision_transfer_shot",false):
			var length:=motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration
			var vertical:=clampf((motor.position.y-290)/length,.5,.98)
			c.direction=[-sqrt(1-vertical*vertical) if upper_id=="R2" else sqrt(1-vertical*vertical),vertical]
		if c.get("revision_final_shot",false):
			var dx:=clampf((motor.position.x-192)/(motor.tuning.shot_burst_speed*motor.tuning.shot_burst_duration),-.8,.8)
			c.direction=[dx,sqrt(1-dx*dx)]
	var requests:=super.control_plan(frame)
	if plan_index<plan.size() and plan[plan_index].get("trigger",{}).get("state","")=="revision_lift_clear" and clear_issued<48:
		var enemy:=observed_enemy("air-enemy")
		if enemy!=null and not enemy.health.terminal and motor.is_on_floor() and controller.action_resources.shot_charges>0 and controller.shoot_ability.cooldown_remaining<=.000001:
			var key:=10000+clear_issued
			if clear_ready_frame<0:clear_ready_frame=frame+maxi(0,1+timing_error(key))
			if frame>=clear_ready_frame:
				var aim:=disturbed_direction(clear_aim(enemy),key)
				controller.router.request_action(&"shoot_release",aim)
				requests.append({"type":"shoot_release","direction":[aim.x,aim.y],"plan_index":plan_index,"noise_key":key})
				clear_issued+=1;clear_ready_frame=-1
	return requests
