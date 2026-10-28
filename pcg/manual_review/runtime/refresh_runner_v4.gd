extends "refresh_runner_v3.gd"
## Read-only scheduling from the actual ferry and hazard definitions.
func condition_met(state: String) -> bool:
	if not super.condition_met(state):return false
	var command: Dictionary=plan[plan_index]
	if not command.has("requires_transfer_window"):return true
	var query: Dictionary=command.requires_transfer_window
	var ferry: ModuleMovingPlatform=null
	var hazard: ModuleSawHazard=null
	for body: ModuleMovingPlatform in context.module.moving_platforms:
		if str(body.definition.platform_id)==str(query.carrier):ferry=body
	for saw: ModuleSawHazard in context.module.hazards:
		if str(saw.definition.source_id)==str(query.hazard):hazard=saw
	if ferry==null or hazard==null:return false
	var phase:=fposmod(context.module.clock/ferry.definition.period()+ferry.definition.initial_phase,1.)
	var departure: float=(float(query.departure_phase)-phase)*ferry.definition.period()
	var all_above:=true;var all_below:=true
	for step: int in 13:
		var clock: float=context.module.clock+departure-.05+step*.05
		var angle:=TAU*(clock/hazard.definition.period+hazard.definition.initial_phase)
		var cy: float=hazard.definition.origin.y+hazard.definition.travel.y*sin(angle)
		all_above=all_above and cy<=float(query.maximum_upper_y)
		all_below=all_below and cy>=float(query.minimum_lower_y)
	return all_above or all_below
