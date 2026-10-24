extends SceneTree
## Real DemoApp full-world rendering; camera-only inspection, never a route proof.
var app: DemoApp
var output_dir := ""
var region := "plains"
var seed_value := "l4-baseline-00"
var map_index := 2
var forest_layout := ""
var capture_size := Vector2i(4096,2304)

func _initialize() -> void:
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output_dir=arg.trim_prefix("--output-dir=")
		elif arg.begins_with("--region="): region=arg.trim_prefix("--region=")
		elif arg.begins_with("--seed="): seed_value=arg.trim_prefix("--seed=")
		elif arg.begins_with("--map="): map_index=int(arg.trim_prefix("--map="))
		elif arg.begins_with("--layout="): forest_layout=arg.trim_prefix("--layout=")
		else: push_error("Unknown capture argument");quit(2);return
	run.call_deferred()

func freeze_callbacks(node: Node) -> void:
	node.set_process(false)
	node.set_physics_process(false)
	# Keep collision objects registered. Only callbacks are frozen for stills.
	for child: Node in node.get_children(): freeze_callbacks(child)

func hide_hud(node: Node) -> void:
	if node is CanvasLayer:
		# The backdrop and foreground are screen-space world presentation layers.
		if node is UnderworldParallax or node is UnderworldForeground: return
		(node as CanvasLayer).visible=false
	for child: Node in node.get_children(): hide_hud(child)

func refresh_presentation(node: Node) -> void:
	if node is UnderworldParallax: (node as UnderworldParallax)._update()
	var script: Script=node.get_script() as Script
	if script!=null and script.resource_path.ends_with("underworld_presentation.gd"):
		node.call("refresh")
	for child: Node in node.get_children(): refresh_presentation(child)

func run() -> void:
	if DisplayServer.get_name()=="headless" or output_dir.is_empty():
		push_error("Actual rendered capture requires a display and output directory");quit(2);return
	if region not in ["plains","thorn_forest"] or map_index not in [1,2]:
		push_error("Unsupported region/map");quit(2);return
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_DISABLED
	root.content_scale_size=Vector2i.ZERO
	root.size=capture_size
	app=DemoApp.new()
	app.meta_persistence_enabled=false
	root.add_child(app)
	await process_frame
	var started: bool=app.start_debug_region(StringName(region),map_index,seed_value,
		ThornForestRegionGenerator.DEPTH_VERSION if not forest_layout.is_empty() else "",forest_layout)
	if not started:
		push_error("Actual debug entry rejected");quit(1);return
	for unused: int in 8:
		await physics_frame
		await process_frame
	if not app.stage is PlainsRegionStage or not (app.stage as PlainsRegionStage).assembly_ok:
		push_error("Actual world assembly failed");quit(1);return
	var stage:=app.stage as PlainsRegionStage
	var manifest: Dictionary=stage.generated.manifest
	var player_before:=app.player.global_position
	freeze_callbacks(app)
	hide_hud(app)
	var camera:=app._run_camera as Camera2D
	var initial_camera:=camera.global_position
	var initial_zoom:=camera.zoom
	var bounds:=stage.bounds.grow(100.0)
	camera.position_smoothing_enabled=false
	camera.offset=Vector2.ZERO
	camera.ignore_rotation=true
	camera.limit_left=-10000000;camera.limit_right=10000000
	camera.limit_top=-10000000;camera.limit_bottom=10000000
	camera.global_position=bounds.get_center()
	var fit:=minf(float(capture_size.x)/bounds.size.x,float(capture_size.y)/bounds.size.y)
	camera.zoom=Vector2.ONE*fit
	camera.reset_smoothing()
	camera.force_update_scroll()
	refresh_presentation(app)
	for unused: int in 4: await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(output_dir)
	var image:=root.get_texture().get_image()
	var path:=output_dir.path_join("whole-map.png")
	var error:=image.save_png(path)
	var receipt: Dictionary={"schema":"map-notes/actual-whole-map-capture/v1","region":region,"root_seed":seed_value,"map_index":map_index,
		"source_game_commit":OS.get_environment("MAP_CAPTURE_GAME_COMMIT"),"engine":Engine.get_version_info(),
		"manifest_hash":manifest.manifest_hash,"generator_version":manifest.version,"layout":manifest.get("layout_version","connected_region"),
		"family":manifest.get("family",""),"area_count":manifest.areas.size(),"connection_count":manifest.connections.size(),
		"world_bounds":[stage.bounds.position.x,stage.bounds.position.y,stage.bounds.size.x,stage.bounds.size.y],
		"capture_bounds":[bounds.position.x,bounds.position.y,bounds.size.x,bounds.size.y],"camera_center":[camera.get_screen_center_position().x,camera.get_screen_center_position().y],
		"zoom":fit,"viewport":[root.size.x,root.size.y],"image_size":[image.get_width(),image.get_height()],
		"image_sha256":FileAccess.get_sha256(path),"save_error":error,"player_before":[player_before.x,player_before.y],
		"player_after":[app.player.global_position.x,app.player.global_position.y],"player_was_moved":app.player.global_position!=player_before,
		"initial_camera":[initial_camera.x,initial_camera.y],"initial_zoom":[initial_zoom.x,initial_zoom.y],
		"inspection_changes":["fit whole existing world with camera","HUD hidden","actor callbacks frozen after eight initial physics frames"],
		"scope":"actual assembled game scene rendered by Godot; not a new-algorithm playable map or route verification"}
	FileAccess.open(output_dir.path_join("receipt.json"),FileAccess.WRITE).store_string(JSON.stringify(receipt,"  ")+"\n")
	# The trace view may not be used as playability evidence.
	if error!=OK or image.get_size()!=capture_size or app.player.global_position!=player_before:
		push_error("Capture integrity failed");quit(1);return
	# Image and receipt are sealed. Drop the 4K rendering load before the existing
	# 1000ms audio-release check; do not enlarge that original cleanup budget.
	app.hide()
	root.size=Vector2i(640,360)
	for layer: Node in app.find_children("*","CanvasLayer",true,false):
		(layer as CanvasLayer).visible=false
	for unused: int in 3: await process_frame
	app.abandon_run()
	var clean: bool=await load("res://tests/audio_teardown.gd").drain_world(app)
	app.free()
	for unused: int in 3: await process_frame
	print("WHOLE MAP CAPTURE: PASS ",region," ",seed_value," ",receipt.layout)
	quit(0 if clean else 1)
