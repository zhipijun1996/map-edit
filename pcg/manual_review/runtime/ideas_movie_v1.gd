extends "review045_movie_v1.gd"
const LOOP=preload("../../prototype/creative_batches/batch30_blockn25/install_v1.gd")
const IDEA_DEFINITION=preload("ideas_definition_v1.gd")
func definition_for(data: Dictionary) -> PlatformingModuleDefinition:
	var original:=super.definition_for(data)
	LOOP.install(original,data)
	if data.get("route_spec",{}).get("from_port","")!=data.get("route_spec",{}).get("to_port",""):return original
	var result=IDEA_DEFINITION.new()
	for property: Dictionary in original.get_property_list():
		if int(property.usage)&PROPERTY_USAGE_STORAGE and property.name!="script":result.set(property.name,original.get(property.name))
	result.allow_same_port_return=true;return result
