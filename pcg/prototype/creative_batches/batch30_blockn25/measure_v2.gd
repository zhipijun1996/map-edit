extends RefCounted
static func snapshot(host) -> Dictionary:
	var out: Array=[]
	for p: ModuleMovingPlatform in host.context.module.moving_platforms:
		var clock: float=host.context.module.clock
		var current: Vector2=p.definition.at_time(clock)
		var previous: Vector2=p.definition.at_time(clock-1.0/60.0)
		var earlier: Vector2=p.definition.at_time(clock-2.0/60.0)
		var physical: Transform2D=PhysicsServer2D.body_get_state(p.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM)
		var state=PhysicsServer2D.body_get_direct_state(p.get_rid())
		var v: Vector2=state.linear_velocity if state!=null else Vector2.ZERO
		out.append({"id":str(p.definition.platform_id),"module_clock":clock,"definition_target":[current.x,current.y],"previous_tick_target":[previous.x,previous.y],"two_tick_target":[earlier.x,earlier.y],"node_pose":[p.position.x,p.position.y],"physics_server_pose":[physical.origin.x,physical.origin.y],"physics_server_velocity":[v.x,v.y]})
	return {"movers":out}
