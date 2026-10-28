extends RefCounted
## Existing exact-union terrain art and official Plains art; no collider writes.
static func install(world: Node2D, module: PlatformingModule, data: Dictionary) -> void:
	module.terrain_candidate_preview = true
	module.queue_redraw()
	var solids: Array[Rect2] = []
	for i: int in data.platforms.size():
		if i not in data.get("one_way_platform_indices", []):
			var p: Array = data.platforms[i]
			solids.append(Rect2(p[0],p[1],p[2],p[3]))
	var paint := PlainsTileComposer.build_rectangles(solids)
	if paint != null:
		paint.z_index = -2
		world.add_child(paint)
	var backdrop := PixelPlainsParallax.new()
	world.add_child(backdrop)
	backdrop.surface.modulate = Color(.72,.78,.84,1.)
	var harp := PixelPlainsScenery.new()
	harp.position = Vector2(200,-2)
	harp.z_index = -3
	world.add_child(harp)

	for child: Node in world.get_children():
		if child is ShotLatch: child.region_presentation = true
	var rope := BridgeRopes.new()
	rope.z_index = -3
	world.add_child(rope)

class BridgeRopes extends Node2D:
	func _draw() -> void:
		var points := PackedVector2Array([Vector2(1324,478),Vector2(1400,492),Vector2(1480,520),Vector2(1560,546),Vector2(1640,564),Vector2(1736,556)])
		draw_polyline(points,Color("a66d45"),2.)
		for pair: Vector4 in [Vector4(1340,481,1340,538),Vector4(1450,510,1450,538),Vector4(1510,530,1510,598),Vector4(1600,556,1600,598),Vector4(1700,560,1700,618)]:
			draw_line(Vector2(pair.x,pair.y),Vector2(pair.z,pair.w),Color("6e9180"),2.)
