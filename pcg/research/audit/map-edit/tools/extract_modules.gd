extends SceneTree
## Run in the minimal extraction project with unmodified, pinned game sources.
## This evaluates data factories only. It does not run or validate gameplay.
var entries: Array = []

func normalize(value: Variant) -> Variant:
	if value is Vector2: return [value.x,value.y]
	if value is Vector2i: return [value.x,value.y]
	if value is Rect2: return [value.position.x,value.position.y,value.size.x,value.size.y]
	if value is Resource:
		var result: Dictionary = {}
		for prop: Dictionary in value.get_property_list():
			if int(prop.usage) & PROPERTY_USAGE_SCRIPT_VARIABLE and prop.name != "script":
				result[prop.name] = normalize(value.get(prop.name))
		return result
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value: result[str(key)] = normalize(value[key])
		return result
	if value is Array or value is PackedInt32Array or value is PackedVector2Array:
		var result: Array = []
		for item: Variant in value: result.append(normalize(item))
		return result
	return value

func add_factory(path: String, method: String, args: Array, suffix: String) -> void:
	var script: Script = load("res://scripts/generation/"+path+".gd")
	var raw: Dictionary = script.callv(method,args)
	assert(not raw.is_empty(),path+"/"+suffix+" returned no geometry")
	entries.append({"id":path+"__"+suffix,"kind":"forest","path":"scripts/generation/"+path+".gd","method":method,"arguments":args,"data":normalize(raw)})

func _initialize() -> void:
	var directory := DirAccess.open("res://resources/generation/modules")
	var files := directory.get_files()
	files.sort()
	for file: String in files:
		if not file.ends_with(".tres"): continue
		var module: Resource = load("res://resources/generation/modules/"+file)
		assert(module != null,"Could not load module "+file)
		entries.append({"id":file.get_basename(),"kind":"resource","path":"resources/generation/modules/"+file,"data":normalize(module)})
	for family: String in ["forest_exploration_modules","forest_playful_module_variants"]:
		var script: Script = load("res://scripts/generation/"+family+".gd")
		for row: Dictionary in script.call("catalogue"):
			add_factory(family,"build",[row.id],str(row.id))
	for id: String in ["seven_bough_reveal","z_descending_return"]:
		for variant: int in 2: add_factory("forest_exploration_places","build",[id,variant],id+"_v"+str(variant))
	for family: String in ["forest_exploration_fallen_trunk","forest_exploration_fruit_crossing"]:
		for variant: int in 2: add_factory(family,"build",[variant],"v"+str(variant))
	for id: String in ["arch_four","bridge_five","recoil_hook","recoil_hook_recoil","hook_hook"]:
		add_factory("forest_air_chain_geometry","build",[id],id)
	for id: String in ["deep_zeroR","shallow"]: add_factory("forest_hollow_trunk_geometry","build",[id],id)
	for method: String in ["build_cavity","build_cavity_elbow","build_aircatch"]:
		add_factory("forest_hollow_trunk_geometry",method,[],method.trim_prefix("build_"))
	for method: String in ["build","build_shared_upper","build_cavity"]:
		add_factory("forest_hollow_upper_candidate",method,[],method)
	for method: String in ["build","build_narrow"]: add_factory("forest_directional_geometry",method,[],method)
	for family: String in ["forest_vertical_chain_geometry","forest_bible_backbranch_geometry","forest_thorn_mouth_geometry"]:
		add_factory(family,"build",[],"default")
	var out := FileAccess.open("res://extracted.json",FileAccess.WRITE)
	out.store_string(JSON.stringify(entries,"\t"))
	out.close()
	print("EXTRACTION_OK ",entries.size())
	quit(0)
