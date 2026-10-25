extends RefCounted
## Main 26e7f2a4 native32px Underworld terrain and original parallax.
## This consumer creates no bodies and never edits geometry or actor resources.
static func install(world: Node2D, module: PlatformingModule, data: Dictionary) -> void:
	world.set_meta("underworld_formal_style",true)
	module.terrain_candidate_preview=true;module.queue_redraw()
	var solids: Array[Rect2]=[]
	for i: int in data.platforms.size():
		if i not in data.get("one_way_platform_indices",[]):
			var p: Array=data.platforms[i];solids.append(Rect2(p[0],p[1],p[2],p[3]))
	var terrain:=UnderworldTerrain.build(solids);terrain.z_index=-2;world.add_child(terrain)
	var backdrop:=UnderworldParallax.new()
	backdrop.configure(world.get_viewport().get_camera_2d(),Rect2(data.world_bounds[0],data.world_bounds[1],data.world_bounds[2],data.world_bounds[3]),{"seed":"valley-complete-v1"})
	world.add_child(backdrop)
	UnderworldActors.install(world)
	for child: Node in world.get_children():
		if child is ShotLatch:child.set_region_presentation(true)
	for ferry: ModuleMovingPlatform in module.moving_platforms:ferry.set_painted_enabled(false);ferry.queue_redraw()
