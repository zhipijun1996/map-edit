extends "review040_runner_v2.gd"
const EXIT_AIR_DEFINITION=preload("air_port_definition_v1.gd")
var review040_air_streak:=0
func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	var original:=super.definition_for(data)
	if data.get("air_port_contracts",[]).is_empty():return original
	var result=EXIT_AIR_DEFINITION.new()
	for property: Dictionary in original.get_property_list():
		if int(property.usage)&PROPERTY_USAGE_STORAGE and property.name!="script":result.set(property.name,original.get(property.name))
	for port: Dictionary in data.air_port_contracts:
		assert(port.surface=="AIR" and port.face=="BOTTOM" and port.permission=="OUTPUT")
		result.air_points.append(Vector2(port.stagingPosition[0],port.stagingPosition[1]))
	if data.has("air_probe_points"):
		for p: Array in data.air_probe_points:result.air_points.append(Vector2(p[0],p[1]))
	return result
func condition_met(state: String) -> bool:
	if state=="enemy_below":
		if not super.condition_met(state):return false
		var q: Dictionary=plan[plan_index].enemy_window
		if not q.has("required_side"):return true
		var enemy:=observed_enemy(str(q.id))
		return (enemy.motor.position.x-motor.position.x)*float(q.required_side)>=0
	return super.condition_met(state)
func make_fixture(data: Dictionary) -> void:
	review040_air_streak=0
	await super.make_fixture(data)
	if data.has("air_goal_probe"):context.anchor_ready=true
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if not active:return
	var boundary: Array=[]
	if current_case.has("air_goal_probe"):boundary=current_case.air_goal_probe.boundary
	else:
		for p: Dictionary in current_case.get("air_port_contracts",[]):
			if p.id==current_case.route_spec.to_port:boundary=p.position
	if boundary.is_empty():return
	var crossed:=motor.position.y-18>=float(boundary[1]) and motor.position.y<=float(boundary[1])+128 and absf(motor.position.x-float(boundary[0]))+12<=32 and motor.velocity.y>0
	review040_air_streak=review040_air_streak+1 if crossed else 0;stable_v3=review040_air_streak;reached_v3=reached_v3 or crossed;captured[-1].air_exit_complete_frames=review040_air_streak
func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if review040_air_streak>0:result.air_exit_complete_frames=review040_air_streak;result.exit_contract="downward AIR full-body crossing; no grounded stability"
	return result
