extends "../valley_complete/pilot.gd"
## A recoil may land on an explicitly declared higher one-way ledge. Use the
## original drop input to reach the exact required support; never move/refill.
func tick(frame: int) -> Array:
	var requested:=super.tick(frame)
	if failed or completed:return requested
	var leg:=active_leg()
	if leg.get("kind","")!="module" or host.plan_index<host.plan.size():return requested
	var higher:bool=host.motor.global_position.y<float(leg.target.position[1])-1.
	var transit:Array=leg.target.get("allowed_transit_support_indices",[])
	if higher and host.motor.is_on_floor() and host.on_one_way_support() and not transit.is_empty() and host.touches_supports(transit):
		var interval:=ceili(host.motor.tuning.drop_through_duration*Engine.physics_ticks_per_second)+2
		if frame-last_drop_frame>=interval:
			if drop_attempts>=8:stop("module_transit_drop_budget",frame);return requested
			_request(&"drop_through",requested);drop_attempts+=1;last_drop_frame=frame
	return requested
