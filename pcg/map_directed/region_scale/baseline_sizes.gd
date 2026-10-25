extends SceneTree
func _initialize()->void:run.call_deferred()
func run()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
	var rows:Array=[]
	for seed_value:String in ["valley-comparison-0","valley-comparison-1","valley-comparison-2","valley-comparison-3","valley-comparison-4"]:
		for difficulty:String in ["intro","advanced"]:
			var g:=PlainsRegionGenerator.new();g.root_bell_mode="v3"
			var result:=g.generate(seed_value,PlayerTuning.load_default(),false,"",difficulty)
			if not result.ok:push_error("formal baseline generation failed");quit(2);return
			var m:Dictionary=result.manifest
			rows.append({"seed":seed_value,"difficulty":difficulty,"version":m.version,"manifest_hash":m.manifest_hash,
				"places":m.areas.size(),"modules":m.nodes.size(),"edges":m.connections.size(),"bounds":m.world_bounds,"rewards":m.rewards.size(),"enemies":m.enemies.size()})
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"Actual current main formal v12 intro and advanced single-map generator sizes; two-map total is a separate campaign scope","rows":rows}));f.close();quit(0)
