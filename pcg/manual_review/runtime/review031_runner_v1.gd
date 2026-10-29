extends "clarified_three_runner_v5.gd"
## AIR INOUT support is an explicit boundary state, never a recovery floor.
func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	if data.get("approved_implementation",{}).get("reviewId","")!="196":return super.definition_for(data)
	var ordinary:=data.duplicate(true);ordinary.erase("air_port_contracts")
	var original:=super.definition_for(ordinary);var result=AIR_DEFINITION.new()
	for property: Dictionary in original.get_property_list():
		if int(property.usage)&PROPERTY_USAGE_STORAGE and property.name!="script":result.set(property.name,original.get(property.name))
	for port: Dictionary in data.get("air_port_contracts",[]):result.air_points.append(Vector2(port.stagingPosition[0],port.stagingPosition[1]))
	return result
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if data.has("review031_ingress_velocity"):
		motor.normal_velocity=Vector2(data.review031_ingress_velocity[0],data.review031_ingress_velocity[1]);context.anchor_ready=true
