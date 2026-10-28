extends SceneTree
## Run against the actual latest game project, never the research physics clone.
## Read-only generator measurements; no pretend full-route physics certificate.
func _initialize() -> void:run.call_deferred()
func run() -> void:
	var output:="";var capture:=""
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--output="):output=argument.trim_prefix("--output=")
		if argument.begins_with("--capture="):capture=argument.trim_prefix("--capture=")
	var rows: Array=[]
	for seed_value: String in ["valley-comparison-0","valley-comparison-1","valley-comparison-2","valley-comparison-3","valley-comparison-4"]:
		var tuning:=PlayerTuning.load_default();var generator:=PlainsRegionGenerator.new()
		generator.root_bell_mode="v3" # DemoApp's currently admitted default
		var actual_seed:=PlainsRegionCampaign.seed_for(seed_value,1)
		var started:=Time.get_ticks_usec();var result:=generator.generate(actual_seed,tuning,false,"","intro")
		rows.append({"seed":seed_value,"ok":result.ok,"generation_usec":Time.get_ticks_usec()-started,
			"manifest":result.get("manifest",{}),"memory_static_bytes":OS.get_static_memory_usage(),
			"generator_source_sha256":FileAccess.get_sha256("res://scripts/generation/plains_region_generator.gd"),
			"player_tuning_sha256":FileAccess.get_sha256("res://config/player_tuning.json")})
	var payload:={"scope":"Actual main game generator, intro full region, same base jump/recoil capability; structural comparison only, not played-through result","rows":rows}
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(payload));file.close()
	if capture.is_empty():quit(0);return
	var app:=DemoApp.new();app.meta_persistence_enabled=false;root.add_child(app)
	if not app.start_plains("valley-comparison-0"):quit(2);return
	for unused: int in 12:await physics_frame
	var stage:=app.stage as PlainsRegionStage
	if stage==null:quit(3);return
	var camera:=Camera2D.new();root.add_child(camera);camera.make_current()
	var bounds:Rect2=stage.bounds
	app._run_camera.set_process(false);app._run_camera.set_physics_process(false)
	app._run_camera.enabled=false
	camera.make_current()
	camera.position=bounds.get_center()
	camera.zoom=Vector2.ONE*minf(float(root.get_visible_rect().size.x)/bounds.size.x,float(root.get_visible_rect().size.y)/bounds.size.y)*.82
	camera.position_smoothing_enabled=false;camera.force_update_scroll()
	app.process_mode=Node.PROCESS_MODE_DISABLED
	stage.map_view.visible=false
	# Disable only the camera follower/UI; original generated world stays live.
	for child: Node in app.get_children():
		if child is CanvasLayer and not child is PixelPlainsParallax:child.visible=false
		if child is Control:child.visible=false
	await process_frame;await RenderingServer.frame_post_draw
	var status:=root.get_texture().get_image().save_png(capture)
	print("BASELINE_CAPTURE ",JSON.stringify({"status":status,"bounds":[bounds.position.x,bounds.position.y,bounds.size.x,bounds.size.y],"manifest":stage.generated.manifest.manifest_hash,"actor_position":[app.controller.motor.position.x,app.controller.motor.position.y]}))
	app.abandon_run();app.queue_free();camera.queue_free();await process_frame;quit(0 if status==OK else 4)
